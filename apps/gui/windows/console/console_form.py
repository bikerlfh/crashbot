# Libraries
from PyQt6 import QtCore
from PyQt6.QtWidgets import QListWidgetItem, QMessageBox, QWidget

# Internal
from apps.constants import HomeBets
from apps.globals import GlobalVars
from apps.gui import services
from apps.gui.graphs.bar_multipliers import BarMultiplier
from apps.gui.windows.console.console_designer import ConsoleDesigner
from apps.utils.logs import services as logs_services
from apps.ws_client import WebSocketClient


class ConsoleForm(QWidget, ConsoleDesigner):
    MAX_LOGS_ITEMS = 50
    receive_log_signal = QtCore.pyqtSignal(dict)
    receive_multipliers_signal = QtCore.pyqtSignal(dict)
    receive_balance_signal = QtCore.pyqtSignal(dict)
    receive_auto_play_signal = QtCore.pyqtSignal(dict)
    receive_game_loaded_signal = QtCore.pyqtSignal(dict)

    def __init__(
        self,
        main_window: any,
    ):
        super().__init__()

        self.logs_to_save = []
        self.home_bet = None
        self.initial_balance = None
        self.balance = None
        self.setupUi(self)
        self.auto_play = False
        self.main_window = main_window
        self.btn_auto_bet.clicked.connect(self.button_auto_bet_clicked_event)
        self.btn_auto_cash_out.clicked.connect(self.button_auto_cash_out_clicked_event)
        self.btn_set_max_amount.clicked.connect(
            self.button_set_max_amount_to_bet_clicked_event
        )
        self.bar_multiplier = BarMultiplier(self.gbox_graph, [], 30)
        self.receive_log_signal.connect(self._on_receive_log)
        self.receive_multipliers_signal.connect(self._on_receive_multipliers)
        self.receive_balance_signal.connect(self._on_receive_balance)
        self.receive_auto_play_signal.connect(self._on_receive_auto_play)
        self.receive_game_loaded_signal.connect(self._on_receive_game_loaded)
        self.btn_auto_bet.setEnabled(False)
        self.btn_set_max_amount.setEnabled(False)
        self.btn_auto_cash_out.setEnabled(False)
        self.txt_max_amount_to_bet.setEnabled(False)
        self.txt_max_amount_to_bet.setInputMask("999999")
        # NOTE at this point the class should have been instantiated.
        self.ws_client = WebSocketClient()

    def __add_item_to_list(self, item: QListWidgetItem):
        current_row = self.list_log.currentRow()
        # add new item to the top
        self.list_log.insertItem(0, item)
        if current_row:
            current_row = current_row + 1 if current_row < self.MAX_LOGS_ITEMS else 1
            self.list_log.setCurrentRow(current_row)
        if self.list_log.count() >= self.MAX_LOGS_ITEMS:
            self.list_log.takeItem(self.MAX_LOGS_ITEMS - 1)

    def initialize(
        self,
        *,
        home_bet_index: int,
        bot_type: str,
        max_amount_to_bet: str,
        auto_play: bool,
        **_kwargs,
    ):
        self.home_bet = HomeBets[home_bet_index]
        self.lbl_home_bet.setText(self.home_bet.name)
        self.lbl_bot_type.setText(f"Bot: {bot_type}")
        self.txt_max_amount_to_bet.setText(str(max_amount_to_bet))
        self.btn_auto_bet.setText("AutoBet ON" if auto_play else "AutoBet OFF")
        self.ws_client.set_home_bet(home_bet_id=self.home_bet.id)

    def button_auto_bet_clicked_event(self):
        self.auto_play = not self.auto_play
        self.main_window.socket.auto_play(auto_play=self.auto_play)

    def button_auto_cash_out_clicked_event(self):
        auto_cash_out = not GlobalVars.get_auto_cash_out()
        GlobalVars.set_auto_cash_out(auto_cash_out)
        self.btn_auto_cash_out.setText(
            "Auto CashOut ON" if auto_cash_out else "Auto CashOut OFF"
        )

    def button_set_max_amount_to_bet_clicked_event(self):
        amount = self.txt_max_amount_to_bet.text()
        if not amount:
            QMessageBox.warning(self, "Error", "Amount is required")
            self.txt_max_amount_to_bet.setFocus()
            return
        amount = float(amount)
        amount_is_valid, min_, max_ = services.validate_max_amount_to_bet(
            home_bet=self.home_bet,
            max_amount_to_bet=amount,
            balance=self.balance,
        )
        if not amount_is_valid:
            QMessageBox.warning(
                self,
                "Amount to bet is not valid",
                f"Amount to bet must be between {min_} and {max_}",
            )
            self.txt_max_amount_to_bet.setFocus()
            return
        self.main_window.socket.set_max_amount_to_bet(max_amount_to_bet=amount)

    def on_auto_play(self, data):
        """
        ws_server callback on autoplay
        :param data: dict(autoPlay: bool)
        :return: None
        """
        self.receive_auto_play_signal.emit(data)

    @QtCore.pyqtSlot(dict)
    def _on_receive_auto_play(self, data: dict):
        try:
            self.auto_play = data.get("auto_play")
            self.btn_auto_bet.setText(
                "AutoBet ON" if self.auto_play else "AutoBet OFF"
            )
            self.btn_auto_cash_out.setEnabled(self.auto_play)
        except Exception as e:
            logs_services.save_gui_log(
                message=f"Error on autoplay: {e}", level="exception"
            )

    def on_update_balance(self, data):
        """
        ws_server callback on update balance
        :param data: dict(balance: float)
        :return: None
        """
        self.receive_balance_signal.emit(data)

    @QtCore.pyqtSlot(dict)
    def _on_receive_balance(self, data: dict):
        try:
            self.balance = float(data.get("balance"))
            if self.initial_balance is None:
                self.initial_balance = self.balance
            self.lbl_balance.setText(str(self.balance))
            profit = round(self.balance - self.initial_balance, 2)
            self.lbl_profit.setText(str(profit))
        except Exception as e:
            logs_services.save_gui_log(
                message=f"Error _on_receive_balance: {e}", level="exception"
            )

    def on_log(self, data):
        """
        ws_server callback on log
        :param data: dict(code: message)
        :return: None
        """
        self.receive_log_signal.emit(data)

    @QtCore.pyqtSlot(dict)
    def _on_receive_log(self, data: dict[str, str]):
        try:
            list_item = services.make_list_item(
                data=data, allowed_codes=self.main_window.allowed_logs
            )
            if list_item:
                self.__add_item_to_list(list_item)
        except Exception as e:
            logs_services.save_gui_log(message=f"Error on log: {e}", level="exception")

    def on_add_multipliers(self, data):
        """
        ws_server callback on add multipliers
        :param data: dict(multipliers: list)
        :return: None
        """
        self.receive_multipliers_signal.emit(data)

    @QtCore.pyqtSlot(dict)
    def _on_receive_multipliers(self, data: dict[str, list]):
        try:
            multipliers = data.get("multipliers", [])
            self.bar_multiplier.add_multipliers(multipliers=multipliers)
        except Exception as e:
            logs_services.save_gui_log(
                message=f"Error on receive multipliers: {e}", level="exception"
            )

    def on_game_loaded(self, data):
        """
        ws_server callback on game loaded
        :param data: dict(game: str)
        :return: None
        """
        self.receive_game_loaded_signal.emit(data)

    @QtCore.pyqtSlot(dict)
    def _on_receive_game_loaded(self, data: dict[str, str]):
        loaded = data.get("loaded", False)
        if loaded:
            self.btn_auto_bet.setEnabled(True)
            self.btn_set_max_amount.setEnabled(True)
            self.txt_max_amount_to_bet.setEnabled(True)
            return
        self.main_window.show_message_box(
            title="Game not loaded",
            message="Please, reload the page and try again",
        )
