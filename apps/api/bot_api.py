# Standard Library
import inspect
import logging
from typing import Any, Dict, List, Optional

# Django
from http import HTTPStatus

# Libraries
from apps.utils.http.rest.response import Response
from apps.api.constants import API_URL
from apps.api.exceptions import (
    BotAPIBadRequestException,
    BotAPINotFoundException,
    BotAPIConnectionException,
    BotAPINoAuthorizationException,
)
from apps.api.models import BetData
from apps.utils.patterns.singleton import Singleton
from apps.utils.http.rest.client import RESTClient

logger = logging.getLogger(__name__)


class BotAPIConnector(metaclass=Singleton):
    def __init__(self):
        self.validate_config()
        headers = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
        }
        self.client = RESTClient(api_url=API_URL, headers=headers)
        self.services = BotAPIServices(client=self.client)

    @staticmethod
    def validate_config():
        assert isinstance(API_URL, str), "API_URL must be a str instance"


class BotAPIServices:
    LOGIN = "/api/token/"
    TOKEN_REFRESH = "/api/token/refresh/"
    TOKEN_VERIFY = "/api/token/verify/"
    HOME_BET = "home-bet/"
    HOME_BET_DETAIL = "home-bet/"
    ADD_MULTIPLIERS = "home-bet/multiplier/"
    GET_PREDICTION = "predictions/predict/"
    GET_BOTS = "predictions/bots/"
    UPDATE_BALANCE = "customers/balance/"
    BET = "bets/"

    def __init__(self, *, client: RESTClient):
        assert isinstance(
            client, RESTClient
        ), "client must be a BotAPIServices instance"
        self.client = client

    @staticmethod
    def validate_response(*, response: Response):
        func_name = inspect.stack()[1][3]
        status_code = response.status
        detail = response.body
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
            logger.exception(f"BotAPIServices :: send_transaction_validator :: {exc}")
            raise BotAPIConnectionException(exc)
        self.validate_response(response=response)
        return response.body

    def token_refresh(self, *, refresh: str) -> Dict[str, Any]:
        """
        token_refresh
        :param refresh:
        :return:
        """
        try:
            response = self.client.post(
                service=self.TOKEN_REFRESH,
                data=dict(
                    refresh=refresh,
                ),
            )
        except Exception as exc:
            logger.exception(f"BotAPIServices :: send_transaction_validator :: {exc}")
            raise BotAPIConnectionException(exc)
        self.validate_response(response=response)
        return response.body

    def token_verify(self, *, token: str) -> bool:
        """
        token_verify
        :param token:
        :return:
        """
        try:
            response = self.client.post(
                service=self.TOKEN_VERIFY,
                data=dict(
                    token=token,
                ),
            )
        except Exception as exc:
            logger.exception(f"BotAPIServices :: send_transaction_validator :: {exc}")
            raise BotAPIConnectionException(exc)
        self.validate_response(response=response)
        return response.status == HTTPStatus.OK

    def get_home_bet(self) -> Dict[str, Any]:
        try:
            response = self.client.get(
                service=self.HOME_BET,
            )
        except Exception as exc:
            logger.exception(f"BotAPIServices :: send_transaction_validator :: {exc}")
            raise BotAPIConnectionException(exc)
        self.validate_response(response=response)
        return response.body

    def get_home_bet_detail(self, *, home_bet_id: int) -> Dict[str, Any]:
        service = f"{self.HOME_BET_DETAIL}home_bet_id={home_bet_id}/"
        try:
            response = self.client.get(
                service=service,
            )
        except Exception as exc:
            logger.exception(f"BotAPIServices :: send_transaction_validator :: {exc}")
            raise BotAPIConnectionException(exc)
        self.validate_response(response=response)
        return response.body

    def add_multipliers(
        self, *, home_bet_id: int, multipliers: List[int]
    ) -> Dict[str, Any]:
        try:
            response = self.client.post(
                service=self.ADD_MULTIPLIERS,
                data=dict(
                    home_bet_id=home_bet_id,
                    multipliers=multipliers,
                ),
            )
        except Exception as exc:
            logger.exception(f"BotAPIServices :: send_transaction_validator :: {exc}")
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
            logger.exception(f"BotAPIServices :: send_transaction_validator :: {exc}")
            raise BotAPIConnectionException(exc)
        self.validate_response(response=response)
        return response.body

    def get_bots(self) -> Dict[str, Any]:
        try:
            response = self.client.get(
                service=self.GET_BOTS,
            )
        except Exception as exc:
            logger.exception(f"BotAPIServices :: send_transaction_validator :: {exc}")
            raise BotAPIConnectionException(exc)
        self.validate_response(response=response)
        return response.body

    def update_balance(
        self,
        *,
        customer_id: int,
        home_bet_id: int,
        balance: int,
    ) -> Dict[str, Any]:
        try:
            response = self.client.post(
                service=self.UPDATE_BALANCE,
                data=dict(
                    customer_id=customer_id,
                    home_bet_id=home_bet_id,
                    balance=balance,
                ),
            )
        except Exception as exc:
            logger.exception(f"BotAPIServices :: send_transaction_validator :: {exc}")
            raise BotAPIConnectionException(exc)
        self.validate_response(response=response)
        return response.body

    def create_bet(
        self,
        *,
        home_bet_id: int,
        balance: float,
        bets: list[BetData],
    ) -> Dict[str, Any]:
        data = dict(
            home_bet_id=home_bet_id, balance=balance, bets=[vars(bet) for bet in bets]
        )
        try:
            response = self.client.post(service=self.BET, data=data)
        except Exception as exc:
            logger.exception(f"BotAPIServices :: send_transaction_validator :: {exc}")
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
            logger.exception(f"BotAPIServices :: send_transaction_validator :: {exc}")
            raise BotAPIConnectionException(exc)
        self.validate_response(response=response)
        return response.body
