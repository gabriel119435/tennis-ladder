from conftest import create_ranking, register_participants


# one ranking from the public list, the api has no single ranking route
def _get_ranking(client, ranking_id):
    return next(r for r in client.get("/api/rankings").get_json() if r["id"] == ranking_id)


def test_get_rankings_public(client):
    res = client.get("/api/rankings")
    assert res.status_code == 200
    assert isinstance(res.get_json(), list)


def test_create_ranking_requires_admin(client):
    res = client.post("/api/rankings", json={"name": "ranking_name01"})
    assert res.status_code == 401


def test_create_ranking_success(admin_client01):
    res = admin_client01.post("/api/rankings", json={"name": "ranking_name01"})
    assert res.status_code == 201
    assert res.get_json() == {"message": "created"}
    ranking = admin_client01.get("/api/rankings").get_json()[0]
    assert ranking["name"] == "ranking_name01"
    assert isinstance(ranking["created_by_admin_id"], int)
    assert ranking["created_by_admin_username"] == "admin1"


def test_get_rankings_admin_id_filter(admin_client01, admin_client02):
    ranking1_id = create_ranking(admin_client01)
    ranking2_id = create_ranking(admin_client02)
    admin1_id = admin_client01.get("/api/me").get_json()["user"]["id"]

    filtered = admin_client01.get(f"/api/rankings?admin_id={admin1_id}").get_json()
    filtered_ids = {r["id"] for r in filtered}
    assert ranking1_id in filtered_ids
    assert ranking2_id not in filtered_ids
    assert all(r["created_by_admin_id"] == admin1_id for r in filtered)

    unfiltered = admin_client01.get("/api/rankings").get_json()
    unfiltered_ids = {r["id"] for r in unfiltered}
    assert ranking1_id in unfiltered_ids
    assert ranking2_id in unfiltered_ids
    usernames = {r["id"]: r["created_by_admin_username"] for r in unfiltered}
    assert (usernames[ranking1_id], usernames[ranking2_id]) == ("admin1", "admin2")


def test_get_rankings_includes_created_ranking(admin_client01):
    ranking_id = create_ranking(admin_client01)
    rankings = admin_client01.get("/api/rankings").get_json()
    assert any(r["id"] == ranking_id and r["name"] == "ranking_name01" for r in rankings)


def test_create_ranking_missing_name(admin_client01):
    res = admin_client01.post("/api/rankings", json={"name": " "})
    assert res.status_code == 400
    assert res.get_json() == {"error": "name_required"}


def test_create_ranking_name_too_long(admin_client01):
    res = admin_client01.post("/api/rankings", json={"name": "x" * 30})
    assert res.status_code == 400
    assert res.get_json() == {"error": "name_too_long"}


def test_create_ranking_word_too_long(admin_client01):
    res = admin_client01.post("/api/rankings", json={"name": "x" * 20})
    assert res.status_code == 400
    assert res.get_json() == {"error": "word_too_long"}


def test_create_ranking_name_wrong_type(admin_client01):
    res = admin_client01.post("/api/rankings", json={"name": 5})
    assert res.status_code == 400
    assert res.get_json() == {"error": "invalid_payload"}


def test_create_ranking_duplicate_name(admin_client01):
    admin_client01.post("/api/rankings", json={"name": "duplicate"})
    res = admin_client01.post("/api/rankings", json={"name": "duplicate"})
    assert res.status_code == 409
    assert res.get_json() == {"error": "ranking_exists"}


def test_create_ranking_duplicate_name_allowed_across_different_admins(admin_client01, admin_client02):
    admin_client01.post("/api/rankings", json={"name": "shared name"})
    res = admin_client02.post("/api/rankings", json={"name": "shared name"})
    assert res.status_code == 201


def test_round_mutations_require_ownership(admin_client01, admin_client02, four_players_admin01):
    ranking_id = create_ranking(admin_client01)
    register_participants(admin_client01, ranking_id, four_players_admin01, "alice", "bob", "charlie")

    start_res = admin_client02.post(f"/api/rankings/{ranking_id}/start")
    close_res = admin_client02.post(f"/api/rankings/{ranking_id}/close")

    for res in (start_res, close_res):
        assert res.status_code == 403
        assert res.get_json() == {"error": "not_owner"}


def test_start_requires_admin(client):
    res = client.post("/api/rankings/1/start")
    assert res.status_code == 401


def test_start_too_few_participants(admin_client01, four_players_admin01):
    ranking_id = create_ranking(admin_client01)
    register_participants(admin_client01, ranking_id, four_players_admin01, "alice", "bob")

    res = admin_client01.post(f"/api/rankings/{ranking_id}/start")
    assert res.status_code == 400
    assert res.get_json() == {"error": "too_few_active_participants"}


def test_start_success_pairs_everyone(admin_client01, four_players_admin01):
    ranking_id = create_ranking(admin_client01)
    register_participants(admin_client01, ranking_id, four_players_admin01, "alice", "bob", "charlie", "dave")

    res = admin_client01.post(f"/api/rankings/{ranking_id}/start")
    assert res.status_code == 201

    ranking = _get_ranking(admin_client01, ranking_id)
    assert ranking["ongoing"] is True
    assert ranking["round"] == 1

    matches = admin_client01.get(f"/api/rankings/{ranking_id}/matches").get_json()
    opponents = {}
    for m in matches:
        opponents.setdefault(m["player_a_id"], []).append(m["player_b_id"])
        opponents.setdefault(m["player_b_id"], []).append(m["player_a_id"])
    assert all(len(set(opponents_for_each_player)) == 2 for opponents_for_each_player in opponents.values())


def test_close_locks_the_round(admin_client01, four_players_admin01):
    ranking_id = create_ranking(admin_client01)
    register_participants(admin_client01, ranking_id, four_players_admin01, "alice", "bob", "charlie", "dave")
    admin_client01.post(f"/api/rankings/{ranking_id}/start")

    res = admin_client01.post(f"/api/rankings/{ranking_id}/close")
    assert res.status_code == 200

    ranking = _get_ranking(admin_client01, ranking_id)
    assert ranking["ongoing"] is False

    matches = admin_client01.get(f"/api/rankings/{ranking_id}/matches").get_json()
    assert all(m["result_type"] == "no_match" for m in matches)
