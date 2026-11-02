from conftest import MISSING_ID, create_ranking, register_participants


def test_participants_add_remove_reactivate(admin_client01, four_players_admin01):
    ranking_id = create_ranking(admin_client01)

    res = admin_client01.post(f"/api/participants/{ranking_id}", json={"player_id": four_players_admin01["alice_id"]})
    assert res.status_code == 201
    assert res.get_json() == {"message": "added"}

    register_participants(admin_client01, ranking_id, four_players_admin01, "bob")

    participants = admin_client01.get(f"/api/participants/{ranking_id}").get_json()
    assert [p["name"] for p in participants] == ["alice", "bob"]

    res = admin_client01.delete(f"/api/participants/{ranking_id}/{four_players_admin01['alice_id']}")
    assert res.status_code == 200
    participants = admin_client01.get(f"/api/participants/{ranking_id}").get_json()
    assert [p["name"] for p in participants] == ["bob"]

    res = admin_client01.post(f"/api/participants/{ranking_id}", json={"player_id": four_players_admin01["alice_id"]})
    assert res.status_code == 200
    assert res.get_json() == {"message": "added"}
    participants = admin_client01.get(f"/api/participants/{ranking_id}").get_json()
    assert [p["name"] for p in participants] == ["alice", "bob"]


def test_add_participant_invalid_player(admin_client01):
    ranking_id = create_ranking(admin_client01)
    res = admin_client01.post(f"/api/participants/{ranking_id}", json={"player_id": MISSING_ID})
    assert res.status_code == 400
    assert res.get_json() == {"error": "invalid_player_id"}


def test_add_participant_player_id_wrong_type(admin_client01):
    ranking_id = create_ranking(admin_client01)
    res = admin_client01.post(f"/api/participants/{ranking_id}", json={"player_id": "1"})
    assert res.status_code == 400
    assert res.get_json() == {"error": "invalid_payload"}


def test_add_participant_ranking_not_found(admin_client01, four_players_admin01):
    res = admin_client01.post(f"/api/participants/{MISSING_ID}", json={"player_id": four_players_admin01["alice_id"]})
    assert res.status_code == 404


def test_participant_mutations_require_ownership(admin_client01, admin_client02, four_players_admin01):
    ranking_id = create_ranking(admin_client01)
    register_participants(admin_client01, ranking_id, four_players_admin01, "alice", "bob", "charlie")

    add_res = admin_client02.post(
        f"/api/participants/{ranking_id}", json={"player_id": four_players_admin01["dave_id"]}
    )
    remove_res = admin_client02.delete(f"/api/participants/{ranking_id}/{four_players_admin01['alice_id']}")

    for res in (add_res, remove_res):
        assert res.status_code == 403
        assert res.get_json() == {"error": "not_owner"}


def test_add_participant_other_admins_player(admin_client02, four_players_admin01):
    ranking_id = create_ranking(admin_client02)
    res = admin_client02.post(f"/api/participants/{ranking_id}", json={"player_id": four_players_admin01["alice_id"]})
    assert res.status_code == 403
    assert res.get_json() == {"error": "not_owner"}


def test_participants_alphabetical_ignoring_accents(admin_client01):
    ranking_id = create_ranking(admin_client01)
    for name in ("joseph", "josé"):
        admin_client01.post("/api/players", json={"name": name})
    for player in admin_client01.get("/api/players").get_json():
        admin_client01.post(f"/api/participants/{ranking_id}", json={"player_id": player["id"]})
    names = [p["name"] for p in admin_client01.get(f"/api/participants/{ranking_id}").get_json()]
    assert names == ["josé", "joseph"]
