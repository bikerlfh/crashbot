# Standard Library
from typing import Optional

# Libraries
from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QStackedWidget, QWidget

# Internal
from apps.gui.constants import ALLOWED_LOG_CODES_TO_SHOW
from apps.gui.socket import SocketIOClient
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
        self.allowed_logs = ALLOWED_LOG_CODES_TO_SHOW
        self.socket = SocketIOClient(
            on_verify=self._on_verify,
            on_login=self.login_screen.on_login,
            on_start_bot=self.parameters_screen.on_start_bot,
            on_log=self.console_screen.on_log,
            on_auto_play=self.console_screen.on_auto_play,
            on_set_max_amount_to_bet=self.console_screen.on_set_max_amount_to_bet,
            on_update_balance=self.console_screen.on_update_balance,
        )
        self.socket.run()
        # verify token login
        self._verify_token()
        self._generate_menu_logs()

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
        self.show_login_screen()
        self.action_crendentials.triggered.connect(self.show_credential)

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
            height += 44
        self.resize(width, height)
        self.setMinimumSize(QtCore.QSize(width, height))
        self.setMaximumSize(QtCore.QSize(width, height))
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def _on_verify(self, data: dict[str, any]) -> None:
        """
        ws callback on verify token
        :param data: dict(logged: bool)
        :return: None
        """
        logged = data.get("logged", False)
        if not logged:
            print("Token is invalid, showing login screen...")
            return
        print("Token is valid, showing main screen...")
        QtCore.QMetaObject.invokeMethod(
            self,
            "show_parameters_screen",
            QtCore.Qt.ConnectionType.QueuedConnection,
        )

    def _verify_token(self) -> None:
        print("Verifying token...")
        self.socket.verify()

    def show_login_screen(self):
        self.__change_screen(
            screen=self.login_screen, width=300, height=250, title="Login"
        )

    @QtCore.pyqtSlot(str, str)
    def show_message_box(self, title: str, message: str):
        print("show_message_box", message)
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
            height=420,
            title="Parameters",
        )

    @QtCore.pyqtSlot()
    def show_console_screen(self):
        data = self.parameters_screen.get_values()
        self.console_screen.set_values(**data)
        self.__change_screen(
            screen=self.console_screen, width=897, height=557, title="Console"
        )

    def show_credential(self):
        self.credential_screen.exec()

    def _generate_menu_logs(self) -> None:
        self.menu_logs.clear()
        for code in self.allowed_logs:
            action = self._add_action(code.capitalize())
            self.menu_logs.addAction(action)

    def _add_action(self, title: str) -> QtGui.QAction:
        action = QtGui.QAction(parent=self)
        action.setText(title)
        action.setCheckable(True)
        action.setChecked(True)
        action.changed.connect(self.action_checkeable)
        return action

    def action_checkeable(self):
        _action: QtGui.QAction = self.sender()
        log_name = _action.text()
        if _action.isChecked():
            self.allowed_logs.append(log_name.lower())
        else:
            self.allowed_logs.remove(log_name.lower())

    def closeEvent(self, event) -> None:
        self.socket.close_game()
        self.socket.stop()
        super().close()
