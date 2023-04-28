# Standard Library
from enum import Enum
from typing import Optional
from apps.utils.logs.logs_db_handler import LogsDBHandler

# Internal
from apps.globals import GlobalVars


class GUIEvent(str, Enum):
    LOG = "log"
    UPDATE_BALANCE = "update_balance"
    ADD_MULTIPLIERS = "add_multipliers"
    ERROR = "error"
    EXCEPTION = "exception"


class LogCode(str, Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    DEBUG = "debug"


def _send_log_to_gui(data: any, code: Optional[LogCode] = LogCode.INFO):
    """
    Send log message to GUI
    :param data: any
    :param code: LogCode
    :return: None
    """
    log_handler = LogsDBHandler(app="GAME")
    data = {"message": data} if isinstance(data, str) else data
    data.update(code=code.value)
    GlobalVars.emit_to_gui(GUIEvent.LOG, data)
    log_handler.insert_log(message=data.get("message"), level=data.get("code"))


class SendEventToGUI:
    class _LogEvent:
        @staticmethod
        def info(message: str):
            _send_log_to_gui(message, LogCode.INFO)

        @staticmethod
        def success(message: str):
            _send_log_to_gui(message, LogCode.SUCCESS)

        @staticmethod
        def warning(message: str):
            _send_log_to_gui(message, LogCode.WARNING)

        @staticmethod
        def error(message: str):
            _send_log_to_gui(message, LogCode.ERROR)

        @staticmethod
        def debug(message: str):
            _send_log_to_gui(message, LogCode.DEBUG)

    log = _LogEvent

    @staticmethod
    def balance(balance: float):
        GlobalVars.emit_to_gui(GUIEvent.UPDATE_BALANCE, dict(balance=balance))

    @staticmethod
    def send_multipliers(multipliers: list[float]):
        GlobalVars.emit_to_gui(GUIEvent.ADD_MULTIPLIERS, dict(multipliers=multipliers))

    @staticmethod
    def error(error: str):
        GlobalVars.emit_to_gui(GUIEvent.ERROR, dict(error=error))

    @staticmethod
    def exception(exception: any):
        exception = isinstance(exception, str) and exception or str(exception)
        GlobalVars.emit_to_gui(GUIEvent.EXCEPTION, dict(exception=exception))

