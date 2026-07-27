"""
Setting Model for TicketMe.
"""
from datetime import datetime
from app.extensions import db

class Setting(db.Model):
    __tablename__ = 'settings'

    id = db.Column(db.Integer, primary_key=True)
    business_name = db.Column(db.String(100), nullable=False, default='TicketMe Events')
    business_phone = db.Column(db.String(30), nullable=True, default='0200000000')
    business_email = db.Column(db.String(120), nullable=True, default='support@ticketme.com')
    business_address = db.Column(db.String(255), nullable=True, default='Accra, Ghana')
    currency = db.Column(db.String(10), nullable=False, default='GHS')
    receipt_footer = db.Column(db.Text, nullable=True, default='Thank you for booking with TicketMe. Keep your ticket QR safe for entry!')
    logo_path = db.Column(db.String(255), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Setting {self.business_name}>'
