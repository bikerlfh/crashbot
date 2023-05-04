# Standard Library
from typing import Optional

# Internal
from apps.api import services as api_services
from apps.utils.local_storage import LocalStorage

local_storage = LocalStorage()


def verify_token(token: Optional[str] = None) -> dict[str, any]:
    token = token or local_storage.get_token()
    if token:
        logged = api_services.request_token_verify(token=token)
        return dict(logged=logged)
    return dict(logged=False)


def login(username: str, password: str) -> dict[str, any]:
    token = local_storage.get_token()
    refresh = local_storage.get_refresh()
    if token:
        verify = verify_token(token=token)
        if verify.get("logged"):
            return verify
    elif refresh:
        token = api_services.request_token_refresh(refresh=refresh)
        if token:
            local_storage.set_token(token=token)
            return dict(logged=True)
    if not username or not password:
        return dict(logged=False)
    token, refresh = api_services.request_login(username=username, password=password)
    if not token or not refresh:
        return dict(logged=False)
    local_storage.set_token(token)
    local_storage.set_refresh(refresh)
    api_services.update_token()
    return dict(logged=True)
