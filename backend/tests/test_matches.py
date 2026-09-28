def test_match_date_stays_null_while_pending(admin_client01, ranking_id):
    matches = admin_client01.get(f'/api/rankings/{ranking_id}/matches').get_json()
    assert all(m['date'] is None and m['result_type'] is None for m in matches)


def test_match_date_set_when_result_entered(admin_client01, ranking_id):
    match_id = admin_client01.get(f'/api/rankings/{ranking_id}/matches').get_json()[0]['id']

    res = admin_client01.patch(f'/api/matches/{match_id}', json={'result_type': 'played', 'sets': [[6, 4], [6, 3]]})
    assert res.status_code == 200

    updated = next(
        m for m in admin_client01.get(f'/api/rankings/{ranking_id}/matches').get_json() if m['id'] == match_id)
    assert updated['date'] is not None
    assert updated['result_type'] == 'played'


def test_match_date_set_by_no_match_fill_on_close(admin_client01, ranking_id):
    res = admin_client01.post(f'/api/rankings/{ranking_id}/close')
    assert res.status_code == 200

    matches = admin_client01.get(f'/api/rankings/{ranking_id}/matches').get_json()
    assert all(m['result_type'] == 'no_match' and m['date'] is not None for m in matches)


def test_played_result_computes_winner(admin_client01, ranking_id):
    match = admin_client01.get(f'/api/rankings/{ranking_id}/matches').get_json()[0]

    res = admin_client01.patch(
        f'/api/matches/{match["id"]}', json={'result_type': 'played', 'sets': [[6, 4], [6, 3]]}
    )
    assert res.status_code == 200

    updated = admin_client01.get(f'/api/rankings/{ranking_id}/matches').get_json()[0]
    assert updated['winner_id'] == match['player_a_id']
    assert updated['sets'] == [
        {'set_number': 1, 'games_a': 6, 'games_b': 4},
        {'set_number': 2, 'games_a': 6, 'games_b': 3},
    ]


def test_invalid_set_score_rejected(admin_client01, ranking_id):
    match_id = admin_client01.get(f'/api/rankings/{ranking_id}/matches').get_json()[0]['id']

    res = admin_client01.patch(f'/api/matches/{match_id}', json={'result_type': 'played', 'sets': [[8, 6], [6, 3]]})
    assert res.status_code == 400
    assert res.get_json() == {'error': 'invalid_set_score'}


def test_walkover_result(admin_client01, ranking_id):
    match = admin_client01.get(f'/api/rankings/{ranking_id}/matches').get_json()[0]

    res = admin_client01.patch(
        f'/api/matches/{match["id"]}', json={'result_type': 'walkover', 'winner_id': match['player_b_id']}
    )
    assert res.status_code == 200

    updated = admin_client01.get(f'/api/rankings/{ranking_id}/matches').get_json()[0]
    assert updated['result_type'] == 'walkover'
    assert updated['winner_id'] == match['player_b_id']
    assert updated['sets'] == []


def test_invalid_walkover_winner_rejected(admin_client01, ranking_id):
    match_id = admin_client01.get(f'/api/rankings/{ranking_id}/matches').get_json()[0]['id']

    res = admin_client01.patch(f'/api/matches/{match_id}', json={'result_type': 'walkover', 'winner_id': 5})
    assert res.status_code == 400
    assert res.get_json() == {'error': 'invalid_winner_id'}


def test_edit_blocked_after_round_closed(admin_client01, ranking_id):
    match_id = admin_client01.get(f'/api/rankings/{ranking_id}/matches').get_json()[0]['id']
    admin_client01.post(f'/api/rankings/{ranking_id}/close')

    res = admin_client01.patch(f'/api/matches/{match_id}', json={'result_type': 'played', 'sets': [[6, 4], [6, 3]]})
    assert res.status_code == 403
    assert res.get_json() == {'error': 'round_closed'}


def test_update_match_requires_admin(client, admin_client01, ranking_id):
    match_id = admin_client01.get(f'/api/rankings/{ranking_id}/matches').get_json()[0]['id']

    res = client.patch(f'/api/matches/{match_id}', json={'result_type': 'played', 'sets': [[6, 4], [6, 3]]})
    assert res.status_code == 401


def test_update_match_not_found(admin_client01):
    res = admin_client01.patch('/api/matches/5', json={'result_type': 'played', 'sets': [[6, 4], [6, 3]]})
    assert res.status_code == 404


def test_update_match_requires_ranking_ownership(admin_client01, admin_client02, ranking_id):
    match_id = admin_client01.get(f'/api/rankings/{ranking_id}/matches').get_json()[0]['id']

    res = admin_client02.patch(f'/api/matches/{match_id}', json={'result_type': 'played', 'sets': [[6, 4], [6, 3]]})
    assert res.status_code == 403
    assert res.get_json() == {'error': 'not_owner'}
