# Standard Library
import logging
from threading import Event, Thread

# Internal
# from pwn import log, listen
from apps.game.ws_server import server as game_server
from apps.globals import GlobalVars
from apps.gui import app as gui_app
from apps.utils.datetime import sleep_now
from apps.ws_client import WebSocketClient

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    GlobalVars.init()
    ws_client = WebSocketClient()
    event = Event()
    ws_server_thread = Thread(
        target=game_server.run_server,
        args=(event,),
        daemon=(not event.is_set()),
    )
    ws_server_thread.start()
    sleep_now(1)
    print("connecting to server")
    ws_client_thread = Thread(
        target=ws_client.run_forever,
        args=(event,),
        daemon=(not event.is_set()),
    )
    ws_client_thread.start()
    while not GlobalVars.is_connected():
        logger.info("waiting to connect all services")
        sleep_now(1)
    gui_app.run_gui()
    event.set()
    ws_server_thread.join()
    ws_client_thread.join()
    ws_client.close()
