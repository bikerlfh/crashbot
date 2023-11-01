# Standard Library
import gettext
import logging
import os
from threading import Event, Thread

# Internal
# from pwn import log, listen
from apps import custom_bots
from apps.game.ws_server import server as game_server
from apps.globals import GlobalVars
from apps.gui import app as gui_app
from apps.utils.datetime import sleep_now

# from apps.ws_client import WebSocketClient

logger = logging.getLogger(__name__)


def _get_base_path(filename: str):
    base_path = os.path.dirname(os.path.abspath(__file__))
    base_path = os.path.join(base_path, filename)
    return base_path


def setup_language(lang):
    domain = "base"
    localedir = _get_base_path("locales")
    translate = gettext.translation(domain, localedir, fallback=True)
    if lang:
        translate = gettext.translation(
            domain, localedir, fallback=True, languages=[lang]
        )
    translate.install()
    _ = translate.gettext
    return _


def init_app():
    GlobalVars.init()
    try:
        setup_language(GlobalVars.config.LANGUAGE)
    except Exception as exc:
        logger.error(f"error loading language: {exc}")
    custom_bot_path = _get_base_path("custom_bots")
    custom_bots_ = custom_bots.read_custom_bots(custom_bot_path)
    GlobalVars.set_bots(custom_bots_)
    # ws_client = WebSocketClient()
    event = Event()
    ws_server_thread = Thread(
        target=game_server.run_server,
        args=(event,),
        daemon=(not event.is_set()),
    )
    ws_server_thread.start()
    sleep_now(1)
    # print("connecting to server")
    # ws_client_thread = Thread(
    #     target=ws_client.run_forever,
    #     args=(event,),
    #     daemon=(not event.is_set()),
    # )
    # ws_client_thread.start()
    GlobalVars.set_ws_client_backend_started(True)
    # while not GlobalVars.is_connected():
    #    logger.info("waiting to connect all services")
    #    sleep_now(1)
    gui_app.run_gui()
    event.set()
    ws_server_thread.join()
    # ws_client_thread.join()
    # ws_client.close()


if __name__ == "__main__":
    init_app()
