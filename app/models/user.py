"""
User Model & RBAC Definitions.
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone_number = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(30), nullable=False, default='Ticket Officer')  # Administrator, Manager, Ticket Officer, Security Officer
    status = db.Column(db.String(20), nullable=False, default='Active')        # Active, Inactive
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    bookings = db.relationship('Booking', backref='creator', lazy=True)
    payments_received = db.relationship('Payment', backref='receiver', lazy=True)
    verifications = db.relationship('Ticket', backref='verifier', lazy=True)
    audit_logs = db.relationship('AuditLog', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == 'Manager'

    @property
    def is_event_manager(self):
        return self.role == 'Manager'

    @property
    def is_manager(self):
        return self.role == 'Manager'

    @property
    def is_ticket_officer(self):
        return self.role in ['Manager', 'Ticket Officer']

    @property
    def is_check_in_officer(self):
        return True

    @property
    def is_security_officer(self):
        return True

    def __repr__(self):
        return f'<User {self.email} ({self.role})>'
