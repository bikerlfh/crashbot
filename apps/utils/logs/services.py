from datetime import datetime
from apps.utils.logs.logs_db_handler import LogsDBHandler


def save_log(
    *,
    message: str,
    level: str,
    timestamp: datetime
):
    LogsDBHandler().insert_log(message, level, timestamp)