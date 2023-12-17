# Standard Library
from enum import Enum


class BookmakerIDS(int, Enum):
    DEFAULT = -1
    DEMO = 1
    BET_PLAY = 2
    ONE_WIN = 3
    RIVALO = 4  # noqa
    ONE_X_BET = 5
    DEMO_TO_THE_MOON = 6
    ECUABET = 7  # noqa

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

    @classmethod
    def values(cls):
        return [key.value for key in cls]
