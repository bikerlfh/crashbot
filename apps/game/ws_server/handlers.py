# Standard Library
from typing import Optional

# Internal
from apps.api import services as api_services
from apps.globals import GlobalVars
from apps.utils.local_storage import LocalStorage

local_storage = LocalStorage()


def _get_customer_data() -> None:
    customer_data = api_services.get_customer_data(
        app_hash_str=GlobalVars.APP_HASH
    )
    GlobalVars.set_plan_with_ai(customer_data.plan.with_ai)
    bots = api_services.get_bots()
    GlobalVars.set_bots(bots=bots)
    crash_app = customer_data.plan.crash_app
    home_bet_game_id = crash_app.home_bet_game_id
    GlobalVars.set_home_bet_game_id(home_bet_game_id)
    GlobalVars.set_allowed_home_bets(crash_app.home_bets)
    local_storage.set_customer_id(customer_id=customer_data.customer_id)


def verify_token(token: Optional[str] = None) -> dict[str, any]:
    token = token or local_storage.get_token()
    if token:
        logged = api_services.request_token_verify()
        if logged:
            _get_customer_data()
        return dict(logged=logged)
    return dict(logged=False)


def login(username: str, password: str) -> dict[str, any]:
    token = local_storage.get_token()
    if token:
        verify = verify_token(token=token)
        if verify.get("logged"):
            return verify
    if not username or not password:
        return dict(logged=False)
    token = api_services.request_login(username=username, password=password)
    if not token:
        return dict(logged=False)
    local_storage.set_token(token)
    api_services.update_token()
    _get_customer_data()
    return dict(logged=True)
