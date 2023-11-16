# Standard Library
import inspect
from datetime import datetime
from typing import Optional

# Internal
from apps.globals import GlobalVars
from apps.utils.logs.logs_db_handler import LogsDBHandler


def save_game_log(
    *, message: str, level: str, timestamp: Optional[datetime] = None
) -> None:
    if GlobalVars.config.IGNORE_DB_LOGS:
        return
    log_handler = LogsDBHandler()
    timestamp = timestamp or datetime.now()
    caller_frame = inspect.stack()[1]
    path = f"{caller_frame.function}::{caller_frame.lineno}"
    log_handler.insert_log(
        message=message,
        level=level,
        app="GAME",
        timestamp=timestamp,
        path=path,
    )


def save_gui_log(
    *, message: str, level: str, timestamp: Optional[datetime] = None
) -> None:
    if GlobalVars.config.IGNORE_DB_LOGS:
        return
    log_handler = LogsDBHandler()
    timestamp = timestamp or datetime.now()
    caller_frame = inspect.stack()[1]
    path = (
        f"{caller_frame.filename}::"
        f"{caller_frame.function}::"
        f"{caller_frame.lineno}"
    )
    log_handler.insert_log(
        message=message, level=level, app="GUI", timestamp=timestamp, path=path
    )
