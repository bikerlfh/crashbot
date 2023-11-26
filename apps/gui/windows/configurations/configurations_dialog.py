# Standard Library
from copy import copy

# Libraries
from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import QDialog, QMessageBox

# Internal
from apps.constants import BullishGameValues
from apps.globals import GlobalVars
from apps.gui import utils as gui_utils
from apps.gui.constants import ICON_NAME, InputMask
from apps.gui.windows.configurations.configurations_designer import (
    ConfigurationsDesigner,
)


class ConfigurationsDialog(QDialog, ConfigurationsDesigner):
    receive_log_signal = QtCore.pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self._resize_font()
        self.setWindowIcon(QtGui.QIcon(ICON_NAME))
        self.console_is_visible = False
        gui_utils.apply_mask_text_input(
            self.txt_multipliers_to_show,
            InputMask.MULTIPLIER_POSITION,
        )
        gui_utils.apply_mask_text_input(
            self.txt_len_bullish_game,
            InputMask.INTEGER,
        )
        gui_utils.apply_mask_text_input(
            self.txt_num_multiplier_in_bar,
            InputMask.INTEGER,
        )
        self.btn_save.clicked.connect(self.button_save_clicked_event)
        self._multi_to_show_last_position = copy(
            GlobalVars.config.MULTIPLIERS_TO_SHOW_LAST_POSITION
        )
        self._num_multiplier_in_bar_graph = copy(
            GlobalVars.config.NUMBER_OF_MULTIPLIERS_IN_BAR_GRAPH
        )
        self._len_bullish_game = copy(
            GlobalVars.config.LEN_WINDOW_TO_BULLISH_GAME
        )
        self._value_bullish_game = copy(
            GlobalVars.config.MIN_VALUE_TO_BULLISH_GAME
        )

    def _resize_font(self):
        gui_utils.resize_font(self.txt_len_bullish_game)
        gui_utils.resize_font(self.txt_multipliers_to_show)
        gui_utils.resize_font(self.cmb_value_bullish_game)
        gui_utils.resize_font(self.txt_num_multiplier_in_bar)
        gui_utils.resize_font(self.lbl_len_bullish_game)
        gui_utils.resize_font(self.lbl_multipliers_to_show)
        gui_utils.resize_font(self.lbl_num_multiplier_in_bar)
        gui_utils.resize_font(self.lbl_value_bullish_game)
        gui_utils.resize_font(self.groupBox)
        gui_utils.resize_font(self.btn_save)

    def initialize(self, *, console_is_visible: bool):
        self.console_is_visible = console_is_visible
        multi_to_show_last_position = (
            GlobalVars.config.MULTIPLIERS_TO_SHOW_LAST_POSITION
        )
        self.txt_multipliers_to_show.setText(
            ",".join([str(i) for i in multi_to_show_last_position])
        )
        self.txt_num_multiplier_in_bar.setText(
            str(GlobalVars.config.NUMBER_OF_MULTIPLIERS_IN_BAR_GRAPH)
        )
        self.txt_len_bullish_game.setText(
            str(GlobalVars.config.LEN_WINDOW_TO_BULLISH_GAME)
        )
        bullish_game_value = BullishGameValues.get_by_value(
            GlobalVars.config.MIN_VALUE_TO_BULLISH_GAME
        )
        self.cmb_value_bullish_game.setCurrentIndex(
            bullish_game_value.get_index()
        )

    def button_save_clicked_event(self):
        multi_to_show_last_position = [
            int(i) for i in self.txt_multipliers_to_show.text().split(",")
        ]
        num_of_mult_in_bar_graph = int(self.txt_num_multiplier_in_bar.text())
        if (
            self.console_is_visible
            and num_of_mult_in_bar_graph < self._num_multiplier_in_bar_graph
        ):
            msg = _(  # noqa
                "The number of multipliers in the bar "
                "graph can not be less than"
            )
            QMessageBox.warning(
                self, "Warning", f"{msg} {self._num_multiplier_in_bar_graph}"
            )
            return
        bullish_game_value = BullishGameValues.get_by_index(
            self.cmb_value_bullish_game.currentIndex()
        )
        GlobalVars.config.write_config(
            multipliers_to_show_last_position=multi_to_show_last_position,
            number_of_multipliers_in_bar_graph=num_of_mult_in_bar_graph,
            min_value_to_determine_bullish_game=bullish_game_value.get_value(),
            len_window_to_determine_bullish_game=int(
                self.txt_len_bullish_game.text()
            ),
        )
        self.close()
