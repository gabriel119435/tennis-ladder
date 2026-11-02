from conftest import create_ranking, register_participants

from app.seed import DEFAULT_RANKING_NAME
from app.settings import DEFAULT_ADMIN_NAME, DEFAULT_ADMIN_PASS


def _default_admin_client(app):
    client = app.test_client()
    client.post("/api/login", json={"username": DEFAULT_ADMIN_NAME, "password": DEFAULT_ADMIN_PASS})
    return client


def test_reset_requires_admin(client):
    assert client.post("/api/reset").status_code == 401


def test_reset_rejects_other_admins(admin_client01):
    res = admin_client01.post("/api/reset")
    assert res.status_code == 403
    assert res.get_json() == {"error": "not_default_admin"}


def test_reset_wipes_and_seeds_the_default_admin(app):
    client = _default_admin_client(app)
    client.post("/api/players", json={"name": "erin"})
    create_ranking(client)
    admin_id = client.get("/api/me").get_json()["user"]["id"]

    assert client.post("/api/reset").status_code == 200

    rankings = client.get(f"/api/rankings?admin_id={admin_id}").get_json()
    names = {p["name"] for p in client.get("/api/players").get_json()}
    assert [r["name"] for r in rankings] == [DEFAULT_RANKING_NAME]
    assert len(names) == 20
    assert "erin" not in names


def test_reset_keeps_other_admins_data(app, admin_client01, four_players_admin01):
    ranking_id = create_ranking(admin_client01)
    register_participants(admin_client01, ranking_id, four_players_admin01, "alice", "bob", "charlie")
    admin_id = admin_client01.get("/api/me").get_json()["user"]["id"]

    _default_admin_client(app).post("/api/reset")

    assert len(admin_client01.get(f"/api/rankings?admin_id={admin_id}").get_json()) == 1
    assert len(admin_client01.get("/api/players").get_json()) == 4
    assert len(admin_client01.get(f"/api/rankings/{ranking_id}/participants").get_json()) == 3
