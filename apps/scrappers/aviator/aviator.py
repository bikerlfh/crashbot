import abc
from typing import List, Union
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page, Locator
from apps.scrappers.aviator.bet_control import BetControl
from apps.scrappers.game_base import AbstractGameBase, Control
from apps.utils.datetime import sleep_now

# from ws.gui_events import send_event_to_gui


class Aviator(AbstractGameBase, abc.ABC):
    def __init__(self, url: str):
        self.playwright: Union[sync_playwright, None] = None
        self._browser: Union[Browser, None] = None
        self._context: Union[BrowserContext, None] = None
        self._page: Union[Page, None] = None
        self._app_game: Union[Locator, None] = None
        self._history_game: Union[Locator, None] = None
        self._balance_element: Union[Locator, None] = None
        self._controls: Union[BetControl, None] = None
        self.minimum_bet: int = 0
        self.maximum_bet: int = 0
        self.maximum_win_for_one_bet: int = 0
        self.url: str = url
        self.multipliers: List[float] = []
        self.balance: int = 0

    def _click(self, element: Locator):
        box = element.bounding_box()
        if not box or not self._page:
            # send_event_to_gui.log.error("page :: box or page does't exists")
            return
        self._page.mouse.move(
            box["x"] + box["width"] / 2, box["y"] + box["height"] / 2, steps=50
        )
        self._page.mouse.click(
            box["x"] + box["width"] / 2, box["y"] + box["height"] / 2, delay=50
        )

    def _get_app_game(self) -> Locator:
        if not self._page:
            """send_event_to_gui.exception({
                "location": "AviatorPage",
                "message": "_getAppGame :: page is null"
            })"""
            print("_getAppGame :: page is null")
            raise Exception("_getAppGame :: page is null")

        _app_game = None
        while True:
            try:
                self._page.locator("app-game").first.wait_for(timeout=50000)
                _app_game = self._page.locator("app-game").first
                _app_game.locator(".result-history").wait_for(timeout=50000)
                return _app_game
            except Exception as e:
                if isinstance(e, TimeoutError):
                    print("page :: error timeout")
                    # send_event_to_gui.log.debug("page :: error timeout")
                    continue
                """send_event_to_gui.exception({
                    "location": "AviatorPage",
                    "message": f"_getAppGame :: {e}"
                })"""
                print(f"_getAppGame :: {e}")
                raise e

    def open(self):
        self.playwright = sync_playwright().start()
        self._browser = self.playwright.chromium.launch(headless=False)
        self._context = self._browser.new_context()
        self._page = self._context.new_page()
        self._page.goto(self.url, timeout=50000)
        self._login()
        self._app_game = self._get_app_game()
        self._history_game = self._app_game.locator(".result-history")
        # send_event_to_gui.log.debug("Result history found")
        self.read_balance()
        self.read_multipliers()
        # await self.read_game_limits()
        self._controls = BetControl(self._app_game)
        self._controls.init()
        print("Aviator loaded")
        print("balance :: ", self.balance)
        print("multipliers :: ", self.multipliers)
        # send_event_to_gui.log.success("Aviator loaded")

    def close(self):
        if not self._page:
            return
        self._page.close()
        self._browser.close()
        # TODO: implment close session of home bet

    def read_game_limits(self):
        if self._app_game is None or self._page is None:
            # send_event_to_gui.exception({
            #     "location": "AviatorPage",
            #     "message": "readGameLimits :: _appGame or _page is null"
            # })
            raise Exception("readGameLimits :: _appGame is null")
        menu = self._app_game.locator(".dropdown-toggle.user")
        if menu is None:
            # send_event_to_gui.exception({
            #     "location": "AviatorPage",
            #     "message": "readGameLimits :: menu is null"
            # })
            raise Exception("readGameLimits :: menu is null")
        menu.click()
        self._page.wait_for_timeout(400)
        app_user_menu = self._app_game.locator("app-settings-menu")
        if app_user_menu is None:
            # send_event_to_gui.exception({
            #     "location": "AviatorPage",
            #     "message": "readGameLimits :: appusermenu is null"
            # })
            raise Exception("readGameLimits :: appusermenu is null")
        list_menu = app_user_menu.locator(".list-menu").last
        menu_limits = list_menu.locator(".list-menu-item").last
        menu_limits.click()
        self._page.wait_for_timeout(400)
        limits = self._page.locator("app-game-limits ul>li>span").all()
        self.minimum_bet = float((limits[0].text_content()).split(" ")[0] or "0")
        self.maximum_bet = float((limits[1].text_content()).split(" ")[0] or "0")
        self.maximum_win_for_one_bet = float(
            (limits[2].text_content()).split(" ")[0] or "0"
        )
        button_close = self._page.locator("ngb-modal-window")
        button_close.click()
        # send_event_to_gui.log.debug(f"minimumBet: {self.minimum_bet}")
        # send_event_to_gui.log.debug(f"maximumBet: {self.maximum_bet}")
        # send_event_to_gui.log.debug(f"maximumWinForOneBet: {self.maximum_win_for_one_bet}")

    def read_balance(self) -> Union[float, None]:
        if self._app_game is None:
            # send_event_to_gui.exception({
            #     "location": "AviatorPage",
            #     "message": "readBalance :: _appGame is null"
            # })
            raise Exception("readBalance :: _appGame is null")
        self._balance_element = self._app_game.locator(".balance>div>.amount")
        if self._balance_element is None:
            # send_event_to_gui.exception({
            #     "location": "AviatorPage",
            #     "message": "readBalance :: balance element is null"
            # })
            raise Exception("balance element is null")
        self.balance = float(self._balance_element.text_content() or "0")
        return self.balance

    def _format_multiplier(self, multiplier: str) -> float:
        return float(multiplier.replace(r"/\s / g", "").replace("x", ""))

    def read_multipliers(self):
        if not self._page or not self._history_game:
            # send_event_to_gui.exception({
            #     "location": "AviatorPage",
            #     "message": "readMultipliers :: the page or the history game not exists"
            # })
            raise Exception(
                "readMultipliers :: the page or the history game not exists"
            )
        items = self._history_game.locator(
            "app-bubble-multiplier.payout.ng-star-inserted"
        ).all()
        items.reverse()
        for item in items:
            multiplier = item.text_content()
            if multiplier is not None:
                self.multipliers.append(self._format_multiplier(multiplier))
        self._page.wait_for_timeout(2000)

    def bet(self, amount: float, multiplier: float, control: Control):
        if self._controls is None:
            # send_event_to_gui.exception({
            #     "location": "AviatorPage",
            #     "message": "AviatorPage :: no _controls"
            # })
            raise Exception("AviatorPage :: no _controls")
        self._controls.bet(amount, multiplier, control)

    def wait_next_game(self):
        if self._history_game is None:
            # send_event_to_gui.exception({
            #    "location": "AviatorPage",
            #    "message": "waitNextGame :: no historyGame"
            # })
            raise Exception("waitNextGame :: no historyGame")
        last_multiplier_saved = self.multipliers[-1]
        self._history_game.locator("app-bubble-multiplier").first.wait_for(timeout=1000)
        while True:
            locator = self._history_game.locator("app-bubble-multiplier").first
            last_multiplier_content = locator.text_content(timeout=1000)
            last_multiplier = (
                self._format_multiplier(last_multiplier_content)
                if last_multiplier_content
                else last_multiplier_saved
            )
            if last_multiplier_saved != last_multiplier:
                self.multipliers.append(last_multiplier)
                # send_event_to_gui.log.success(f"New Multiplier: {last_multiplier}")
                self.multipliers = self.multipliers[1:]
                return
            sleep_now(200)
