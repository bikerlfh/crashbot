# Standard Library
from enum import Enum


class ConditionON(str, Enum):
    # values are float
    EVERY_WIN = "every_win"
    EVERY_LOSS = "every_loss"
    STREAK_WINS = "streak_wins"
    STREAK_LOSSES = "streak_losses"
    STREAK_N_MULTIPLIER_LESS_THAN = "streak_n_multiplier_less_than"
    STREAK_N_MULTIPLIER_GREATER_THAN = "streak_multiplier_greater_than"
    # values are percentage
    PROFIT_GREATER_THAN = "profit_greater_than"
    PROFIT_LESS_THAN = "profit_less_than"


class ConditionAction(str, Enum):
    # values are percentage
    INCREASE_BET_AMOUNT = "increase_bet_amount"
    DECREASE_BET_AMOUNT = "decrease_bet_amount"
    RESET_BET_AMOUNT = "reset_bet_amount"
    # values are float
    UPDATE_MULTIPLIER = "update_multiplier"
    RESET_MULTIPLIER = "reset_multiplier"
    # values are boolean
    IGNORE_MODEL = "ignore_model"
    MAKE_BET = "make_bet"
