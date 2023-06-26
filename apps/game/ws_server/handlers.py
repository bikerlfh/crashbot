# Standard Library
from typing import Optional

# Internal
from apps.api import services as api_services
from apps.utils.local_storage import LocalStorage

local_storage = LocalStorage()


def _get_customer_data() -> None:
    customer_data = api_services.get_customer_data()
    home_bets = []
    for home_bet in customer_data.home_bets:
        home_bets.append(vars(home_bet))
    local_storage.set_home_bets(home_bets=home_bets)
    local_storage.set_customer_id(customer_id=customer_data.customer_id)


def verify_token(token: Optional[str] = None) -> dict[str, any]:
    token = token or local_storage.get_token()
    if token:
        logged = api_services.request_token_verify(token=token)
        if logged:
            _get_customer_data()
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
            api_services.update_token()
            _get_customer_data()
            return dict(logged=True)
    if not username or not password:
        return dict(logged=False)
    token, refresh = api_services.request_login(
        username=username, password=password
    )
    if not token or not refresh:
        return dict(logged=False)
    local_storage.set_token(token)
    local_storage.set_refresh(refresh)
    api_services.update_token()
    _get_customer_data()
    return dict(logged=True)
