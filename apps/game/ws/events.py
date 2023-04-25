from apps.api import services as api_services
from apps.utils.local_storage import LocalStorage

local_storage = LocalStorage()


def login(data: dict[str, any]) -> bool:
    """
    ws callback for login
    :param data: dict(logged: bool)
    :return: None
    """
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return False

    token, refresh = api_services.request_login(username=username, password=password)
    if not token or not refresh:
        return False
    local_storage.set(LocalStorage.LocalStorageKeys.TOKEN.value, token)
    local_storage.set(LocalStorage.LocalStorageKeys.REFRESH.value, refresh)
    return True


def verify(data: dict[str, any]) -> bool:
    """
    ws callback for verify
    :param data: dict(logged: bool)
    :return: None
    """
    token = data.get("token")
    if not token:
        return False
    is_valid = api_services.request_token_verify(token=token)
    return is_valid
