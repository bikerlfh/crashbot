# Libraries
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

# Internal
from apps.game.bookmakers.constants import BookmakerIDS
from apps.gui.gui_events import SendEventToGUI
from apps.scrappers.aviator.aviator_base import AviatorBase


class AviatorECUABET(AviatorBase, configuration=BookmakerIDS.ECUABET.value):
    def __init__(self, *, url: str, **kwargs):
        super().__init__(url=url, **kwargs)
        self._frame = None

    async def _login(self):
        if not self._page:
            raise Exception("_login :: page is null")
        SendEventToGUI.log.warning(
            _("please set username and password to login!")  # noqa
        )

    async def _get_app_game(self):
        if not self._page:
            raise Exception("_getAppGame :: page is null")
        while True:
            try:
                await self._page.wait_for_selector(
                    "[src*='https://casino.virtualsoft.tech']", timeout=50000
                )
                await self._page.wait_for_timeout(2000)
                frame_1 = self._page.frame_locator(
                    "[src*='https://casino.virtualsoft.tech']"
                ).first
                self._frame = frame_1.frame_locator(
                    "[src*='spribegaming.com']"
                ).first
                self._app_game = self._frame.locator("app-game").first
                await self._app_game.locator(".result-history").wait_for(
                    timeout=5000
                )
                return self._app_game
            except Exception as e:
                if isinstance(e, PlaywrightTimeoutError):
                    continue
                raise e

    async def read_game_limits(self):
        if self._frame is None:
            raise Exception("readGameLimits :: _frame is null")

        if self._app_game is None or self._page is None:
            raise Exception("readGameLimits :: _appGame is null")

        menu = self._app_game.locator(".dropdown-toggle.user")
        if menu is None:
            raise Exception("readGameLimits :: menu is null")

        await menu.click()
        await self._page.wait_for_timeout(400)

        app_user_menu = self._app_game.locator("app-settings-menu")
        if app_user_menu is None:
            raise Exception("readGameLimits :: appusermenu is null")

        list_menu = app_user_menu.locator(".list-menu").last
        menu_limits = list_menu.locator(".list-menu-item").last
        await menu_limits.click()
        await self._page.wait_for_timeout(400)

        limits = await self._frame.locator("app-game-limits ul>li>span").all()
        self.minimum_bet = float(
            (await limits[0].text_content() or "0").split(" ")[0]
        )
        self.maximum_bet = float(
            (await limits[1].text_content() or "0").split(" ")[0]
        )
        self.maximum_win_for_one_bet = float(
            (await limits[2].text_content() or "0").split(" ")[0]
        )

        button_close = self._frame.locator("ngb-modal-window")
        await button_close.click()
