from apps.scrappers.aviator.aviator import Aviator


class AviatorDemo(Aviator):
    def __init__(self, url: str):
        super().__init__(url)
        self._frame = None

    def _login(self):
        if not self._page or not self._context:
            raise Exception("_login :: page or context are null")

        self._page.get_by_role("button", name="Play Demo").click()
        self._page.get_by_role("button", name="Yes I’m over 18").click()
        self._page.wait_for_timeout(2000)
        pages = self._context.pages
        self._page = pages[1]
