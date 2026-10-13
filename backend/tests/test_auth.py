import pytest

from app import DEFAULT_ADMIN_PASS
from app.admin import create_admin


def test_login_success(client):
    res = client.post('/api/login', json={'username': 'admin', 'password': DEFAULT_ADMIN_PASS})
    assert res.status_code == 200
    assert res.get_json()['user']['username'] == 'admin'


def test_login_cookie_samesite_strict(client):
    res = client.post('/api/login', json={'username': 'admin', 'password': DEFAULT_ADMIN_PASS})
    assert 'SameSite=Strict' in res.headers['Set-Cookie']


def test_login_wrong_password(client):
    res = client.post('/api/login', json={'username': 'admin', 'password': 'wrong'})
    assert res.status_code == 401
    assert res.get_json() == {'error': 'invalid_credentials'}


def test_login_unknown_username(client):
    res = client.post('/api/login', json={'username': 'nobody', 'password': 'whatever'})
    assert res.status_code == 401
    assert res.get_json() == {'error': 'invalid_credentials'}


def test_login_username_wrong_type(client):
    res = client.post('/api/login', json={'username': 123, 'password': 'whatever'})
    assert res.status_code == 400
    assert res.get_json() == {'error': 'invalid_payload'}


def test_login_wrong_method(client):
    res = client.get('/api/login')
    assert res.status_code == 405
    assert res.get_json() == {'error': 'method_not_allowed'}


def test_login_malformed_json(client):
    res = client.post('/api/login', data='not json', content_type='application/json')
    assert res.status_code == 400
    assert res.get_json() == {'error': 'bad_request'}


def test_me_when_logged_out(client):
    res = client.get('/api/me')
    assert res.status_code == 200
    assert res.get_json() == {'user': None}


def test_me_when_logged_in(admin_client01):
    res = admin_client01.get('/api/me')
    assert res.status_code == 200
    assert res.get_json()['user']['username'] == 'admin1'


def test_logout(admin_client01):
    res = admin_client01.post('/api/logout')
    assert res.status_code == 200
    assert admin_client01.get('/api/me').get_json() == {'user': None}


def test_logout_requires_login(client):
    res = client.post('/api/logout')
    assert res.status_code == 401


def test_create_admin_stores_username_lowercase(client):
    assert create_admin('mixedCase', DEFAULT_ADMIN_PASS) is True
    res = client.post('/api/login', json={'username': 'mixedCase', 'password': DEFAULT_ADMIN_PASS})
    assert res.status_code == 200
    assert res.get_json()['user']['username'] == 'mixedcase'


def test_create_admin_duplicate_username_case_insensitive():
    create_admin('duplicate', 'admin_pass1')
    assert create_admin('duplicate', 'admin_pass2') is False


def test_create_admin_password_too_short():
    with pytest.raises(ValueError, match='password_too_short'):
        create_admin('short_pass_admin', 'short')


def test_create_admin_password_too_long():
    with pytest.raises(ValueError, match='password_too_long'):
        create_admin('long_pass_admin', 'x' * 30)
