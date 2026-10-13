import logging
import os
import re

from flask import Flask, jsonify
from flask_login import LoginManager
from sqlalchemy import select
from werkzeug.exceptions import HTTPException

from app.admin import create_admin
from app.db import get_session, engine, Base
from app.models import Admin, AuthAdmin
from app.routes.auth import auth_bp
from app.routes.matches import matches_bp
from app.routes.participants import participants_bp
from app.routes.players import players_bp
from app.routes.rankings import rankings_bp
from app.routes.standings import standings_bp
from app.validation import password_error

login_manager = LoginManager()
logger = logging.getLogger(__name__)

DEFAULT_ADMIN_PASS = "admin_pass"


def create_app():
    # same as flask default format: [2026-10-13 10:00:00,000] INFO in __init__: admin created
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s")
    _apply_migrations()
    # needs the final schema, so it runs after every migration
    _create_default_admin()

    app = Flask(__name__)
    secret_key = os.environ.get("SECRET_KEY")
    if not secret_key:
        logger.warning("using insecure default secret key")
        secret_key = "dev-default-value"
    app.secret_key = secret_key
    # session cookie is never sent on requests coming from other sites
    app.config["SESSION_COOKIE_SAMESITE"] = "Strict"
    # SESSION_COOKIE_SECURE=1: session cookie only travels over https, for deploys behind https
    app.config["SESSION_COOKIE_SECURE"] = os.environ.get("SESSION_COOKIE_SECURE") == "1"

    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        with get_session() as session:
            admin_ = session.get(Admin, int(user_id))
            if not admin_:
                return None
            return AuthAdmin.from_admin(admin_)

    @app.errorhandler(HTTPException)
    def handle_http_error(e):
        if re.fullmatch(r"[a-z_]+", e.description):
            return jsonify({"error": e.description}), e.code
        # "Method Not Allowed" -> "method_not_allowed"
        return jsonify({"error": e.name.lower().replace(" ", "_")}), e.code

    _register_blueprints(app)

    return app


# migrations are by default idempotent, are always applied on startup
def _apply_migrations():
    _migration_000_create_db()


def _migration_000_create_db():
    Base.metadata.create_all(engine)  # idempotent: no op if tables already exist


# data step, not a migration: runs on every startup, creates the admin only if missing
def _create_default_admin():
    with get_session() as session:
        # admin already exists, ADMIN_PASS is not read
        if session.scalars(select(Admin).filter_by(username="admin")).one_or_none():
            return
    create_admin("admin", _get_admin_pass())
    logger.info("admin created")


def _get_admin_pass():
    # ADMIN_PASS unset or empty: use a known weak default, for local dev only
    admin_pass = os.environ.get("ADMIN_PASS") or DEFAULT_ADMIN_PASS
    error = password_error(admin_pass)
    if error:
        raise ValueError(f"ADMIN_PASS: {error}")
    return admin_pass


def _register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(players_bp)
    app.register_blueprint(rankings_bp)
    app.register_blueprint(participants_bp)
    app.register_blueprint(matches_bp)
    app.register_blueprint(standings_bp)
