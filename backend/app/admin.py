from sqlalchemy import select
from sqlalchemy.exc import OperationalError
from werkzeug.security import generate_password_hash

from app.db import get_session
from app.models import Admin
from app.validation import password_error


def create_admin(username, password):
    username = username.strip().lower()
    error = password_error(password)
    if error:
        raise ValueError(error)

    try:
        with get_session(write=True) as session:
            if session.scalars(select(Admin).filter_by(username=username)).one_or_none():
                return False
            session.add(Admin(username=username, password_hash=generate_password_hash(password)))
            return True
    except OperationalError:
        raise ValueError("db_error")
