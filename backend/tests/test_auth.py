import pytest

from app import DEFAULT_ADMIN_PASS
from app.admin import create_admin


def test_login_success(client):
    res = client.post('/api/login', json={'username': 'admin', 'password': DEFAULT_ADMIN_PASS})
    assert res.status_code == 200
    assert res.get_json()['user']['username'] == 'admin'


def test_login_wrong_password(client):
    res = client.post('/api/login', json={'username': 'admin', 'password': 'wrong'})
    assert res.status_code == 401
    assert res.get_json() == {'error': 'invalid_credentials'}


def test_login_unknown_username(client):
    res = client.post('/api/login', json={'username': 'nobody', 'password': 'whatever'})
    assert res.status_code == 401
    assert res.get_json() == {'error': 'invalid_credentials'}


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


def test_change_password_requires_admin(client):
    res = client.patch('/api/admin/password', json={'old_password': DEFAULT_ADMIN_PASS, 'new_password': 'new_pass'})
    assert res.status_code == 401


def test_change_password_wrong_old(admin_client01):
    res = admin_client01.patch('/api/admin/password', json={'old_password': 'wrong', 'new_password': 'new_pass'})
    assert res.status_code == 400
    assert res.get_json() == {'error': 'wrong_current_password'}


def test_change_password_too_short(admin_client01):
    res = admin_client01.patch('/api/admin/password', json={'old_password': 'admin_pass1', 'new_password': 'short'})
    assert res.status_code == 400
    assert res.get_json() == {'error': 'password_too_short'}


def test_change_password_success(admin_client01, client):
    try:
        res = admin_client01.patch(
            '/api/admin/password', json={'old_password': 'admin_pass1', 'new_password': 'new_pass'}
        )
        assert res.status_code == 200
        assert client.post('/api/login', json={'username': 'admin1', 'password': 'admin_pass1'}).status_code == 401
        assert client.post('/api/login', json={'username': 'admin1', 'password': 'new_pass'}).status_code == 200
    finally:
        revert = admin_client01.patch(
            '/api/admin/password', json={'old_password': 'new_pass', 'new_password': 'admin_pass1'}
        )
        assert revert.status_code == 200


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
