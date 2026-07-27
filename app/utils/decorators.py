"""
Custom decorators for Role-Based Access Control (RBAC).
"""
from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def role_required(*roles):
    """
    Decorator that restricts access to users with specified roles.
    Example: @role_required('Administrator', 'Event Manager')
    """
    allowed = set(roles)
    if 'Event Manager' in allowed or 'Manager' in allowed:
        allowed.update(['Event Manager', 'Manager'])
    if 'Check-In Officer' in allowed or 'Security Officer' in allowed:
        allowed.update(['Check-In Officer', 'Security Officer'])

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))
            if current_user.role not in allowed:
                flash('Access denied: You do not have permission to view this resource.', 'danger')
                if current_user.role in ['Check-In Officer', 'Security Officer']:
                    return redirect(url_for('verification.index'))
                return redirect(url_for('dashboard.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
