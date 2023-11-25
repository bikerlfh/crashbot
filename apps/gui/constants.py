# Standard Library
from enum import Enum

# Libraries
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

ICON_NAME = "favicon.ico"


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


class LANGUAGES(str, Enum):
    ENGLISH = "en"
    SPANISH = "es"


class InputMask(str, Enum):
    FLOAT = r"^\d*\.?\d*$"
    INTEGER = r"^\d*$"
    MULTIPLIER_POSITION = r"^[\d*\,\d*]+$"


DEFAULT_FONT_SIZE = 10
MAC_FONT_SIZE = 13
