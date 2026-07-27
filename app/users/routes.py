"""
User Management Blueprint for TicketMe.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.user import User
from app.utils.decorators import role_required

users_bp = Blueprint('users', __name__, url_prefix='/users')

@users_bp.route('/')
@login_required
@role_required('Manager')
def index():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('users/index.html', users=users)

@users_bp.route('/create', methods=['GET', 'POST'])
@login_required
@role_required('Manager')
def create():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        phone_number = request.form.get('phone_number', '').strip()
        role = request.form.get('role', 'Ticket Officer')
        password = request.form.get('password', '')

        if not full_name or not email or not password:
            flash('Full Name, Email, and Password are required.', 'warning')
            return redirect(url_for('users.create'))

        existing = User.query.filter_by(email=email).first()
        if existing:
            flash('A user with this email address already exists.', 'danger')
            return redirect(url_for('users.create'))

        user = User(
            full_name=full_name,
            email=email,
            phone_number=phone_number,
            role=role,
            status='Active'
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash(f'User {email} created successfully.', 'success')
        return redirect(url_for('users.index'))

    return render_template('users/create.html')

@users_bp.route('/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('Manager')
def edit(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        user.full_name = request.form.get('full_name', '').strip()
        user.phone_number = request.form.get('phone_number', '').strip()
        user.role = request.form.get('role', user.role)
        user.status = request.form.get('status', user.status)

        new_password = request.form.get('password', '').strip()
        if new_password:
            user.set_password(new_password)

        db.session.commit()
        flash(f'User {user.email} updated successfully.', 'success')
        return redirect(url_for('users.index'))

    return render_template('users/edit.html', user=user)

@users_bp.route('/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@role_required('Manager')
def toggle_status(user_id):
    user = User.query.get_or_404(user_id)
    user.status = 'Inactive' if user.status == 'Active' else 'Active'
    db.session.commit()
    flash(f"User '{user.email}' status changed to {user.status}.", 'info')
    return redirect(url_for('users.index'))

@users_bp.route('/<int:user_id>/delete', methods=['POST'])
@login_required
@role_required('Manager')
def delete(user_id):
    if current_user.id == user_id:
        flash('You cannot delete your own account while logged in.', 'danger')
        return redirect(url_for('users.index'))
    user = User.query.get_or_404(user_id)
    email = user.email
    db.session.delete(user)
    db.session.commit()
    flash(f'User "{email}" deleted successfully.', 'success')
    return redirect(url_for('users.index'))

