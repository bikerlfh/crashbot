# Standard Library
from enum import Enum
from os import getenv

# Libraries
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

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

DATA_FILE_PATH = getenv("DATA_FILE_PATH", "data")
CREDENTIALS_FILE_PATH = f"{DATA_FILE_PATH}/credentials.csv"
