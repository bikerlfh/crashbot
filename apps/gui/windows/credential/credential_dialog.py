# Libraries
from PyQt6 import QtWidgets

# Internal
from apps.globals import GlobalVars
from apps.gui import services
from apps.gui.windows.credential.credential_designer import CredentialDesigner


class CredentialDialog(QtWidgets.QDialog, CredentialDesigner):
    def __init__(self):
        super().__init__()
        self.credentials = []
        self.setupUi(self)
        self.show_credentials()
        self.btn_save.clicked.connect(self.btn_save_clicked)
        self.lst_credentials_home_bet.itemSelectionChanged.connect(
            self.home_bet_changed
        )
        self.btn_remove.clicked.connect(self.btn_remove_clicked)
        self.btn_remove_all.clicked.connect(self.btn_remove_all_clicked)
        self.home_bet_changed()
        self.HomeBets = []

    def initialize(self):
        self.HomeBets = GlobalVars.get_allowed_home_bets()
        self.__fill_cmb_fields()

    def show_credentials(self):
        self.tab_credentials.setCurrentIndex(0)
        self.credentials = services.get_credentials()
        self.lst_credentials_home_bet.clear()
        if not self.credentials:
            return
        for credential in self.credentials:
            home_bet = credential["home_bet"]
            item = QtWidgets.QListWidgetItem(home_bet)
            self.lst_credentials_home_bet.addItem(item)

    def __fill_cmb_fields(self):
        count_cmb_home_bet = self.cmb_home_bet.count()
        for key, val in enumerate(self.HomeBets):
            if key >= count_cmb_home_bet:
                self.cmb_home_bet.addItem("")
            self.cmb_home_bet.setItemText(key, val.name)

    def btn_save_clicked(self):
        home_bet = self.cmb_home_bet.currentText()
        username = self.txt_username.text()
        password = self.txt_password.text()
        if not home_bet:
            QtWidgets.QMessageBox.warning(self, "Error", "Select a home bet")
            return
        if not username or not password:
            QtWidgets.QMessageBox.warning(self, "Error", "Enter username and password")
            return

        credential = dict(home_bet=home_bet, username=username, password=password)
        services.save_credentials(credential=credential)
        self.txt_username.setText("")
        self.txt_password.setText("")
        self.txt_username.setFocus()
        self.show_credentials()

    def btn_remove_clicked(self):
        items = self.lst_credentials_home_bet.selectedItems()
        if not items:
            return
        item = items[0]
        home_bet = item.text()
        services.remove_credentials(home_bet=home_bet)
        self.show_credentials()

    def btn_remove_all_clicked(self):
        services.remove_credentials()
        self.show_credentials()

    def home_bet_changed(self):
        items = self.lst_credentials_home_bet.selectedItems()
        if not items:
            self.btn_remove.setDisabled(True)
            return
        self.btn_remove.setDisabled(False)
