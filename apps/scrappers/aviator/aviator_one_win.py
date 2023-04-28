# Internal
from apps.scrappers.aviator.aviator import Aviator
from apps.utils.datetime import sleep_now
from apps.gui.gui_events import SendEventToGUI


class AviatorOneWin(Aviator):
    def __init__(self, url: str):
        super().__init__(url)
        self._frame = None

    async def _login(self):
        if not self._page:
            raise Exception("_login :: page is null")

        page_login_button = self._page.locator("button.login")
        await self._click(page_login_button)
        sleep_now(1)

        username = globals().get("username")
        password = globals().get("password")

        if not username or not password:
            SendEventToGUI.log.warning(
                "please set username and password to login!"
            )
            return

        user_name_input = self._page.locator("input[name='login']")
        password_input = self._page.locator("input[name='password']")

        user_name_input.type(username, delay=100)
        password_input.type(password, delay=100)
        self._page.wait_for_timeout(1000)

        login_button_2 = self._page.locator(
            "button.modal-button[type='submit']"
        )
        await self._click(login_button_2)
        await self._page.wait_for_timeout(2000)

    async def _get_app_game(self):
        if not self._page:
            raise Exception("_getAppGame :: page is null")

        await self._page.wait_for_url(
            "**/casino/play/spribe_aviator**", timeout=50000
        )

        while True:
            try:
                self._frame = self._page.locator(
                    ".CasinoGamePromoted_game_vXIG_"
                ).frame_locator("[src^=https]")
                self._app_game = self._frame.locator("app-game").first
                await self._app_game.locator(".result-history").wait_for(
                    timeout=5000
                )
                return self._app_game
            except Exception as e:
                if isinstance(e, TimeoutError):
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
