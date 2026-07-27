"""
Authentication Blueprint for TicketMe.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models.user import User
from app.models.audit_log import AuditLog

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash('Invalid email address or password.', 'danger')
            return redirect(url_for('auth.login'))

        if user.status != 'Active':
            flash('Your account has been deactivated. Please contact an administrator.', 'danger')
            return redirect(url_for('auth.login'))

        login_user(user, remember=remember)

        # Log action
        log = AuditLog(
            user_id=user.id,
            action='LOGIN',
            details=f"User {user.email} logged in successfully.",
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()

        flash(f'Welcome back, {user.full_name}!', 'success')
        next_page = request.args.get('next')
        if not next_page and user.role in ['Check-In Officer', 'Security Officer']:
            return redirect(url_for('verification.index'))
        return redirect(next_page or url_for('dashboard.index'))

    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    log = AuditLog(
        user_id=current_user.id,
        action='LOGOUT',
        details=f"User {current_user.email} logged out.",
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()

    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_pwd = request.form.get('current_password', '')
        new_pwd = request.form.get('new_password', '')
        confirm_pwd = request.form.get('confirm_password', '')

        if not current_user.check_password(current_pwd):
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('auth.change_password'))

        if len(new_pwd) < 6:
            flash('New password must be at least 6 characters long.', 'warning')
            return redirect(url_for('auth.change_password'))

        if new_pwd != confirm_pwd:
            flash('New passwords do not match.', 'danger')
            return redirect(url_for('auth.change_password'))

        current_user.set_password(new_pwd)
        db.session.commit()

        flash('Your password has been updated successfully.', 'success')
        return redirect(url_for('dashboard.index'))

    return render_template('auth/change_password.html')

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        phone_number = request.form.get('phone_number', '').strip()

        if not full_name:
            flash('Full name is required.', 'warning')
            return redirect(url_for('auth.profile'))

        current_user.full_name = full_name
        current_user.phone_number = phone_number
        db.session.commit()

        flash('Profile details updated successfully.', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('auth/profile.html')
