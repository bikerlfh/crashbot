# Libraries
from PyQt6 import QtCore, QtWidgets

# Internal
from apps.constants import BotType, HomeBets
from apps.gui import services
from apps.gui.windows.parameter.parameter_designer import ParameterDesigner
from apps.utils.logs import services as logs_services

# from PyQt6.QtCore import Q_ARG, QMetaObject


class ParameterForm(QtWidgets.QWidget, ParameterDesigner):
    receive_start_bot_signal = QtCore.pyqtSignal(dict)

    def __init__(self, main_window: any):
        super().__init__()
        self.values = None
        self.setupUi(self)
        self.main_window = main_window
        self.btn_start.clicked.connect(self.button_start_clicked_event)
        self.cmb_home_bet.currentIndexChanged.connect(
            self.__set_max_amount_to_bet
        )
        self.__fill_cmb_fields()
        self.__set_max_amount_to_bet(0)
        self.receive_start_bot_signal.connect(self._on_receive_start_bot)

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
        min_, max_ = services.get_range_amount_to_bet(
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
            QtWidgets.QMessageBox.warning(
                self, "Error", "Set a max amount to bet"
            )
            return

        home_bet = HomeBets[home_bet_index]
        home_bet_id = home_bet.id
        max_amount_to_bet = float(max_amount_to_bet)
        amount_is_valid = services.validate_max_amount_to_bet(
            home_bet=home_bet,
            max_amount_to_bet=max_amount_to_bet,
        )
        if not amount_is_valid:
            min_, max_ = services.get_range_amount_to_bet(
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
        if not data:
            return
        if self.chk_use_credentials.isChecked():
            home_bet_index = self.cmb_home_bet.currentIndex()
            home_bet = HomeBets[home_bet_index]
            credential = services.get_credentials_by_home_bet(
                home_bet=home_bet.name
            )
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
        self.receive_start_bot_signal.emit(data)

    def _on_receive_start_bot(self, data: dict[str, any]):
        try:
            started = data.get("started", False)
            if not started:
                error = data.get("error", None)
                self.main_window.show_message_box(
                    error.get("code", ""), error.get("message")
                )
                """QMetaObject.invokeMethod(
                    self.main_window,
                    "show_message_box",
                    Q_ARG(str, error.get("code", "")),
                    Q_ARG(str, error.get("message")),
                )"""
                self.btn_start.setDisabled(False)
                return
            self.main_window.show_console_screen()
            """QMetaObject.invokeMethod(
                self.main_window,
                "show_console_screen",
                Qt.ConnectionType.QueuedConnection,
            )"""
        except Exception as e:
            logs_services.save_gui_log(
                message=f"Error on_start_bot: {e}", level="exception"
            )
