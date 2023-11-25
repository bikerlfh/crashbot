# Standard Library
from copy import deepcopy

# Libraries
from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QListWidgetItem,
    QPushButton,
    QTreeWidgetItem,
)

# Internal
from apps.api.models import Bot, BotCondition, BotConditionAction
from apps.constants import BotType
from apps.custom_bots.handlers import CustomBotsEncryptHandler
from apps.custom_bots.validations import CustomBotValidationHandler
from apps.game.bots.constants import ConditionAction, ConditionON
from apps.globals import GlobalVars
from apps.gui.constants import ICON_NAME
from apps.gui.windows.config_bot import services as config_bot_services
from apps.gui.windows.config_bot.config_bot_designer import ConfigBotDesigner
from apps.gui.windows.config_bot.constants import (
    ConfigKeyButton,
    ConfigKeyCheckBox,
    ConfigKeyComboBox,
)
from crashbot import _get_base_path

PATH_CUSTOM_BOTS = _get_base_path("custom_bots")


class ConfigBotDialog(QDialog, ConfigBotDesigner):
    def __init__(
        self,
        main_window: any,
    ):
        super().__init__()
        self.bots = []
        self.bot_selected = None
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon(ICON_NAME))
        self.main_window = main_window
        self.cmb_bots.currentIndexChanged.connect(
            self.on_current_index_changed
        )
        self.btn_add_bot.clicked.connect(self.on_btn_add_bot_clicked)
        self.btn_save.clicked.connect(self.on_btn_save_clicked)
        self.tree_configuration.header().setStretchLastSection(True)
        self.tree_configuration.setColumnWidth(0, 300)
        self.tree_configuration.doubleClicked.connect(
            self.on_tree_double_clicked
        )
        self.tree_configuration.currentItemChanged.connect(
            self.on_tree_item_changed
        )

    def initialize(self):
        self.bots = deepcopy(GlobalVars.get_bots())
        self.__fill_cmb_fields()

    @QtCore.pyqtSlot(int)
    def on_current_index_changed(self, index):
        self.lst_errors.clear()
        if index < 0:
            self.bot_selected = None
            self.tree_configuration.clear()
            return
        self.bot_selected = self.bots[index]
        self.__fill_tree_fields(bot=self.bot_selected)

    def on_tree_double_clicked(self, index):
        current_item = self.tree_configuration.currentItem()
        if current_item:
            if index.column() == 0:
                current_item.setFlags(
                    current_item.flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable
                )

    def on_tree_item_changed(self):
        current_item = self.tree_configuration.currentItem()
        if current_item:
            current_item.setFlags(
                current_item.flags() | QtCore.Qt.ItemFlag.ItemIsEditable
            )
            self.tree_configuration.editItem(current_item, 1)

    def on_btn_add_bot_clicked(self):
        self.lst_errors.clear()
        self.cmb_bots.setCurrentIndex(-1)
        self.__add_bot()

    def on_btn_save_clicked(self):
        self.lst_errors.clear()
        if self.tree_configuration.topLevelItemCount() == 0:
            return
        data = config_bot_services.get_data_tree(tree=self.tree_configuration)
        bot = Bot(id=1, **data)

        errors = self.validate_name_bot(bot=bot)
        errors.extend(CustomBotValidationHandler(bot=bot).validate_bot())
        if errors:
            self.__add_errors(errors=errors)
            return
        encrypted_bot = CustomBotsEncryptHandler(PATH_CUSTOM_BOTS)
        if self.bot_selected:
            self.bots.remove(self.bot_selected)
            if self.bot_selected.name != bot.name:
                encrypted_bot.remove(bot=self.bot_selected)
        encrypted_bot.save(bot=bot)
        self.bots.append(bot)
        GlobalVars.clear_bots()
        GlobalVars.set_bots(bots=self.bots)
        self.__fill_cmb_fields()
        # initialize bots
        game = GlobalVars.get_game()
        if game and game.bot.BOT_NAME == bot.name:
            self.main_window.socket.change_bot(bot_name=bot.name)
            self.close()
        else:
            self.main_window.console_screen.update_bots()

    def _on_btn_add_tree_clicked(self) -> None:
        item = self.tree_configuration.currentItem()
        if item:
            self.__add_child(item=item)

    def _on_btn_remove_tree_clicked(self) -> None:
        item = self.tree_configuration.currentItem()
        if item:
            self.__remove_child(parent=item)

    def __fill_cmb_fields(self):
        self.cmb_bots.clear()
        for bot in self.bots:
            self.cmb_bots.addItem(bot.name)
        self.cmb_bots.setCurrentIndex(-1)

    def __add_bot(self):
        bot = Bot(
            id=-1,
            name="",
            bot_type="",
            number_of_min_bets_allowed_in_bank=0,
            risk_factor=0,
            min_multiplier_to_bet=0,
            min_multiplier_to_recover_losses=0,
            min_probability_to_bet=0,
            min_category_percentage_to_bet=0,
            max_recovery_percentage_on_max_bet=0,
            min_average_model_prediction=0,
            stop_loss_percentage=0,
            take_profit_percentage=0,
            conditions=[],
        )
        self.__fill_tree_fields(bot=bot)

    def __add_child(self, item: QTreeWidgetItem) -> None:
        key = item.text(0)
        last_item_id = item.childCount() + 1
        data = None
        if key in ConfigKeyButton.to_list():
            match key:
                case "conditions":
                    data = BotCondition(
                        id=last_item_id,
                        condition_on="",
                        condition_on_value=0,
                        actions=[],
                        others={},
                        condition_on_value_2=None,
                    )
                case "actions":
                    data = BotConditionAction(
                        condition_action="",
                        action_value=0,
                    )
        if data:
            key_singular = config_bot_services.get_key_singular(key)
            child = self._add_item_tree_child(
                item, f"{key_singular} {last_item_id}", data.dict()
            )
            item.setExpanded(True)
            child.setExpanded(True)
            self.tree_configuration.setCurrentItem(child.child(0))

    @staticmethod
    def __remove_child(*, parent: QTreeWidgetItem) -> None:
        parent.parent().removeChild(parent)

    def __add_combo_box(self, parent: QTreeWidgetItem, key, value) -> None:
        match key:
            case ConfigKeyComboBox.BOT_TYPE:
                items = BotType.to_list()
            case ConfigKeyComboBox.CONDITION_ON:
                items = ConditionON.to_list()
            case ConfigKeyComboBox.CONDITION_ACTION:
                items = ConditionAction.to_list()
            case _:
                return
        cmb = QComboBox()
        cmb.addItems(items)
        if value:
            cmb.setCurrentText(value)
        self.tree_configuration.setItemWidget(parent, 1, cmb)

    def __add_button(self, parent: QTreeWidgetItem, action: str) -> None:
        column = 1
        btn = QPushButton()
        match action:
            case "add":
                btn.setText("+")
                btn.clicked.connect(self._on_btn_add_tree_clicked)
            case "remove":
                btn.setText("-")
                btn.clicked.connect(self._on_btn_remove_tree_clicked)
        self.tree_configuration.setItemWidget(parent, column, btn)

    def __add_check_box(self, parent: QTreeWidgetItem, value) -> None:
        check = QCheckBox()
        check.setChecked(value == "True")
        parent.setText(1, "")
        self.tree_configuration.setItemWidget(parent, 1, check)

    def __add_control(self, parent: QTreeWidgetItem, key, value) -> None:
        _key = key.split(" ").pop(0)
        if _key in ConfigKeyComboBox.to_list():
            self.__add_combo_box(parent, _key, value)
        elif _key in ConfigKeyButton.to_list():
            self.__add_button(
                parent=parent, action=ConfigKeyButton.get_action_by_key(_key)
            )
        elif _key in ConfigKeyCheckBox.to_list():
            self.__add_check_box(parent, value)

    def _add_item_tree_child(
        self, parent: QTreeWidgetItem, key, value
    ) -> QTreeWidgetItem:
        _value = str(value) if isinstance(value, (int, float, str)) else ""
        item = QTreeWidgetItem(parent)
        item.setText(0, key)
        item.setText(1, _value)
        self.__add_control(item, key, _value)

        if isinstance(value, (list, tuple)):
            key_singular = config_bot_services.get_key_singular(key)
            for i, val in enumerate(value):
                self._add_item_tree_child(item, f"{key_singular} {i + 1}", val)
        elif isinstance(value, dict):
            for k, val in value.items():
                self._add_item_tree_child(item, k, val)
        return item

    def __fill_tree_fields(self, *, bot: Bot):
        fields = bot.dict()
        self.tree_configuration.clear()

        for key, value in fields.items():
            if key == "id":
                continue
            self._add_item_tree_child(self.tree_configuration, key, value)

    def __add_errors(self, *, errors: list[str]) -> None:
        for error in errors:
            item = QListWidgetItem(error, self.lst_errors)
            item.setForeground(QtGui.QColor("red"))
            self.lst_errors.addItem(item)

    def validate_name_bot(self, bot: Bot) -> list[str]:
        if self.bot_selected:
            if self.bot_selected.name == bot.name:
                return []
            bot_names = [bot.name for bot in self.bots]
            if bot.name in bot_names:
                return [_("Name bot already exists")]  # noqa
        return []
