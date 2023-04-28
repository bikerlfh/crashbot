# Libraries
from PyQt6.QtWidgets import QListWidgetItem, QMessageBox, QWidget

# Internal
from apps.constants import HomeBets
from apps.gui import services
from apps.gui.graphs.bar_multipliers import BarMultiplier
from apps.gui.windows.console.console_designer import ConsoleDesigner


class ConsoleForm(QWidget, ConsoleDesigner):
    MAX_LOGS_ITEMS = 50

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
        self.btn_set_max_amount.clicked.connect(
            self.button_set_max_amount_to_bet_clicked_event
        )
        self.bar_multiplier = BarMultiplier(self.gbox_graph, [], 30)

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

    def set_values(
        self,
        *,
        home_bet_index: int,
        bot_type: str,
        max_amount_to_bet: str,
        auto_play: bool,
        **kwargs,
    ):
        self.home_bet = HomeBets[home_bet_index]
        self.lbl_home_bet.setText(self.home_bet.name)
        self.lbl_bot_type.setText(f"Bot: {bot_type}")
        self.txt_max_amount_to_bet.setText(str(max_amount_to_bet))
        self.btn_auto_bet.setText("AutoBet ON" if auto_play else "AutoBet OFF")

    def button_auto_bet_clicked_event(self):
        self.auto_play = not self.auto_play
        self.main_window.socket.auto_play(auto_play=self.auto_play)

    def button_set_max_amount_to_bet_clicked_event(self):
        amount = self.txt_max_amount_to_bet.text()
        if not amount:
            QMessageBox.warning(self, "Error", "Amount is required")
            self.txt_max_amount_to_bet.setFocus()
            return
        amount = float(amount)
        amount_is_valid = services.validate_max_amount_to_bet(
            home_bet=self.home_bet,
            max_amount_to_bet=amount,
            balance=self.balance,
        )
        if not amount_is_valid:
            min_, max_ = services.get_range_amount_to_bet(
                min_bet=self.home_bet.min_bet,
                max_bet=self.home_bet.max_bet,
            )
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
        ws callback on autoplay
        :param data: dict(autoPlay: bool)
        :return: None
        """
        self.btn_auto_bet.setText(
            "AutoBet ON" if data.get("auto_play") else "AutoBet OFF"
        )

    def on_set_max_amount_to_bet(self, data):
        """
        ws callback on set max amount to bet
        :param data: dict(maxAmountToBet: float)
        :return: None
        """
        pass

    def on_update_balance(self, data):
        """
        ws callback on update balance
        :param data: dict(balance: float)
        :return: None
        """
        self.balance = float(data.get("balance"))
        if self.initial_balance is None:
            self.initial_balance = self.balance
        self.lbl_balance.setText(str(self.balance))
        profit = round(self.balance - self.initial_balance, 2)
        self.lbl_profit.setText(str(profit))

    def on_log(self, data):
        """
        ws callback on log
        :param data: dict(code: message)
        :return: None
        """
        # self.logs_to_save.append(data)
        # if len(self.logs_to_save) > self.MAX_LOGS_ITEMS:
        #    utils.save_logs(logs=self.logs_to_save)
        #    self.logs_to_save = []
        list_item = services.make_list_item(
            data=data, allowed_codes=self.main_window.allowed_logs
        )
        if list_item:
            self.__add_item_to_list(list_item)

    def on_add_multipliers(self, data):
        """
        ws callback on add multipliers
        :param data: dict(multipliers: list)
        :return: None
        """
        multipliers = data.get("multipliers", [])
        self.bar_multiplier.add_multipliers(multipliers=multipliers)
