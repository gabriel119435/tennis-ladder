from conftest import create_ranking, register


def test_standings_reflects_results(admin_client01, ranking_id):
    matches = admin_client01.get(f'/api/rankings/{ranking_id}/matches').get_json()
    first_match = matches[0]
    admin_client01.patch(
        f'/api/matches/{first_match["id"]}', json={'result_type': 'played', 'sets': [[6, 4], [6, 3]]}
    )
    admin_client01.post(f'/api/rankings/{ranking_id}/close')

    standings = admin_client01.get(f'/api/standings/{ranking_id}').get_json()
    by_id = {row['id']: row for row in standings}
    assert by_id[first_match['player_a_id']]['points'] == 100
    assert by_id[first_match['player_b_id']]['points'] == 25
    other_ids = {p for p in by_id if p not in (first_match['player_a_id'], first_match['player_b_id'])}
    assert all(by_id[p]['points'] == 0 for p in other_ids)


def test_standings_orders_ties_by_registration(admin_client01, four_players_admin01):
    ranking_id = create_ranking(admin_client01)
    register(admin_client01, ranking_id, four_players_admin01, 'dave', 'bob', 'alice')

    standings = admin_client01.get(f'/api/standings/{ranking_id}').get_json()
    # nobody's played yet: everyone ties on points/sets/games/matches.
    # order falls through to registration order, not alphabetical, dave registered first.
    assert [row['name'] for row in standings] == ['dave', 'bob', 'alice']


def test_standings_not_found(client):
    res = client.get('/api/standings/1')
    assert res.status_code == 404
