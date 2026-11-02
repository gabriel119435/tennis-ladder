from functools import wraps

from flask import abort
from flask_login import current_user

from app.models import AuthAdmin


def require_admin(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        # admin type, not just logged in, so a future non admin login can't pass
        if not isinstance(current_user, AuthAdmin):
            abort(401, "unauthorized")
        return f(*args, **kwargs)

    return wrapped
