from datetime import date as date_type

from flask import Blueprint, jsonify, abort
from flask_login import current_user
from sqlalchemy import select

from app.db import get_session
from app.models import Ranking, RankingParticipant, Player
from app.routes.helpers.decorators import require_admin
from app.routes.helpers.payload import get_body, get_int

participants_bp = Blueprint("participants", __name__)


@participants_bp.route("/api/participants/<int:ranking_id>")
def get_participants(ranking_id):
    with get_session() as session:
        rows = session.execute(
            select(RankingParticipant, Player.name)
            .join(Player, RankingParticipant.player_id == Player.id)
            .where(RankingParticipant.ranking_id == ranking_id)
            .order_by(RankingParticipant.id)
        ).all()
    return jsonify([_serialize_participant(participant, name) for participant, name in rows])


@participants_bp.route("/api/participants/<int:ranking_id>", methods=["POST"])
@require_admin
def add_participant(ranking_id):
    data = get_body()
    player_id = get_int(data, "player_id")
    if not player_id:
        abort(400, "player_id_required")

    with get_session(write=True) as session:
        ranking = session.get(Ranking, ranking_id)
        if not ranking:
            abort(404, "not_found")
        player = session.get(Player, player_id)
        if not player:
            abort(400, "invalid_player_id")
        if ranking.created_by_admin_id != current_user.id or player.created_by_admin_id != current_user.id:
            abort(403, "not_owner")

        participant = _get_participant(session, ranking_id, player_id)
        if participant:
            participant.active = True
            status = 200
        else:
            participant = RankingParticipant(
                ranking_id=ranking_id,
                player_id=player_id,
                active=True,
                joined_at=date_type.today().isoformat(),
            )
            session.add(participant)
            session.flush()
            status = 201

        return jsonify(_serialize_participant(participant, player.name)), status


def _serialize_participant(participant, name):
    return {
        "id": participant.id,
        "ranking_id": participant.ranking_id,
        "player_id": participant.player_id,
        "name": name,
        "active": participant.active,
        "joined_at": participant.joined_at,
    }


@participants_bp.route("/api/participants/<int:ranking_id>/<int:player_id>", methods=["DELETE"])
@require_admin
def remove_participant(ranking_id, player_id):
    with get_session(write=True) as session:
        ranking = session.get(Ranking, ranking_id)
        if not ranking:
            abort(404, "not_found")
        if ranking.created_by_admin_id != current_user.id:
            abort(403, "not_owner")

        participant = _get_participant(session, ranking_id, player_id)
        if not participant:
            abort(404, "not_found")
        participant.active = False

    return jsonify({"message": "removed"})


def _get_participant(session, ranking_id, player_id):
    return session.scalars(
        select(RankingParticipant).where(
            RankingParticipant.ranking_id == ranking_id,
            RankingParticipant.player_id == player_id
        )
    ).one_or_none()
