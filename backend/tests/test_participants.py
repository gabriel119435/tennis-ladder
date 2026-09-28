from conftest import create_ranking, register


def test_participants_add_remove_reactivate(admin_client01, four_players_admin01):
    ranking_id = create_ranking(admin_client01)

    res = admin_client01.post(
        f'/api/participants/{ranking_id}',
        json={'player_id': four_players_admin01['alice_id']}
    )
    assert res.status_code == 201
    body = res.get_json()
    assert body['player_id'] == four_players_admin01['alice_id']
    assert body['ranking_id'] == ranking_id
    assert body['active'] is True
    assert isinstance(body['id'], int)

    register(admin_client01, ranking_id, four_players_admin01, 'bob')

    participants = admin_client01.get(f'/api/participants/{ranking_id}').get_json()
    assert {p['name']: p['active'] for p in participants} == {'alice': True, 'bob': True}

    res = admin_client01.delete(f'/api/participants/{ranking_id}/{four_players_admin01["alice_id"]}')
    assert res.status_code == 200
    participants = admin_client01.get(f'/api/participants/{ranking_id}').get_json()
    assert {p['name']: p['active'] for p in participants} == {'alice': False, 'bob': True}

    res = admin_client01.post(
        f'/api/participants/{ranking_id}',
        json={'player_id': four_players_admin01['alice_id']}
    )
    assert res.status_code == 200
    body = res.get_json()
    assert body['player_id'] == four_players_admin01['alice_id']
    assert body['active'] is True
    participants = admin_client01.get(f'/api/participants/{ranking_id}').get_json()
    assert {p['name']: p['active'] for p in participants} == {'alice': True, 'bob': True}


def test_add_participant_invalid_player(admin_client01):
    ranking_id = create_ranking(admin_client01)
    res = admin_client01.post(f'/api/participants/{ranking_id}', json={'player_id': 5})
    assert res.status_code == 400
    assert res.get_json() == {'error': 'invalid_player_id'}


def test_add_participant_ranking_not_found(admin_client01, four_players_admin01):
    res = admin_client01.post('/api/participants/1', json={'player_id': four_players_admin01['alice_id']})
    assert res.status_code == 404


def test_participant_mutations_require_ownership(admin_client01, admin_client02, four_players_admin01):
    ranking_id = create_ranking(admin_client01)
    register(admin_client01, ranking_id, four_players_admin01, 'alice', 'bob', 'charlie')

    add_res = admin_client02.post(
        f'/api/participants/{ranking_id}', json={'player_id': four_players_admin01['dave_id']}
    )
    remove_res = admin_client02.delete(f'/api/participants/{ranking_id}/{four_players_admin01["alice_id"]}')

    for res in (add_res, remove_res):
        assert res.status_code == 403
        assert res.get_json() == {'error': 'not_owner'}
