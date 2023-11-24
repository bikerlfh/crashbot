# Standard Library
from enum import Enum


class ValueTypeData(type, Enum):
    INTEGER = int
    FLOAT = float
    BOOLEAN = bool
    STRING = str
    PERCENTAGE = float
    LIST = list
