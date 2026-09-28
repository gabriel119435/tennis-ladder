from sqlalchemy import select
from sqlalchemy.exc import OperationalError
from werkzeug.security import generate_password_hash

from app.db import get_session
from app.models import Admin


def create_admin(username, password):
    username = username.strip().lower()
    if len(password) < 8:
        raise ValueError("password_too_short")
    if len(password) > 25:
        raise ValueError("password_too_long")

    try:
        with get_session(write=True) as session:
            if session.scalars(select(Admin).filter_by(username=username)).one_or_none():
                return False
            session.add(Admin(username=username, password_hash=generate_password_hash(password)))
            return True
    except OperationalError:
        raise ValueError("db_error")
