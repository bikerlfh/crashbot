from enum import Enum
from os import getenv

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor


class Event(Enum):
    VERIFY = "verify"
    LOGIN = "login"
    START_BOT = "startBot"
    AUTO_PLAY = "autoPlay"
    CLOSE_GAME = "closeGame"
    SET_MAX_AMOUNT_TO_BET = "setMaxAmountToBet"
    # events from server
    LOG = "log"
    UPDATE_BALANCE = "update_balance"
    ERROR = "error"
    EXCEPTION = "exception"


BotTypes = ["aggressive", "tight", "loose"]
# the key is the position of the combobox
HomeBets = {
    0: {
        "id": 1,
        "name": "Demo",
        "min_bet": 1,
        "max_bet": 100,
    },
    1: {
        "id": 2,
        "name": "Bet Play",
        "min_bet": 100,
        "max_bet": 50000,
    },
    2: {
        "id": 3,
        "name": "One Win",
        "min_bet": 500,
        "max_bet": 500000,
    },
    3: {  # NOQA
        "id": 4,
        "name": "Rivalo",  # NOQA
        "min_bet": 500,
        "max_bet": 500000,
    },
}


LOG_CODES = {
    "info": {
        "foreground": None,
        "background": None,
    },
    "success": {
        "foreground": QColor(Qt.GlobalColor.green),
        "background": None,
    },
    "warning": {
        "foreground": QColor(Qt.GlobalColor.yellow),
        # "background": QColor(Qt.GlobalColor.yellow),
    },
    "error": {
        "foreground": QColor(Qt.GlobalColor.red),
        # "background": QColor(Qt.GlobalColor.red),
    },
    "debug": {
        "foreground": QColor(Qt.GlobalColor.white),
        "background": QColor(Qt.GlobalColor.darkBlue),
    },
}


URL_SOCKET = getenv("URL_SOCKET", "http://localhost:5000")
MAX_AMOUNT_HOME_BET_PERCENTAGE = float(
    getenv("MAX_AMOUNT_HOME_BET_PERCENTAGE", 0.5)
)
MAX_AMOUNT_BALANCE_PERCENTAGE = float(
    getenv("MAX_AMOUNT_BALANCE_PERCENTAGE", 0.1)
)

ALLOWED_LOG_CODES_TO_SHOW = getenv(
    "ALLOWED_LOG_CODES", ",".join([code for code in LOG_CODES.keys()])
).split(",")

DATA_FILE_PATH = getenv("DATA_FILE_PATH", "data")
CREDENTIALS_FILE_PATH = f"{DATA_FILE_PATH}/credentials.csv"
