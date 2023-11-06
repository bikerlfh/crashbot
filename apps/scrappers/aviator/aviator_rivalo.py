# Libraries
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

# Internal
from apps.game.bookmakers.constants import BookmakerIDS
from apps.globals import GlobalVars
from apps.gui.gui_events import SendEventToGUI
from apps.scrappers.aviator.aviator_base import AviatorBase
from apps.utils.datetime import sleep_now


class AviatorRivalo(  # noqa
    AviatorBase, configuration=BookmakerIDS.RIVALO.value
):
    def __init__(self, *, url: str, **kwargs):
        super().__init__(url=url, **kwargs)
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
        page_login_button = self._page.locator("a[href='/login']")
        await self._click(page_login_button)
        sleep_now(3)
        username = GlobalVars.get_username()
        password = GlobalVars.get_password()
        if not username or not password:
            SendEventToGUI.log.success(
                _("Please set username and password to login!")  # noqa
            )
            return
        username_input = self._page.locator("input#email")
        password_input = self._page.locator("input#password")
        login_button = self._page.locator(
            "div[data-test-id='login-submit-button']>button"
        )

        await username_input.type(username, delay=100)
        await password_input.type(password, delay=100)
        await self._click(login_button)
        sleep_now(3)

    async def _get_app_game(self):
        if not self._page:
            raise Exception("_getAppGame :: page is null")
        while True:
            try:
                await self._page.wait_for_selector(
                    "#IframeContainer", timeout=50000
                )
                await self._page.wait_for_timeout(2000)
                frame_1 = self._page.frame_locator(
                    "[src*='https://gamelaunch.everymatrix.com/Loader/"
                    "Start/2363/aviator-spribe']"
                ).first
                self._frame = frame_1.frame_locator(
                    "[src*='spribegaming.com']"
                ).first
                self._app_game = self._frame.locator("app-game").first
                await self._app_game.wait_for(timeout=5000)
                await self._app_game.locator(".result-history").wait_for(
                    timeout=5000
                )
                return self._app_game
            except Exception as e:
                if isinstance(e, PlaywrightTimeoutError):
                    continue
                raise e
