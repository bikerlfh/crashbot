# Standard Library
from enum import Enum

# Internal
from apps.utils.types import PercentageNumber


class ValueTypeData(Enum):
    INTEGER = int
    FLOAT = float
    BOOLEAN = bool
    STRING = str
    PERCENTAGE = PercentageNumber
    LIST = list
