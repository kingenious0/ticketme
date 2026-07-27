"""
Customer Model for TicketMe.
"""
from datetime import datetime
from app.extensions import db

class Customer(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False, index=True)
    email = db.Column(db.String(120), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    bookings = db.relationship('Booking', backref='customer', lazy=True, cascade='all, delete-orphan')
    tickets = db.relationship('Ticket', backref='customer', lazy=True)

    def __repr__(self):
        return f'<Customer {self.name} - {self.phone_number}>'
