import sys

import qdarktheme
from PyQt6.QtWidgets import QApplication

from apps.gui.forms.main.main_form import MainForm
import threading
from apps.game.ws import server as game_server

if __name__ == "__main__":
    x = threading.Thread(target=game_server.run_server, args={})
    x.start()
    app = QApplication(sys.argv)
    qdarktheme.setup_theme("dark")
    window = MainForm()
    sys.exit(app.exec())
