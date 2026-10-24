from flask import abort, request


def get_body():
    data = request.get_json()
    if data is None:
        data = {}
    if not isinstance(data, dict):
        abort(400, "invalid_payload")
    return data


def get_list(data, key):
    value = data.get(key)
    if value is None:
        return []
    if not isinstance(value, list):
        abort(400, "invalid_payload")
    return value


def get_str(data, key, default=None):
    value = data.get(key)
    if value is None:
        return default
    if not isinstance(value, str):
        abort(400, "invalid_payload")
    return value


def get_int(data, key):
    value = data.get(key)
    if value is None:
        return None
    if not is_int(value):
        abort(400, "invalid_payload")
    return value


# bool is a subclass of int in python, true/false would pass as 1/0 without the second check
def is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)
