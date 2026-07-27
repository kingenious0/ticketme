import pytest
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.event import Event
from app.models.ticket_type import TicketType
from app.models.customer import Customer
from datetime import date, datetime

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def admin_user(app):
    user = User(
        full_name="Admin Test",
        email="admin@test.com",
        role="Administrator",
        status="Active"
    )
    user.set_password("Admin123!")
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def sample_event(app):
    ev = Event(
        name="Test Gala 2026",
        venue="Accra Conference Centre",
        event_date=date(2026, 12, 31),
        start_time=datetime.strptime("19:00", "%H:%M").time(),
        status="Upcoming"
    )
    db.session.add(ev)
    db.session.commit()

    tt = TicketType(
        event_id=ev.id,
        name="VIP",
        price=150.00,
        total_quantity=50,
        available_quantity=50,
        status="Active"
    )
    db.session.add(tt)
    db.session.commit()
    return ev

@pytest.fixture
def sample_customer(app):
    c = Customer(name="Ama Serwaa", phone_number="0244999888", email="ama@test.com")
    db.session.add(c)
    db.session.commit()
    return c
