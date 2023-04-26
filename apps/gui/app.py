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
    window = MainForm()
    sys.exit(app.exec())
