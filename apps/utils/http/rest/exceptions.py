# Standard Library
from typing import Any, Dict, List, Optional, Union

# Libraries
from app.utils.fastapi.formatters import ErrorFormatter
# Fast api
from starlette import status


class APIException(Exception):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'A server error occurred.'
    default_code = 'error'

    def __init__(
        self,
        detail: Optional[Union[str, List[Dict[str, Any]]]] = None,
        code: Optional[str] = None
    ):
        if detail is None:
            detail = self.default_detail

        if code is None:
            code = self.default_code

        formatter = ErrorFormatter(errors=detail, code=code)
        self.message = formatter()
        self.code = code


class NotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Not found.'
    default_code = 'not_found'


class ValidationError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid input.'
    default_code = 'invalid'


class AuthenticationFailed(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Incorrect authentication credentials.'
    default_code = 'authentication_failed'


class NotAuthenticated(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Authentication credentials were not provided.'
    default_code = 'not_authenticated'


class PermissionDenied(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'You do not have permission to perform this action.'
    default_code = 'permission_denied'


class IntegrityExceptionError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Model with the attribute already exists.'
    default_code = 'integrity_error'

    def __init__(self, detail=None, code=None):
        super().__init__(detail=detail, code=code)
        if code is None:
            code = self.default_code
        msg = getattr(detail, 'message', str(detail))
        try:
            model, attribute = msg.split(":")[1].strip().split(".")
            detail = f'{model} with the {attribute} already exists.'
        except ValueError:
            detail = msg
        formatter = ErrorFormatter(errors=detail, code=code)
        self.message = formatter()
        self.code = code
