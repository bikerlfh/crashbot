# Standard Library
from enum import Enum


class WSEvent(str, Enum):
    VERIFY = "verify"
    LOGIN = "login"
    START_BOT = "startBot"
    AUTO_PLAY = "autoPlay"
    CLOSE_GAME = "closeGame"
    SET_MAX_AMOUNT_TO_BET = "setMaxAmountToBet"
    # events from server
    LOG = "log"
    ADD_MULTIPLIERS = "add_multipliers"
    UPDATE_BALANCE = "update_balance"
    GAME_LOADED = "game_loaded"
    RECEIVE_MULTIPLIER_POSITIONS = "receive_multiplier_positions"
    ERROR = "error"
    EXCEPTION = "exception"


class BotType(Enum):
    AGGRESSIVE = "aggressive"
    TIGHT = "tight"
    LOOSE = "loose"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

    @classmethod
    def to_list(cls):
        return [key.value for key in cls]


class BetType(str, Enum):
    MANUAL = "manual"
    AUTOMATIC = "automatic"
