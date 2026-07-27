"""
Ticket Management & PDF Generation Blueprint for TicketMe.
"""
from flask import Blueprint, render_template, request, send_file, flash, redirect, url_for
from flask_login import login_required
from app.models.ticket import Ticket
from app.models.booking import Booking
from app.utils.pdf_generator import generate_ticket_pdf
from app.utils.decorators import role_required

tickets_bp = Blueprint('tickets', __name__, url_prefix='/tickets')

@tickets_bp.route('/')
@login_required
def index():
    search = request.args.get('search', '').strip()
    status = request.args.get('status', '').strip()
    page = request.args.get('page', 1, type=int)

    query = Ticket.query
    if search:
        query = query.filter(Ticket.ticket_number.ilike(f'%{search}%'))
    if status:
        query = query.filter(Ticket.status == status)

    pagination = query.order_by(Ticket.created_at.desc()).paginate(page=page, per_page=15, error_out=False)
    return render_template('tickets/index.html', pagination=pagination, search=search, selected_status=status)

@tickets_bp.route('/booking/<int:booking_id>')
@login_required
def booking_tickets(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    tickets = Ticket.query.filter_by(booking_id=booking_id).all()
    return render_template('tickets/booking_tickets.html', booking=booking, tickets=tickets)

@tickets_bp.route('/<int:ticket_id>')
@login_required
def detail(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    return render_template('tickets/detail.html', ticket=ticket)

@tickets_bp.route('/<int:ticket_id>/print')
@login_required
def print_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    return render_template('tickets/print.html', ticket=ticket)

@tickets_bp.route('/<int:ticket_id>/pdf')
@login_required
def pdf(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    pdf_buffer = generate_ticket_pdf(ticket)
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"Ticket_{ticket.ticket_number}.pdf",
        mimetype='application/pdf'
    )
