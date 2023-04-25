# Standard Library
from typing import Optional

# Libraries
from PyQt6 import QtWidgets
from PyQt6.QtCore import Q_ARG, QMetaObject, Qt

# Internal
from apps.constants import BotType, HomeBets
from apps.gui.forms.parameter.parameter_designer import ParameterDesigner
from apps.gui.services import utils


class ParameterForm(QtWidgets.QWidget, ParameterDesigner):
    def __init__(self, main_window: any):
        super().__init__()
        self.values = None
        self.setupUi(self)
        self.__fill_cmb_fields()
        self.main_window = main_window
        self.btn_start.clicked.connect(self.button_start_clicked_event)
        self.cmb_home_bet.currentIndexChanged.connect(self.__set_max_amount_to_bet)
        self.__set_max_amount_to_bet(0)

    def __fill_cmb_fields(self):
        count_cmb_bot = self.cmb_home_bet.count()
        for key, val in enumerate(HomeBets):
            if key >= count_cmb_bot:
                self.cmb_home_bet.addItem("")
            self.cmb_home_bet.setItemText(key, val.name)
        count_cmb_bot = self.cmb_bot_type.count()
        bot_type = BotType.to_list()
        for i in range(len(bot_type)):
            if i >= count_cmb_bot:
                self.cmb_bot_type.addItem("")
            self.cmb_bot_type.setItemText(i, bot_type[i].title())

    def __set_max_amount_to_bet(self, index: int):
        home_bet = HomeBets[index]
        min_, max_ = utils.get_range_amount_to_bet(
            min_bet=home_bet.min_bet,
            max_bet=home_bet.max_bet,
        )
        self.txt_max_bet_amount.setText(str(min_))

    def get_values(self) -> dict[str, any] | None:
        bot_type = self.cmb_bot_type.currentText().lower()
        home_bet_index = self.cmb_home_bet.currentIndex()
        max_amount_to_bet = self.txt_max_bet_amount.text()
        auto_play = self.chk_autoplay.isChecked()
        if not bot_type:
            QtWidgets.QMessageBox.warning(self, "Error", "Select a bot type")
            return
        if home_bet_index < 0:
            QtWidgets.QMessageBox.warning(self, "Error", "Select a home bet")
            return
        if not max_amount_to_bet:
            QtWidgets.QMessageBox.warning(self, "Error", "Set a max amount to bet")
            return

        home_bet = HomeBets[home_bet_index]
        home_bet_id = home_bet.id
        max_amount_to_bet = float(max_amount_to_bet)
        amount_is_valid = utils.validate_max_amount_to_bet(
            home_bet=home_bet,
            max_amount_to_bet=max_amount_to_bet,
        )
        if not amount_is_valid:
            min_, max_ = utils.get_range_amount_to_bet(
                min_bet=home_bet.min_bet,
                max_bet=home_bet.max_bet,
            )
            QtWidgets.QMessageBox.warning(
                self,
                "Amount to bet is not valid",
                f"Amount to bet must be between {min_} and {max_}",
            )
            return
        return dict(
            bot_type=bot_type,
            home_bet_index=home_bet_index,
            home_bet_id=home_bet_id,
            max_amount_to_bet=max_amount_to_bet,
            auto_play=auto_play,
        )

    def button_start_clicked_event(self):
        data = self.get_values()
        if data:
            if self.chk_use_credentials.isChecked():
                home_bet_index = self.cmb_home_bet.currentIndex()
                home_bet = HomeBets[home_bet_index]
                credential = utils.get_credentials_by_home_bet(home_bet=home_bet.name)
                data["username"] = credential.get("username")
                data["password"] = credential.get("password")
            self.main_window.socket.start_bot(
                bot_type=data.get("bot_type"),
                home_bet_id=data.get("home_bet_id"),
                max_amount_to_bet=data.get("max_amount_to_bet"),
                auto_play=data.get("auto_play", False),
                username=data.get("username"),
                password=data.get("password"),
            )
            self.btn_start.setDisabled(True)

    def on_start_bot(self, data: dict[str, any]):
        """
        ws callback on start bot
        :param data: dict(started: bool)
        :return: None
        """
        print("parameter_form :: on_start_bot", data)
        started = data.get("started", False)
        print("on_start_bot :: started", data)
        if not started:
            error = data.get("error", None)
            # TODO invokeMethod QMessageBox from MainWindow
            QMetaObject.invokeMethod(
                self.main_window,
                "show_message_box",
                Q_ARG(str, error.get("code", "")),
                Q_ARG(str, error.get("message")),
            )
            self.btn_start.setDisabled(False)
            return
        QMetaObject.invokeMethod(
            self.main_window,
            "show_console_screen",
            Qt.ConnectionType.QueuedConnection,
        )
