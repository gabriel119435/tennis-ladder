import os

from app.validation import name_error, password_error

# values read once from env vars at import, the fallbacks are known weak defaults for local dev only
# admin password is only stored on the startup when creating the default admin
# it also builds _DUMMY_HASH. admin name is read on every login, /api/me and reset
DEFAULT_ADMIN_NAME = (os.environ.get("DEFAULT_ADMIN_NAME") or "administrador").strip().lower()
DEFAULT_ADMIN_PASS = os.environ.get("DEFAULT_ADMIN_PASS") or "senha secreta"
# SEED_RANKING=0 skips the sample ranking that comes with the default admin
SEED_RANKING = os.environ.get("SEED_RANKING", "1") == "1"


def check_settings():
    # same rules as every other admin name and password, for both the env value and the fallback
    # runs on startup, so a bad value stops the app instead of failing on the default admin creation
    errors = {
        "DEFAULT_ADMIN_NAME": name_error(DEFAULT_ADMIN_NAME),
        "DEFAULT_ADMIN_PASS": password_error(DEFAULT_ADMIN_PASS),
    }
    for var, error in errors.items():
        if error:
            raise ValueError(f"{var}: {error}")
