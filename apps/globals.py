from enum import Enum


auto_play = False
max_amount_to_bet = 0


class LocalStorageKeys(Enum):
    TOKEN = "token"
    REFRESH = "refresh"
