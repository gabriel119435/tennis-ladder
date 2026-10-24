SETS = [[6, 4], [6, 3]]


def test_matches_carry_player_names(admin_client01, ranking_id):
    matches = admin_client01.get(f"/api/rankings/{ranking_id}/matches").get_json()
    names = {"alice", "bob", "charlie", "dave"}
    assert all(m["player_a_name"] in names and m["player_b_name"] in names for m in matches)


def test_get_matches_not_found(client):
    res = client.get("/api/rankings/1/matches")
    assert res.status_code == 404


def test_result_entered_sets_played(admin_client01, ranking_id):
    match_id = admin_client01.get(f"/api/rankings/{ranking_id}/matches").get_json()[0]["id"]

    res = admin_client01.post(f"/api/matches/{match_id}/result", json={"sets": SETS})
    assert res.status_code == 201

    updated = next(
        m for m in admin_client01.get(f"/api/rankings/{ranking_id}/matches").get_json() if m["id"] == match_id
    )
    assert updated["result_type"] == "played"


def test_close_fills_no_match(admin_client01, ranking_id):
    res = admin_client01.post(f"/api/rankings/{ranking_id}/close")
    assert res.status_code == 200

    matches = admin_client01.get(f"/api/rankings/{ranking_id}/matches").get_json()
    assert all(m["result_type"] == "no_match" for m in matches)


def test_played_result_computes_winner(admin_client01, ranking_id):
    match = admin_client01.get(f"/api/rankings/{ranking_id}/matches").get_json()[0]

    res = admin_client01.post(f"/api/matches/{match['id']}/result", json={"sets": SETS})
    assert res.status_code == 201

    updated = admin_client01.get(f"/api/rankings/{ranking_id}/matches").get_json()[0]
    assert updated["winner_id"] == match["player_a_id"]
    assert updated["sets"] == [{"games_a": 6, "games_b": 4}, {"games_a": 6, "games_b": 3}]


def test_create_result_twice_rejected(admin_client01, ranking_id):
    match_id = admin_client01.get(f"/api/rankings/{ranking_id}/matches").get_json()[0]["id"]
    body = {"sets": SETS}

    admin_client01.post(f"/api/matches/{match_id}/result", json=body)
    res = admin_client01.post(f"/api/matches/{match_id}/result", json=body)
    assert res.status_code == 409
    assert res.get_json() == {"error": "result_exists"}


def test_invalid_set_score_rejected(admin_client01, ranking_id):
    match_id = admin_client01.get(f"/api/rankings/{ranking_id}/matches").get_json()[0]["id"]

    res = admin_client01.post(f"/api/matches/{match_id}/result", json={"sets": [[1, 2], [6, 3]]})
    assert res.status_code == 400
    assert res.get_json() == {"error": "invalid_set_score"}


def test_set_score_wrong_type_rejected(admin_client01, ranking_id):
    match_id = admin_client01.get(f"/api/rankings/{ranking_id}/matches").get_json()[0]["id"]

    res = admin_client01.post(f"/api/matches/{match_id}/result", json={"sets": [[6.5, 3], [6, 3]]})
    assert res.status_code == 400
    assert res.get_json() == {"error": "invalid_sets"}


def test_walkover_result(admin_client01, ranking_id):
    match = admin_client01.get(f"/api/rankings/{ranking_id}/matches").get_json()[0]

    res = admin_client01.post(f"/api/matches/{match['id']}/result", json={"wo_winner_id": match["player_b_id"]})
    assert res.status_code == 201

    updated = admin_client01.get(f"/api/rankings/{ranking_id}/matches").get_json()[0]
    assert updated["result_type"] == "walkover"
    assert updated["winner_id"] == match["player_b_id"]
    assert updated["sets"] == []


def test_invalid_walkover_winner_rejected(admin_client01, ranking_id):
    match_id = admin_client01.get(f"/api/rankings/{ranking_id}/matches").get_json()[0]["id"]

    res = admin_client01.post(f"/api/matches/{match_id}/result", json={"wo_winner_id": 5})
    assert res.status_code == 400
    assert res.get_json() == {"error": "invalid_winner_id"}


def test_walkover_winner_wrong_type_rejected(admin_client01, ranking_id):
    match_id = admin_client01.get(f"/api/rankings/{ranking_id}/matches").get_json()[0]["id"]

    res = admin_client01.post(f"/api/matches/{match_id}/result", json={"wo_winner_id": True})
    assert res.status_code == 400
    assert res.get_json() == {"error": "invalid_payload"}


def test_sets_and_wo_winner_rejected(admin_client01, ranking_id):
    match = admin_client01.get(f"/api/rankings/{ranking_id}/matches").get_json()[0]

    res = admin_client01.post(
        f"/api/matches/{match['id']}/result",
        json={"sets": SETS, "wo_winner_id": match["player_b_id"]},
    )
    assert res.status_code == 400
    assert res.get_json() == {"error": "sets_or_wo_winner"}


def test_no_sets_no_wo_winner_rejected(admin_client01, ranking_id):
    match_id = admin_client01.get(f"/api/rankings/{ranking_id}/matches").get_json()[0]["id"]

    res = admin_client01.post(f"/api/matches/{match_id}/result", json={})
    assert res.status_code == 400
    assert res.get_json() == {"error": "sets_or_wo_winner"}


def test_walkover_with_empty_sets_accepted(admin_client01, ranking_id):
    match = admin_client01.get(f"/api/rankings/{ranking_id}/matches").get_json()[0]

    res = admin_client01.post(
        f"/api/matches/{match['id']}/result",
        json={"sets": [], "wo_winner_id": match["player_b_id"]},
    )
    assert res.status_code == 201


def test_create_result_blocked_after_round_closed(admin_client01, ranking_id):
    match_id = admin_client01.get(f"/api/rankings/{ranking_id}/matches").get_json()[0]["id"]
    admin_client01.post(f"/api/rankings/{ranking_id}/close")

    res = admin_client01.post(f"/api/matches/{match_id}/result", json={"sets": SETS})
    assert res.status_code == 403
    assert res.get_json() == {"error": "round_closed"}


def test_create_result_requires_admin(client, admin_client01, ranking_id):
    match_id = admin_client01.get(f"/api/rankings/{ranking_id}/matches").get_json()[0]["id"]

    res = client.post(f"/api/matches/{match_id}/result", json={"sets": SETS})
    assert res.status_code == 401


def test_create_result_match_not_found(admin_client01):
    res = admin_client01.post("/api/matches/5/result", json={"sets": SETS})
    assert res.status_code == 404


def test_create_result_requires_ranking_ownership(admin_client01, admin_client02, ranking_id):
    match_id = admin_client01.get(f"/api/rankings/{ranking_id}/matches").get_json()[0]["id"]

    res = admin_client02.post(f"/api/matches/{match_id}/result", json={"sets": SETS})
    assert res.status_code == 403
    assert res.get_json() == {"error": "not_owner"}


def test_delete_result_then_enter_again(admin_client01, ranking_id):
    match_id = admin_client01.get(f"/api/rankings/{ranking_id}/matches").get_json()[0]["id"]
    admin_client01.post(f"/api/matches/{match_id}/result", json={"sets": SETS})

    res = admin_client01.delete(f"/api/matches/{match_id}/result")
    assert res.status_code == 200
    cleared = admin_client01.get(f"/api/rankings/{ranking_id}/matches").get_json()[0]
    assert (cleared["result_type"], cleared["winner_id"], cleared["sets"]) == (None, None, [])

    res = admin_client01.post(f"/api/matches/{match_id}/result", json={"sets": [[3, 6], [3, 6]]})
    assert res.status_code == 201


def test_delete_result_on_pending_match(admin_client01, ranking_id):
    match_id = admin_client01.get(f"/api/rankings/{ranking_id}/matches").get_json()[0]["id"]

    res = admin_client01.delete(f"/api/matches/{match_id}/result")
    assert res.status_code == 404
    assert res.get_json() == {"error": "result_not_found"}


def test_delete_result_blocked_after_round_closed(admin_client01, ranking_id):
    match_id = admin_client01.get(f"/api/rankings/{ranking_id}/matches").get_json()[0]["id"]
    admin_client01.post(f"/api/rankings/{ranking_id}/close")

    res = admin_client01.delete(f"/api/matches/{match_id}/result")
    assert res.status_code == 403
    assert res.get_json() == {"error": "round_closed"}


def test_delete_result_requires_ranking_ownership(admin_client01, admin_client02, ranking_id):
    match_id = admin_client01.get(f"/api/rankings/{ranking_id}/matches").get_json()[0]["id"]
    admin_client01.post(f"/api/matches/{match_id}/result", json={"sets": SETS})

    res = admin_client02.delete(f"/api/matches/{match_id}/result")
    assert res.status_code == 403
    assert res.get_json() == {"error": "not_owner"}
