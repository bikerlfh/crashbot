# Standard Library
from datetime import datetime
from typing import Optional

# Internal
from apps.utils.logs.logs_db_handler import LogsDBHandler


def save_game_log(
    *, message: str, level: str, timestamp: Optional[datetime] = None
) -> None:
    log_handler = LogsDBHandler()
    timestamp = timestamp or datetime.now()
    log_handler.insert_log(
        message=message, level=level, app="GAME", timestamp=timestamp
    )


def save_gui_log(
    *, message: str, level: str, timestamp: Optional[datetime] = None
) -> None:
    log_handler = LogsDBHandler()
    timestamp = timestamp or datetime.now()
    log_handler.insert_log(
        message=message, level=level, app="GUI", timestamp=timestamp
    )
