# Standard Library
import os
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class BotAPIException(Exception):
    """Base exception for all API exceptions"""

    pass


class BotAPIBadRequestException(BotAPIException):
    """Exception for 400 status code"""

    pass


class BotAPINotFoundException(BotAPIException):
    """Exception for 404 status code"""

    pass


class BotAPIConnectionException(BotAPIException):
    """Exception for 500 status code"""

    pass


class BotAPINoAuthorizationException(BotAPIException):
    """Exception for 401 status code"""

    pass


@dataclass
class ErrorAPI:
    message: str
    close_app: Optional[bool] = False

    def exc_error(self) -> None:
        if self.close_app:
            print(self.message)
            os._exit(0)  # noqa


class APICodeError(ErrorAPI, Enum):
    E00 = ErrorAPI(
        message="An unexpected error occurred, try again", close_app=True
    )
    AUTH01 = ErrorAPI(message="Authentication failed")
    AUTH02 = ErrorAPI(
        message="You are not allowed to use this application", close_app=True
    )

    @classmethod
    def get_by_code(cls, code: str):
        try:
            return next(error for error in cls if error.name == code)
        except (Exception,):
            return None
