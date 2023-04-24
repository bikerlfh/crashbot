from typing import Optional

from PyQt6.QtWidgets import QListWidgetItem

from apps.constants import HomeBet
from apps.gui.services.constants import (
    ALLOWED_LOG_CODES_TO_SHOW,
    CREDENTIALS_FILE_PATH,
    LOG_CODES,
    MAX_AMOUNT_BALANCE_PERCENTAGE,
    MAX_AMOUNT_HOME_BET_PERCENTAGE,
)
from apps.gui.utils import csv
from apps.gui.utils.encrypt import Encrypt


def make_list_item(
    *,
    data: dict[str, any],
    allowed_codes: Optional[list[str]] = None,
) -> QListWidgetItem | None:
    """
    Make list item
    :param data: data
    :param allowed_codes: allowed codes
    :return: QListWidgetItem
    """
    allowed_codes = allowed_codes or ALLOWED_LOG_CODES_TO_SHOW
    code = data.get("code", None)
    if code not in allowed_codes:
        return
    message = data.get("message")
    item = QListWidgetItem(message)
    code_data = LOG_CODES.get(code, {})
    foreground = code_data.get("foreground", None)
    background = code_data.get("background", None)
    if foreground is not None:
        item.setForeground(foreground)
    if background is not None:
        item.setBackground(background)
    return item


def get_range_amount_to_bet(
    *,
    min_bet: float,
    max_bet: float,
    balance: Optional[float] = None,
) -> tuple[float, float]:
    """
    Get range amount to bet
    :param min_bet: min bet allowed by home bet
    :param max_bet: max bet allowed by home bet
    :param balance: balance
    :return: tuple
    """
    min_bet = min_bet * 3
    max_bet = max_bet * MAX_AMOUNT_HOME_BET_PERCENTAGE
    if balance:
        min_bet = min(min_bet, balance)
        max_balance = balance * MAX_AMOUNT_BALANCE_PERCENTAGE
        max_bet = min(max_bet, max_balance)
    return min_bet, max_bet


def validate_max_amount_to_bet(
    *,
    home_bet: HomeBet,
    max_amount_to_bet: float,
    balance: Optional[float] = None,
) -> bool:
    """
    Validate max bet amount
    :param home_bet: home bet
    :param max_amount_to_bet: amount to bet
    :param balance: balance
    :return: bool
    """
    min_bet = home_bet.min_bet
    max_bet = home_bet.max_bet
    min_bet, max_bet = get_range_amount_to_bet(
        min_bet=min_bet,
        max_bet=max_bet,
        balance=balance,
    )
    return min_bet <= max_amount_to_bet <= max_bet


def save_credentials(
    *,
    credential: dict[str, any],
) -> None:
    """
    Save credentials
    :param credential: credentials
    :return: None
    """
    file_name = CREDENTIALS_FILE_PATH
    data = csv.read_data(file_name=file_name) or []
    data = [item for item in data if item.get("home_bet") != credential.get("home_bet")]
    credential["username"] = Encrypt().encrypt(credential["username"])
    credential["password"] = Encrypt().encrypt(credential["password"])
    data.append(credential)
    csv.write_data_truncate(file_name=file_name, data=data)


def remove_credentials(*, home_bet: str = None) -> None:
    """
    Remove credentials
    :param home_bet: home bet
    :return: None
    """
    file_name = CREDENTIALS_FILE_PATH
    if home_bet is None:
        csv.write_data_truncate(file_name=file_name, data=[])
        return
    data = csv.read_data(file_name=file_name) or []
    data = [item for item in data if item.get("home_bet") != home_bet]
    csv.write_data_truncate(file_name=file_name, data=data)


def get_credentials() -> list[dict[str, any]] | None:
    """
    Get credentials
    :return: list[dict]
    """
    file_name = CREDENTIALS_FILE_PATH
    data = csv.read_data(file_name=file_name)
    return data


def get_credentials_by_home_bet(*, home_bet: str) -> dict[str, any]:
    """
    Get credentials by home bet
    :param home_bet: home bet
    :return: dict
    """
    credentials = get_credentials()
    if not credentials:
        return {}
    for credential in credentials:
        if credential.get("home_bet") == home_bet:
            credential["username"] = Encrypt().decrypt(credential["username"])
            credential["password"] = Encrypt().decrypt(credential["password"])
            return credential
    return {}
