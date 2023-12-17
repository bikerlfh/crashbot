# Libraries
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

# Internal
from apps.game.bookmakers.constants import BookmakerIDS
from apps.globals import GlobalVars
from apps.gui.gui_events import SendEventToGUI
from apps.scrappers.to_the_moon.to_the_moon_base import ToTheMoonBase
from apps.utils.datetime import sleep_now


class ToTheMoonOneWin(ToTheMoonBase, configuration=BookmakerIDS.ONE_WIN.value):
    def __init__(self, *, url: str, **kwargs):
        super().__init__(url=url, **kwargs)
        # self._frame = None

    async def _login(self):
        if not self._page:
            raise Exception("_login :: page is null")

        page_login_button = self._page.locator("button.login")
        await self._click(page_login_button)
        sleep_now(1)

        username = GlobalVars.get_username()
        password = GlobalVars.get_password()

        if not username or not password:
            SendEventToGUI.log.warning(
                _("please set username and password to login!")  # noqa
            )
            return

        user_name_input = self._page.locator("input[name='login']")
        password_input = self._page.locator("input[name='password']")

        await user_name_input.type(username, delay=100)
        await password_input.type(password, delay=100)
        await self._page.wait_for_timeout(1000)

        login_button_2 = self._page.locator(
            "button.modal-button[type='submit']"
        )
        await self._click(login_button_2)
        await self._page.wait_for_timeout(2000)

    async def _get_app_game(self):
        if not self._page:
            raise Exception("_getAppGame :: page is null")
        while True:
            try:
                await self._page.wait_for_selector(
                    "#infingames-iframe", timeout=50000
                )

                SendEventToGUI.log.info("loading game. please wait...")
                await self._page.wait_for_timeout(30000)
                SendEventToGUI.log.debug("searching for the frame of the game")
                frame_1 = self._page.frame_locator(
                    "[src*='https://modelplat.com/gm/"
                    "index.html?gameName=ag_to_the_moon']"
                ).first
                frame_2 = frame_1.frame_locator(
                    "[src*='https://api-prod.infingame.com/ag-launch/"
                    "1win/prod?gameName=ag_to_the_moon']"
                ).first
                self._frame = frame_2.frame_locator(
                    "[src*='https://api-prod.infingame.com/ag-launch/"
                    "1win/prod?gameName=ag_to_the_moon']"
                ).first
                self._app_game = self._frame.locator("main").first
                await self._app_game.locator(
                    ".content-top__history>#rate_history"
                ).wait_for(timeout=5000)
                return self._app_game
            except Exception as e:
                if isinstance(e, PlaywrightTimeoutError):
                    continue
                raise e
