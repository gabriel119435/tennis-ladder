import random

from flask import Blueprint, abort, jsonify, request
from flask_login import current_user
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.db import get_session
from app.models import Ranking
from app.rounds import close_current_round, start_next_round
from app.routes.helpers.decorators import require_admin
from app.routes.helpers.ownership import get_owned_ranking
from app.routes.helpers.payload import get_body, get_str
from app.validation import validate_name

rankings_bp = Blueprint("rankings", __name__)


@rankings_bp.route("/api/rankings")
def get_rankings():
    admin_id = request.args.get("admin_id")
    if admin_id is not None:
        try:
            admin_id = int(admin_id)
        except ValueError:
            abort(400, "invalid_payload")
    with get_session() as session:
        # serialized after the session closes, so the owner is loaded now
        query = select(Ranking).options(selectinload(Ranking.created_by_admin)).order_by(Ranking.id.desc())
        if admin_id is not None:
            query = query.where(Ranking.created_by_admin_id == admin_id)
        rankings = session.scalars(query).all()
    return jsonify([_serialize_ranking(r) for r in rankings])


@rankings_bp.route("/api/rankings", methods=["POST"])
@require_admin
def create_ranking():
    data = get_body()
    name = validate_name(get_str(data, "name"))

    try:
        with get_session(write=True) as session:
            session.add(Ranking(name=name, created_by_admin_id=current_user.id))
        return jsonify({"message": "created"}), 201
    except IntegrityError:
        abort(409, "ranking_exists")


def _serialize_ranking(ranking):
    return {
        "id": ranking.id,
        "name": ranking.name,
        "ongoing": ranking.ongoing,
        "round": ranking.round,
        # read by edit button enabling
        "created_by_admin_id": ranking.created_by_admin_id,
        # ranking picker value: ranking - user
        "created_by_admin_username": ranking.created_by_admin.username,
    }


@rankings_bp.route("/api/rankings/<int:ranking_id>/start", methods=["POST"])
@require_admin
def start_round(ranking_id):
    with get_session(write=True) as session:
        ranking = get_owned_ranking(session, ranking_id)
        if ranking.ongoing:
            abort(409, "round_ongoing")
        try:
            start_next_round(session, ranking, random.Random())
        except ValueError as e:
            abort(400, str(e))

    return jsonify({"message": "started"}), 201


@rankings_bp.route("/api/rankings/<int:ranking_id>/close", methods=["POST"])
@require_admin
def close_round(ranking_id):
    with get_session(write=True) as session:
        close_current_round(session, get_owned_ranking(session, ranking_id))

    return jsonify({"message": "closed"})
