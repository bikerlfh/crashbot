# Libraries
from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import QComboBox, QPushButton, QTreeWidgetItem, QWidget

# Internal
from apps.api.models import Bot, BotCondition, BotConditionAction
from apps.constants import BotType
from apps.game.bots.constants import ConditionAction, ConditionON
from apps.globals import GlobalVars
from apps.gui.constants import ICON_NAME
from apps.gui.windows.config_bot.config_bot_designer import ConfigBotDesigner
from apps.gui.windows.config_bot.constants import (
    ConfigKeyButton,
    ConfigKeyComboBox,
)
from apps.utils.local_storage import LocalStorage

local_storage = LocalStorage()


class ConfigBotDialog(QWidget, ConfigBotDesigner):
    def __init__(self):
        super().__init__()
        self.bots = []
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon(ICON_NAME))
        self.cmb_bots.currentIndexChanged.connect(
            self.on_current_index_changed
        )
        self.on_current_index_changed(self.cmb_bots.currentIndex())
        self.btn_add_bot.clicked.connect(self.on_btn_add_bot_clicked)
        self.btn_save.clicked.connect(self.on_btn_save_clicked)
        self.tree_configuration.header().setStretchLastSection(True)
        self.tree_configuration.setColumnWidth(0, 300)

    def initialize(self):
        self.bots = GlobalVars.get_bots()
        self.__fill_cmb_fields()

    def __fill_cmb_fields(self):
        self.cmb_bots.clear()
        for bot in self.bots:
            self.cmb_bots.addItem(bot.name)
        self.cmb_bots.insertItem(0, "")
        self.cmb_bots.setCurrentIndex(0)

    @QtCore.pyqtSlot(int)
    def on_current_index_changed(self, index):
        if index <= 0:
            self.tree_configuration.clear()
            return
        self.__fill_tree_fields(bot=self.bots[index - 1])

    def on_btn_add_bot_clicked(self):
        self.cmb_bots.setCurrentIndex(0)
        self.__add_bot()

    def on_btn_save_clicked(self):
        data = self._get_data_tree()
        print(data)

    def _get_data_tree(self) -> dict[str, any]:
        def _get_dict_from_tree_item(
            item: QTreeWidgetItem,
        ) -> dict[str, any] | list[dict[str, any]]:
            _data = {}
            for i in range(item.childCount()):
                child = item.child(i)
                if child.childCount() > 0:
                    _data[child.text(0)] = _get_dict_from_tree_item(child)
                else:
                    _data[child.text(0)] = child.text(1)
            values = list(_data.values())
            if values:
                if isinstance(values[0], dict):
                    return values
            return _data

        data = _get_dict_from_tree_item(
            self.tree_configuration.invisibleRootItem()
        )
        return data

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

    def __add_control(self, parent: QTreeWidgetItem, key, value) -> None:
        if key in ConfigKeyComboBox.to_list():
            self.__add_combo_box(parent, key, value)
        elif key in ConfigKeyButton.to_list():
            self.__add_button(
                parent=parent, action=ConfigKeyButton.get_action_by_key(key)
            )

    def _on_btn_add_tree_clicked(self) -> None:
        item = self.tree_configuration.currentItem()
        if item:
            self.__add_child(item=item)

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
            key_singular = self._get_key_singular(key)
            self._add_item_tree_child(
                item, f"{key_singular} {last_item_id}", data.__dict__
            )

    def _on_btn_remove_tree_clicked(self) -> None:
        item = self.tree_configuration.currentItem()
        if item:
            self.__remove_child(parent=item)

    @staticmethod
    def __remove_child(*, parent: QTreeWidgetItem) -> None:
        parent.parent().removeChild(parent)

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

    def _add_item_tree_child(
        self, parent: QTreeWidgetItem, key, value
    ) -> None:
        _value = str(value) if isinstance(value, (int, float, str)) else ""
        item = QTreeWidgetItem(parent)
        item.setText(0, key)
        item.setText(1, _value)
        self.__add_control(item, key, _value)
        item.setFlags(item.flags() | QtCore.Qt.ItemFlag.ItemIsEditable)

        if isinstance(value, (list, tuple)):
            key_singular = self._get_key_singular(key)
            for i, val in enumerate(value):
                _val = val.__dict__ if isinstance(val, object) else val
                self._add_item_tree_child(
                    item, f"{key_singular} {i + 1}", _val
                )
        elif isinstance(value, dict):
            for k, val in value.items():
                self._add_item_tree_child(item, k, val)

    def __fill_tree_fields(self, *, bot: Bot):
        fields = bot.__dict__
        self.tree_configuration.clear()

        for key, value in fields.items():
            if key == "id":
                continue
            self._add_item_tree_child(self.tree_configuration, key, value)

    @staticmethod
    def _get_key_singular(key: str) -> str:
        return key[:-1] if key.endswith("s") else key
