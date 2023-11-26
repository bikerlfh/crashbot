# Standard Library
from enum import Enum


class WSEvent(str, Enum):
    VERIFY = "verify"
    LOGIN = "login"
    START_BOT = "startBot"
    AUTO_PLAY = "autoPlay"
    CHANGE_BOT = "changeBot"
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


class BullishGameValues(dict[str, any], Enum):
    LOW = {"value": 0.26, "index": 0}
    MEDIUM = {"value": 0.5, "index": 1}
    HIGH = {"value": 0.7, "index": 2}

    def get_value(self) -> float:
        return self.value["value"]

    def get_index(self) -> int:
        return self.value["index"]

    @staticmethod
    def get_by_index(index: int) -> any:
        for value in BullishGameValues:
            if value.value["index"] == index:
                return value
        return None

    @staticmethod
    def get_by_value(value: float) -> any:
        for val in BullishGameValues:
            if val.value["value"] == value:
                return val
        return None
