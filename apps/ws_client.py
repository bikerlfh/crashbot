# Standard Library
import json
import os
from dataclasses import dataclass

# Libraries
import websocket

# Internal
from apps.globals import GlobalVars
from apps.utils.datetime import sleep_now
from apps.utils.patterns.singleton import Singleton


@dataclass
class SocketMessage:
    func: str
    data: dict[str, any]


class WebSocketClient(metaclass=Singleton):
    """
    Client of websocket connected with the backend ws channel server
    """

    def __init__(self):
        self.url = GlobalVars.config.WS_URL
        self.ws = websocket.WebSocketApp(
            self.url,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            on_open=self.on_open,
        )

    def _force_close(self):
        self.ws.close()
        sleep_now(1)
        os.system("killall node")
        os._exit(0)  # noqa

    def error_event(self, ws_error_code: str, **_kwargs):
        print(f"WS BACKEND :: ws_error_code:{ws_error_code}")
        self._force_close()

    @staticmethod
    def notify_allowed_to_save(allowed: bool, **_kwargs):
        GlobalVars.set_allowed_to_save_multipliers(allowed=allowed)

    def validate_app_version(self, app_version: str, **_kwargs):
        if GlobalVars.APP_VERSION != app_version:
            print(f"Please update the app to version: {app_version}")
            self._force_close()

    def user_already_connected(self, **_kwargs):
        print("User already connected!!!!")
        self._force_close()

    def set_home_bet(self, *, home_bet_id: int, customer_id: int) -> None:
        message = SocketMessage(
            func="set_home_bet",
            data=dict(home_bet_id=home_bet_id, customer_id=customer_id),
        )
        if self.ws.sock.connected:
            self.ws.send(json.dumps(vars(message)))

    def on_message(self, ws, message):
        message = json.loads(message)
        func_name = message.get("func", None)
        kwargs = message.get("data", {})
        if not func_name:
            return
        # methods = dir(self)
        func = getattr(self, func_name, None)
        if not func:
            return
        func(**kwargs)

    def on_close(self, ws, error):
        GlobalVars.set_ws_client_backend_started(started=False)
        self.close()
        print("WS BACKEND :: Connection closed")

    def on_error(self, ws, error):
        print("Error WS Backend:", error)
        os._exit(0)  # noqa

    def on_open(self, ws, **_kwargs):
        GlobalVars.set_ws_client_backend_started(started=True)
        print("WS BACKEND :: Connection established")

    def run_forever(self, *_args, **_kwargs):
        websocket.enableTrace(False)
        self.ws.run_forever()

    def close(self):
        print("WS BACKEND :: Connection closed")
        self.ws.close()
