"""
Dashboard Blueprint for TicketMe.
"""
from datetime import datetime, date
from flask import Blueprint, render_template
from flask_login import login_required
from sqlalchemy import func
from app.extensions import db
from app.models.event import Event
from app.models.booking import Booking
from app.models.payment import Payment
from app.models.ticket import Ticket
from app.models.customer import Customer

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    today = date.today()

    # KPI 1: Today's Revenue
    todays_revenue = db.session.query(func.coalesce(func.sum(Payment.amount), 0.00))\
        .filter(func.date(Payment.payment_date) == today, Payment.payment_status == 'Paid').scalar()

    # KPI 2: Total Tickets Sold
    total_tickets_sold = db.session.query(func.count(Ticket.id)).scalar()

    # KPI 3: Upcoming Events Count
    upcoming_events_count = Event.query.filter(Event.status.in_(['Upcoming', 'Ongoing'])).count()

    # KPI 4: Active Bookings
    active_bookings_count = Booking.query.filter(Booking.status.in_(['Pending', 'Confirmed'])).count()

    # Recent Bookings & Payments
    recent_bookings = Booking.query.order_by(Booking.created_at.desc()).limit(5).all()
    recent_payments = Payment.query.order_by(Payment.payment_date.desc()).limit(5).all()
    upcoming_events = Event.query.filter(Event.status.in_(['Upcoming', 'Ongoing'])).order_by(Event.event_date.asc()).limit(5).all()

    return render_template(
        'dashboard/index.html',
        todays_revenue=todays_revenue,
        total_tickets_sold=total_tickets_sold,
        upcoming_events_count=upcoming_events_count,
        active_bookings_count=active_bookings_count,
        recent_bookings=recent_bookings,
        recent_payments=recent_payments,
        upcoming_events=upcoming_events
    )
