from app.models.booking import Booking
from app.models.ticket import Ticket

def test_gate_verification_and_double_entry_prevention(client, admin_user, sample_event, sample_customer):
    client.post('/auth/login', data={'email': 'admin@test.com', 'password': 'Admin123!'})
    tt = sample_event.ticket_types[0]

    # Create Booking and Record Payment
    client.post('/bookings/create', data={
        'event_id': sample_event.id,
        'customer_id': sample_customer.id,
        'ticket_type_id': tt.id,
        'quantity': 1
    })
    booking = Booking.query.first()
    client.post(f'/payments/record/{booking.id}', data={
        'payment_method': 'Cash',
        'amount': 150.00
    })

    ticket = Ticket.query.filter_by(booking_id=booking.id).first()
    assert ticket.status == 'Unused'

    # Gate check 1: Search ticket number
    res1 = client.get(f'/verification/check?ticket_number={ticket.ticket_number}')
    assert res1.status_code == 200
    assert b'VALID TICKET' in res1.data

    # Mark ticket as USED
    res_mark = client.post(f'/verification/{ticket.id}/mark-used', follow_redirects=True)
    assert res_mark.status_code == 200
    assert ticket.status == 'Used'

    # Gate check 2: Second scan should show ALREADY USED & prevent double entry
    res2 = client.get(f'/verification/check?ticket_number={ticket.ticket_number}')
    assert b'ALREADY USED' in res2.data or b'INVALID' in res2.data
