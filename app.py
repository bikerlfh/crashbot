# Standard Library
import sys
import threading

# Libraries
import qdarktheme
from PyQt6.QtWidgets import QApplication

# Internal
from apps.game.ws import server as game_server
from apps.globals import GlobalVars
from apps.gui.windows.main.main_form import MainForm
from apps.utils.datetime import sleep_now

if __name__ == "__main__":
    GlobalVars.init()
    ws_server_thread = threading.Thread(target=game_server.run_server, args={})
    ws_server_thread.start()
    sleep_now(1)
    app = QApplication(sys.argv)
    qdarktheme.setup_theme("dark")
    window = MainForm()
    sys.exit(app.exec())
