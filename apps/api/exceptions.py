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
