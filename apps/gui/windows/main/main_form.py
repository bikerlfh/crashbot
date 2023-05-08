# Standard Library
from typing import Optional, cast

# Libraries
from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QStackedWidget, QWidget

# Internal
from apps.constants import VERSION
from apps.globals import GlobalVars
from apps.gui.socket_io_client import SocketIOClient
from apps.gui.utils import os as utils_os
from apps.gui.windows.console.console_form import ConsoleForm
from apps.gui.windows.credential.credential_dialog import CredentialDialog
from apps.gui.windows.login.login_form import LoginForm
from apps.gui.windows.main.main_designer import MainDesigner
from apps.gui.windows.parameter.parameter_form import ParameterForm


class MainForm(QMainWindow, MainDesigner):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
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
        )
        self.socket.run()
        # verify token login
        self._verify_token()

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
        self.showMaximized()
        self.action_crendentials.triggered.connect(self.show_credential)
        self.action_exit.triggered.connect(self.closeEvent)
        self.show_login_screen()

    def _load_version(self) -> None:
        self.lbl_version.setText(VERSION)
        self.statusbar.addPermanentWidget(self.lbl_version)

    def __change_screen(
        self,
        *,
        screen: QWidget,
        width: int,
        height: int,
        title: Optional[str] = None
    ) -> None:
        if title:
            self.setWindowTitle(title)
        self.stacked_widget.setCurrentWidget(screen)
        # if it's not osX, add height to window (menu bar)
        if utils_os.is_linux() or utils_os.is_windows():
            height += 55
        self.resize(width, height)
        q_size = QtCore.QSize(width, height)
        # q_rect = QtCore.QRect(0, 0, width, height)
        self.setMinimumSize(q_size)
        self.setMaximumSize(q_size)
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        # self.setGeometry(q_rect)

    def _on_verify(self, data: dict[str, any]) -> None:
        """
        ws_server callback on verify token
        :param data: dict(logged: bool)
        :return: None
        """
        logged = data.get("logged", False)
        if not logged:
            return
        QtCore.QMetaObject.invokeMethod(
            self,
            "show_parameters_screen",
            QtCore.Qt.ConnectionType.QueuedConnection,
        )

    def _verify_token(self) -> None:
        self.socket.verify()

    def show_login_screen(self):
        self.__change_screen(
            screen=self.login_screen, width=300, height=280, title="Login"
        )

    @QtCore.pyqtSlot(str, str)
    def show_message_box(self, title: str, message: str):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText(message)
        msg.setWindowTitle(title)
        msg.exec()

    @QtCore.pyqtSlot()
    def show_parameters_screen(self):
        self.__change_screen(
            screen=self.parameters_screen,
            width=412,
            height=291,
            title="Parameters",
        )

    @QtCore.pyqtSlot()
    def show_console_screen(self):
        data = self.parameters_screen.get_values()
        self.console_screen.initialize(**data)
        self.__change_screen(
            screen=self.console_screen, width=897, height=557, title="Console"
        )

    def show_credential(self):
        self.credential_screen.exec()

    def _add_action(self, title: str) -> QtGui.QAction:
        action = QtGui.QAction(parent=self)
        action.setText(title)
        action.setCheckable(True)
        action.setChecked(True)
        action.changed.connect(self.action_checkeable)
        return action

    def _generate_menu_logs(self) -> None:
        self.menu_logs.clear()
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

    def closeEvent(self, event) -> None:
        if self.socket and self.socket.is_connected:
            self.socket.close_game()
            self.socket.stop()
        super().close()
