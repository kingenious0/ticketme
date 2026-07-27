"""
Payment Model for TicketMe.
"""
from datetime import datetime
from app.extensions import db

class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    payment_number = db.Column(db.String(30), unique=True, nullable=False, index=True) # PAY-2026-00001
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.String(30), nullable=False) # Cash, MTN Mobile Money, Telecel Cash, Bank Transfer, Card
    transaction_reference = db.Column(db.String(100), nullable=True)
    payment_status = db.Column(db.String(20), nullable=False, default='Paid') # Pending, Paid, Refunded
    received_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Payment {self.payment_number} ({self.amount})>'
