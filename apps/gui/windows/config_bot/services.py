# Libraries
from PyQt6.QtWidgets import QCheckBox, QComboBox, QTreeWidget, QTreeWidgetItem

# Internal
from apps.gui.windows.config_bot.constants import (
    ConfigKeyCheckBox,
    ConfigKeyComboBox,
)


def format_data_tree(*, data: dict[str, any]) -> dict[str, any]:
    """
    Returns a dict with the data formatted to be displayed in the tree
    @param data:
    @return: dict
    """
    _key_not_convert_float = (
        ConfigKeyCheckBox.to_list() + ConfigKeyComboBox.to_list() + ["id"]
    )

    def _format_data(_data: dict[str, any]) -> dict[str, any]:
        for key, value in _data.items():
            if isinstance(value, dict):
                _data[key] = _format_data(value)
            elif isinstance(value, list):
                _data[key] = [_format_data(item) for item in value]
            else:
                if key not in _key_not_convert_float:
                    try:
                        _data[key] = float(value)
                    except ValueError:
                        pass
                else:
                    _data[key] = str(value)
        return _data

    return _format_data(data)


def get_data_tree(*, tree: QTreeWidget) -> dict[str, any]:
    """
    Returns a dict with the data from the tree
    @param tree:
    @return: dict
    """

    def _get_dict_from_tree_item(
        item: QTreeWidgetItem,
    ) -> dict[str, any] | list[dict[str, any]]:
        _data = {}
        for i in range(item.childCount()):
            child = item.child(i)
            if child.childCount() > 0:
                _data[child.text(0)] = _get_dict_from_tree_item(child)
            else:
                _value = child.text(1).strip()
                _widget = tree.itemWidget(child, 1)
                if isinstance(_widget, QComboBox):
                    _value = _widget.currentText()
                elif isinstance(_widget, QCheckBox):
                    _value = int(_widget.isChecked())
                _data[child.text(0)] = _value

        values = list(_data.values())
        if values:
            if isinstance(values[0], dict):
                return values
        return _data

    data = _get_dict_from_tree_item(tree.invisibleRootItem())
    return format_data_tree(data=data)


def get_key_singular(key: str) -> str:
    return key[:-1] if key.endswith("s") else key
