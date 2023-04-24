from PyQt6 import QtWidgets
from PyQt6.QtCore import QMetaObject, Qt

from apps.gui.forms.login.login_designer import LoginDesigner
from apps.utils.local_storage import LocalStorage
from apps.globals import LocalStorageKeys
from apps.api import services as api_services

local_storage = LocalStorage()


class LoginForm(QtWidgets.QWidget, LoginDesigner):
    def __init__(self, main_window: any):
        super().__init__()
        self.setupUi(self)
        self.main_window = main_window
        self.btn_login.clicked.connect(self.button_login_clicked_event)
        self.btn_login.setDisabled(False)

    def on_login(self, data: dict[str, any]) -> None:
        """
        ws callback for login
        :param data: dict(logged: bool)
        :return: None
        """
        logged = data.get("logged", False)
        if not logged:
            # TODO add message box with error in credentials
            print("login failed", data)
            self.btn_login.setDisabled(False)
            return
        QMetaObject.invokeMethod(
            self.main_window,
            "show_parameters_screen",
            Qt.ConnectionType.QueuedConnection,
        )

    def button_login_clicked_event(self):
        username = self.txt_username.text()
        password = self.txt_password.text()
        self.btn_login.setDisabled(True)
        token, refresh = api_services.request_login(
            username=username,
            password=password
        )
        if not token or not refresh:
            self.btn_login.setDisabled(False)
            return
        local_storage.set(LocalStorageKeys.TOKEN.value, token)
        local_storage.set(LocalStorageKeys.REFRESH.value, refresh)
        QMetaObject.invokeMethod(
            self.main_window,
            "show_parameters_screen",
            Qt.ConnectionType.QueuedConnection,
        )

