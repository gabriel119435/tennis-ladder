from datetime import date

from sqlalchemy import select

from app.db import get_session
from app.models import Admin, Match, Ranking, RankingParticipant
from app.stats import compute_history, compute_standings


def _make_ranking(name):
    with get_session(write=True) as session:
        admin_id = session.scalars(select(Admin.id).filter_by(username='admin1')).one()
        ranking = Ranking(name=name, created_by_admin_id=admin_id)
        session.add(ranking)
        session.flush()
        return ranking.id


def _make_participant(ranking_id, player_id, active=True):
    with get_session(write=True) as session:
        session.add(
            RankingParticipant(
                ranking_id=ranking_id,
                player_id=player_id,
                active=active,
                joined_at=date.today().isoformat(),
            )
        )


def _make_match(ranking_id, round_, player_a_id, player_b_id, result_type='played', winner_id=None):
    with get_session(write=True) as session:
        session.add(
            Match(
                ranking_id=ranking_id,
                round=round_,
                player_a_id=player_a_id,
                player_b_id=player_b_id,
                result_type=result_type,
                winner_id=winner_id,
                date=date.today().isoformat(),
            )
        )


def test_compute_history_counts_played_matches_and_tracks_last_round(four_players_admin01):
    ranking_id = _make_ranking('history counts test')
    alice_id, bob_id = four_players_admin01['alice_id'], four_players_admin01['bob_id']

    _make_match(ranking_id, 1, alice_id, bob_id)
    _make_match(ranking_id, 3, alice_id, bob_id)

    with get_session() as session:
        history, last_played = compute_history(session, ranking_id)

    assert history[alice_id][bob_id] == 2
    assert history[bob_id][alice_id] == 2
    assert last_played[alice_id][bob_id] == 3
    assert last_played[bob_id][alice_id] == 3


def test_compute_history_ignores_walkover_and_no_match(four_players_admin01):
    ranking_id = _make_ranking('history ignore test')
    alice_id, bob_id = four_players_admin01['alice_id'], four_players_admin01['bob_id']

    _make_match(ranking_id, 1, alice_id, bob_id, result_type='walkover')
    _make_match(ranking_id, 2, alice_id, bob_id, result_type='no_match')

    with get_session() as session:
        history, last_played = compute_history(session, ranking_id)

    assert history == {}
    assert last_played == {}


def test_compute_standings_walkover_points(four_players_admin01):
    ranking_id = _make_ranking('walkover points test')
    alice_id, bob_id = four_players_admin01['alice_id'], four_players_admin01['bob_id']
    _make_participant(ranking_id, alice_id)
    _make_participant(ranking_id, bob_id)
    _make_match(ranking_id, 1, alice_id, bob_id, result_type='walkover', winner_id=alice_id)

    with get_session() as session:
        rows = compute_standings(session, ranking_id)

    by_id = {row['id']: row for row in rows}
    assert by_id[alice_id]['points'] == 100
    assert by_id[bob_id]['points'] == -100


def test_compute_standings_no_match_points(four_players_admin01):
    ranking_id = _make_ranking('no_match points test')
    alice_id, bob_id = four_players_admin01['alice_id'], four_players_admin01['bob_id']
    _make_participant(ranking_id, alice_id)
    _make_participant(ranking_id, bob_id)
    _make_match(ranking_id, 1, alice_id, bob_id, result_type='no_match')

    with get_session() as session:
        rows = compute_standings(session, ranking_id)

    by_id = {row['id']: row for row in rows}
    assert by_id[alice_id]['points'] == 0
    assert by_id[bob_id]['points'] == 0
    assert by_id[alice_id]['matches_played'] == 1
    assert by_id[bob_id]['matches_played'] == 1


def test_compute_standings_skips_inactive_player_but_keeps_opponent(four_players_admin01):
    ranking_id = _make_ranking('inactive skip test')
    alice_id, bob_id = four_players_admin01['alice_id'], four_players_admin01['bob_id']
    _make_participant(ranking_id, alice_id, active=True)
    _make_participant(ranking_id, bob_id, active=False)
    _make_match(ranking_id, 1, alice_id, bob_id, result_type='walkover', winner_id=alice_id)

    with get_session() as session:
        rows = compute_standings(session, ranking_id)

    by_id = {row['id']: row for row in rows}
    assert bob_id not in by_id
    assert by_id[alice_id]['points'] == 100
