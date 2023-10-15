# Libraries
from PyQt6 import QtCore, QtWidgets

# Internal
from apps.constants import BotType, HomeBets
from apps.globals import GlobalVars
from apps.gui import services
from apps.gui.windows.parameter.parameter_designer import ParameterDesigner
from apps.utils.local_storage import LocalStorage
from apps.utils.logs import services as logs_services

local_storage = LocalStorage()


class ParameterForm(QtWidgets.QWidget, ParameterDesigner):
    receive_start_bot_signal = QtCore.pyqtSignal(dict)

    def __init__(self, main_window: any):
        super().__init__()
        self.values = None
        self.setupUi(self)
        self.chk_use_ai.setVisible(False)
        self.main_window = main_window
        self.btn_start.clicked.connect(self.button_start_clicked_event)
        self.receive_start_bot_signal.connect(self._on_receive_start_bot)
        self.HomeBets = HomeBets

    def initialize(self):
        """
        invoke after get info of customer
        :return:
        """
        home_bets_data = local_storage.get_home_bets()
        if home_bets_data:
            home_bets_ = []
            for home_bet in home_bets_data:
                home_bet_id = home_bet["id"]
                home_bet_ = list(
                    filter(lambda x: x.id == home_bet_id, HomeBets)
                )
                if home_bet_:
                    home_bet_ = home_bet_[0]
                    home_bet_.url = home_bet["url"]
                    home_bet_.min_bet = home_bet["min_bet"]
                    home_bet_.max_bet = home_bet["max_bet"]
                    home_bets_.append(home_bet_)
            GlobalVars.set_allowed_home_bets(home_bets_)
            self.HomeBets = home_bets_
        else:
            GlobalVars.set_allowed_home_bets(HomeBets)
        if GlobalVars.get_plan_with_ai():
            self.chk_use_ai.setVisible(True)
            self.chk_use_ai.setEnabled(True)
        self.__fill_cmb_fields()

    def __fill_cmb_fields(self):
        count_cmb_bot = self.cmb_home_bet.count()
        for key, val in enumerate(self.HomeBets):
            if key >= count_cmb_bot:
                self.cmb_home_bet.addItem("")
            self.cmb_home_bet.setItemText(key, val.name)
        count_cmb_bot = self.cmb_bot_type.count()
        bot_type = BotType.to_list()
        custom_bots = GlobalVars.get_custom_bots()
        if custom_bots:
            # bot_type.extend([bot.name for bot in custom_bots])  # noqa
            for i in range(len(custom_bots)):
                bot_type.insert(i, custom_bots[i].name)  # noqa
        for i in range(len(bot_type)):
            if i >= count_cmb_bot:
                self.cmb_bot_type.addItem("")
            self.cmb_bot_type.setItemText(i, bot_type[i])

    def get_values(self) -> dict[str, any] | None:
        bot_types = BotType.to_list()
        bot_type = self.cmb_bot_type.currentText()
        if bot_type not in bot_types:
            custom_bot = list(
                filter(
                    lambda x: x.name == bot_type, GlobalVars.get_custom_bots()
                )
            )[0]
            GlobalVars.set_custom_bot_selected(custom_bot)
            bot_type = custom_bot.bot_type  # noqa
        home_bet_index = self.cmb_home_bet.currentIndex()
        if not bot_type:
            QtWidgets.QMessageBox.warning(self, "Error", "Select a bot type")
            return
        if home_bet_index < 0:
            QtWidgets.QMessageBox.warning(self, "Error", "Select a home bet")
            return

        home_bet = self.HomeBets[home_bet_index]
        home_bet_id = home_bet.id
        return dict(
            bot_type=bot_type,
            home_bet_index=home_bet_index,
            home_bet_id=home_bet_id,
            max_amount_to_bet=0,
            auto_play=False,
        )

    def button_start_clicked_event(self):
        data = self.get_values()
        if not data:
            return
        use_game_ai = self.chk_use_ai.isChecked()
        if self.chk_use_credentials.isChecked():
            home_bet_index = self.cmb_home_bet.currentIndex()
            home_bet = self.HomeBets[home_bet_index]
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
            use_game_ai=use_game_ai,
            username=data.get("username"),
            password=data.get("password"),
        )
        self.btn_start.setDisabled(True)

    def on_start_bot(self, data: dict[str, any]):
        """
        ws_server callback on start bot
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
                self.btn_start.setDisabled(False)
                return
            self.main_window.show_console_screen()
        except Exception as e:
            logs_services.save_gui_log(
                message=f"Error on_start_bot: {e}", level="exception"
            )
