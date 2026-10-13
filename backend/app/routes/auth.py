from flask import Blueprint, jsonify, abort
from flask_login import login_user, logout_user, current_user
from sqlalchemy import select
from werkzeug.security import check_password_hash

from app.db import get_session
from app.models import Admin, AuthAdmin
from app.routes.helpers.decorators import require_admin
from app.routes.helpers.payload import get_body, get_str

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/me")
def me():
    if current_user.is_authenticated:
        return jsonify({"user": _serialize_admin(current_user)})
    return jsonify({"user": None})


def _serialize_admin(admin):
    return {"id": admin.id, "username": admin.username}


@auth_bp.route("/api/login", methods=["POST"])
def login():
    data = get_body()
    username = get_str(data, "username", "").strip().lower()
    password = get_str(data, "password", "")

    with get_session() as session:
        admin = session.scalars(select(Admin).filter_by(username=username)).one_or_none()

        if not admin or not check_password_hash(admin.password_hash, password):
            abort(401, "invalid_credentials")

        login_user(AuthAdmin.from_admin(admin))
        return jsonify({"user": _serialize_admin(admin)})


@auth_bp.route("/api/logout", methods=["POST"])
@require_admin
def logout():
    logout_user()
    return jsonify({"message": "logged out"})
