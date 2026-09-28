from datetime import date as date_type

from flask import Blueprint, request, jsonify, abort
from flask_login import current_user
from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from app.db import get_session
from app.models import Match, Ranking, SetScore
from app.routes.helpers.annotations import require_admin
from app.scoring import match_winner

matches_bp = Blueprint("matches", __name__)


@matches_bp.route("/api/rankings/<int:ranking_id>/matches")
def get_matches(ranking_id):
    round_param = request.args.get("round", type=int)
    with get_session() as session:
        query = select(Match).options(selectinload(Match.sets)).where(Match.ranking_id == ranking_id)
        if round_param is not None:
            query = query.where(Match.round == round_param)
        matches = session.scalars(query.order_by(Match.round, Match.id)).all()
    return jsonify([_serialize_match(m) for m in matches])


def _serialize_match(match):
    return {
        "id": match.id,
        "round": match.round,
        "player_a_id": match.player_a_id,
        "player_b_id": match.player_b_id,
        "result_type": match.result_type,
        "winner_id": match.winner_id,
        "date": match.date,
        "sets": [{"set_number": s.set_number, "games_a": s.games_a, "games_b": s.games_b} for s in match.sets],
    }


@matches_bp.route("/api/matches/<int:match_id>", methods=["PATCH"])
@require_admin
def update_match(match_id):
    data = request.get_json() or {}
    result_type = data.get("result_type")
    if result_type not in ("played", "walkover"):
        abort(400, "invalid_result_type")

    with get_session(write=True) as session:
        match = session.get(Match, match_id)
        if not match:
            abort(404, "not_found")
        ranking = session.get(Ranking, match.ranking_id)
        if ranking.created_by_admin_id != current_user.id:
            abort(403, "not_owner")
        if not ranking.ongoing or match.round != ranking.round:
            abort(403, "round_closed")

        session.execute(delete(SetScore).where(SetScore.match_id == match_id))

        if result_type == "played":
            try:
                sets = [(int(a), int(b)) for a, b in data.get("sets", [])]
            except (ValueError, TypeError):
                abort(400, "invalid_sets")
            try:
                winner_side = match_winner(sets)
            except ValueError as e:
                abort(400, str(e))
            for i, (games_a, games_b) in enumerate(sets, start=1):
                session.add(SetScore(match_id=match_id, set_number=i, games_a=games_a, games_b=games_b))
            match.winner_id = match.player_a_id if winner_side == "a" else match.player_b_id
        else:
            winner_id = data.get("winner_id")
            if winner_id not in (match.player_a_id, match.player_b_id):
                abort(400, "invalid_winner_id")
            match.winner_id = winner_id

        match.result_type = result_type
        match.date = date_type.today().isoformat()

    return jsonify({"message": "saved"})
