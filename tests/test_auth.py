def test_login_success(client, admin_user):
    response = client.post('/auth/login', data={
        'email': 'admin@test.com',
        'password': 'Admin123!'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Welcome back' in response.data or b'Executive Dashboard' in response.data

def test_login_failure(client, admin_user):
    response = client.post('/auth/login', data={
        'email': 'admin@test.com',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    assert b'Invalid email address or password' in response.data
