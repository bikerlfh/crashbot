# Standard Library
from threading import Event, Thread

# Internal
from apps.game.ws import server as game_server
from apps.globals import GlobalVars
from apps.gui import app as gui_app
from apps.utils.datetime import sleep_now

if __name__ == "__main__":
    GlobalVars.init()
    event = Event()
    ws_server_thread = Thread(
        target=game_server.run_server,
        args=(event,),
        daemon=(not event.is_set()),
    )
    ws_server_thread.start()
    sleep_now(1)
    gui_app.run_gui()
    event.set()
    ws_server_thread.join()
