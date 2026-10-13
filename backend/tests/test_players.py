def test_get_players_public(client, four_players_admin01):
    res = client.get('/api/players')
    assert res.status_code == 200
    names = {p['name'] for p in res.get_json()}
    assert {'alice', 'bob', 'charlie', 'dave'} <= names


def test_create_player_requires_admin(client):
    res = client.post('/api/players', json={'name': 'erin'})
    assert res.status_code == 401


def test_create_player_success(admin_client01):
    res = admin_client01.post('/api/players', json={'name': 'erin'})
    assert res.status_code == 201
    body = res.get_json()
    assert body['name'] == 'erin'
    assert isinstance(body['id'], int)
    assert isinstance(body['created_by_admin_id'], int)


def test_get_players_admin_id_filter(admin_client01, admin_client02, four_players_admin01):
    admin_client02.post('/api/players', json={'name': 'erin'})
    admin1_id = admin_client01.get('/api/me').get_json()['user']['id']
    alice_id = four_players_admin01['alice_id']

    filtered = admin_client01.get(f'/api/players?admin_id={admin1_id}').get_json()
    filtered_names = {p['name'] for p in filtered}
    assert 'alice' in filtered_names
    assert 'erin' not in filtered_names
    assert all(p['created_by_admin_id'] == admin1_id for p in filtered)

    unfiltered = admin_client01.get('/api/players').get_json()
    unfiltered_names = {p['name'] for p in unfiltered}
    assert 'alice' in unfiltered_names
    assert 'erin' in unfiltered_names
    assert alice_id in {p['id'] for p in unfiltered}


def test_create_player_missing_name(admin_client01):
    res = admin_client01.post('/api/players', json={'name': '  '})
    assert res.status_code == 400
    assert res.get_json() == {'error': 'name_required'}


def test_create_player_name_too_long(admin_client01):
    res = admin_client01.post('/api/players', json={'name': 'x' * 30})
    assert res.status_code == 400
    assert res.get_json() == {'error': 'name_too_long'}


def test_create_player_name_wrong_type(admin_client01):
    res = admin_client01.post('/api/players', json={'name': 5})
    assert res.status_code == 400
    assert res.get_json() == {'error': 'invalid_payload'}


def test_create_player_duplicate_name(admin_client01, four_players_admin01):
    res = admin_client01.post('/api/players', json={'name': 'alice'})
    assert res.status_code == 409
    assert res.get_json() == {'error': 'player_exists'}


def test_create_player_duplicate_name_case_insensitive(admin_client01, four_players_admin01):
    res = admin_client01.post('/api/players', json={'name': 'ALICE'})
    assert res.status_code == 409
    assert res.get_json() == {'error': 'player_exists'}


def test_create_player_stores_name_lowercase(admin_client01):
    admin_client01.post('/api/players', json={'name': 'Erin'})

    names = {p['name'] for p in admin_client01.get('/api/players').get_json()}
    assert 'erin' in names
    assert 'Erin' not in names


def test_rename_player_success(admin_client01, four_players_admin01):
    alice_id = four_players_admin01['alice_id']
    res = admin_client01.patch(f'/api/players/{alice_id}', json={'name': 'alicia'})
    assert res.status_code == 200
    body = res.get_json()
    assert body['id'] == alice_id
    assert body['name'] == 'alicia'

    names = {p['name'] for p in admin_client01.get('/api/players').get_json()}
    assert 'alicia' in names
    assert 'alice' not in names


def test_rename_player_requires_ownership(admin_client02, four_players_admin01):
    alice_id = four_players_admin01['alice_id']
    res = admin_client02.patch(f'/api/players/{alice_id}', json={'name': 'alicia'})
    assert res.status_code == 403
    assert res.get_json() == {'error': 'not_owner'}


def test_create_player_duplicate_name_allowed_across_different_admins(admin_client02, four_players_admin01):
    res = admin_client02.post('/api/players', json={'name': 'alice'})
    assert res.status_code == 201
