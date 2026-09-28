from flask import Blueprint, request, jsonify, abort
from flask_login import current_user
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.db import get_session
from app.models import Player
from app.routes.helpers.annotations import require_admin

players_bp = Blueprint("players", __name__)


@players_bp.route("/api/players")
def get_players():
    admin_id = request.args.get("admin_id", type=int)
    with get_session() as session:
        query = select(Player).order_by(Player.id)
        if admin_id is not None:
            query = query.where(Player.created_by_admin_id == admin_id)
        players = session.scalars(query).all()
    return jsonify([_serialize_player(p) for p in players])


@players_bp.route("/api/players", methods=["POST"])
@require_admin
def create_player():
    name = _validate_player_name(request.get_json() or {})
    player = Player(name=name, created_by_admin_id=current_user.id)
    try:
        with get_session(write=True) as session:
            session.add(player)
            session.flush()
            return jsonify(_serialize_player(player)), 201
    except IntegrityError:
        abort(409, "player_exists")


@players_bp.route("/api/players/<int:player_id>", methods=["PATCH"])
@require_admin
def rename_player(player_id):
    name = _validate_player_name(request.get_json() or {})
    try:
        with get_session(write=True) as session:
            player = session.get(Player, player_id)
            if not player:
                abort(404, "not_found")
            if player.created_by_admin_id != current_user.id:
                abort(403, "not_owner")
            player.name = name
            return jsonify(_serialize_player(player)), 200
    except IntegrityError:
        abort(409, "player_exists")


def _validate_player_name(data):
    name = data.get("name", "").strip().lower()
    if not name:
        abort(400, "name_required")
    if len(name) > 25:
        abort(400, "name_too_long")
    return name


def _serialize_player(player):
    return {"id": player.id, "name": player.name, "created_by_admin_id": player.created_by_admin_id}
