from sqlalchemy import delete

from app.db import get_session
from app.models import Player


def test_get_players_requires_admin(client):
    res = client.get("/api/players")
    assert res.status_code == 401


def test_create_player_requires_admin(client):
    res = client.post("/api/players", json={"name": "erin"})
    assert res.status_code == 401


def test_create_player_success(admin_client01):
    res = admin_client01.post("/api/players", json={"name": "erin"})
    assert res.status_code == 201
    assert res.get_json() == {"message": "created"}
    assert [p["name"] for p in admin_client01.get("/api/players").get_json()] == ["erin"]


def test_get_players_only_own(admin_client01, admin_client02, four_players_admin01):
    admin_client02.post("/api/players", json={"name": "erin"})

    admin1_names = [p["name"] for p in admin_client01.get("/api/players").get_json()]
    assert admin1_names == ["alice", "bob", "charlie", "dave"]

    admin2_names = [p["name"] for p in admin_client02.get("/api/players").get_json()]
    assert admin2_names == ["erin"]


def test_create_player_missing_name(admin_client01):
    res = admin_client01.post("/api/players", json={"name": " "})
    assert res.status_code == 400
    assert res.get_json() == {"error": "name_required"}


def test_create_player_name_too_long(admin_client01):
    res = admin_client01.post("/api/players", json={"name": "x" * 30})
    assert res.status_code == 400
    assert res.get_json() == {"error": "name_too_long"}


def test_create_player_word_too_long(admin_client01):
    res = admin_client01.post("/api/players", json={"name": "x" * 20})
    assert res.status_code == 400
    assert res.get_json() == {"error": "word_too_long"}


def test_create_player_name_wrong_type(admin_client01):
    res = admin_client01.post("/api/players", json={"name": 5})
    assert res.status_code == 400
    assert res.get_json() == {"error": "invalid_payload"}


def test_create_player_duplicate_name(admin_client01, four_players_admin01):
    res = admin_client01.post("/api/players", json={"name": "alice"})
    assert res.status_code == 409
    assert res.get_json() == {"error": "player_exists"}


def test_create_player_duplicate_name_case_insensitive(admin_client01, four_players_admin01):
    res = admin_client01.post("/api/players", json={"name": "ALICE"})
    assert res.status_code == 409
    assert res.get_json() == {"error": "player_exists"}


def test_create_player_stores_name_lowercase(admin_client01):
    admin_client01.post("/api/players", json={"name": "Erin"})

    names = {p["name"] for p in admin_client01.get("/api/players").get_json()}
    assert "erin" in names
    assert "Erin" not in names


def test_rename_player_success(admin_client01, four_players_admin01):
    alice_id = four_players_admin01["alice_id"]
    res = admin_client01.patch(f"/api/players/{alice_id}", json={"name": "alicia"})
    assert res.status_code == 200
    assert res.get_json() == {"message": "renamed"}

    names = {p["name"] for p in admin_client01.get("/api/players").get_json()}
    assert "alicia" in names
    assert "alice" not in names


def test_rename_player_requires_ownership(admin_client02, four_players_admin01):
    alice_id = four_players_admin01["alice_id"]
    res = admin_client02.patch(f"/api/players/{alice_id}", json={"name": "alicia"})
    assert res.status_code == 403
    assert res.get_json() == {"error": "not_owner"}


def test_rename_player_taken_name_then_deleted(admin_client01, four_players_admin01):
    alice_id = four_players_admin01["alice_id"]
    res = admin_client01.patch(f"/api/players/{alice_id}", json={"name": "bob"})
    assert res.status_code == 409
    assert res.get_json() == {"error": "player_exists"}

    with get_session(write=True) as session:
        session.execute(delete(Player).where(Player.id == alice_id))
    res = admin_client01.patch(f"/api/players/{alice_id}", json={"name": "alicia"})
    assert res.status_code == 404
    assert res.get_json() == {"error": "not_found"}


def test_create_player_duplicate_name_allowed_across_different_admins(admin_client02, four_players_admin01):
    res = admin_client02.post("/api/players", json={"name": "alice"})
    assert res.status_code == 201


def test_get_players_alphabetical_ignoring_accents(admin_client01):
    for name in ("joseph", "josé"):
        admin_client01.post("/api/players", json={"name": name})
    names = [p["name"] for p in admin_client01.get("/api/players").get_json()]
    assert names == ["josé", "joseph"]
