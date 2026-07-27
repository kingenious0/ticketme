"""
Payment Recording Blueprint for TicketMe.
Automates Booking Confirmation & Ticket/QR Code Generation.
"""
import uuid
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.booking import Booking
from app.models.payment import Payment
from app.models.ticket import Ticket
from app.utils.qr_generator import generate_ticket_qr
from app.utils.decorators import role_required

payments_bp = Blueprint('payments', __name__, url_prefix='/payments')

def generate_payment_number():
    year = datetime.now().year
    last_pay = Payment.query.filter(Payment.payment_number.like(f'PAY-{year}-%'))\
        .order_by(Payment.id.desc()).first()
    if last_pay:
        try:
            last_seq = int(last_pay.payment_number.rsplit('-', 1)[1])
            new_seq = last_seq + 1
        except (ValueError, IndexError):
            new_seq = 1
    else:
        new_seq = 1
    return f"PAY-{year}-{new_seq:05d}"

def generate_ticket_number():
    year = datetime.now().year
    unique_suffix = uuid.uuid4().hex[:6].upper()
    return f"TKT-{year}-{unique_suffix}"

@payments_bp.route('/')
@login_required
@role_required('Administrator', 'Manager', 'Ticket Officer')
def index():
    search = request.args.get('search', '').strip()
    method = request.args.get('method', '').strip()
    page = request.args.get('page', 1, type=int)

    query = Payment.query.join(Booking)
    if search:
        query = query.filter(
            (Payment.payment_number.ilike(f'%{search}%')) |
            (Payment.transaction_reference.ilike(f'%{search}%')) |
            (Booking.booking_number.ilike(f'%{search}%'))
        )
    if method:
        query = query.filter(Payment.payment_method == method)

    pagination = query.order_by(Payment.payment_date.desc()).paginate(page=page, per_page=15, error_out=False)
    return render_template('payments/index.html', pagination=pagination, search=search, selected_method=method)

@payments_bp.route('/record/<int:booking_id>', methods=['GET', 'POST'])
@login_required
@role_required('Administrator', 'Manager', 'Ticket Officer')
def record(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    if booking.status == 'Confirmed':
        flash('Payment has already been recorded and booking is confirmed.', 'info')
        return redirect(url_for('bookings.detail', booking_id=booking.id))

    if booking.status == 'Cancelled':
        flash('Cannot record payment for a cancelled booking.', 'danger')
        return redirect(url_for('bookings.detail', booking_id=booking.id))

    if request.method == 'POST':
        payment_method = request.form.get('payment_method', 'Cash')
        transaction_reference = request.form.get('transaction_reference', '').strip()
        amount = request.form.get('amount', type=float, default=float(booking.total_amount))
        notes = request.form.get('notes', '').strip()

        if amount < float(booking.total_amount):
            flash(f'Payment amount (GHS {amount:.2f}) must meet or exceed total amount (GHS {booking.total_amount:.2f}).', 'danger')
            return redirect(url_for('payments.record', booking_id=booking.id))

        payment_number = generate_payment_number()

        payment = Payment(
            payment_number=payment_number,
            booking_id=booking.id,
            amount=amount,
            payment_method=payment_method,
            transaction_reference=transaction_reference if transaction_reference else None,
            payment_status='Paid',
            received_by_id=current_user.id,
            notes=notes if notes else None
        )
        db.session.add(payment)

        # 1. Update Booking Status -> Confirmed
        booking.status = 'Confirmed'

        # 2. Decrement TicketType stock
        if booking.ticket_type.available_quantity >= booking.quantity:
            booking.ticket_type.available_quantity -= booking.quantity
        else:
            booking.ticket_type.available_quantity = 0

        # 3. Generate Tickets & QR Codes for each unit
        generated_tickets = []
        for i in range(booking.quantity):
            ticket_no = generate_ticket_number()
            # Verification data encoded in QR
            qr_path = generate_ticket_qr(ticket_no, verification_data=f"TICKETME:{ticket_no}:{booking.event.id}")

            ticket = Ticket(
                ticket_number=ticket_no,
                booking_id=booking.id,
                customer_id=booking.customer_id,
                event_id=booking.event_id,
                ticket_type_id=booking.ticket_type_id,
                qr_code_path=qr_path,
                status='Unused'
            )
            db.session.add(ticket)
            generated_tickets.append(ticket)

        db.session.commit()

        flash(f'Payment {payment_number} recorded! Booking confirmed and {len(generated_tickets)} ticket(s) generated with QR codes.', 'success')
        return redirect(url_for('tickets.booking_tickets', booking_id=booking.id))

    return render_template('payments/record.html', booking=booking)
