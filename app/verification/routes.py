"""
Ticket Verification Gate Blueprint for TicketMe.
Security Officer Portal for QR Code Scanning & Double Entry Prevention.
"""
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.ticket import Ticket
from app.models.audit_log import AuditLog
from app.utils.decorators import role_required

verification_bp = Blueprint('verification', __name__, url_prefix='/verification')

@verification_bp.route('/')
@login_required
@role_required('Administrator', 'Manager', 'Security Officer', 'Ticket Officer')
def index():
    return render_template('verification/index.html')

@verification_bp.route('/check', methods=['GET', 'POST'])
@login_required
@role_required('Administrator', 'Manager', 'Security Officer', 'Ticket Officer')
def check():
    ticket_number = request.args.get('ticket_number', '').strip() or request.form.get('ticket_number', '').strip()

    # Parse raw QR code content if formatted like TICKETME:TKT-2026-XXXXX:1
    if ticket_number.startswith('TICKETME:'):
        parts = ticket_number.split(':')
        if len(parts) >= 2:
            ticket_number = parts[1]

    if not ticket_number:
        flash('Please enter or scan a valid ticket number.', 'warning')
        return redirect(url_for('verification.index'))

    ticket = Ticket.query.filter_by(ticket_number=ticket_number).first()

    return render_template('verification/result.html', ticket=ticket, queried_number=ticket_number)

@verification_bp.route('/<int:ticket_id>/mark-used', methods=['POST'])
@login_required
@role_required('Administrator', 'Manager', 'Security Officer', 'Ticket Officer')
def mark_used(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)

    if ticket.status == 'Used':
        flash(f'Ticket {ticket.ticket_number} was already marked as USED on {ticket.verified_at.strftime("%Y-%m-%d %H:%M:%S")}.', 'warning')
        return redirect(url_for('verification.check', ticket_number=ticket.ticket_number))

    if ticket.status == 'Cancelled':
        flash(f'Ticket {ticket.ticket_number} is CANCELLED and cannot be used.', 'danger')
        return redirect(url_for('verification.check', ticket_number=ticket.ticket_number))

    ticket.status = 'Used'
    ticket.verified_by_id = current_user.id
    ticket.verified_at = datetime.utcnow()

    log = AuditLog(
        user_id=current_user.id,
        action='VERIFY_TICKET',
        details=f"Ticket {ticket.ticket_number} verified and marked USED at {ticket.event.name}.",
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()

    flash(f'SUCCESS: Ticket {ticket.ticket_number} verified! Entry granted.', 'success')
    return render_template('verification/confirmed.html', ticket=ticket)
