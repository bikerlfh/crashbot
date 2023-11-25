# Libraries
from PyQt6.QtWidgets import QCheckBox, QComboBox, QTreeWidget, QTreeWidgetItem


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
                _value = child.text(1)
                _widget = tree.itemWidget(child, 1)
                if isinstance(_widget, QComboBox):
                    _value = _widget.currentText()
                elif isinstance(_widget, QCheckBox):
                    _value = _widget.isChecked()
                elif _value.isdigit():
                    _value = float(_value)
                _data[child.text(0)] = _value

        values = list(_data.values())
        if values:
            if isinstance(values[0], dict):
                return values
        return _data

    data = _get_dict_from_tree_item(tree.invisibleRootItem())
    return data


def get_key_singular(key: str) -> str:
    return key[:-1] if key.endswith("s") else key
