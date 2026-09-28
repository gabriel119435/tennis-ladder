import os

from sqlalchemy import delete, select
from werkzeug.security import generate_password_hash

# must be set before any app import so db.py picks it up at module load time
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

import pytest

from app import create_app
from app.db import get_session
from app.models import Admin, Player, Ranking, RankingParticipant, Match, SetScore


# session is the entire test runtime, so once per test run
@pytest.fixture(scope='session')
def app():
    app = create_app()
    app.config['TESTING'] = True
    return app


# function-scoped so each test starts unauthenticated with a clean cookie jar
@pytest.fixture
def client(app):
    return app.test_client()


def _get_or_create_admin(username, password):
    with get_session(write=True) as session:
        admin = session.scalars(select(Admin).filter_by(username=username)).one_or_none()
        if not admin:
            admin = Admin(username=username, password_hash=generate_password_hash(password))
            session.add(admin)
            session.flush()
        return admin.id


@pytest.fixture
def admin_client01(app):
    _get_or_create_admin('admin1', 'admin_pass1')
    test_client = app.test_client()
    test_client.post('/api/login', json={'username': 'admin1', 'password': 'admin_pass1'})
    return test_client


@pytest.fixture
def admin_client02(app):
    _get_or_create_admin('admin2', 'admin_pass2')
    test_client = app.test_client()
    test_client.post('/api/login', json={'username': 'admin2', 'password': 'admin_pass2'})
    return test_client


@pytest.fixture(autouse=True)  # runs for every test, so no test leaks data into the next
def _clean_db(app):
    yield
    with get_session(write=True) as session:
        session.execute(delete(SetScore))
        session.execute(delete(Match))
        session.execute(delete(RankingParticipant))
        session.execute(delete(Ranking))
        session.execute(delete(Player))
        session.execute(delete(Admin).where(Admin.username != 'admin'))


@pytest.fixture
def four_players_admin01(app):
    admin1_id = _get_or_create_admin('admin1', 'admin_pass1')
    with get_session(write=True) as session:
        players = [
            Player(name=name, created_by_admin_id=admin1_id) for name in ('alice', 'bob', 'charlie', 'dave')
        ]
        session.add_all(players)
        session.flush()
        return {f'{p.name}_id': p.id for p in players}


def create_ranking(admin_client, name='ranking_name01'):
    res = admin_client.post('/api/rankings', json={'name': name})
    return res.get_json()['id']


def register(admin_client, ranking_id, four_players, *names):
    for name in names:
        admin_client.post(
            f'/api/participants/{ranking_id}',
            json={'player_id': four_players[f'{name}_id']}
        )


@pytest.fixture
def ranking_id(admin_client01, four_players_admin01):
    ranking_id = create_ranking(admin_client01)
    register(admin_client01, ranking_id, four_players_admin01, 'alice', 'bob', 'charlie', 'dave')
    admin_client01.post(f'/api/rankings/{ranking_id}/start')
    return ranking_id
