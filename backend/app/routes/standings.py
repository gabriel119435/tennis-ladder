from flask import Blueprint, jsonify, abort

from app.db import get_session
from app.models import Ranking
from app.stats import compute_standings

standings_bp = Blueprint("standings", __name__)


@standings_bp.route("/api/standings/<int:ranking_id>")
def get_standings(ranking_id):
    with get_session() as session:
        if not session.get(Ranking, ranking_id):
            abort(404, "not_found")
        standings = compute_standings(session, ranking_id)
    return jsonify(standings)
