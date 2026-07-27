"""
Event Model for TicketMe.
"""
from datetime import datetime
from app.extensions import db

class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    venue = db.Column(db.String(150), nullable=False)
    event_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=True)
    banner_image = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='Upcoming') # Upcoming, Ongoing, Completed, Cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    ticket_types = db.relationship('TicketType', backref='event', lazy=True, cascade='all, delete-orphan')
    bookings = db.relationship('Booking', backref='event', lazy=True)
    tickets = db.relationship('Ticket', backref='event', lazy=True)

    def __repr__(self):
        return f'<Event {self.name} on {self.event_date}>'
