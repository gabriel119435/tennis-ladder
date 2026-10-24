from sqlalchemy import select

from app.models import Match, SetScore
from app.pairing import build_round_pairings
from app.scoring import match_winner
from app.stats import compute_history, compute_standings


def start_next_round(session, ranking, rng):
    standings = compute_standings(session, ranking.id)
    standings_order = [row["id"] for row in standings]
    history, last_played = compute_history(session, ranking.id)
    pairs = build_round_pairings(standings_order, history, rng, last_played)

    ranking.ongoing = True
    ranking.round += 1
    for player_a_id, player_b_id in pairs:
        session.add(
            Match(
                ranking_id=ranking.id,
                round=ranking.round,
                player_a_id=player_a_id,
                player_b_id=player_b_id,
            )
        )


def close_current_round(session, ranking):
    pending = session.scalars(
        select(Match).where(
            Match.ranking_id == ranking.id,
            Match.round == ranking.round,
            Match.result_type.is_(None),
        )
    ).all()
    for match in pending:
        match.result_type = "no_match"
    ranking.ongoing = False


def save_result(session, match, result_type, sets, winner_id):
    if result_type == "played":
        winner_side = match_winner(sets)
        for i, (games_a, games_b) in enumerate(sets, start=1):
            session.add(SetScore(match_id=match.id, set_number=i, games_a=games_a, games_b=games_b))
        match.winner_id = match.player_a_id if winner_side == "a" else match.player_b_id
    else:
        if winner_id not in (match.player_a_id, match.player_b_id):
            raise ValueError("invalid_winner_id")
        match.winner_id = winner_id
    match.result_type = result_type
