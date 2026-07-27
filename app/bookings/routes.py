"""
Booking Engine Blueprint for TicketMe.
"""
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.event import Event
from app.models.customer import Customer
from app.models.ticket_type import TicketType
from app.models.booking import Booking
from app.utils.decorators import role_required

bookings_bp = Blueprint('bookings', __name__, url_prefix='/bookings')

def generate_booking_number():
    year = datetime.now().year
    last_booking = Booking.query.filter(Booking.booking_number.like(f'BK-{year}-%'))\
        .order_by(Booking.id.desc()).first()
    if last_booking:
        try:
            last_seq = int(last_booking.booking_number.rsplit('-', 1)[1])
            new_seq = last_seq + 1
        except (ValueError, IndexError):
            new_seq = 1
    else:
        new_seq = 1
    return f"BK-{year}-{new_seq:05d}"

@bookings_bp.route('/')
@login_required
@role_required('Administrator', 'Manager', 'Ticket Officer')
def index():
    search = request.args.get('search', '').strip()
    status = request.args.get('status', '').strip()
    page = request.args.get('page', 1, type=int)

    query = Booking.query.join(Customer).join(Event)
    if search:
        query = query.filter(
            (Booking.booking_number.ilike(f'%{search}%')) |
            (Customer.name.ilike(f'%{search}%')) |
            (Customer.phone_number.ilike(f'%{search}%')) |
            (Event.name.ilike(f'%{search}%'))
        )
    if status:
        query = query.filter(Booking.status == status)

    pagination = query.order_by(Booking.created_at.desc()).paginate(page=page, per_page=15, error_out=False)
    return render_template('bookings/index.html', pagination=pagination, search=search, selected_status=status)

@bookings_bp.route('/create', methods=['GET', 'POST'])
@login_required
@role_required('Administrator', 'Manager', 'Ticket Officer')
def create():
    events = Event.query.filter(Event.status.in_(['Upcoming', 'Ongoing'])).order_by(Event.name.asc()).all()
    customers = Customer.query.order_by(Customer.name.asc()).all()

    if request.method == 'POST':
        event_id = request.form.get('event_id', type=int)
        customer_id = request.form.get('customer_id', type=int)
        ticket_type_id = request.form.get('ticket_type_id', type=int)
        quantity = request.form.get('quantity', type=int, default=1)

        if not event_id or not customer_id or not ticket_type_id or quantity <= 0:
            flash('Please select an Event, Customer, Ticket Type, and valid Quantity.', 'warning')
            return redirect(url_for('bookings.create'))

        ticket_type = TicketType.query.get_or_404(ticket_type_id)

        if ticket_type.available_quantity < quantity:
            flash(f'Only {ticket_type.available_quantity} tickets available for {ticket_type.name}. Requested: {quantity}.', 'danger')
            return redirect(url_for('bookings.create'))

        unit_price = ticket_type.price
        total_amount = unit_price * quantity
        booking_number = generate_booking_number()

        booking = Booking(
            booking_number=booking_number,
            event_id=event_id,
            customer_id=customer_id,
            ticket_type_id=ticket_type_id,
            quantity=quantity,
            unit_price=unit_price,
            total_amount=total_amount,
            status='Pending',
            user_id=current_user.id
        )

        db.session.add(booking)
        db.session.commit()

        flash(f'Booking {booking_number} created successfully. Proceed to record payment.', 'success')
        return redirect(url_for('bookings.detail', booking_id=booking.id))

    return render_template('bookings/create.html', events=events, customers=customers)

@bookings_bp.route('/<int:booking_id>')
@login_required
def detail(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    return render_template('bookings/detail.html', booking=booking)

@bookings_bp.route('/<int:booking_id>/cancel', methods=['POST'])
@login_required
@role_required('Administrator', 'Manager')
def cancel(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.status == 'Cancelled':
        flash('Booking is already cancelled.', 'info')
        return redirect(url_for('bookings.detail', booking_id=booking_id))

    # If booking was confirmed, return quantity to ticket type
    if booking.status == 'Confirmed':
        booking.ticket_type.available_quantity += booking.quantity
        for t in booking.tickets:
            t.status = 'Cancelled'

    booking.status = 'Cancelled'
    db.session.commit()

    flash(f'Booking {booking.booking_number} has been cancelled.', 'danger')
    return redirect(url_for('bookings.detail', booking_id=booking_id))

@bookings_bp.route('/api/ticket-types/<int:event_id>')
@login_required
def get_ticket_types_for_event(event_id):
    tts = TicketType.query.filter_by(event_id=event_id, status='Active').all()
    data = [{'id': t.id, 'name': t.name, 'price': float(t.price), 'available': t.available_quantity} for t in tts]
    return jsonify(data)

@bookings_bp.route('/<int:booking_id>/delete', methods=['POST'])
@login_required
@role_required('Administrator', 'Manager')
def delete(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    b_num = booking.booking_number
    if booking.status == 'Confirmed':
        booking.ticket_type.available_quantity += booking.quantity
    
    db.session.delete(booking)
    db.session.commit()
    flash(f'Booking {b_num} deleted successfully.', 'success')
    return redirect(url_for('bookings.index'))

