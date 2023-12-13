# Standard Library
import asyncio
import random
from typing import Optional, Union

# Libraries
from playwright.async_api import Locator
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright

# Internal
from apps.game.models import Bet
from apps.gui.gui_events import SendEventToGUI
from apps.scrappers.aviator.bet_control import BetControl
from apps.scrappers.game_base import AbstractCrashGameBase, Control
from apps.utils.datetime import sleep_now
from apps.utils.display import format_amount_to_display
from apps.utils.patterns.factory import ConfigurationFactory


class AviatorBase(AbstractCrashGameBase, ConfigurationFactory):
    """
    Aviator base scrapper
    Use Factory to implement a new bookmaker (home_bet)
    import all the classes in apps/game/bookmakers/__init__.py
    """

    def __init__(self, *, url: str, **kwargs):
        super().__init__(url=url)

    async def _click(self, element: Locator):
        box = await element.bounding_box()
        if not box or not self._page:
            SendEventToGUI.log.error("page :: box or page does't exists")
            return
        await self._page.mouse.move(
            box["x"] + box["width"] / 2, box["y"] + box["height"] / 2, steps=50
        )
        await self._page.mouse.click(
            box["x"] + box["width"] / 2, box["y"] + box["height"] / 2, delay=50
        )

    async def _login(self):
        pass

    async def _get_app_game(self) -> Locator:
        if not self._page:
            SendEventToGUI.exception(
                {
                    "location": "AviatorPage",
                    "message": "_getAppGame :: page is null",
                }
            )
            raise Exception("_getAppGame :: page is null")

        _app_game = None
        while True:
            try:
                await self._page.locator("app-game").first.wait_for(
                    timeout=50000
                )
                _app_game = self._page.locator("app-game").first
                await _app_game.locator(".result-history").wait_for(
                    timeout=50000
                )
                return _app_game
            except Exception as e:
                if isinstance(e, PlaywrightTimeoutError):
                    SendEventToGUI.log.debug("get app game :: timeout")
                    continue
                SendEventToGUI.exception(
                    {
                        "location": "AviatorPage",
                        "message": f"_getAppGame :: {e}",
                    }
                )
                raise e

    async def open(self):
        self.playwright = await async_playwright().start()
        # to lunch the browser maximized add args=["--start-maximized"]
        self._browser = await self.playwright.chromium.launch(headless=False)
        self._context = await self._browser.new_context(no_viewport=True)
        self._page = await self._context.new_page()
        await self._page.goto(self.url, timeout=100000)
        await self._login()
        self._app_game = await self._get_app_game()
        self._history_game = self._app_game.locator(".result-history")
        SendEventToGUI.log.debug("Result history found")
        await self.read_balance()
        await self.read_multipliers()
        await self.read_currency()
        # await self.read_game_limits()
        self._controls = BetControl(self._app_game)
        await self._controls.init()
        SendEventToGUI.log.success(_("Aviator loaded"))  # noqa

    async def close(self):
        if not self._page:
            return
        await self._page.close()
        await self._browser.close()
        # TODO: implement close session of home bet

    async def read_game_limits(self):
        if self._app_game is None or self._page is None:
            SendEventToGUI.exception(
                {
                    "location": "AviatorPage",
                    "message": "readGameLimits :: _appGame or _page is null",
                }
            )
            raise Exception("readGameLimits :: _appGame is null")
        menu = self._app_game.locator(".dropdown-toggle.user")
        if menu is None:
            SendEventToGUI.exception(
                {
                    "location": "AviatorPage",
                    "message": "readGameLimits :: menu is null",
                }
            )
            raise Exception("readGameLimits :: menu is null")
        await menu.click()
        await self._page.wait_for_timeout(400)
        app_user_menu = self._app_game.locator("app-settings-menu")
        if app_user_menu is None:
            SendEventToGUI.exception(
                {
                    "location": "AviatorPage",
                    "message": "readGameLimits :: appusermenu is null",
                }
            )
            raise Exception("readGameLimits :: appusermenu is null")
        list_menu = app_user_menu.locator(".list-menu").last
        menu_limits = list_menu.locator(".list-menu-item").last
        await menu_limits.click()
        await self._page.wait_for_timeout(400)
        limits = await self._page.locator("app-game-limits ul>li>span").all()
        self.minimum_bet = float(
            (await limits[0].text_content()).split(" ")[0] or "0"
        )
        self.maximum_bet = float(
            (await limits[1].text_content()).split(" ")[0] or "0"
        )
        self.maximum_win_for_one_bet = float(
            (await limits[2].text_content()).split(" ")[0] or "0"
        )
        button_close = self._page.locator("ngb-modal-window")
        await button_close.click()
        SendEventToGUI.log.debug(f"minimumBet: {self.minimum_bet}")
        SendEventToGUI.log.debug(f"maximumBet: {self.maximum_bet}")
        SendEventToGUI.log.debug(
            f"maximumWinForOneBet: {self.maximum_win_for_one_bet}"
        )

    async def read_balance(self) -> Union[float, None]:
        if self._app_game is None:
            SendEventToGUI.exception(
                {
                    "location": "AviatorPage",
                    "message": "readBalance :: _appGame is null",
                }
            )
            raise Exception("readBalance :: _appGame is null")
        self._balance_element = self._app_game.locator(".balance>div>.amount")
        if self._balance_element is None:
            SendEventToGUI.exception(
                {
                    "location": "AviatorPage",
                    "message": "readBalance :: balance element is null",
                }
            )
            raise Exception("balance element is null")
        self.balance = float(await self._balance_element.text_content() or "0")
        return self.balance

    async def read_currency(self) -> str:
        if self._app_game is None:
            SendEventToGUI.exception(
                {
                    "location": "AviatorPage",
                    "message": "read_currency :: _appGame is null",
                }
            )
            raise Exception("read_currency :: _appGame is null")
        self._currency_element = self._app_game.locator(
            ".balance>div>.currency"
        )
        if self._currency_element is None:
            SendEventToGUI.exception(
                {
                    "location": "AviatorPage",
                    "message": "read_currency :: balance element is null",
                }
            )
            raise Exception("currency element is null")
        self.currency = (
            await self._currency_element.text_content() or self.currency
        )
        return self.currency

    async def read_multipliers(self):
        if not self._page or not self._history_game:
            SendEventToGUI.exception(
                {
                    "location": "AviatorPage",
                    "message": "readMultipliers :: the page or "
                    "the history game not exists",
                }
            )
            raise Exception(
                "readMultipliers :: the page or the history game not exists"
            )
        items = await self._history_game.locator(
            "app-bubble-multiplier.payout.ng-star-inserted"
        ).all()
        items.reverse()
        for item in items:
            multiplier = await item.text_content()
            if multiplier is not None:
                self.multipliers.append(self._format_multiplier(multiplier))
        await self._page.wait_for_timeout(2000)

    async def bet(
        self, *, bets: list[Bet], use_auto_cash_out: Optional[bool] = True
    ):
        if self._controls is None:
            SendEventToGUI.exception(
                {
                    "location": "AviatorPage",
                    "message": "AviatorPage :: no _controls",
                }
            )
            raise Exception("AviatorPage :: no _controls")
        manual_cash_out_tasks = []
        for i, bet in enumerate(bets):
            if len(bets) > 1:
                control = Control.Control1 if i == 0 else Control.Control2
            else:
                index_ = random.randint(1, 2)
                control = Control.Control1 if index_ == 1 else Control.Control2
            SendEventToGUI.log.info(
                f"{_('Sending bet to aviator')} ${format_amount_to_display(bet.amount)} * "  # noqa
                f"{bet.multiplier} control: {control.value}"
            )
            await self._controls.bet(
                amount=bet.amount,
                multiplier=bet.multiplier,
                control=control,
                use_auto_cash_out=use_auto_cash_out,
            )
            sleep_now(0.5)
            if not use_auto_cash_out:
                manual_cash_out_tasks.append(
                    self._controls.wait_manual_cash_out(
                        amount=bet.amount,
                        multiplier=bet.multiplier,
                        control=control,
                    )
                )
        if manual_cash_out_tasks:
            await asyncio.gather(*manual_cash_out_tasks)
            SendEventToGUI.log.debug("Finished manual cash out tasks")

    async def wait_next_game(self):
        if self._history_game is None:
            SendEventToGUI.exception(
                {
                    "location": "AviatorPage",
                    "message": "waitNextGame :: no historyGame",
                }
            )
            raise Exception("waitNextGame :: no historyGame")
        last_multiplier_saved = self.multipliers[-1]
        while True:
            try:
                await self._history_game.locator(
                    "app-bubble-multiplier"
                ).first.wait_for(timeout=5000)
                locator = self._history_game.locator(
                    "app-bubble-multiplier",
                ).first
                last_multiplier_content = await locator.text_content(
                    timeout=1000
                )
                last_multiplier = (
                    self._format_multiplier(last_multiplier_content)
                    if last_multiplier_content
                    else last_multiplier_saved
                )
                if last_multiplier_saved != last_multiplier:
                    self.multipliers.append(last_multiplier)
                    SendEventToGUI.log.success(
                        f"{_('Last Multiplier')}: {last_multiplier}"  # noqa
                    )
                    self.multipliers = self.multipliers[1:]
                    return
                sleep_now(0.2)
            except Exception as e:
                if isinstance(e, PlaywrightTimeoutError):
                    SendEventToGUI.log.debug("wait_next_game :: timeout")
                    continue
                SendEventToGUI.exception(
                    {
                        "location": "AviatorPage",
                        "message": f"wait_next_game :: {e}",
                    }
                )
                raise e
