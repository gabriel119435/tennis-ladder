import random

from flask import Blueprint, abort, jsonify
from flask_login import current_user

from app.admin import wipe_admin
from app.db import get_session
from app.routes.helpers.decorators import require_admin
from app.seed import seed_ranking
from app.settings import DEFAULT_ADMIN_NAME

reset_bp = Blueprint("reset", __name__)


@reset_bp.route("/api/reset", methods=["POST"])
@require_admin
def reset():
    if current_user.username != DEFAULT_ADMIN_NAME:
        abort(403, "not_default_admin")
    with get_session(write=True) as session:
        wipe_admin(session, current_user.id)
        seed_ranking(session, current_user.id, random.Random())
    return jsonify({"message": "reset"})
