"""
Ticket Types Management Blueprint for TicketMe.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.extensions import db
from app.models.event import Event
from app.models.ticket_type import TicketType
from app.utils.decorators import role_required

ticket_types_bp = Blueprint('ticket_types', __name__, url_prefix='/ticket-types')

@ticket_types_bp.route('/')
@login_required
@role_required('Administrator', 'Manager')
def index():
    event_id = request.args.get('event_id', type=int)
    events = Event.query.order_by(Event.name.asc()).all()

    query = TicketType.query
    if event_id:
        query = query.filter(TicketType.event_id == event_id)

    ticket_types = query.order_by(TicketType.created_at.desc()).all()
    return render_template('ticket_types/index.html', ticket_types=ticket_types, events=events, selected_event_id=event_id)

@ticket_types_bp.route('/create', methods=['GET', 'POST'])
@login_required
@role_required('Administrator', 'Manager')
def create():
    events = Event.query.filter(Event.status.in_(['Upcoming', 'Ongoing'])).order_by(Event.name.asc()).all()

    if request.method == 'POST':
        event_id = request.form.get('event_id', type=int)
        preset_name = request.form.get('preset_name', '').strip()
        custom_name = request.form.get('custom_name', '').strip()
        name = request.form.get('name', '').strip()
        
        if not name:
            name = custom_name if preset_name == '__custom__' else preset_name

        price = request.form.get('price', type=float)
        quantity = request.form.get('total_quantity', type=int)
        status = request.form.get('status', 'Active')

        if not event_id or not name or price is None or quantity is None:
            flash('Event, Ticket Type, Price, and Total Quantity are required.', 'warning')
            return redirect(url_for('ticket_types.create'))

        ticket_type = TicketType(
            event_id=event_id,
            name=name,
            price=price,
            total_quantity=quantity,
            available_quantity=quantity,
            status=status
        )
        db.session.add(ticket_type)
        db.session.commit()

        flash(f'Ticket type "{name}" added successfully.', 'success')
        return redirect(url_for('ticket_types.index', event_id=event_id))

    selected_event_id = request.args.get('event_id', type=int)
    return render_template('ticket_types/create.html', events=events, selected_event_id=selected_event_id)

@ticket_types_bp.route('/<int:tt_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('Administrator', 'Manager')
def edit(tt_id):
    tt = TicketType.query.get_or_404(tt_id)
    events = Event.query.order_by(Event.name.asc()).all()

    if request.method == 'POST':
        tt.event_id = request.form.get('event_id', type=int)
        
        preset_name = request.form.get('preset_name', '').strip()
        custom_name = request.form.get('custom_name', '').strip()
        name = request.form.get('name', '').strip()
        
        if not name:
            name = custom_name if preset_name == '__custom__' else preset_name
            
        if name:
            tt.name = name

        new_price = request.form.get('price', type=float)
        new_total_qty = request.form.get('total_quantity', type=int)
        tt.status = request.form.get('status', tt.status)

        if new_total_qty is not None and new_total_qty != tt.total_quantity:
            qty_diff = new_total_qty - tt.total_quantity
            tt.total_quantity = new_total_qty
            tt.available_quantity = max(0, tt.available_quantity + qty_diff)

        if new_price is not None:
            tt.price = new_price

        db.session.commit()
        flash(f'Ticket type "{tt.name}" updated successfully.', 'success')
        return redirect(url_for('ticket_types.index', event_id=tt.event_id))

    return render_template('ticket_types/edit.html', tt=tt, events=events)

@ticket_types_bp.route('/<int:tt_id>/delete', methods=['POST'])
@login_required
@role_required('Administrator', 'Manager')
def delete(tt_id):
    tt = TicketType.query.get_or_404(tt_id)
    name = tt.name
    event_id = tt.event_id
    db.session.delete(tt)
    db.session.commit()
    flash(f'Ticket type "{name}" deleted successfully.', 'success')
    return redirect(url_for('ticket_types.index', event_id=event_id))

