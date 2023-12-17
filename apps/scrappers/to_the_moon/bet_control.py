# Standard Library
from typing import Optional

# Libraries
from playwright.async_api import Locator
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

# Internal
from apps.gui.gui_events import SendEventToGUI
from apps.scrappers.game_base import AbstractControlBase, Control
from apps.utils.datetime import sleep_now


class BetControl(AbstractControlBase):
    # TODO implement no auto cash out
    # btn-main--bet
    # btn-main--cancel
    # btn-main--cash-out

    BTN_BET_SELECTOR = "btn-main--bet"
    BTN_BET_DANGER_SELECTOR = "btn-main--cancel"
    BTN_CASH_OUT_SELECTOR = "btn-main--cash-out"

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
        self._multiplier_element: Optional[Locator] = None
        self.was_load = False

    async def init(self):
        while True:
            try:
                await self.aviator_page.locator(
                    ".content-top__control-panel"
                ).first.wait_for(timeout=15000)
                break
            except Exception as e:
                if isinstance(e, PlaywrightTimeoutError):
                    SendEventToGUI.log.debug(
                        f"BetControl :: init :: timeout :: {e}"
                    )
                    continue
        top_play_screen = self.aviator_page.locator(
            ".content-top__play-screen"
        ).first
        self._multiplier_element = top_play_screen.locator("h1#rate").first
        bet_controls = self.aviator_page.locator(".content-top__control-panel")
        # validating if the game has 2 controls
        count_controls = await bet_controls.count()
        if count_controls == 1:
            await bet_controls.first.locator("button.btn-ctrl-1").first.click()
        _bet_controls = await bet_controls.all()
        self._bet_control_1 = _bet_controls[0]
        self._bet_control_2 = _bet_controls[1]
        # remove class is-hidden
        await self._bet_control_2.evaluate(
            "(element, classNameToRemove) => "
            "element.classList.remove(classNameToRemove)",
            "is-hidden",
        )
        sleep_now(2)
        input_app_spinner_1 = self._bet_control_1.locator(".bet-wrap").first
        input_app_spinner_2 = self._bet_control_2.locator(".bet-wrap").first

        self._amount_input_1 = input_app_spinner_1.locator("input").first
        self._amount_input_2 = input_app_spinner_2.locator("input").first

        # self._bet_switcher_button_1 = self._bet_control_1.locator(
        #     ".tabs-bet-auto__tab-1"
        # ).first
        # self._auto_switcher_button_1 = self._bet_control_1.locator(
        #     ".tabs-bet-auto__tab-2"
        # ).first
        # self._bet_switcher_button_2 = self._bet_control_2.locator(
        #     ".tabs-bet-auto__tab-3"
        # ).first
        # self._auto_switcher_button_2 = self._bet_control_2.locator(
        #     ".tabs-bet-auto__tab-4"
        # ).first
        #
        # self._auto_cash_out_switcher_1 = self._bet_control_1.locator(
        #     "input.auto-cash-switch"
        # ).last
        # self._auto_cash_out_switcher_2 = self._bet_control_2.locator(
        #     "input.auto-cash-switch"
        # ).last

        # await self._auto_switcher_button_1.click(delay=self._random_delay())
        # await self._auto_switcher_button_2.click(delay=self._random_delay())

        # cash_out_spinner_1 = self._bet_control_1.locator(
        #     ".control-panel__cash-out-ctrl"
        # ).first
        # cash_out_spinner_2 = self._bet_control_2.locator(
        #     ".control-panel__cash-out-ctrl"
        # ).first
        #
        # self._auto_cash_out_multiplier_1 = cash_out_spinner_1.locator(
        #     "input.auto-cash-input"
        # ).first
        # self._auto_cash_out_multiplier_2 = cash_out_spinner_2.locator(
        #     "input.auto-cash-input"
        # ).first

        # bet_buttons = self.aviator_page.locator("button.bet")
        # bet_buttons = self.aviator_page.locator("button.btn-success.bet")
        self._bet_button_1 = self._bet_control_1.locator(
            "button[name='bet_btn']"
        ).first
        self._bet_button_2 = self._bet_control_2.locator(
            "button[name='bet_btn']"
        ).first
        self.was_load = True

    async def set_auto_cash_out(
        self,
        *,
        control: Control,
        multiplier: Optional[float] = 0.0,
        enabled: Optional[bool] = True,
    ):
        if enabled:
            SendEventToGUI.log.info(
                _("this function is not available for this game")  # noqa
            )
        return

    async def update_amount(self, *, amount: float, control: Control):
        input_element = self._amount_input_1
        if control == Control.Control2:
            input_element = self._amount_input_2

        if input_element is None:
            raise Exception("updateAmount :: input null")
        value_ = (await input_element.input_value(timeout=1000)).replace(
            " ", ""
        )
        value = round(float(value_), 0)
        if value != amount:
            await input_element.fill("", timeout=1000)
            if amount - int(amount) == 0:
                amount = int(amount)
            await input_element.type(
                str(amount), delay=self._random_delay(500)
            )
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
        selector_ = "button[name='bet_btn']"
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
        multiplier_ = 0
        while multiplier_ < multiplier:
            # cash_out button
            status_ = await get_status_of_btn(btn_)
            if status_ != 1:
                break
            value_ = await self._multiplier_element.text_content(timeout=2000)
            if " " in value_:
                return
            multiplier_ = float(value_.replace("x", ""))
            if multiplier_ >= multiplier:
                await btn_.click()
                return
            # sleep_now(0.05)
