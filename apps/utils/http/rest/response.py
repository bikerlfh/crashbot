# Standard Library
import json


class Response:
    """Class to convert a rest api response

    Attributes:
        status: An integer with the status code of the response.
        headers: A dict with the headers of the response.
        body: A dict with the body of the response.
    """

    def __init__(self, res):
        self.status = res.status_code
        self.headers = res.headers
        self.body = self._get_body(res)

    def _get_body(self, res):
        try:
            return res.json()
        except json.JSONDecodeError:
            return res.text
