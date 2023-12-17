# Standard Library
from enum import Enum
from typing import Optional

# Internal
from apps.globals import GlobalVars
from apps.utils.logs import services as log_services


class GUIEvent(str, Enum):
    LOG = "log"
    UPDATE_BALANCE = "update_balance"
    ADD_MULTIPLIERS = "add_multipliers"
    RECEIVE_MULTIPLIER_POSITIONS = "receive_multiplier_positions"
    GAME_LOADED = "game_loaded"
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
    data = {"message": data} if isinstance(data, str) else data
    data.update(code=code.value)
    GlobalVars.emit_to_gui(GUIEvent.LOG, data)
    log_services.save_game_log(
        message=data.get("message"), level=data.get("code")
    )


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
            if not GlobalVars.config.DEBUG:
                return
            _send_log_to_gui(message, LogCode.DEBUG)

    log = _LogEvent

    @staticmethod
    def send_balance(*, balance: float, initial_balance: float):
        GlobalVars.emit_to_gui(
            GUIEvent.UPDATE_BALANCE,
            dict(balance=balance, initial_balance=initial_balance),
        )

    @staticmethod
    def send_multipliers(multipliers: list[float]):
        GlobalVars.emit_to_gui(
            GUIEvent.ADD_MULTIPLIERS, dict(multipliers=multipliers)
        )

    @staticmethod
    def send_multiplier_positions(
        positions: list[tuple[int, int]], len_multipliers: int
    ):
        """
        Send multiplier positions to GUI
        @param positions: tuple of list of multipliers
        @param len_multipliers: length of multipliers
        """
        GlobalVars.emit_to_gui(
            GUIEvent.RECEIVE_MULTIPLIER_POSITIONS,
            data=dict(positions=positions, len_multipliers=len_multipliers),
        )

    @staticmethod
    def game_loaded(is_game_loaded: bool):
        GlobalVars.emit_to_gui(
            GUIEvent.GAME_LOADED, dict(loaded=is_game_loaded)
        )

    @staticmethod
    def error(error: str):
        GlobalVars.emit_to_gui(GUIEvent.ERROR, dict(error=error))

    @staticmethod
    def exception(exception: any):
        exception = isinstance(exception, str) and exception or str(exception)
        GlobalVars.emit_to_gui(GUIEvent.EXCEPTION, dict(exception=exception))
