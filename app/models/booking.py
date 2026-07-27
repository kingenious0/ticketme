"""
Booking Model for TicketMe.
"""
from datetime import datetime
from app.extensions import db

class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)
    booking_number = db.Column(db.String(30), unique=True, nullable=False, index=True) # BK-2026-00001
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    ticket_type_id = db.Column(db.Integer, db.ForeignKey('ticket_types.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending') # Pending, Confirmed, Cancelled
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) # Staff who booked
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    payments = db.relationship('Payment', backref='booking', lazy=True, cascade='all, delete-orphan')
    tickets = db.relationship('Ticket', backref='booking', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Booking {self.booking_number} ({self.status})>'
