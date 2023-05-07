# Standard Library
import json
from dataclasses import dataclass

# Libraries
import websocket

# Internal
from apps.globals import GlobalVars
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
        self.url = GlobalVars.config.API_URL.replace("http", "ws")
        self.url = f"{self.url}/bot/"
        self.ws = websocket.WebSocketApp(
            self.url,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            on_open=self.on_open,
        )

    @staticmethod
    def notify_allowed_to_save(allowed: bool, **_kwargs):
        GlobalVars.set_allowed_to_save_multipliers(allowed=allowed)

    def set_home_bet(self, home_bet_id: int) -> None:
        message = SocketMessage(
            func="set_home_bet", data=dict(home_bet_id=home_bet_id)
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

    def on_close(self, **_kwargs):
        GlobalVars.set_ws_client_backend_started(started=False)
        self.close()
        print("WS BACKEND :: Connection closed")

    def on_error(self, error, **kwargs):
        print("Error:", error)

    def on_open(self, ws, **_kwargs):
        print("WS BACKEND :: Connection established")
        GlobalVars.set_ws_client_backend_started(started=True)

    def run_forever(self, *_args, **_kwargs):
        websocket.enableTrace(False)
        self.ws.run_forever()

    def close(self):
        print("WS BACKEND :: Connection closed")
        self.ws.close()
