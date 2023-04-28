# Standard Library
import sys

# Libraries
import numpy as np
import qdarktheme
from bar_multipliers import BarMultiplier
from PyQt6 import QtCore
from PyQt6.QtWidgets import QApplication, QGroupBox, QMainWindow, QPushButton


class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 640, 480)
        self.gbox_graph = QGroupBox(parent=self)
        self.gbox_graph.setGeometry(QtCore.QRect(0, 10, 631, 281))
        self.gbox_graph.setTitle("")
        self.gbox_graph.setObjectName("gbox_graph")
        self.bar_multiplier = BarMultiplier(
            self.gbox_graph,
            [
                1.5,
                1.2,
                1.2,
                2,
                3,
                4,
                1,
                444,
                6,
                1,
                5,
                2,
                3,
                6,
                5,
                4,
                8,
                5,
                1,
                21,
                23,
                5,
                65,
                1,
                2,
                5,
                1,
                1,
                1,
            ],
            30,
        )

        # Create a button to add data to the plot
        # Create a button to add data to the plot
        self.button = QPushButton("Add Data", self)
        self.button.clicked.connect(self.add_data)
        self.bar_multiplier.draw()

    def add_data(self):
        self.bar_multiplier.add_multipliers([1.0])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    qdarktheme.setup_theme("dark")
    window = MyMainWindow()
    window.show()
    sys.exit(app.exec())
