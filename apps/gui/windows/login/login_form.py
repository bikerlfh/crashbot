# Libraries
from PyQt6 import QtCore, QtWidgets

# Internal
from apps.gui.windows.login.login_designer import LoginDesigner


class LoginForm(QtWidgets.QWidget, LoginDesigner):
    receive_login_signal = QtCore.pyqtSignal(dict)

    def __init__(self, main_window: any):
        super().__init__()
        self.setupUi(self)
        self.main_window = main_window
        self.btn_login.clicked.connect(self.button_login_clicked_event)
        self.btn_login.setDisabled(False)
        self.receive_login_signal.connect(self._on_receive_login)

    def disable_login(self, active: bool):
        self.txt_username.setDisabled(active)
        self.txt_password.setDisabled(active)
        self.btn_login.setDisabled(active)

    def clear(self):
        self.txt_username.setText("")
        self.txt_password.setText("")

    def button_login_clicked_event(self):
        self.main_window.socket.login(
            username=self.txt_username.text(),
            password=self.txt_password.text(),
        )
        self.disable_login(True)

    def on_login(self, data: dict[str, any]) -> None:
        """
        ws_server callback for login
        :param data: dict(logged: bool)
        :return: None
        """
        self.receive_login_signal.emit(data)

    def _on_receive_login(self, data: dict[str, any]) -> None:
        logged = data.get("logged", False)
        if not logged:
            # TODO add message box with error in credentials
            self.main_window.show_message_box(
                title="Error",
                message="Invalid credentials",
                # icon=QtWidgets.QMessageBox.Icon.Critical,
            )
            self.disable_login(False)
            return
        self.main_window.show_parameters_screen()
        self.disable_login(False)
