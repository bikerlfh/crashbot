# Standard Library
from typing import Optional, cast

# Libraries
from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QStackedWidget, QWidget

# Internal
from apps.globals import GlobalVars
from apps.gui.constants import ICON_NAME, LANGUAGES
from apps.gui.socket_io_client import SocketIOClient
from apps.gui.windows.config_bot.config_bot_dialog import ConfigBotDialog
from apps.gui.windows.configurations.configurations_dialog import (
    ConfigurationsDialog,
)
from apps.gui.windows.console.console_form import ConsoleForm
from apps.gui.windows.credential.credential_dialog import CredentialDialog
from apps.gui.windows.login.login_form import LoginForm
from apps.gui.windows.main.main_designer import MainDesigner
from apps.gui.windows.parameter.parameter_form import ParameterForm
from apps.utils import os as utils_os
from apps.utils.local_storage import LocalStorage

local_storage = LocalStorage()


class MainForm(QMainWindow, MainDesigner):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon(ICON_NAME))
        self.__init_screen()
        self.allowed_logs = GlobalVars.config.ALLOWED_LOG_CODES_TO_SHOW
        self._generate_menu_logs()
        self._load_version()
        self.socket = SocketIOClient(
            on_verify=self._on_verify,
            on_login=self.login_screen.on_login,
            on_start_bot=self.parameters_screen.on_start_bot,
            on_log=self.console_screen.on_log,
            on_auto_play=self.console_screen.on_auto_play,
            on_update_balance=self.console_screen.on_update_balance,
            on_add_multipliers=self.console_screen.on_add_multipliers,
            on_game_loaded=self.console_screen.on_game_loaded,
            on_receive_multiplier_positions=(
                self.console_screen.on_receive_multiplier_positions
            ),
        )
        self.socket.run()
        # verify token login
        self._verify_token()
        self.console_is_visible = False

    def __init_screen(self) -> None:
        self.stacked_widget = QStackedWidget(self)
        self.login_screen = LoginForm(self)
        self.parameters_screen = ParameterForm(self)
        self.console_screen = ConsoleForm(self)
        self.stacked_widget.addWidget(self.login_screen)
        self.stacked_widget.addWidget(self.parameters_screen)
        self.stacked_widget.addWidget(self.console_screen)
        self.setCentralWidget(self.stacked_widget)
        self.credential_screen = CredentialDialog()
        self.configuration_dialog = ConfigurationsDialog()
        self.config_bots = ConfigBotDialog(self)
        self.showMaximized()
        self.action_crendentials.triggered.connect(self.show_credential)
        self.action_parameters.triggered.connect(self.show_configuration)
        self.action_bots.triggered.connect(self.show_bots)
        self.action_exit.triggered.connect(self.closeEvent)
        self.action_signout.triggered.connect(self._action_sign_out)
        self.action_spanish.triggered.connect(self._action_change_language)
        self.action_english.triggered.connect(self._action_change_language)
        self.show_login_screen()
        self.action_english.setChecked(True)
        lang = LANGUAGES(GlobalVars.config.LANGUAGE)
        if lang == LANGUAGES.SPANISH:
            self.action_spanish.setChecked(True)
            self.action_english.setChecked(False)

    def _load_version(self) -> None:
        self.lbl_version.setText(GlobalVars.APP_VERSION)
        self.statusbar.addPermanentWidget(self.lbl_version)

    def __change_screen(
        self,
        *,
        screen: QWidget,
        width: int,
        height: int,
        title: Optional[str] = None,
        apply_max_min_size: Optional[bool] = True,
    ) -> None:
        if title:
            self.setWindowTitle(title)
        self.stacked_widget.setCurrentWidget(screen)
        # if it's not osX, add height to window (menu bar)
        height += 22
        if utils_os.is_linux() or utils_os.is_windows():
            height += 33
        q_size = QtCore.QSize(width, height)
        # self.setBaseSize(q_size)
        self.resize(width, height)
        self.setMinimumSize(q_size)
        self.setMaximumSize(QtCore.QSize(50000, 50000))
        if apply_max_min_size:
            self.setMinimumSize(q_size)
            self.setMaximumSize(q_size)
        else:
            self.setMinimumSize(QtCore.QSize(200, 100))
        cp = self.screen().availableGeometry().center()
        qr = self.frameGeometry()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def _on_verify(self, data: dict[str, any]) -> None:
        """
        ws_server callback on verify token
        :param data: dict(logged: bool)
        :return: None
        """
        logged = data.get("logged", False)
        if not logged:
            self.login_screen.disable_login(False)
            return
        QtCore.QMetaObject.invokeMethod(
            self,
            "show_parameters_screen",
            QtCore.Qt.ConnectionType.QueuedConnection,
        )

    def _verify_token(self) -> None:
        self.socket.verify()
        self.login_screen.disable_login(True)

    @QtCore.pyqtSlot(str, str)
    def show_message_box(self, title: str, message: str):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText(message)
        msg.setWindowTitle(title)
        msg.exec()

    def show_login_screen(self):
        self.menubar.setVisible(False)
        self.__change_screen(
            screen=self.login_screen,
            width=300,
            height=230,
            title=f"{GlobalVars.APP_NAME} - Login",
        )

    @QtCore.pyqtSlot()
    def show_parameters_screen(self):
        self.menubar.setVisible(True)
        self.parameters_screen.initialize()
        self.__change_screen(
            screen=self.parameters_screen,
            width=412,
            height=291,
            title=f"{GlobalVars.APP_NAME}",
        )

    @QtCore.pyqtSlot()
    def show_console_screen(self):
        data = self.parameters_screen.get_values()
        self.console_screen.initialize(**data)
        self.__change_screen(
            screen=self.console_screen,
            width=897,
            height=520,
            title=GlobalVars.APP_NAME,
            apply_max_min_size=False,
        )
        self.menu_language.setEnabled(False)
        self.console_is_visible = True

    def show_credential(self):
        self.credential_screen.initialize()
        self.credential_screen.exec()

    def show_configuration(self):
        self.configuration_dialog.initialize(
            console_is_visible=self.console_is_visible
        )
        self.configuration_dialog.exec()

    def show_bots(self):
        self.config_bots.initialize()
        self.config_bots.exec()

    def _add_action(self, title: str) -> QtGui.QAction:
        action = QtGui.QAction(parent=self)
        action.setText(title)
        action.setCheckable(True)
        action.setChecked(True)
        action.changed.connect(self.action_checkeable)
        return action

    def _generate_menu_logs(self) -> None:
        self.menu_logs.clear()
        if not GlobalVars.config.DEBUG:
            self.menubar.removeAction(self.menu_view.menuAction())
            return
        for code in self.allowed_logs:
            action = self._add_action(code.capitalize())
            self.menu_logs.addAction(action)

    def action_checkeable(self):
        _action = cast(QtGui.QAction, self.sender())
        log_name = _action.text()
        if _action.isChecked():
            self.allowed_logs.append(log_name.lower())
            return
        self.allowed_logs.remove(log_name.lower())

    def _action_change_language(self):
        _action = cast(QtGui.QAction, self.sender())
        language_ = LANGUAGES.ENGLISH
        if _action == self.action_english:
            self.action_spanish.setChecked(False)
            self.action_english.setChecked(True)
        else:
            self.action_english.setChecked(False)
            self.action_spanish.setChecked(True)
            language_ = LANGUAGES.SPANISH
        GlobalVars.config.write_config(language=language_.value)
        self.show_message_box(
            title="Info",
            message=_(  # noqa
                "You must restart the application to apply the changes"
            ),
        )

    def _action_sign_out(self):
        self.socket.close_game()
        # self.socket.stop()
        local_storage.remove_token()
        self.show_login_screen()
        self.login_screen.clear()

    def closeEvent(self, event) -> None:
        if self.socket and self.socket.is_connected:
            self.socket.close_game()
            self.socket.stop()
        super().close()
