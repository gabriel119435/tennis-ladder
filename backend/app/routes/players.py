from flask import Blueprint, request, jsonify, abort
from flask_login import current_user
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.constants import PLAYER_NAME_MAX_LENGTH
from app.db import get_session
from app.models import Player
from app.routes.helpers.decorators import require_admin
from app.routes.helpers.payload import get_body, get_str
from app.validation import validate_name

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
    name = _validate_player_name(get_body())
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
    name = _validate_player_name(get_body())
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
    return validate_name(get_str(data, "name"), PLAYER_NAME_MAX_LENGTH)


def _serialize_player(player):
    return {"id": player.id, "name": player.name, "created_by_admin_id": player.created_by_admin_id}
