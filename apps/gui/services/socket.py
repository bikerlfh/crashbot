from typing import Callable, Optional

import socketio
from PyQt6 import QtCore

from apps.gui.services.constants import Event
from apps.game.ws.constants import WS_SERVER_PORT, WS_SERVER_HOST


class SocketIOClient(QtCore.QThread):
    def __init__(
        self,
        *,
        on_verify: Optional[Callable] = None,
        on_login: Optional[Callable] = None,
        on_start_bot: Optional[Callable] = None,
        on_auto_play: Optional[Callable] = None,
        on_close_game: Optional[Callable] = None,
        on_set_max_amount_to_bet: Optional[Callable] = None,
        on_log: Optional[Callable] = None,
        on_update_balance: Optional[Callable] = None,
        on_error: Optional[Callable] = None,
        on_exception: Optional[Callable] = None,
    ):
        super().__init__()
        self.WS_SERVER_URL = f"http://{WS_SERVER_HOST}:{WS_SERVER_PORT}"
        self.on_verify = on_verify
        self.on_login = on_login
        self.on_start_bot = on_start_bot
        self.on_auto_play = on_auto_play
        self.on_close_game = on_close_game
        self.on_set_max_amount_to_bet = on_set_max_amount_to_bet
        self.on_log = on_log
        self.on_update_balance = on_update_balance
        self.on_error = on_error
        self.on_exception = on_exception
        self.__sio = socketio.Client()
        self.__assign_events()

    def __assign_events(self) -> None:
        # Define Events
        self.__sio.on("connect", self._on_connect)
        self.__sio.on("disconnect", self._on_disconnect)
        self.__sio.on(Event.VERIFY.value, self.on_verify or self._on_default)
        self.__sio.on(Event.LOGIN.value, self.on_login or self._on_default)
        self.__sio.on(Event.START_BOT.value, self.on_start_bot or self._on_default)
        self.__sio.on(Event.AUTO_PLAY.value, self.on_auto_play or self._on_default)
        self.__sio.on(Event.CLOSE_GAME.value, self.on_close_game or self._on_default)
        self.__sio.on(Event.LOG.value, self.on_log or self._on_default)
        self.__sio.on(
            Event.SET_MAX_AMOUNT_TO_BET.value,
            self.on_set_max_amount_to_bet or self._on_default,
        )
        self.__sio.on(
            Event.UPDATE_BALANCE.value,
            self.on_update_balance or self._on_default,
        )
        self.__sio.on(Event.ERROR.value, self.on_error or self._on_default)
        self.__sio.on(Event.EXCEPTION.value, self.on_exception or self._on_default)

    def __execute_event(self, event: Event, data: any) -> None:
        self.__sio.emit(event.value, data)

    @staticmethod
    def _on_connect() -> None:
        print(f"GUI :: connected to server: {WS_SERVER_HOST}:{WS_SERVER_PORT}")

    @staticmethod
    def _on_disconnect() -> None:
        print("GUI :: disconnect from server")

    @staticmethod
    def _on_default(data: any) -> None:
        print(f"WS callback not specify!!!: {data}")

    def run(self) -> None:
        self.__sio.connect(self.WS_SERVER_URL)

    def stop(self) -> None:
        self.__sio.disconnect()

    def verify(self) -> None:
        # this verify if the login is valid
        self.__execute_event(Event.VERIFY, {})

    def login(self, *, username: str, password) -> None:
        data = dict(username=username, password=password)
        self.__execute_event(Event.LOGIN, data)

    def start_bot(
        self,
        *,
        bot_type: str,
        home_bet_id: int,
        max_amount_to_bet: float,
        auto_play: bool,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        data = dict(
            bot_type=bot_type,
            home_bet_id=home_bet_id,
            max_amount_to_bet=max_amount_to_bet,
            auto_play=auto_play,
            username=username,
            password=password,
        )
        self.__execute_event(Event.START_BOT, data)

    def auto_play(self, *, auto_play: bool) -> None:
        data = dict(auto_play=auto_play)
        self.__execute_event(Event.AUTO_PLAY, data)

    def set_max_amount_to_bet(self, *, max_amount_to_bet: float) -> None:
        data = dict(max_amount_to_bet=max_amount_to_bet)
        self.__execute_event(Event.SET_MAX_AMOUNT_TO_BET, data)

    def close_game(self) -> None:
        self.__execute_event(Event.CLOSE_GAME, {})
