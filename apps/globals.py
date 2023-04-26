"""
globals variables
use globals().get('auto_play') to get value
use globals().setdefault('auto_play', False) to set value
"""
# Standard Library
import asyncio
from enum import Enum
from typing import Callable
from threading import Event
# Libraries
from socketio import AsyncServer


class GlobalVars:
    SIO: AsyncServer = None
    GAME: any = None
    WS_SERVER_EVENT: Event

    class VARS(str, Enum):
        AUTO_PLAY = "AUTO_PLAY"
        MAX_AMOUNT_TO_BET = "MAX_AMOUNT_TO_BET"
        ADD_LOG = "ADD_LOG"
        USERNAME = "USERNAME"
        PASSWORD = "PASSWORD"
        EMIT_TO_GUI = "EMIT_TO_GUI"

    @staticmethod
    def init() -> None:
        globals().setdefault(GlobalVars.VARS.AUTO_PLAY, False)
        globals().setdefault(GlobalVars.VARS.MAX_AMOUNT_TO_BET, 0)
        globals().setdefault(GlobalVars.VARS.ADD_LOG, None)
        globals().setdefault(GlobalVars.VARS.USERNAME, None)
        globals().setdefault(GlobalVars.VARS.PASSWORD, None)
        globals().setdefault(GlobalVars.VARS.EMIT_TO_GUI, None)

    @classmethod
    def set_game(cls, game: any) -> None:
        cls.GAME = game

    @classmethod
    def get_game(cls) -> any:
        return cls.GAME

    @staticmethod
    def get_auto_play() -> bool:
        return globals().get(GlobalVars.VARS.AUTO_PLAY)

    @staticmethod
    def set_auto_play(auto_play: bool) -> None:
        globals()[GlobalVars.VARS.AUTO_PLAY] = auto_play

    @staticmethod
    def get_max_amount_to_bet() -> float:
        return globals().get(GlobalVars.VARS.MAX_AMOUNT_TO_BET)

    @staticmethod
    def set_max_amount_to_bet(max_amount_to_bet: float) -> None:
        globals()[GlobalVars.VARS.MAX_AMOUNT_TO_BET] = max_amount_to_bet

    @staticmethod
    def get_add_log_callback() -> Callable:
        return globals().get(GlobalVars.VARS.ADD_LOG)

    @staticmethod
    def set_add_log_call_back(add_log: Callable) -> None:
        globals()[GlobalVars.VARS.ADD_LOG] = add_log

    @staticmethod
    def get_username() -> str:
        return globals().get(GlobalVars.VARS.USERNAME)

    @staticmethod
    def set_username(username: str) -> None:
        globals()[GlobalVars.VARS.USERNAME] = username

    @staticmethod
    def get_password() -> str:
        return globals().get(GlobalVars.VARS.PASSWORD)

    @staticmethod
    def set_password(password: str) -> None:
        globals()[GlobalVars.VARS.PASSWORD] = password

    @classmethod
    def set_io(cls, sio: AsyncServer) -> None:
        cls.SIO = sio

    @classmethod
    def get_io(cls) -> AsyncServer:
        return cls.SIO

    @classmethod
    def emit_to_gui(cls, event: str, data: any) -> None:
        if not cls.SIO:
            print("SIO is None")
            return
        asyncio.run_coroutine_threadsafe(
            cls.SIO.emit(event, data=data), asyncio.get_event_loop()
        )
