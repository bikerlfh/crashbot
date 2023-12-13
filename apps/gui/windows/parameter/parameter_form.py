# Libraries
from PyQt6 import QtCore, QtWidgets

# Internal
from apps.api.models import HomeBetGameModel, HomeBetModel
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
        self.cmb_game.currentTextChanged.connect(self.__load_home_bets)
        self.home_bet_games: list[HomeBetGameModel] = []
        self.home_bets: list[HomeBetModel] = []
        self.games: list[str]

    def update_bots(self):
        count_cmb_bot = self.cmb_bot_type.count()
        bots = GlobalVars.get_bots()
        for i in range(len(bots)):
            if i >= count_cmb_bot:
                self.cmb_bot_type.addItem("")
            self.cmb_bot_type.setItemText(i, bots[i].name)  # noqa

    def initialize(self):
        """
        invoke after get info of customer
        :return:
        """
        self.home_bet_games = GlobalVars.get_home_bet_games()
        self.home_bets = GlobalVars.get_allowed_home_bets()
        if GlobalVars.get_plan_with_ai():
            self.chk_use_ai.setVisible(True)
            self.chk_use_ai.setEnabled(True)
        self.__fill_cmb_fields()

    def __fill_cmb_fields(self):
        count_cmb_games = self.cmb_game.count()
        self.games = set([game.crash_game for game in self.home_bet_games])
        _key = 0
        for game in list(self.games):
            if _key >= count_cmb_games:
                self.cmb_game.addItem("")
            self.cmb_game.setItemText(_key, game)
            _key += 1
        self.update_bots()

    def __load_home_bets(self, game: str):
        home_bet_ids = [
            g.home_bet_id for g in self.home_bet_games if g.crash_game == game
        ]  # noqa
        self.cmb_home_bet.clear()
        count_cmb_home_bet = self.cmb_home_bet.count()
        home_bets = [
            home_bet
            for home_bet in self.home_bets
            if home_bet.id in home_bet_ids
        ]  # noqa
        for key, val in enumerate(home_bets):
            if key >= count_cmb_home_bet:
                self.cmb_home_bet.addItem("")
            self.cmb_home_bet.setItemText(key, val.name)

    def get_values(self) -> dict[str, any] | None:
        bot_name = self.cmb_bot_type.currentText()
        home_bet_index = self.cmb_home_bet.currentIndex()
        if not bot_name:
            QtWidgets.QMessageBox.warning(self, "Error", "Select a bot")
            return
        if home_bet_index < 0:
            QtWidgets.QMessageBox.warning(self, "Error", "Select a home bet")
            return
        home_bet_name = self.cmb_home_bet.currentText()
        home_bet = next(
            filter(lambda x: x.name == home_bet_name, self.home_bets), None
        )
        home_bet_id = home_bet.id  # noqa
        return dict(
            bot_name=bot_name,
            home_bet_id=home_bet_id,
            max_amount_to_bet=0,
            auto_play=False,
        )

    def button_start_clicked_event(self):
        data = self.get_values()
        if not data:
            return
        # get home_bet_game_id
        game = self.cmb_game.currentText()
        home_bet_id = data.get("home_bet_id")
        home_bet_game = [
            g
            for g in self.home_bet_games
            if g.crash_game == game and g.home_bet_id == home_bet_id
        ][0]
        GlobalVars.set_home_bet_game_selected(home_bet_game)
        GlobalVars.set_home_bet_game_id(home_bet_game.id)
        use_game_ai = self.chk_use_ai.isChecked()
        if self.chk_use_credentials.isChecked():
            home_bet_index = self.cmb_home_bet.currentIndex()
            home_bet = self.home_bets[home_bet_index]
            credential = services.get_credentials_by_home_bet(
                home_bet=home_bet.name  # noqa
            )
            data["username"] = credential.get("username")
            data["password"] = credential.get("password")
        self.main_window.socket.start_bot(
            bot_name=data.get("bot_name"),
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
