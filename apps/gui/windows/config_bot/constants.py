# Standard Library
from enum import Enum


class ConfigKeyButton(Enum):
    CONDITIONS = dict(
        key="conditions",
        action_button="add",
    )
    ACTIONS = dict(
        key="actions",
        action_button="add",
    )
    CONDITION = dict(
        key="condition",
        action_button="remove",
    )
    ACTION = dict(
        key="action",
        action_button="remove",
    )

    @classmethod
    def to_list(cls):
        return [item.value.get("key") for item in cls]

    @classmethod
    def get_action_by_key(cls, key: str) -> str:
        for item in cls:
            if item.value.get("key") == key:
                return item.value.get("action_button")
        return ""


class ConfigKeyComboBox(str, Enum):
    BOT_TYPE = "bot_type"
    CONDITION_ON = "condition_on"
    CONDITION_ACTION = "condition_action"

    @classmethod
    def to_list(cls):
        return [item for item in cls]


class ConfigKeyCheckBox(str, Enum):
    ONLY_BULLISH_GAMES = "only_bullish_games"
    MAKE_SECOND_BET = "make_second_bet"

    @classmethod
    def to_list(cls):
        return [item for item in cls]
