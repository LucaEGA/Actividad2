import json
from app.models import User

def test_register_user_success(client, init_database):
    response = client.post('/api/v1/auth/register', json={
        'username': 'newuser',
        'password': 'newpassword'
    })
    assert response.status_code == 201
    assert response.json['message'] == 'User registered successfully'
    assert User.query.filter_by(username='newuser').first() is not None

def test_register_user_duplicate(client, init_database):
    client.post('/api/v1/auth/register', json={'username': 'testuser', 'password': 'password'})
    response = client.post('/api/v1/auth/register', json={'username': 'testuser', 'password': 'password'})
    assert response.status_code == 400
    assert 'User already exists' in response.json['message']

def test_register_user_missing_fields(client, init_database):
    response = client.post('/api/v1/auth/register', json={'username': 'useronly'})
    assert response.status_code == 400
    assert 'Username and password required' in response.json['message']

def test_login_user_success(client, init_database):
    client.post('/api/v1/auth/register', json={'username': 'loginuser', 'password': 'loginpass'})
    response = client.post('/api/v1/auth/login', json={'username': 'loginuser', 'password': 'loginpass'})
    assert response.status_code == 200
    assert 'token' in response.json

def test_login_user_invalid_password(client, init_database):
    client.post('/api/v1/auth/register', json={'username': 'loginuser2', 'password': 'loginpass'})
    response = client.post('/api/v1/auth/login', json={'username': 'loginuser2', 'password': 'wrongpassword'})
    assert response.status_code == 401
    assert 'Invalid username or password' in response.json['message']

def test_login_user_not_exist(client, init_database):
    response = client.post('/api/v1/auth/login', json={'username': 'nonexistent', 'password': 'password'})
    assert response.status_code == 401
    assert 'Invalid username or password' in response.json['message']
