# Libraries
from PyQt6 import QtCore
from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtWidgets import QListWidgetItem, QMessageBox, QWidget

# Internal
from apps.globals import GlobalVars
from apps.gui import services
from apps.gui.constants import DEFAULT_FONT_SIZE, MAC_FONT_SIZE
from apps.gui.graphs.bar_multipliers import BarMultiplier
from apps.gui.windows.console.console_designer import ConsoleDesigner
from apps.utils import os as os_utils
from apps.utils.display import format_amount_to_display
from apps.utils.local_storage import LocalStorage
from apps.utils.logs import services as logs_services
from apps.ws_client import WebSocketClient

local_storage = LocalStorage()


class ConsoleForm(QWidget, ConsoleDesigner):
    MAX_LOGS_ITEMS = 50
    receive_log_signal = QtCore.pyqtSignal(dict)
    receive_multipliers_signal = QtCore.pyqtSignal(dict)
    receive_balance_signal = QtCore.pyqtSignal(dict)
    receive_auto_play_signal = QtCore.pyqtSignal(dict)
    receive_game_loaded_signal = QtCore.pyqtSignal(dict)
    receive_multiplier_positions_signal = QtCore.pyqtSignal(dict)

    def __init__(
        self,
        main_window: any,
    ):
        super().__init__()
        self.logs_to_save = []
        self.home_bet = None
        self.bot = None
        self.initial_balance = None
        self.balance = None
        self.auto_play = False
        self.setupUi(self)
        self._resize_font()
        self.__fill_cmb_fields()
        self.main_window = main_window
        self.btn_auto_bet.clicked.connect(self.button_auto_bet_clicked_event)
        self.btn_auto_cash_out.clicked.connect(
            self.button_auto_cash_out_clicked_event
        )
        self.btn_set_max_amount.clicked.connect(
            self.button_set_max_amount_to_bet_clicked_event
        )
        self.bar_multiplier = BarMultiplier(
            self.gbox_graph,
            [],
        )
        self.receive_log_signal.connect(self._on_receive_log)
        self.receive_multipliers_signal.connect(self._on_receive_multipliers)
        self.receive_balance_signal.connect(self._on_receive_balance)
        self.receive_auto_play_signal.connect(self._on_receive_auto_play)
        self.receive_game_loaded_signal.connect(self._on_receive_game_loaded)
        self.receive_multiplier_positions_signal.connect(
            self._on_receive_multiplier_positions
        )
        self.cmb_bot.currentIndexChanged.connect(self.cmb_bot_changed)
        self.btn_auto_bet.setEnabled(False)
        self.btn_set_max_amount.setEnabled(False)
        self.btn_auto_cash_out.setEnabled(False)
        self.txt_max_amount_to_bet.setEnabled(False)
        regex = QRegularExpression(r"^\d*\.?\d*$")
        validator = QRegularExpressionValidator(regex)
        self.txt_max_amount_to_bet.setValidator(validator)
        # NOTE at this point the class should have been instantiated.
        self.ws_client = WebSocketClient()

    def update_bots(self):
        self.__fill_cmb_fields()
        self.cmb_bot.setEnabled(True)

    def __fill_cmb_fields(self):
        count_cmb_bot = self.cmb_bot.count()
        bots = GlobalVars.get_bots()
        for i in range(len(bots)):
            if i >= count_cmb_bot:
                self.cmb_bot.addItem("")
            self.cmb_bot.setItemText(i, bots[i].name)  # noqa
        self.cmb_bot.setEnabled(False)

    def __add_item_to_list(self, item: QListWidgetItem):
        current_row = self.list_log.currentRow()
        # add new item to the top
        self.list_log.insertItem(0, item)
        if current_row:
            current_row = (
                current_row + 1 if current_row < self.MAX_LOGS_ITEMS else 1
            )
            self.list_log.setCurrentRow(current_row)
        if self.list_log.count() >= self.MAX_LOGS_ITEMS:
            self.list_log.takeItem(self.MAX_LOGS_ITEMS - 1)

    def initialize(
        self,
        *,
        home_bet_index: int,
        bot_name: str,
        max_amount_to_bet: str,
        auto_play: bool,
        **_kwargs,
    ):
        home_bets = GlobalVars.get_allowed_home_bets()
        self.home_bet = home_bets[home_bet_index]
        self.bot = next(
            filter(lambda x: x.name == bot_name, GlobalVars.get_bots()),
            None,
        )
        self.lbl_home_bet.setText(self.home_bet.name)  # noqa
        bots = GlobalVars.get_bots()
        bot_index = 0
        for i in range(len(bots)):
            if bots[i].name == bot_name:  # noqa
                bot_index = i
                break
        self.cmb_bot.setCurrentIndex(bot_index)
        self.txt_max_amount_to_bet.setText(str(max_amount_to_bet))
        text_ = _("Stop Bot") if auto_play else _("Start Bot")  # noqa
        self.btn_auto_bet.setText(text_)
        # self.ws_client.set_home_bet(
        #     home_bet_id=self.home_bet.id,  # noqa
        #     customer_id=local_storage.get_customer_id(),
        # )

    def _resize_font(self):
        font_size = (
            DEFAULT_FONT_SIZE if not os_utils.is_macos() else MAC_FONT_SIZE
        )

        def _set_font(widget: any):
            font = widget.font()
            font.setPointSize(font_size)
            widget.setFont(font)

        _set_font(self.txt_max_amount_to_bet)
        _set_font(self.btn_set_max_amount)
        _set_font(self.list_log)
        _set_font(self.btn_auto_bet)
        _set_font(self.label)
        _set_font(self.label_2)
        _set_font(self.lbl_balance)
        _set_font(self.lbl_profit)
        _set_font(self.label_4)
        _set_font(self.lbl_home_bet)
        _set_font(self.cmb_bot)
        _set_font(self.btn_auto_cash_out)
        _set_font(self.gbox_graph)
        _set_font(self.label_5)
        _set_font(self.lbl_profit_per)
        _set_font(self.groupBox)
        _set_font(self.lbl_mul_1)
        _set_font(self.lbl_mul_2)
        _set_font(self.lbl_mul_3)
        _set_font(self.lbl_mul_4)
        _set_font(self.lbl_mul_5)
        _set_font(self.lbl_mul_6)
        _set_font(self.lbl_mul_2)

    def button_auto_bet_clicked_event(self):
        self.auto_play = not self.auto_play
        self.main_window.socket.auto_play(auto_play=self.auto_play)

    def button_auto_cash_out_clicked_event(self):
        auto_cash_out = not GlobalVars.get_auto_cash_out()
        GlobalVars.set_auto_cash_out(auto_cash_out)
        text_ = (
            _("Turn off auto cash out")  # noqa
            if auto_cash_out
            else _("Turn on auto cash out")  # noqa
        )  # noqa
        self.btn_auto_cash_out.setText(text_)

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
            min_ = format_amount_to_display(min_)
            max_ = format_amount_to_display(max_)
            QMessageBox.warning(
                self,
                _("Amount to bet is not valid"),  # noqa
                f"{_('Amount to bet must be between')} {min_} {_('and')} {max_}",  # noqa
            )
            self.txt_max_amount_to_bet.setFocus()
            return
        number_of_min_bets_allowed_in_bank = (
            self.bot.number_of_min_bets_allowed_in_bank
        )
        num_bets_in_bank = self.balance / amount
        if num_bets_in_bank < number_of_min_bets_allowed_in_bank:
            amount_ = amount * number_of_min_bets_allowed_in_bank
            amount_ = format_amount_to_display(amount_)
            QMessageBox.warning(
                self,
                _("The balance is very low"),  # noqa
                f"{_('The selected bot recommends to have at least')} ${amount_} "  # noqa
                f"{_('in the bank. ¡Play at your own risk!')}",  # noqa
            )
        self.main_window.socket.set_max_amount_to_bet(max_amount_to_bet=amount)

    def cmb_bot_changed(self, index):
        bot_name = self.cmb_bot.currentText()
        if not bot_name:
            return
        bot = next(
            filter(lambda x: x.name == bot_name, GlobalVars.get_bots()),
            None,
        )
        if not bot:
            return
        self.main_window.socket.change_bot(bot_name=bot.name)

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
            amount = GlobalVars.get_max_amount_to_bet()
            if not amount:
                self.main_window.show_message_box(
                    title="Error",
                    message=_("Please, set the max amount to bet"),  # noqa
                )
                return
            self.auto_play = data.get("auto_play")
            text_ = _("Stop Bot") if self.auto_play else _("Start Bot")  # noqa
            self.btn_auto_bet.setText(text_)
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
            balance_ = format_amount_to_display(self.balance)
            self.lbl_balance.setText(str(balance_))
            profit = round(self.balance - self.initial_balance, 2)
            self.lbl_profit.setText(f"{profit}")
            profit_percentage = 0
            if self.initial_balance > 0:
                profit_percentage = round(
                    (profit / self.initial_balance) * 100, 2
                )
                profit_percentage = format_amount_to_display(profit_percentage)
            self.lbl_profit_per.setText(f"{profit_percentage}%")
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
            logs_services.save_gui_log(
                message=f"Error on log: {e}", level="exception"
            )

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
            self.cmb_bot.setEnabled(True)
            self.btn_auto_bet.setEnabled(True)
            self.btn_set_max_amount.setEnabled(True)
            self.txt_max_amount_to_bet.setEnabled(True)
            return
        self.main_window.show_message_box(
            title="Game not loaded",
            message="Please, reload the page and try again",
        )

    def update_multiplier_positions(
        self, *, positions: list[tuple[int, int]], len_multipliers: int
    ) -> None:
        for i in range(len(positions)):
            multiplier, position = positions[i]
            lbl_mul = getattr(self, f"lbl_mul_{i+1}", None)
            if not lbl_mul:
                break
            if position < 0:
                position = f"> {len_multipliers}"
            lbl_mul.setText(f"{multiplier} : {position}")

    def on_receive_multiplier_positions(self, positions):
        """
        ws_server callback on add multipliers
        :param positions: dict(multipliers: list)
        :return: None
        """
        self.receive_multiplier_positions_signal.emit(positions)

    @QtCore.pyqtSlot(dict)
    def _on_receive_multiplier_positions(self, data: dict):
        positions = data.get("positions", [])
        len_multipliers = data.get("len_multipliers", 0)
        self.update_multiplier_positions(
            positions=positions, len_multipliers=len_multipliers
        )
