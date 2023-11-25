# Standard Library
from enum import Enum


class PercentageNumber:
    def __init__(self, value: float):
        self.value = value

    def is_valid(self) -> bool:
        return 0 <= self.value <= 1


class ValueTypeData(Enum):
    INTEGER = int
    FLOAT = float
    BOOLEAN = bool
    STRING = str
    PERCENTAGE = PercentageNumber
    LIST = list
