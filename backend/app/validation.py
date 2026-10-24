from flask import abort

from app.constants import NAME_MAX_LENGTH, NAME_WORD_MAX_LENGTH, PASSWORD_MAX_LENGTH, PASSWORD_MIN_LENGTH


def password_error(password):
    if len(password) < PASSWORD_MIN_LENGTH:
        return "password_too_short"
    if len(password) > PASSWORD_MAX_LENGTH:
        return "password_too_long"
    return None


def name_error(name):
    if not name:
        return "name_required"
    if len(name) > NAME_MAX_LENGTH:
        return "name_too_long"
    if any(len(word) > NAME_WORD_MAX_LENGTH for word in name.split()):
        return "word_too_long"
    return None


def validate_name(name):
    name = (name or "").strip().lower()
    error = name_error(name)
    if error:
        abort(400, error)
    return name
