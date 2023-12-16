# Libraries
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

# Internal
from apps.game.bookmakers.constants import BookmakerIDS
from apps.scrappers.to_the_moon.to_the_moon_base import ToTheMoonBase
from apps.utils.datetime import sleep_now


class ToTheMoonOneWinDemo(
    ToTheMoonBase, configuration=BookmakerIDS.DEMO_TO_THE_MOON.value
):
    def __init__(self, *, url: str, **kwargs):
        super().__init__(url=url, **kwargs)

    async def _get_app_game(self):
        if not self._page:
            raise Exception("_getAppGame :: page is null")
        while True:
            try:
                # await self._page.wait_for_url(self.url, timeout=50000)
                sleep_now(10)
                self._app_game = self._page.locator("main").first
                await self._app_game.locator(
                    ".content-top__history>#rate_history"
                ).wait_for(timeout=5000)
                self._frame = self._page
                return self._app_game
            except Exception as e:
                if isinstance(e, PlaywrightTimeoutError):
                    continue
                raise e
