from flask import Blueprint, request, jsonify, abort
from flask_login import login_user, logout_user, current_user
from sqlalchemy import select
from werkzeug.security import check_password_hash, generate_password_hash

from app.db import get_session
from app.models import Admin
from app.routes.helpers.annotations import require_admin

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
    data = request.get_json() or {}
    username = data.get("username", "").strip().lower()
    password = data.get("password", "")

    with get_session() as session:
        admin = session.scalars(select(Admin).filter_by(username=username)).one_or_none()

        if not admin or not check_password_hash(admin.password_hash, password):
            abort(401, "invalid_credentials")

        login_user(admin)
        return jsonify({"user": _serialize_admin(admin)})


@auth_bp.route("/api/logout", methods=["POST"])
@require_admin
def logout():
    logout_user()
    return jsonify({"message": "logged out"})


@auth_bp.route("/api/admin/password", methods=["PATCH"])
@require_admin
def change_admin_password():
    data = request.get_json() or {}
    old_password = data.get("old_password", "")
    new_password = data.get("new_password", "")

    if not check_password_hash(current_user.password_hash, old_password):
        abort(400, "wrong_current_password")

    if len(new_password) < 8:
        abort(400, "password_too_short")
    if len(new_password) > 25:
        abort(400, "password_too_long")

    with get_session(write=True) as session:
        new_pass_hash = generate_password_hash(new_password)
        admin = session.get(Admin, current_user.id)
        admin.password_hash = new_pass_hash

    return jsonify({"message": "password updated"})
