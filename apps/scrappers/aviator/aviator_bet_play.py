# Internal
from apps.globals import GlobalVars
from apps.gui.gui_events import SendEventToGUI
from apps.scrappers.aviator.aviator import Aviator


class AviatorBetPlay(Aviator):
    def __init__(self, url: str):
        super().__init__(url)
        self._frame = None

    async def _login(self):
        if not self._page:
            SendEventToGUI.exception(
                dict(
                    location="AviatorBetPlay._login",
                    message="page is null",
                )
            )
            return
        username = GlobalVars.get_username()
        password = GlobalVars.get_password()
        if not username or not password:
            SendEventToGUI.log.success(_("Please set username and password to login!")) # noqa
            return
        username_input = self._page.locator("input#userName")
        password_input = self._page.locator("input#password")
        login_button = self._page.locator("button#btnLoginPrimary")

        await username_input.type(username, delay=100)
        await password_input.type(password, delay=100)
        await self._click(login_button)
        await self._page.locator("#spanUser").wait_for(timeout=50000)
        search_button = self._page.locator("input.inputSearch")
        await self._page.wait_for_timeout(1000)
        await search_button.type("aviator", delay=150)
        await self._page.wait_for_timeout(2000)
        # TODO fix this
        # await self._page.locator("button.btnSlot").wait_for(timeout=5000)
        # await self._click(self._page.locator("button.btnSlot").first)

    async def _get_app_game(self):
        if not self._page:
            raise Exception("_getAppGame :: page is null")

        await self._page.wait_for_url(
            "**/slots/launchGame?gameCode=SPB_aviator**", timeout=50000
        )
        while True:
            try:
                self._frame = (
                    self._page.frame_locator("#gameFrame")
                    .frame_locator("#spribe-game")
                    .first
                )
                self._app_game = self._frame.locator("app-game").first
                await self._app_game.locator(".result-history").wait_for(timeout=5000)
                return self._app_game
            except Exception as e:
                if isinstance(e, TimeoutError):
                    SendEventToGUI.log.debug("_get_app_game :: timeout")
                    continue
                SendEventToGUI.log.debug(f"_get_app_game :: exception :: {str(e)}")
                # raise e

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
        self.minimum_bet = float((await limits[0].text_content()).split(" ")[0] or "0")
        self.maximum_bet = float((await limits[1].text_content()).split(" ")[0] or "0")
        self.maximum_win_for_one_bet = float(
            (await limits[2].text_content()).split(" ")[0] or "0"
        )

        button_close = self._frame.locator("ngb-modal-window")
        await button_close.click()
