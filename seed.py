"""
Seed script for TicketMe Event Ticketing System - Populates Manager and Ticket Officer accounts, events, and settings.
"""

import os
import pymysql
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

def auto_create_database():
    db_uri = os.getenv('DATABASE_URL') or os.getenv('SQLALCHEMY_DATABASE_URI', '')
    if not db_uri or 'mysql' not in db_uri:
        return
    try:
        clean_url = db_uri.replace('mysql+pymysql://', 'http://').replace('mysql://', 'http://')
        parsed = urlparse(clean_url)
        db_name = parsed.path.lstrip('/')
        host = parsed.hostname or 'localhost'
        port = parsed.port or 3306
        user = parsed.username or 'root'
        password = parsed.password or ''
        
        if db_name:
            conn = pymysql.connect(host=host, port=port, user=user, password=password)
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            conn.commit()
            conn.close()
            print(f"[+] Ensured MySQL database `{db_name}` exists on {host}:{port}.")
    except Exception as e:
        print(f"[!] Database auto-creation notice: {e}")

auto_create_database()

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.event import Event
from app.models.ticket_type import TicketType
from app.models.customer import Customer
from app.models.setting import Setting
from datetime import date, time, datetime

app = create_app()


def seed_database():
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("[+] Database tables re-created successfully.")

        # Seed Settings if not exists
        setting = Setting.query.first()
        if not setting:
            setting = Setting()
            db.session.add(setting)
            db.session.commit()
        print("[+] App settings initialized.")

        # Seed Manager
        manager = User.query.filter_by(email='manager@ticketme.com').first()
        if not manager:
            manager = User(
                full_name='Event Manager',
                email='manager@ticketme.com',
                phone_number='0201111111',
                role='Manager',
                status='Active'
            )
            manager.set_password('manager123')
            db.session.add(manager)
            print("[+] Created Manager: manager@ticketme.com / manager123")
        else:
            manager.role = 'Manager'
            manager.set_password('manager123')

        # Seed Ticket Officer
        officer = User.query.filter_by(email='officer@ticketme.com').first()
        if not officer:
            officer = User(
                full_name='Yaa Ticket Officer',
                email='officer@ticketme.com',
                phone_number='0202222222',
                role='Ticket Officer',
                status='Active'
            )
            officer.set_password('officer123')
            db.session.add(officer)
            print("[+] Created Ticket Officer: officer@ticketme.com / officer123")
        else:
            officer.role = 'Ticket Officer'
            officer.set_password('officer123')

        db.session.commit()

        # Seed Events & Ticket Types if empty
        if Event.query.count() == 0:
            ev1 = Event(
                name='Accra Music Festival 2026',
                venue='Independence Square, Accra',
                event_date=date(2026, 12, 24),
                start_time=time(18, 0),
                end_time=time(23, 59),
                description='The biggest end-of-year music concert featuring top artistes across West Africa.',
                status='Upcoming'
            )
            db.session.add(ev1)
            db.session.commit()

            tt1 = TicketType(event_id=ev1.id, name='Regular Access', price=100.0, total_quantity=500, available_quantity=500)
            tt2 = TicketType(event_id=ev1.id, name='VIP Front Row', price=250.0, total_quantity=100, available_quantity=100)
            db.session.add_all([tt1, tt2])
            db.session.commit()
            print("[+] Populated sample events and ticket types.")

        # Seed Customers if empty
        if Customer.query.count() == 0:
            c1 = Customer(name='Yaw Addo', phone_number='0244998877', email='yaw@gmail.com')
            c2 = Customer(name='Esi Darko', phone_number='0277112233', email='esi@yahoo.com')
            db.session.add_all([c1, c2])
            db.session.commit()
            print("[+] Populated sample customers.")

        print("[+] TicketMe database seeding completed successfully!")

if __name__ == '__main__':
    seed_database()
