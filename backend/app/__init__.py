import os

from flask import Flask, jsonify
from flask_cors import CORS
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

login_manager = LoginManager()

DEFAULT_ADMIN_PASS = "admin_pass"


def create_app():
    apply_migrations()

    app = Flask(__name__)
    secret_key = os.environ.get("SECRET_KEY")
    if not secret_key:
        print("warning: using insecure default public key")
        secret_key = "dev-default-value"
    app.secret_key = secret_key

    CORS(
        app,
        origins=os.environ.get("CORS_ORIGINS", "http://localhost:5173"),
        supports_credentials=True,
    )

    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        with get_session() as session:
            admin_ = session.scalars(select(Admin).filter_by(id=int(user_id))).one_or_none()
            if not admin_:
                return None
            return AuthAdmin(id=admin_.id, username=admin_.username, password_hash=admin_.password_hash)

    @login_manager.unauthorized_handler
    def unauthorized():
        return jsonify({"error": "unauthorized"}), 401

    @app.errorhandler(HTTPException)
    def handle_http_error(e):
        return jsonify({"error": e.description}), e.code

    _register_blueprints(app)

    return app


# migrations are by default idempotent, are always applied on startup
def apply_migrations():
    _migration_000_create_db()
    _migration_001_create_admin()


def _migration_000_create_db():
    Base.metadata.create_all(engine)  # idempotent: no op if tables already exist


def _migration_001_create_admin():
    admin_pass = os.environ.get("ADMIN_PASS", DEFAULT_ADMIN_PASS)
    if create_admin("admin", admin_pass):
        print(f"admin created, password: {admin_pass}")


def _register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(players_bp)
    app.register_blueprint(rankings_bp)
    app.register_blueprint(participants_bp)
    app.register_blueprint(matches_bp)
    app.register_blueprint(standings_bp)
