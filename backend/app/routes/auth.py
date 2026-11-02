from flask import Blueprint, abort, jsonify
from flask_login import current_user, login_user, logout_user
from sqlalchemy import select
from werkzeug.security import check_password_hash, generate_password_hash

from app.db import get_session
from app.models import Admin, AuthAdmin
from app.routes.helpers.decorators import require_admin
from app.routes.helpers.payload import get_body, get_str
from app.settings import DEFAULT_ADMIN_NAME, DEFAULT_ADMIN_PASS

auth_bp = Blueprint("auth", __name__)

# missing admin still runs password hash check, same response time
_DUMMY_HASH = generate_password_hash(DEFAULT_ADMIN_PASS)


@auth_bp.route("/api/me")
def me():
    if current_user.is_authenticated:
        return jsonify({"user": _serialize_admin(current_user)})
    return jsonify({"user": None})


def _serialize_admin(admin):
    return {"id": admin.id, "username": admin.username, "is_default": admin.username == DEFAULT_ADMIN_NAME}


@auth_bp.route("/api/login", methods=["POST"])
def login():
    data = get_body()
    username = get_str(data, "username", "").strip().lower()
    password = get_str(data, "password", "")

    with get_session() as session:
        admin = session.scalars(select(Admin).filter_by(username=username)).one_or_none()

        password_hash = admin.password_hash if admin else _DUMMY_HASH
        if not check_password_hash(password_hash, password) or not admin:
            abort(401, "invalid_credentials")

        login_user(AuthAdmin.from_admin(admin))
        return jsonify({"user": _serialize_admin(admin)})


@auth_bp.route("/api/logout", methods=["POST"])
@require_admin
def logout():
    logout_user()
    return jsonify({"message": "logged out"})
