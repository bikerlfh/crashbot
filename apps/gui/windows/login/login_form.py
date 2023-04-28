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

    def button_login_clicked_event(self):
        self.main_window.socket.login(
            username=self.txt_username.text(),
            password=self.txt_password.text(),
        )
        self.btn_login.setDisabled(True)

    def on_login(self, data: dict[str, any]) -> None:
        """
        ws callback for login
        :param data: dict(logged: bool)
        :return: None
        """
        self.receive_login_signal.emit(data)

    def _on_receive_login(self, data: dict[str, any]) -> None:
        logged = data.get("logged", False)
        if not logged:
            # TODO add message box with error in credentials
            self.btn_login.setDisabled(False)
            return
        self.main_window.show_parameters_screen()
        """ QMetaObject.invokeMethod(
            self.main_window,
            "show_parameters_screen",
            Qt.ConnectionType.QueuedConnection,
        )"""
