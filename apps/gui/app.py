# Standard Library
import sys

# Libraries
import qdarktheme
from PyQt6.QtWidgets import QApplication

# Internal
from apps.gui.windows.main.main_form import MainForm


def run_gui():
    app = QApplication(sys.argv)
    qdarktheme.setup_theme("dark")
    try:
        window = MainForm()
        sys.exit(app.exec())
    except Exception as e:
        print("EXCEPTION RUNNING GUI: ", e)
        sys.exit(app.exec())
