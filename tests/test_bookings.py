from app.models.booking import Booking
from app.models.payment import Payment
from app.models.ticket import Ticket

def test_booking_and_payment_workflow(client, admin_user, sample_event, sample_customer):
    # Login
    client.post('/auth/login', data={'email': 'admin@test.com', 'password': 'Admin123!'})

    tt = sample_event.ticket_types[0]

    # Create Booking
    res = client.post('/bookings/create', data={
        'event_id': sample_event.id,
        'customer_id': sample_customer.id,
        'ticket_type_id': tt.id,
        'quantity': 2
    }, follow_redirects=True)

    assert res.status_code == 200
    booking = Booking.query.first()
    assert booking is not None
    assert booking.status == 'Pending'
    assert booking.quantity == 2
    assert float(booking.total_amount) == 300.00 # 2 * 150.00

    # Record Payment
    pay_res = client.post(f'/payments/record/{booking.id}', data={
        'payment_method': 'MTN Mobile Money',
        'transaction_reference': 'MOMO123456',
        'amount': 300.00,
        'notes': 'Test payment'
    }, follow_redirects=True)

    assert pay_res.status_code == 200
    assert booking.status == 'Confirmed'

    # Check generated tickets & QR codes
    tickets = Ticket.query.filter_by(booking_id=booking.id).all()
    assert len(tickets) == 2
    assert tickets[0].status == 'Unused'
    assert tickets[0].qr_code_path is not None
