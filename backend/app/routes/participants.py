from flask import Blueprint, abort, jsonify
from flask_login import current_user
from sqlalchemy import select

from app.db import get_session
from app.models import Player, Ranking, RankingParticipant
from app.routes.helpers.decorators import require_admin
from app.routes.helpers.ownership import get_owned_ranking
from app.routes.helpers.payload import get_body, get_int
from app.routes.helpers.sorting import name_sort_key

participants_bp = Blueprint("participants", __name__)


@participants_bp.route("/api/rankings/<int:ranking_id>/participants")
def get_participants(ranking_id):
    with get_session() as session:
        if not session.get(Ranking, ranking_id):
            abort(404, "not_found")
        rows = session.execute(
            select(RankingParticipant, Player.name)
            .join(Player, RankingParticipant.player_id == Player.id)
            .where(RankingParticipant.ranking_id == ranking_id, RankingParticipant.active.is_(True))
        ).all()
    rows = sorted(rows, key=lambda row: name_sort_key(row.name))
    return jsonify([_serialize_participant(participant, name) for participant, name in rows])


@participants_bp.route("/api/rankings/<int:ranking_id>/participants", methods=["POST"])
@require_admin
def add_participant(ranking_id):
    data = get_body()
    player_id = get_int(data, "player_id")
    if not player_id:
        abort(400, "player_id_required")

    with get_session(write=True) as session:
        get_owned_ranking(session, ranking_id)
        player = session.get(Player, player_id)
        if not player:
            abort(400, "invalid_player_id")
        if player.created_by_admin_id != current_user.id:
            abort(403, "not_owner")

        participant = _get_participant(session, ranking_id, player_id)
        if participant:
            participant.active = True
            status = 200
        else:
            session.add(
                RankingParticipant(
                    ranking_id=ranking_id,
                    player_id=player_id,
                    active=True,
                )
            )
            status = 201

    return jsonify({"message": "added"}), status


def _serialize_participant(participant, name):
    return {"player_id": participant.player_id, "name": name}


@participants_bp.route("/api/rankings/<int:ranking_id>/participants/<int:player_id>", methods=["DELETE"])
@require_admin
def remove_participant(ranking_id, player_id):
    with get_session(write=True) as session:
        get_owned_ranking(session, ranking_id)
        participant = _get_participant(session, ranking_id, player_id)
        if not participant:
            abort(404, "not_found")
        participant.active = False

    return jsonify({"message": "removed"})


def _get_participant(session, ranking_id, player_id):
    return session.scalars(
        select(RankingParticipant).where(
            RankingParticipant.ranking_id == ranking_id, RankingParticipant.player_id == player_id
        )
    ).one_or_none()
