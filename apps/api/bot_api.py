# Standard Library
import inspect
import logging
from http import HTTPStatus
from typing import Any, Dict, List, Optional

# Internal
from apps.api.exceptions import (
    APICodeError,
    BotAPIBadRequestException,
    BotAPIConnectionException,
    BotAPINoAuthorizationException,
    BotAPINotFoundException,
)
from apps.api.models import BetData
from apps.globals import GlobalVars
from apps.utils.http.rest.client import RESTClient
from apps.utils.http.rest.response import Response
from apps.utils.local_storage import LocalStorage
from apps.utils.patterns.singleton import Singleton

logger = logging.getLogger(__name__)

local_storage = LocalStorage()


class BotAPIConnector(metaclass=Singleton):
    def __init__(self):
        self.validate_config()
        self.API_URL = GlobalVars.config.API_URL
        headers = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            "Authorization": f"Token {local_storage.get_token()}",
        }
        self.client = RESTClient(api_url=self.API_URL, headers=headers)
        self.services = BotAPIServices(client=self.client)

    @staticmethod
    def validate_config():
        assert isinstance(
            GlobalVars.config.API_URL, str
        ), "API_URL must be a str instance"

    def update_token(self):
        token = local_storage.get_token()
        self.client.headers["Authorization"] = f"Token {token}"

    def remove_token(self):
        self.client.headers.pop("Authorization", None)


class BotAPIServices:
    LOGIN = "api/auth/login/"
    VERIFY_TOKEN = "api/auth/verify/"
    ADD_MULTIPLIERS = "api/home-bet/multiplier/"
    GET_PREDICTION = "api/predictions/predict/"
    GET_BOTS = "api/predictions/bots/"
    GET_POSITIONS = "api/predictions/positions/"
    CUSTOMER_DATA = "api/customers/me/"
    CUSTOMER_LIVE = "api/customers/live/"
    BET = "api/bets/"

    def __init__(self, *, client: RESTClient):
        assert isinstance(
            client, RESTClient
        ), "client must be a BotAPIServices instance"
        self.client = client

    @staticmethod
    def validate_api_code_error(error: dict):
        if not isinstance(error, dict):
            return
        errors = error.get("errors")
        if not errors:
            return
        for error in errors:
            code = error.get("code")
            _error = APICodeError.get_by_code(code)
            if _error:
                _error.value.exc_error()
        return errors

    @staticmethod
    def validate_response(*, response: Response, ignore_errors: bool = False):
        func_name = inspect.stack()[1][3]
        status_code = response.status
        detail = response.body
        if not ignore_errors:
            BotAPIServices.validate_api_code_error(detail)
        error_code = detail.get("code") if isinstance(detail, dict) else None
        if status_code >= HTTPStatus.INTERNAL_SERVER_ERROR:
            logger.error(
                f"BotAPIServices :: {func_name} :: "
                f"response status {status_code} :: {detail}"
            )
            raise BotAPIConnectionException(detail)
        if status_code == HTTPStatus.UNAUTHORIZED:
            logger.error(
                f"BotAPIServices :: {func_name} :: "
                f"response status {status_code} :: {detail}"
            )
            raise BotAPINoAuthorizationException(detail)
        if status_code == HTTPStatus.NOT_FOUND and error_code:
            logger.error(
                f"BotAPIServices :: {func_name} :: "
                f"response status {status_code} :: {detail}"
            )
            raise BotAPINotFoundException(detail, response.status)
        if status_code == HTTPStatus.BAD_REQUEST:
            raise BotAPIBadRequestException(detail, status_code)
        if status_code >= HTTPStatus.MULTIPLE_CHOICES:
            logger.error(
                f"BotAPIServices :: {func_name} :: "
                f"response status {status_code} :: {detail}"
            )
            raise BotAPINotFoundException(detail, response.status)

    def login(self, *, username: str, password: str) -> Dict[str, Any]:
        """
        login
        :param username:
        :param password:
        :return:
        """
        try:
            response = self.client.post(
                service=self.LOGIN,
                data=dict(
                    username=username,
                    password=password,
                ),
            )
        except Exception as exc:
            logger.exception(f"BotAPIServices :: login :: {exc}")
            raise BotAPIConnectionException(exc)
        self.validate_response(response=response)
        return response.body

    def request_verify_token(self) -> bool:
        """
        verify_token
        :return:
        """
        try:
            response = self.client.get(
                service=self.VERIFY_TOKEN,
            )
        except Exception as exc:
            logger.exception(f"BotAPIServices :: token_verify :: {exc}")
            raise BotAPIConnectionException(exc)
        self.validate_response(response=response, ignore_errors=True)
        return response.status == HTTPStatus.OK

    def add_multipliers(
        self, *, home_bet_game_id: int, multipliers_data: List[dict[str, any]]
    ) -> Dict[str, Any]:
        try:
            response = self.client.post(
                service=self.ADD_MULTIPLIERS,
                data=dict(
                    home_bet_game_id=home_bet_game_id,
                    multipliers_data=multipliers_data,
                ),
            )
        except Exception as exc:
            logger.exception(f"BotAPIServices :: add_multipliers :: {exc}")
            raise BotAPIConnectionException(exc)
        self.validate_response(response=response)
        return response.body

    def request_prediction(
        self,
        *,
        home_bet_id: int,
        multipliers: List[int],
        model_home_bet_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        data = dict(
            home_bet_id=home_bet_id,
            multipliers=multipliers,
        )
        if model_home_bet_id:
            data["model_home_bet_id"] = model_home_bet_id
        try:
            response = self.client.post(service=self.GET_PREDICTION, data=data)
        except Exception as exc:
            logger.exception(f"BotAPIServices :: request_prediction :: {exc}")
            raise BotAPIConnectionException(exc)
        self.validate_response(response=response)
        return response.body

    def get_bots(self, *, bot_type: Optional[str] = None) -> Dict[str, Any]:
        try:
            service = self.GET_BOTS
            if bot_type is not None:
                service = f"{service}?bot_type={bot_type}"
            response = self.client.get(
                service=service,
            )
        except Exception as exc:
            logger.exception(f"BotAPIServices :: get_bots :: {exc}")
            raise BotAPIConnectionException(exc)
        self.validate_response(response=response)
        return response.body

    def get_multiplier_positions(
        self, *, home_bet_game_id: int
    ) -> Dict[str, Any]:
        service = f"{self.GET_POSITIONS}?home_bet_game_id={home_bet_game_id}"
        try:
            response = self.client.get(
                service=service,
            )
        except Exception as exc:
            logger.exception(f"BotAPIServices :: get_positions :: {exc}")
            raise BotAPIConnectionException(exc)
        self.validate_response(response=response)
        return response.body

    def get_me_data(self, *, app_hash_str: str) -> Dict[str, Any]:
        try:
            response = self.client.get(
                service=f"{self.CUSTOMER_DATA}?app_hash_str={app_hash_str}"
            )
        except Exception as exc:
            logger.exception(f"BotAPIServices :: get_me_data :: {exc}")
            raise BotAPIConnectionException(exc)
        self.validate_response(response=response, ignore_errors=False)
        return response.body

    def customer_live(
        self,
        *,
        home_bet_id: int,
        balance: float,
        currency: Optional[str] = None,
        closing_session: Optional[bool] = False,
    ) -> Dict[str, Any]:
        try:
            response = self.client.post(
                service=self.CUSTOMER_LIVE,
                data=dict(
                    home_bet_id=home_bet_id,
                    amount=balance,
                    currency=currency,
                    closing_session=closing_session,
                ),
            )
        except Exception as exc:
            logger.exception(f"BotAPIServices :: get_me_data :: {exc}")
            raise BotAPIConnectionException(exc)
        self.validate_response(response=response)
        return response.body

    def create_bet(
        self,
        *,
        home_bet_id: int,
        bets: list[BetData],
    ) -> Dict[str, Any]:
        data = dict(
            home_bet_id=home_bet_id,
            bets=[vars(bet) for bet in bets],
        )
        try:
            response = self.client.post(service=self.BET, data=data)
        except Exception as exc:
            logger.exception(f"BotAPIServices :: create_bet :: {exc}")
            raise BotAPIConnectionException(exc)
        self.validate_response(response=response)
        return response.body

    def get_bet(
        self,
        *,
        bet_id: int,
    ) -> Dict[str, Any]:
        service = f"{self.BET}bet_id={bet_id}/"
        try:
            response = self.client.get(
                service=service,
            )
        except Exception as exc:
            logger.exception(f"BotAPIServices :: get_bet :: {exc}")
            raise BotAPIConnectionException(exc)
        self.validate_response(response=response)
        return response.body
