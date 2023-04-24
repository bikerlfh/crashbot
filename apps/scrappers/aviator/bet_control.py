import random
from playwright.sync_api import Locator
from typing import Optional
from enum import Enum
# from game.utils import round_number
# from ws.gui_events import send_event_to_gui


class Control(Enum):
    Control1 = 1
    Control2 = 2


class BetControl:
    def __init__(self, aviator_page: Locator):
        self.aviator_page = aviator_page
        self._bet_control_1: Optional[Locator] = None
        self._bet_control_2: Optional[Locator] = None
        self._amount_input_1: Optional[Locator] = None
        self._amount_input_2: Optional[Locator] = None
        self._bet_switcher_button_1: Optional[Locator] = None
        self._auto_switcher_button_1: Optional[Locator] = None
        self._bet_switcher_button_2: Optional[Locator] = None
        self._auto_switcher_button_2: Optional[Locator] = None
        self._auto_cash_out_switcher_1: Optional[Locator] = None
        self._auto_cash_out_switcher_2: Optional[Locator] = None
        self._auto_cash_out_multiplier_1: Optional[Locator] = None
        self._auto_cash_out_multiplier_2: Optional[Locator] = None
        self._bet_button_1: Optional[Locator] = None
        self._bet_button_2: Optional[Locator] = None

        self.is_active_auto_cash_out_control_1 = False
        self.is_active_auto_cash_out_control_2 = False
        self.was_load = False

    def _random_delay(self) -> int:
        min_ = 15
        max_ = 50
        return random.randint(min_, max_)
