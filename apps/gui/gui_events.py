from typing import Optional
from enum import Enum


class LogCode(Enum):
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
    data = {"message": data} if isinstance(data, str) else data
    data.update(code=code.value)
    print(f"send log to gui {data}")
    add_log_func = globals().get("add_log")
    if not add_log_func:
        print(f"Error in _send_log_to_gui: add_log_func is None")
        return
    add_log_func(data=data, code=code)


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
