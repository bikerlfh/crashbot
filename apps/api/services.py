# Standard Library
import logging
from typing import Optional

# Internal
from apps.api.bot_api import BotAPIConnector
from apps.api.exceptions import BotAPINoAuthorizationException
from apps.api.models import (
    BetData,
    Bot,
    CustomerData,
    HomeBet,
    MultiplierPositions,
    Positions,
    Prediction,
)

logger = logging.getLogger(__name__)


def update_token() -> None:
    """
    update_token
    :return:
    """
    bot_connector = BotAPIConnector()
    bot_connector.update_token()


def request_login(*, username: str, password: str) -> tuple[str | None, str | None]:
    """
    request_login
    :param username:
    :param password:
    :return: access, refresh
    """
    bot_connector = BotAPIConnector()
    try:
        response = bot_connector.services.login(username=username, password=password)
        access = response.get("access")
        refresh = response.get("refresh")
        return access, refresh
    except BotAPINoAuthorizationException:
        return None, None
    except Exception as exc:
        logger.exception(f"BotAPIServices :: request_login :: {exc}")
        return None, None


def request_token_refresh(*, refresh: str) -> str | None:
    """
    request_token_refresh
    :param refresh:
    :return:
    """
    bot_connector = BotAPIConnector()
    try:
        response = bot_connector.services.token_refresh(refresh=refresh)
        access = response.get("access")
        return access
    except BotAPINoAuthorizationException:
        return None
    except Exception as exc:
        logger.exception(f"BotAPIServices :: request_token_refresh :: {exc}")
        return None


def request_token_verify(*, token: str) -> bool:
    """
    request_token_verify
    :param token:
    :return:
    """
    bot_connector = BotAPIConnector()
    try:
        is_valid = bot_connector.services.token_verify(token=token)
        return is_valid
    except BotAPINoAuthorizationException:
        return False
    except Exception as exc:
        logger.exception(f"BotAPIServices :: request_token_verify :: {exc}")
        return False


def get_home_bets() -> list[HomeBet]:
    """
    request_home_bet
    :return:
    """
    bot_connector = BotAPIConnector()
    home_bets = bot_connector.services.get_home_bet()
    data = [HomeBet(**data) for data in home_bets]
    return data


def add_multipliers(*, home_bet_id: int, multipliers: list[float]) -> dict[str, any]:
    """
    add_multipliers
    :param home_bet_id:
    :param multipliers:
    :return:
    """
    bot_connector = BotAPIConnector()
    response = bot_connector.services.add_multipliers(
        home_bet_id=home_bet_id, multipliers=multipliers
    )
    return response


def request_prediction(
    *,
    home_bet_id: int,
    multipliers: list[float],
    model_home_bet_id: Optional[int] = None,
) -> list[Prediction]:
    """
    request_prediction
    :param home_bet_id:
    :param multipliers:
    :param model_home_bet_id:
    :return:
    """
    bot_connector = BotAPIConnector()
    response = bot_connector.services.request_prediction(
        home_bet_id=home_bet_id,
        multipliers=multipliers,
        model_home_bet_id=model_home_bet_id,
    )
    predictions = response.get("predictions")
    data = [Prediction(**prediction) for prediction in predictions]
    return data


def get_bots(bot_type: str) -> list[Bot]:
    """
    get_bot
    :param bot_type:
    :return:
    """
    bot_connector = BotAPIConnector()
    response = bot_connector.services.get_bots(bot_type=bot_type)
    bots = response.get("bots")
    data = [Bot(**bot) for bot in bots]
    return data


def get_multiplier_positions(*, home_bet_id: int) -> MultiplierPositions:
    bot_connector = BotAPIConnector()
    response = bot_connector.services.get_multiplier_positions(home_bet_id=home_bet_id)
    all_time = response.get("all_time", {})
    today = response.get("today", {})
    all_time_ = {}
    today_ = {}
    for key, value in all_time.items():
        all_time_[int(key)] = Positions(**value)
    for key, value in today.items():
        today_[int(key)] = Positions(**value)
    positions = MultiplierPositions(
        all_time=all_time_,
        today=today_,
    )
    return positions


def get_customer_data() -> CustomerData:
    bot_connector = BotAPIConnector()
    data = bot_connector.services.get_me_data()
    return CustomerData(**data)


def update_customer_balance(
    *, customer_id: int, home_bet_id: int, balance: float
) -> None:
    """
    update_balance
    :param customer_id:
    :param home_bet_id:
    :param balance:
    :return:
    """
    bot_connector = BotAPIConnector()
    bot_connector.services.update_balance(
        customer_id=customer_id, home_bet_id=home_bet_id, balance=balance
    )


def create_bets(*, home_bet_id: int, bets: list[BetData]) -> list[BetData]:
    """
    create_bets
    :param home_bet_id:
    :param bets:
    :return:
    """
    bot_connector = BotAPIConnector()
    response = bot_connector.services.create_bet(home_bet_id=home_bet_id, bets=bets)
    bets = response.get("bets", [])
    data = [BetData(**bet) for bet in bets]
    return data


def get_bet(*, bet_id: int) -> BetData:
    """
    get_bet
    :param bet_id:
    :return:
    """
    bot_connector = BotAPIConnector()
    response = bot_connector.services.get_bet(bet_id=bet_id)
    data = BetData(**response)
    return data
