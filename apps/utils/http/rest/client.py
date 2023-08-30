# Standard Library
import logging
from typing import Any, Callable, Dict, List, Optional, Union

# Libraries
import requests

# Current Folder
from .response import Response

logger = logging.getLogger(__name__)


class RESTClient:
    """
    Rest client based in requests library, have basic method of http,
    and can save the credentials and header in every call.

    Attributes:
        TIMEOUT: An integer with the default timeout.
    """

    TIMEOUT = 60
    VERIFY = True
    auth = {}

    def __init__(
        self, *, api_url: str, headers: Optional[Dict[str, Any]] = None
    ):
        self.api_url = api_url
        if headers:
            self.headers = headers

    def delete(
        self,
        *,
        service: str,
        kwargs: Optional[Dict[str, Any]] = None,
        sensible_keys: Optional[List[str]] = (),
    ) -> Response:
        func_params = {"service": service}
        logger.info(f"delete_request :: start :: {func_params}")
        return self._send_request(
            method=requests.delete,
            service=service,
            kwargs=kwargs,
            sensible_keys=sensible_keys,
        )

    def get(
        self,
        *,
        service: str,
        kwargs: Optional[Dict[str, Any]] = None,
        sensible_keys: Optional[List[str]] = (),
    ) -> Response:
        func_params = {"service": service}
        logger.info(f"get_request :: start :: {func_params}")
        return self._send_request(
            method=requests.get,
            service=service,
            kwargs=kwargs,
            sensible_keys=sensible_keys,
        )

    def put(
        self,
        *,
        service: str,
        data: Optional[Union[List, Dict[str, Any]]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
        sensible_keys: Optional[List[str]] = (),
    ) -> Response:
        func_params = {"service": service}
        logger.info(f"put_request :: start :: {func_params}")
        return self._send_request(
            method=requests.put,
            service=service,
            data=data,
            kwargs=kwargs,
            sensible_keys=sensible_keys,
        )

    def post(
        self,
        *,
        service: str,
        data: Union[List, Dict[str, Any]],
        kwargs: Optional[Dict[str, Any]] = None,
        sensible_keys: Optional[List[str]] = (),
    ) -> Response:
        func_params = {"service": service}
        logger.info(f"post_request :: start :: {func_params}")
        return self._send_request(
            method=requests.post,
            service=service,
            data=data,
            kwargs=kwargs,
            sensible_keys=sensible_keys,
        )

    def patch(
        self,
        *,
        service: str,
        data: Union[List, Dict[str, Any]],
        kwargs: Optional[Dict[str, Any]] = None,
        sensible_keys: Optional[List[str]] = (),
    ) -> Response:
        func_params = {"service": service}
        logger.info(f"patch_request :: start :: {func_params}")
        return self._send_request(
            method=requests.patch,
            service=service,
            data=data,
            kwargs=kwargs,
            sensible_keys=sensible_keys,
        )

    def _send_request(
        self,
        *,
        method: Callable,
        service: str,
        data: Optional[Union[List, Dict[str, Any]]] = None,
        kwargs: Optional[Dict[str, Any]] = dict,
        sensible_keys: Optional[List[str]] = (),  # noqa
    ) -> Response:
        data = data or {}
        service_name = f"{self.api_url}/{service}"

        func_params = {"method": method, "service": service}
        logger.info(f"_send_request :: start :: {func_params}")
        data = data or {}
        url = service_name
        args = {
            "url": url,
            "headers": self.headers,
            "timeout": self.TIMEOUT,
            "verify": self.VERIFY,
            "auth": self.auth,
        }

        if data:
            args.update(json=data)

        if kwargs:
            args.update(**kwargs)
        response = method(**args)
        msg = f"response :: status {response.status_code}"
        logger.info(msg)
        response = Response(response)
        return response
