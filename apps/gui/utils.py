# Libraries
from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator

# Internal
from apps.gui.constants import DEFAULT_FONT_SIZE, MAC_FONT_SIZE, InputMask
from apps.utils import os as os_utils


def resize_font(widget: any):
    font_size = DEFAULT_FONT_SIZE if not os_utils.is_macos() else MAC_FONT_SIZE
    font = widget.font()
    font.setPointSize(font_size)
    widget.setFont(font)


def apply_mask_text_input(text_input_widget: any, mask: InputMask):
    regex = QRegularExpression(mask.value)
    validator = QRegularExpressionValidator(regex)
    text_input_widget.setValidator(validator)
