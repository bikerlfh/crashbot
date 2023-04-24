# Standard Library
import copy
import logging
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Union

# Libraries
import requests

# from utils.core.sensible import obfuscate_sensible_data

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

    def __init__(self, *, api_url: str, headers: Optional[Dict[str, Any]] = None):
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
        sensible_keys: Optional[List[str]] = (),
    ) -> Response:
        data = data or {}
        service_name = f"{self.api_url}/{service}"
        try:
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
        except Exception as exc:
            error = str(exc)
            # self._log(
            #     http_method=method.__name__,
            #     request_data=data,
            #     service_name=service_name,
            #     error=error,
            #     sensible_keys=sensible_keys
            # )
            raise

        # self._log(
        #     http_method=method.__name__,
        #     request_data=data,
        #     response_data=response.body,
        #     service_name=service_name,
        #     status_code=response.status,
        #     sensible_keys=sensible_keys
        # )
        return response

    """def _log(
        self,
        *,
        http_method: str,
        request_data: Dict[str, Any],
        service_name: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        sensible_keys: Optional[List[str]] = ()
    ) -> None:
        timestamp = datetime.utcnow()
        request_data_cp = copy.deepcopy(request_data)
        response_data_cp = copy.deepcopy(response_data)
        obfuscate_sensible_data(
            sensible_keys=sensible_keys, data=request_data_cp
        )
        obfuscate_sensible_data(
            sensible_keys=sensible_keys, data=response_data_cp
        )
        integration_log = EgressAPILog(
            http_method=http_method,
            service_name=service_name,
            timestamp=timestamp,
            request_data=request_data_cp,
            response_data=response_data_cp,
            status_code=status_code,
            error=error
        )
        integration_log.save()"""
