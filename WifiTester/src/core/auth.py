import bcrypt
from ..utils.storage import get_setting, set_setting

_PASSWORD_KEY = "app_password"


def is_first_run() -> bool:
    return get_setting(_PASSWORD_KEY) == ""


def set_password(password: str):
    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    set_setting(_PASSWORD_KEY, pw_hash)


def check_password(password: str) -> bool:
    stored = get_setting(_PASSWORD_KEY)
    if not stored:
        return True
    return bcrypt.checkpw(password.encode(), stored.encode())
