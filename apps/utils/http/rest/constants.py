# Standard Library
from enum import Enum


class HTTPMethods(str, Enum):
    GET = "get"
    HEAD = "head"
    POST = "post"
    PUT = "put"
    DELETE = "delete"
    OPTIONS = "options"
    PATCH = "patch"
