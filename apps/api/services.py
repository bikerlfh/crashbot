# Standard Library
import logging
from typing import Optional

# Internal
from apps.api.bot_api import BotAPIConnector
from apps.api.exceptions import BotAPINoAuthorizationException
from apps.api.models import BetData, Bot, Prediction

logger = logging.getLogger(__name__)


def request_login(
    *, username: str, password: str
) -> tuple[str | None, str | None]:
    """
    request_login
    :param username:
    :param password:
    :return: access, refresh
    """
    bot_connector = BotAPIConnector()
    try:
        response = bot_connector.services.login(
            username=username, password=password
        )
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


def get_home_bets() -> dict[str, any]:
    """
    request_home_bet
    :return:
    """
    bot_connector = BotAPIConnector()
    response = bot_connector.services.get_home_bet()
    return response


def add_multipliers(
    *, home_bet_id: int, multipliers: list[float]
) -> dict[str, any]:
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


def update_balance(
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


def create_bets(
    *, home_bet_id: int, balance: float, bets: list[BetData]
) -> list[BetData]:
    """
    create_bets
    :param home_bet_id:
    :param balance:
    :param bets:
    :return:
    """
    bot_connector = BotAPIConnector()
    response = bot_connector.services.create_bet(
        home_bet_id=home_bet_id, balance=balance, bets=bets
    )
    bets = response.get("bets")
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
