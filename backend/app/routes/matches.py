from datetime import date as date_type

from flask import Blueprint, request, jsonify, abort
from flask_login import current_user
from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from app.db import get_session
from app.models import Match, Ranking, SetScore
from app.routes.helpers.decorators import require_admin
from app.routes.helpers.payload import get_body, get_int, get_list, get_str
from app.scoring import match_winner

matches_bp = Blueprint("matches", __name__)


@matches_bp.route("/api/rankings/<int:ranking_id>/matches")
def get_matches(ranking_id):
    round_param = request.args.get("round", type=int)
    with get_session() as session:
        query = (
            select(Match)
            .options(selectinload(Match.sets), selectinload(Match.player_a), selectinload(Match.player_b))
            .where(Match.ranking_id == ranking_id)
        )
        if round_param is not None:
            query = query.where(Match.round == round_param)
        matches = session.scalars(query.order_by(Match.round, Match.id)).all()
    return jsonify([_serialize_match(m) for m in matches])


def _serialize_match(match):
    return {
        "id": match.id,
        "round": match.round,
        "player_a_id": match.player_a_id,
        "player_a_name": match.player_a.name,
        "player_b_id": match.player_b_id,
        "player_b_name": match.player_b.name,
        "result_type": match.result_type,
        "winner_id": match.winner_id,
        "date": match.date,
        "sets": [{"set_number": s.set_number, "games_a": s.games_a, "games_b": s.games_b} for s in match.sets],
    }


@matches_bp.route("/api/matches/<int:match_id>/result", methods=["POST"])
@require_admin
def create_result(match_id):
    data = get_body()
    result_type = get_str(data, "result_type")
    if result_type not in ("played", "walkover"):
        abort(400, "invalid_result_type")

    with get_session(write=True) as session:
        match = _get_open_match(session, match_id)
        if match.result_type is not None:
            abort(409, "result_exists")

        if result_type == "played":
            sets = get_list(data, "sets")
            # type() is int excludes bool, isinstance would let true/false through as 1/0
            sets_valid = all(
                isinstance(set_, list) and len(set_) == 2 and all(type(score) is int for score in set_)
                for set_ in sets
            )
            if not sets_valid:
                abort(400, "invalid_sets")
            sets = [tuple(set_) for set_ in sets]
            try:
                winner_side = match_winner(sets)
            except ValueError as e:
                abort(400, str(e))
            for i, (games_a, games_b) in enumerate(sets, start=1):
                session.add(SetScore(match_id=match_id, set_number=i, games_a=games_a, games_b=games_b))
            match.winner_id = match.player_a_id if winner_side == "a" else match.player_b_id
        else:
            winner_id = get_int(data, "winner_id")
            if winner_id not in (match.player_a_id, match.player_b_id):
                abort(400, "invalid_winner_id")
            match.winner_id = winner_id

        match.result_type = result_type
        match.date = date_type.today().isoformat()

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
        match.date = None

    return jsonify({"message": "cleared"})


def _get_open_match(session, match_id):
    match = session.get(Match, match_id)
    if not match:
        abort(404, "not_found")
    ranking = session.get(Ranking, match.ranking_id)
    if ranking.created_by_admin_id != current_user.id:
        abort(403, "not_owner")
    if not ranking.ongoing or match.round != ranking.round:
        abort(403, "round_closed")
    return match
