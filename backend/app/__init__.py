import logging
import os
import re

from flask import Flask, jsonify
from flask_login import LoginManager
from sqlalchemy import select
from werkzeug.exceptions import HTTPException

from app.admin import create_admin
from app.db import get_session
from app.migrations import apply_migrations
from app.models import Admin, AuthAdmin
from app.routes.auth import auth_bp
from app.routes.matches import matches_bp
from app.routes.participants import participants_bp
from app.routes.players import players_bp
from app.routes.rankings import rankings_bp
from app.routes.reset import reset_bp
from app.routes.standings import standings_bp
from app.settings import DEFAULT_ADMIN_NAME, DEFAULT_ADMIN_PASS, DEFAULT_ADMIN_SEED_RANKING, check_settings

login_manager = LoginManager()
logger = logging.getLogger(__name__)


def create_app():
    # same as flask default format: [2026-10-13 10:00:00,000] INFO in __init__: admin created
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s")
    # fails startup on an invalid env value, before any of them is used
    check_settings()
    apply_migrations()
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
        if not user_id.isdigit():
            return None
        with get_session() as session:
            _admin = session.get(Admin, int(user_id))
            if not _admin:
                return None
            return AuthAdmin.from_admin(_admin)

    @app.errorhandler(HTTPException)
    def handle_http_error(e):
        # a snake_case description is an error code, sent as is: a typo reaches the ui as "<code> not found", by design
        # any other text, like werkzeug's default sentences, falls back to the status name below
        if re.fullmatch(r"[a-z_]+", e.description):
            return jsonify({"error": e.description}), e.code
        # "Method Not Allowed" -> "method_not_allowed"
        return jsonify({"error": e.name.lower().replace(" ", "_")}), e.code

    _register_blueprints(app)

    return app


# data step, not a migration: runs on every startup, creates the admin only if missing
def _create_default_admin():
    with get_session() as session:
        # admin already exists, DEFAULT_ADMIN_PASS is not used
        if session.scalars(select(Admin).filter_by(username=DEFAULT_ADMIN_NAME)).one_or_none():
            return
    # the sample ranking comes only with the default admin during startup that creates it
    # DEFAULT_ADMIN_SEED_RANKING=0 skips it
    create_admin(
        DEFAULT_ADMIN_NAME,
        DEFAULT_ADMIN_PASS,
        seed=DEFAULT_ADMIN_SEED_RANKING,
    )
    logger.info("admin created")


def _register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(players_bp)
    app.register_blueprint(rankings_bp)
    app.register_blueprint(participants_bp)
    app.register_blueprint(matches_bp)
    app.register_blueprint(standings_bp)
    app.register_blueprint(reset_bp)
