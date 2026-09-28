import random
from datetime import date as date_type

from flask import Blueprint, request, jsonify, abort
from flask_login import current_user
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.db import get_session
from app.models import Ranking, Match
from app.pairing import build_round_pairings, MIN_ACTIVE_TO_START
from app.routes.helpers.annotations import require_admin
from app.stats import compute_standings, compute_history

rankings_bp = Blueprint("rankings", __name__)


@rankings_bp.route("/api/rankings")
def get_rankings():
    admin_id = request.args.get("admin_id", type=int)
    with get_session() as session:
        query = select(Ranking).order_by(Ranking.id.desc())
        if admin_id is not None:
            query = query.where(Ranking.created_by_admin_id == admin_id)
        rankings = session.scalars(query).all()
    return jsonify([_serialize_ranking(r) for r in rankings])


@rankings_bp.route("/api/rankings/<int:ranking_id>")
def get_ranking(ranking_id):
    with get_session() as session:
        ranking = session.get(Ranking, ranking_id)
        if not ranking:
            abort(404, "not_found")
        return jsonify(_serialize_ranking(ranking))


@rankings_bp.route("/api/rankings", methods=["POST"])
@require_admin
def create_ranking():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    if not name:
        abort(400, "name_required")
    if len(name) > 50:
        abort(400, "name_too_long")

    ranking = Ranking(name=name, created_by_admin_id=current_user.id)
    try:
        with get_session(write=True) as session:
            session.add(ranking)
            session.flush()
            return jsonify(_serialize_ranking(ranking)), 201
    except IntegrityError:
        abort(409, "ranking_exists")


def _serialize_ranking(ranking):
    return {
        "id": ranking.id,
        "name": ranking.name,
        "ongoing": ranking.ongoing,
        "round": ranking.round,
        "created_by_admin_id": ranking.created_by_admin_id,
    }


@rankings_bp.route("/api/rankings/<int:ranking_id>/start", methods=["POST"])
@require_admin
def start_round(ranking_id):
    with get_session(write=True) as session:
        ranking = session.get(Ranking, ranking_id)
        if not ranking:
            abort(404, "not_found")
        if ranking.created_by_admin_id != current_user.id:
            abort(403, "not_owner")

        standings = compute_standings(session, ranking_id)
        if len(standings) < MIN_ACTIVE_TO_START:
            abort(400, "too_few_active_participants")

        standings_order = [row["id"] for row in standings]
        history, last_played = compute_history(session, ranking_id)
        pairs = build_round_pairings(standings_order, history, random.Random(), last_played)

        ranking.ongoing = True
        ranking.round += 1
        for player_a_id, player_b_id in pairs:
            session.add(
                Match(
                    ranking_id=ranking_id,
                    round=ranking.round,
                    player_a_id=player_a_id,
                    player_b_id=player_b_id,
                )
            )

    return jsonify({"message": "started"}), 201


@rankings_bp.route("/api/rankings/<int:ranking_id>/close", methods=["POST"])
@require_admin
def close_round(ranking_id):
    with get_session(write=True) as session:
        ranking = session.get(Ranking, ranking_id)
        if not ranking:
            abort(404, "not_found")
        if ranking.created_by_admin_id != current_user.id:
            abort(403, "not_owner")

        today = date_type.today().isoformat()
        pending = session.scalars(
            select(Match).where(
                Match.ranking_id == ranking_id, Match.round == ranking.round, Match.result_type.is_(None)
            )
        ).all()

        for match in pending:
            match.result_type = "no_match"
            match.date = today

        ranking.ongoing = False

    return jsonify({"message": "closed"})
