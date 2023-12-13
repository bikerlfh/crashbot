"""
globals variables
use globals().get('auto_play') to get value
use globals().setdefault('auto_play', False) to set value
"""
# Standard Library
import asyncio
import copy
import logging
from enum import Enum
from threading import Event

# Libraries
from socketio import AsyncServer

# Internal
from apps.config import Config
from apps.utils.security import encrypt

# from apps.utils.session_time import SessionTime


logger = logging.getLogger(__name__)


class GlobalVars:
    APP_NAME: str = "CrashBot"
    APP_VERSION: str = "1.5.0"
    APP_HASH: str = None
    SIO: AsyncServer = None
    GAME: any = None
    WS_SERVER_EVENT: Event
    config: Config
    # session_time: SessionTime

    class VARS(str, Enum):
        BASE_PATH = "BASE_PATH"
        HOME_BET_GAMES = "HOME_BET_GAMES"
        HOME_BET_GAME_ID = "HOME_BET_GAME_ID"
        CURRENCY = "CURRENCY"
        AUTO_PLAY = "AUTO_PLAY"
        MAX_AMOUNT_TO_BET = "MAX_AMOUNT_TO_BET"
        ALLOWED_HOME_BETS = "ALLOWED_HOME_BETS"
        USERNAME = "USERNAME"
        PASSWORD = "PASSWORD"
        EMIT_TO_GUI = "EMIT_TO_GUI"
        AUTO_CASH_OUT = "AUTO_CASH_OUT"
        ALLOWED_TO_SAVE_MULTIPLIERS = "ALLOWED_TO_SAVE_MULTIPLIERS"
        WS_CLIENT_BACKEND_STARTED = "WS_CLIENT_BACKEND_STARTED"
        BOTS = "BOTS"
        PLAN_WITH_AI = "PLAN_WITH_AI"

    @staticmethod
    def init(base_path: str) -> None:
        GlobalVars.APP_HASH = encrypt.md5(
            f"{GlobalVars.APP_NAME}{GlobalVars.APP_VERSION}"
        )
        # GlobalVars.session_time = SessionTime()
        globals().setdefault(GlobalVars.VARS.BASE_PATH, base_path)
        globals().setdefault(GlobalVars.VARS.HOME_BET_GAMES, [])
        globals().setdefault(GlobalVars.VARS.HOME_BET_GAME_ID, None)
        globals().setdefault(GlobalVars.VARS.CURRENCY, None)
        globals().setdefault(GlobalVars.VARS.AUTO_PLAY, False)
        globals().setdefault(GlobalVars.VARS.MAX_AMOUNT_TO_BET, 0)
        globals().setdefault(GlobalVars.VARS.ALLOWED_HOME_BETS, [])
        globals().setdefault(GlobalVars.VARS.USERNAME, None)
        globals().setdefault(GlobalVars.VARS.PASSWORD, None)
        globals().setdefault(GlobalVars.VARS.EMIT_TO_GUI, None)
        globals().setdefault(GlobalVars.VARS.AUTO_CASH_OUT, False)
        globals().setdefault(GlobalVars.VARS.WS_CLIENT_BACKEND_STARTED, False)
        globals().setdefault(
            GlobalVars.VARS.ALLOWED_TO_SAVE_MULTIPLIERS, False
        )
        globals().setdefault(GlobalVars.VARS.BOTS, [])
        globals().setdefault(GlobalVars.VARS.PLAN_WITH_AI, False)
        GlobalVars.init_config()

    @classmethod
    def init_config(cls) -> None:
        cls.config = Config(cls.get_base_path())

    @classmethod
    def is_connected(cls) -> bool:
        """
        add everything you need to start the app to work properly
        """
        ws_client_stated = cls.get_ws_client_backend_started()
        return ws_client_stated

    @classmethod
    def set_game(cls, game: any) -> None:
        cls.GAME = game

    @classmethod
    def get_game(cls) -> any:
        return cls.GAME

    @staticmethod
    def get_base_path() -> str:
        return globals().get(GlobalVars.VARS.BASE_PATH)

    @staticmethod
    def get_home_bet_games() -> list[object]:
        return globals().get(GlobalVars.VARS.HOME_BET_GAMES)

    @staticmethod
    def set_home_bet_games(home_bet_games: list[object]) -> None:
        globals()[GlobalVars.VARS.HOME_BET_GAMES] = home_bet_games

    @staticmethod
    def get_home_bet_game_id() -> int:
        return globals().get(GlobalVars.VARS.HOME_BET_GAME_ID)

    @staticmethod
    def set_home_bet_game_id(home_bet_game_id: int) -> None:
        globals()[GlobalVars.VARS.HOME_BET_GAME_ID] = home_bet_game_id

    @staticmethod
    def get_currency() -> str:
        return globals().get(GlobalVars.VARS.CURRENCY)

    @staticmethod
    def set_currency(currency: str) -> None:
        globals()[GlobalVars.VARS.CURRENCY] = currency

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
    def get_allowed_home_bets() -> list[object]:
        return globals().get(GlobalVars.VARS.ALLOWED_HOME_BETS)

    @staticmethod
    def set_allowed_home_bets(allowed_home_bet: list[object]) -> None:
        globals()[GlobalVars.VARS.ALLOWED_HOME_BETS] = allowed_home_bet

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

    @staticmethod
    def get_auto_cash_out() -> bool:
        return globals().get(GlobalVars.VARS.AUTO_CASH_OUT)

    @staticmethod
    def set_auto_cash_out(auto_cash_out: bool) -> None:
        globals()[GlobalVars.VARS.AUTO_CASH_OUT] = auto_cash_out

    @classmethod
    def set_allowed_to_save_multipliers(cls, allowed: bool) -> None:
        globals()[GlobalVars.VARS.ALLOWED_TO_SAVE_MULTIPLIERS] = allowed
        logger.info(
            "ALLOWED_TO_SAVE_MULTIPLIERS: ",
            cls.get_allowed_to_save_multipliers(),
        )

    @classmethod
    def get_allowed_to_save_multipliers(cls) -> bool:
        return globals().get(GlobalVars.VARS.ALLOWED_TO_SAVE_MULTIPLIERS)

    @classmethod
    def get_ws_client_backend_started(cls) -> bool:
        return globals().get(GlobalVars.VARS.WS_CLIENT_BACKEND_STARTED)

    @classmethod
    def set_ws_client_backend_started(cls, started: bool) -> None:
        globals()[GlobalVars.VARS.WS_CLIENT_BACKEND_STARTED] = started

    @classmethod
    def get_bots(cls) -> list[object]:
        return globals().get(GlobalVars.VARS.BOTS)

    @classmethod
    def clear_bots(cls) -> None:
        globals()[GlobalVars.VARS.BOTS] = []

    @classmethod
    def set_bots(cls, bots: list[object]) -> None:
        _bots = copy.copy(cls.get_bots())
        _bots.extend(bots)
        globals()[GlobalVars.VARS.BOTS] = _bots

    @classmethod
    def get_plan_with_ai(cls) -> bool:
        return globals().get(GlobalVars.VARS.PLAN_WITH_AI)

    @classmethod
    def set_plan_with_ai(cls, plan_with_ai: bool) -> None:
        globals()[GlobalVars.VARS.PLAN_WITH_AI] = plan_with_ai

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
