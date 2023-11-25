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
    CustomerLiveData,
    Multiplier,
    MultiplierPositions,
    PlanData,
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


def request_login(*, username: str, password: str) -> str | None:
    """
    request_login
    :param username:
    :param password:
    :return: access, refresh
    """
    bot_connector = BotAPIConnector()
    try:
        bot_connector.remove_token()
        response = bot_connector.services.login(
            username=username, password=password
        )
        token = response.get("token")
        return token
    except BotAPINoAuthorizationException:
        return None
    except Exception as exc:
        logger.exception(f"BotAPIServices :: request_login :: {exc}")
        return None


def request_token_verify() -> bool:
    """
    request_token_verify
    :return:
    """
    bot_connector = BotAPIConnector()
    try:
        bot_connector.update_token()
        is_valid = bot_connector.services.request_verify_token()
        return is_valid
    except BotAPINoAuthorizationException:
        return False
    except Exception as exc:
        logger.exception(f"BotAPIServices :: request_token_verify :: {exc}")
        return False


def add_multipliers(
    *, home_bet_game_id: int, multipliers_data: list[Multiplier]
) -> dict[str, any]:
    """
    add_multipliers
    :param home_bet_game_id:
    :param multipliers_data:
    :return:
    """
    bot_connector = BotAPIConnector()
    response = bot_connector.services.add_multipliers(
        home_bet_game_id=home_bet_game_id,
        multipliers_data=[
            multiplier.__dict__() for multiplier in multipliers_data
        ],
    )
    return response


def request_prediction(
    *,
    home_bet_game_id: int,
    multipliers: list[float],
    model_home_bet_id: Optional[int] = None,
) -> list[Prediction]:
    """
    request_prediction
    :param home_bet_game_id:
    :param multipliers:
    :param model_home_bet_id:
    :return:
    """
    bot_connector = BotAPIConnector()
    response = bot_connector.services.predict(
        home_bet_game_id=home_bet_game_id,
        multipliers=multipliers,
        model_home_bet_id=model_home_bet_id,
    )
    predictions = response.get("predictions")
    data = [Prediction(**prediction) for prediction in predictions]
    return data


def get_bots(*, bot_type: Optional[str] = None) -> list[Bot]:
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


def get_multiplier_positions(*, home_bet_game_id: int) -> MultiplierPositions:
    bot_connector = BotAPIConnector()
    response = bot_connector.services.get_multiplier_positions(
        home_bet_game_id=home_bet_game_id
    )
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


def get_customer_data(*, app_hash_str: str) -> CustomerData:
    bot_connector = BotAPIConnector()
    data = bot_connector.services.get_me_data(app_hash_str=app_hash_str)
    customer_data = CustomerData(
        customer_id=data.get("customer_id"),
        plan=PlanData(**data.get("plan")),
    )
    return customer_data


def request_customer_live(
    *,
    home_bet_id: int,
    balance: float,
    currency: Optional[str] = None,
    closing_session: Optional[bool] = False,
) -> CustomerLiveData:
    bot_connector = BotAPIConnector()
    data = bot_connector.services.customer_live(
        home_bet_id=home_bet_id,
        balance=round(balance, 2),
        currency=currency,
        closing_session=closing_session,
    )
    customer_live_data = CustomerLiveData(**data)
    return customer_live_data


def create_bets(*, home_bet_id: int, bets: list[BetData]) -> list[BetData]:
    """
    create_bets
    :param home_bet_id:
    :param bets:
    :return:
    """
    bot_connector = BotAPIConnector()
    response = bot_connector.services.create_bet(
        home_bet_id=home_bet_id, bets=bets
    )
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
