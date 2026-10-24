from flask import Blueprint, abort, jsonify
from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from app.db import get_session
from app.models import Match, Ranking, SetScore
from app.rounds import save_result
from app.routes.helpers.decorators import require_admin
from app.routes.helpers.ownership import get_owned_ranking
from app.routes.helpers.payload import get_body, get_int, get_list, is_int

matches_bp = Blueprint("matches", __name__)


@matches_bp.route("/api/rankings/<int:ranking_id>/matches")
def get_matches(ranking_id):
    with get_session() as session:
        ranking = session.get(Ranking, ranking_id)
        if not ranking:
            abort(404, "not_found")
        matches = session.scalars(
            select(Match)
            .options(selectinload(Match.sets), selectinload(Match.player_a), selectinload(Match.player_b))
            .where(Match.ranking_id == ranking_id, Match.round == ranking.round)
            .order_by(Match.id)
        ).all()
    return jsonify([_serialize_match(m) for m in matches])


def _serialize_match(match):
    return {
        "id": match.id,
        "player_a_id": match.player_a_id,
        "player_a_name": match.player_a.name,
        "player_b_id": match.player_b_id,
        "player_b_name": match.player_b.name,
        "result_type": match.result_type,
        "winner_id": match.winner_id,
        "sets": [{"games_a": s.games_a, "games_b": s.games_b} for s in match.sets],
    }


@matches_bp.route("/api/matches/<int:match_id>/result", methods=["POST"])
@require_admin
def create_result(match_id):
    data = get_body()
    sets = get_list(data, "sets")
    wo_winner_id = get_int(data, "wo_winner_id")

    # exactly one: scores mean played, a wo winner means walkover, an empty form sends sets: []
    if bool(sets) == (wo_winner_id is not None):
        abort(400, "sets_or_wo_winner")

    with get_session(write=True) as session:
        match = _get_open_match(session, match_id)
        if match.result_type is not None:
            abort(409, "result_exists")

        if sets:
            result_type, winner_id = "played", None

            # fmt: off
            valid_sets = all(
                isinstance(set_, list) and len(set_) == 2 and all(map(is_int, set_)) for set_ in sets
            )
            # fmt: on

            if not valid_sets:
                abort(400, "invalid_sets")

            sets = [tuple(set_) for set_ in sets]
        else:
            result_type, sets, winner_id = "walkover", None, wo_winner_id

        try:
            save_result(session, match, result_type, sets, winner_id)
        except ValueError as e:
            abort(400, str(e))

    return jsonify({"message": "saved"}), 201


@matches_bp.route("/api/matches/<int:match_id>/result", methods=["DELETE"])
@require_admin
def delete_result(match_id):
    with get_session(write=True) as session:
        match = _get_open_match(session, match_id)
        if match.result_type is None:
            abort(404, "result_not_found")
        session.execute(delete(SetScore).where(SetScore.match_id == match_id))
        match.result_type = None
        match.winner_id = None

    return jsonify({"message": "cleared"})


def _get_open_match(session, match_id):
    match = session.get(Match, match_id)
    if not match:
        abort(404, "not_found")
    ranking = get_owned_ranking(session, match.ranking_id)
    if not ranking.ongoing or match.round != ranking.round:
        abort(403, "round_closed")
    return match
