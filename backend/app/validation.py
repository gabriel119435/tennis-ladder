from flask import abort

from app.constants import PASSWORD_MAX_LENGTH, PASSWORD_MIN_LENGTH


def password_error(password):
    if len(password) < PASSWORD_MIN_LENGTH:
        return "password_too_short"
    if len(password) > PASSWORD_MAX_LENGTH:
        return "password_too_long"
    return None


def validate_name(name, max_length):
    name = (name or "").strip().lower()
    if not name:
        abort(400, "name_required")
    if len(name) > max_length:
        abort(400, "name_too_long")
    return name
