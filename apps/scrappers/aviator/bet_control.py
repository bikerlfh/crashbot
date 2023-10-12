# Standard Library
from typing import Optional

# Libraries
from playwright.async_api import Locator

# Internal
from apps.gui.gui_events import SendEventToGUI
from apps.scrappers.game_base import AbstractControlBase, Control
from apps.utils.datetime import sleep_now


class BetControl(AbstractControlBase):
    # TODO implement no auto cash out
    BTN_BET_SELECTOR = "btn-success.bet"
    BTN_BET_DANGER_SELECTOR = "btn-danger.bet"
    BTN_CASH_OUT_SELECTOR = "btn-warning.cashout"

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
        self.was_load = False

    async def init(self):
        await self.aviator_page.locator("app-bet-control").first.wait_for(
            timeout=15000
        )
        bet_controls = self.aviator_page.locator("app-bet-control")
        # validating if the game has 2 controls
        count_controls = await bet_controls.count()
        if count_controls == 1:
            await bet_controls.first.locator(
                "sec-hand-btn.add.btn"
            ).first.click()
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

        cash_out_spinner_1 = self._bet_control_1.locator(
            ".cashout-spinner-wrapper"
        ).first
        cash_out_spinner_2 = self._bet_control_2.locator(
            ".cashout-spinner-wrapper"
        ).first

        self._auto_cash_out_multiplier_1 = cash_out_spinner_1.locator(
            "input"
        ).first
        self._auto_cash_out_multiplier_2 = cash_out_spinner_2.locator(
            "input"
        ).first

        # bet_buttons = self.aviator_page.locator("button.bet")
        # bet_buttons = self.aviator_page.locator("button.btn-success.bet")
        self._bet_button_1 = self._bet_control_1.locator("button.bet").first
        self._bet_button_2 = self._bet_control_2.locator("button.bet").first
        self.was_load = True

    async def set_auto_cash_out(
        self,
        *,
        control: Control,
        multiplier: Optional[float] = 0.0,
        enabled: Optional[bool] = True,
    ):
        auto_cash_out_multiplier = self._auto_cash_out_multiplier_1
        auto_cash_out_switcher = self._auto_cash_out_switcher_1
        if control == Control.Control2:
            auto_cash_out_multiplier = self._auto_cash_out_multiplier_2
            auto_cash_out_switcher = self._auto_cash_out_switcher_2

        if not auto_cash_out_multiplier:
            raise Exception("buttons null autoCashOutMultiplier")
        is_switcher_enabled = await auto_cash_out_multiplier.is_enabled()
        if (
            enabled
            and not is_switcher_enabled
            or not enabled
            and is_switcher_enabled
        ):
            await auto_cash_out_switcher.click(delay=self._random_delay(1000))
        if not enabled:
            return
        value = round(
            float(await auto_cash_out_multiplier.input_value(timeout=1000)), 2
        )
        if value != multiplier:
            await auto_cash_out_multiplier.fill("", timeout=1000)
            await auto_cash_out_multiplier.type(
                str(multiplier), delay=self._random_delay(500)
            )

    async def update_amount(self, *, amount: float, control: Control):
        input_element = self._amount_input_1
        if control == Control.Control2:
            input_element = self._amount_input_2

        if input_element is None:
            raise Exception("updateAmount :: input null")

        value = round(float(await input_element.input_value(timeout=1000)), 0)
        if value != amount:
            await input_element.fill("", timeout=1000)
            await input_element.type(str(amount), delay=self._random_delay(500))
        # self.aviator_page.wait_for_timeout(500)

    async def bet(
        self,
        *,
        amount: float,
        multiplier: float,
        control: Control,
        use_auto_cash_out: Optional[bool] = False,
    ) -> None:
        if multiplier is None or amount is None:
            raise Exception("bet :: no multiplier or amount")

        await self.set_auto_cash_out(
            control=control,
            multiplier=multiplier,
            enabled=use_auto_cash_out,
        )
        await self.update_amount(amount=amount, control=control)

        if self._bet_button_1 is None or self._bet_button_2 is None:
            raise Exception("bet :: bet button null. control")

        if control == Control.Control1:
            await self._bet_button_1.click(delay=self._random_delay())
            return

        await self._bet_button_2.click(delay=self._random_delay())

    async def wait_manual_cash_out(
        self, *, amount: float, multiplier: float, control: Control
    ) -> None:
        async def get_status_of_btn(btn_locator: Locator) -> int:
            """
            get the status of the button
            :param btn_locator:
            :return: -1: btn without bet
                      0: btn with bet
                      1: btn with cash out
                      -2 btn not found
            """
            class_ = await btn_locator.get_attribute("class")
            class_ = class_.replace(" ", ".")
            if self.BTN_CASH_OUT_SELECTOR in class_:
                return 1
            elif self.BTN_BET_DANGER_SELECTOR in class_:
                return 0
            elif self.BTN_BET_SELECTOR in class_:
                return -1
            return -2

        selector_ = (
            f"button.{self.BTN_BET_SELECTOR}, "
            f"button.{self.BTN_CASH_OUT_SELECTOR}, "
            f"button.{self.BTN_BET_DANGER_SELECTOR}"
        )
        bet_control = (
            self._bet_control_1
            if control == Control.Control1
            else self._bet_control_2
        )
        while True:
            await bet_control.locator(selector_).wait_for(timeout=5000)
            btn_ = bet_control.locator(selector_).first
            if not await btn_.is_visible():
                sleep_now(1)
                continue
            status_ = await get_status_of_btn(btn_)
            match status_:
                case -2:  # noqa
                    SendEventToGUI.log.debug(
                        f"wait_manual_cash_out :: button not found :: "
                        f"control {control.value}"
                    )
                    return
                case -1:  # noqa
                    # bet button without bet
                    SendEventToGUI.log.debug(
                        f"wait_manual_cash_out :: bet button without bet :: "
                        f"control {control.value}"
                    )
                    return
                case 0:
                    # bet button with bet
                    sleep_now(0.8)
                    continue
                case 1:
                    break
        started = False
        multiplier_ = 0
        while multiplier_ < multiplier:
            # cash_out button
            value_ = float(
                (await btn_.text_content(timeout=2000)).split(" ")[-2]
            )
            multiplier_ = round(value_ / amount, 2)
            if multiplier_ == 1 and started is True:
                break
            started = True
            if multiplier_ >= multiplier:
                await btn_.click()
                return
            # sleep_now(0.05)
