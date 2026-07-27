"""
TicketType Model for TicketMe.
"""
from datetime import datetime
from app.extensions import db

class TicketType(db.Model):
    __tablename__ = 'ticket_types'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False) # Regular, VIP, VVIP, Early Bird, etc.
    price = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    total_quantity = db.Column(db.Integer, nullable=False, default=100)
    available_quantity = db.Column(db.Integer, nullable=False, default=100)
    status = db.Column(db.String(20), nullable=False, default='Active') # Active, Inactive
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    bookings = db.relationship('Booking', backref='ticket_type', lazy=True)
    tickets = db.relationship('Ticket', backref='ticket_type', lazy=True)

    def __repr__(self):
        return f'<TicketType {self.name} for Event #{self.event_id}>'
