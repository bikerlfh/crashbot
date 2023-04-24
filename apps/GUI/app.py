import sys

import qdarktheme
from PyQt6.QtWidgets import QApplication

from apps.forms.main.main_form import MainForm

if __name__ == "__main__":
    app = QApplication(sys.argv)
    qdarktheme.setup_theme("dark")
    window = MainForm()
    sys.exit(app.exec())
