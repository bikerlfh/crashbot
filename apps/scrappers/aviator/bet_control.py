# Standard Library
import random
from enum import Enum
from typing import Optional

# Libraries
from playwright.async_api import Locator

# Internal
from apps.scrappers.game_base import AbstractControlBase, Control

# from game.utils import round_number
# from ws.gui_events import send_event_to_gui


class BetControl(AbstractControlBase):
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
        return random.randint(15, 50)

    async def init(self):
        bet_controls = self.aviator_page.locator("app-bet-control")
        self._bet_control_1 = bet_controls.first
        self._bet_control_2 = bet_controls.last

        input_app_spinner_1 = self._bet_control_1.locator(
            ".bet-block>app-spinner"
        ).first
        input_app_spinner_2 = self._bet_control_2.locator(
            ".bet-block>app-spinner"
        ).first

        self._amount_input_1 = input_app_spinner_1.locator("input").first
        self._amount_input_2 = input_app_spinner_2.locator("input").first

        buttons_switcher_1 = await self._bet_control_1.locator(
            "app-navigation-switcher>div>button"
        ).all()
        buttons_switcher_2 = await self._bet_control_2.locator(
            "app-navigation-switcher>div>button"
        ).all()

        self._bet_switcher_button_1 = buttons_switcher_1[0]
        self._auto_switcher_button_1 = buttons_switcher_1[1]
        self._bet_switcher_button_2 = buttons_switcher_2[0]
        self._auto_switcher_button_2 = buttons_switcher_2[1]

        self._auto_cash_out_switcher_1 = self._bet_control_1.locator(
            "app-ui-switcher"
        ).last
        self._auto_cash_out_switcher_2 = self._bet_control_2.locator(
            "app-ui-switcher"
        ).last

        await self._auto_switcher_button_1.click(delay=self._random_delay())
        await self._auto_switcher_button_2.click(delay=self._random_delay())
        await self._auto_cash_out_switcher_1.click(delay=self._random_delay())
        await self._auto_cash_out_switcher_2.click(delay=self._random_delay())

        cash_out_spinner_1 = self._bet_control_1.locator(
            ".cashout-spinner-wrapper"
        ).first
        cash_out_spinner_2 = self._bet_control_2.locator(
            ".cashout-spinner-wrapper"
        ).first

        self._auto_cash_out_multiplier_1 = cash_out_spinner_1.locator("input").first
        self._auto_cash_out_multiplier_2 = cash_out_spinner_2.locator("input").first

        bet_buttons = self.aviator_page.locator("button.bet")
        self._bet_button_1 = bet_buttons.first
        self._bet_button_2 = bet_buttons.last

        self.was_load = True

    async def set_auto_cash_out(self, multiplier, control):
        auto_cash_out_multiplier = self._auto_cash_out_multiplier_1
        if control == Control.Control2:
            auto_cash_out_multiplier = self._auto_cash_out_multiplier_2

        if not auto_cash_out_multiplier:
            raise Exception("buttons null autoCashOutMultiplier")

        value = round(
            float(await auto_cash_out_multiplier.input_value(timeout=1000)), 2
        )
        if value != multiplier:
            await auto_cash_out_multiplier.fill("", timeout=1000)
            await auto_cash_out_multiplier.type(str(multiplier), delay=100)

    async def update_amount(self, amount, control):
        input_element = self._amount_input_1
        if control == Control.Control2:
            input_element = self._amount_input_2

        if input_element is None:
            raise Exception("updateAmount :: input null")

        value = round(float(await input_element.input_value(timeout=1000)), 0)
        if value != amount:
            await input_element.fill("", timeout=1000)
            await input_element.type(str(amount), delay=100)
        # self.aviator_page.wait_for_timeout(500)

    async def bet(self, amount, multiplier, control):
        if multiplier is None or amount is None:
            raise Exception("bet :: no multiplier or amount")

        await self.set_auto_cash_out(multiplier, control)
        await self.update_amount(amount, control)

        if self._bet_button_1 is None or self._bet_button_2 is None:
            raise Exception("bet :: bet button null. control")

        if control == Control.Control1:
            await self._bet_button_1.click(delay=self._random_delay())
            # self.aviator_page.wait_for_timeout(1000)
            return

        await self._bet_button_2.click(delay=self._random_delay())
        # self.aviator_page.wait_for_timeout(1000)
