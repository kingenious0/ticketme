"""
Reports & Analytics Blueprint for TicketMe.
"""
import csv
import io
from datetime import datetime, date
from flask import Blueprint, render_template, request, Response, flash, redirect, url_for
from flask_login import login_required
from sqlalchemy import func
from app.extensions import db
from app.models.payment import Payment
from app.models.booking import Booking
from app.models.ticket import Ticket
from app.models.event import Event
from app.models.customer import Customer
from app.utils.decorators import role_required

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/')
@login_required
@role_required('Manager')
def index():
    # Overall summary stats
    total_revenue = db.session.query(func.coalesce(func.sum(Payment.amount), 0.00)).filter(Payment.payment_status == 'Paid').scalar()
    total_bookings = Booking.query.count()
    total_tickets = Ticket.query.count()
    total_customers = Customer.query.count()

    # Sales by event
    event_sales = db.session.query(
        Event.name,
        func.count(Booking.id).label('booking_count'),
        func.coalesce(func.sum(Booking.total_amount), 0.00).label('total_revenue')
    ).join(Booking, Event.id == Booking.event_id)\
     .filter(Booking.status == 'Confirmed')\
     .group_by(Event.id).all()

    # Sales by payment method
    method_sales = db.session.query(
        Payment.payment_method,
        func.count(Payment.id).label('transaction_count'),
        func.coalesce(func.sum(Payment.amount), 0.00).label('total_amount')
    ).filter(Payment.payment_status == 'Paid')\
     .group_by(Payment.payment_method).all()

    return render_template(
        'reports/index.html',
        total_revenue=total_revenue,
        total_bookings=total_bookings,
        total_tickets=total_tickets,
        total_customers=total_customers,
        event_sales=event_sales,
        method_sales=method_sales
    )

@reports_bp.route('/export/<report_type>')
@login_required
@role_required('Manager')
def export_csv(report_type):
    output = io.StringIO()
    writer = csv.writer(output)

    if report_type == 'payments':
        writer.writerow(['Payment Ref', 'Booking Ref', 'Customer', 'Amount (GHS)', 'Method', 'Txn Ref', 'Date'])
        payments = Payment.query.order_by(Payment.payment_date.desc()).all()
        for p in payments:
            writer.writerow([
                p.payment_number,
                p.booking.booking_number if p.booking else '',
                p.booking.customer.name if p.booking and p.booking.customer else '',
                f"{p.amount:.2f}",
                p.payment_method,
                p.transaction_reference or '',
                p.payment_date.strftime('%Y-%m-%d %H:%M:%S')
            ])
        filename = "TicketMe_Payments_Report.csv"

    elif report_type == 'tickets':
        writer.writerow(['Ticket Number', 'Booking Ref', 'Event', 'Customer', 'Ticket Type', 'Status', 'Verified At'])
        tickets = Ticket.query.order_by(Ticket.created_at.desc()).all()
        for t in tickets:
            writer.writerow([
                t.ticket_number,
                t.booking.booking_number if t.booking else '',
                t.event.name if t.event else '',
                t.customer.name if t.customer else '',
                t.ticket_type.name if t.ticket_type else '',
                t.status,
                t.verified_at.strftime('%Y-%m-%d %H:%M:%S') if t.verified_at else 'Unverified'
            ])
        filename = "TicketMe_Tickets_Report.csv"

    else:
        flash('Invalid report type requested.', 'danger')
        return redirect(url_for('reports.index'))

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )
