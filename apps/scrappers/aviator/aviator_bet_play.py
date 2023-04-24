from apps.scrappers.aviator.aviator import Aviator


class AviatorBetPlay(Aviator):
    def __init__(self, url: str):
        super().__init__(url)
        self._frame = None

    def _login(self):
        if not self._page:
            raise Exception("_login :: page is null")

        username = globals().get('username')
        password = globals().get('password')

        if username and password:
            username_input = self._page.locator("input#userName")
            password_input = self._page.locator("input#password")
            login_button = self._page.locator("button#btnLoginPrimary")

            username_input.type(username, delay=100)
            password_input.type(password, delay=100)
            self._click(login_button)
        else:
            print("Please set username and password to login!")

        self._page.locator("#spanUser").wait_for(timeout=50000)
        search_button = self._page.locator("input.inputSearch")
        self._page.wait_for_timeout(1000)
        search_button.type("aviator", delay=150)
        self._page.wait_for_timeout(2000)
        # TODO fix this
        # self._click(self._page.locator("button.btnSlot"))

    def _get_app_game(self):
        if not self._page:
            raise Exception("_getAppGame :: page is null")

        self._page.wait_for_url("**/slots/launchGame?gameCode=SPB_aviator**", timeout=50000)

        while True:
            try:
                self._frame = self._page.frame_locator("#gameFrame").frame_locator("#spribe-game")
                self._app_game = self._frame.locator("app-game").first
                self._app_game.locator(".result-history").wait_for(timeout=5000)
                return self._app_game
            except Exception as e:
                if isinstance(e, TimeoutError):
                    print("page :: error timeout")
                    continue
                raise e

    def read_game_limits(self):
        if self._frame is None:
            raise Exception("readGameLimits :: _frame is null")

        if self._app_game is None or self._page is None:
            raise Exception("readGameLimits :: _appGame is null")

        menu = self._app_game.locator(".dropdown-toggle.user")

        if menu is None:
            raise Exception("readGameLimits :: menu is null")

        menu.click()
        self._page.wait_for_timeout(400)

        app_user_menu = self._app_game.locator("app-settings-menu")

        if app_user_menu is None:
            raise Exception("readGameLimits :: appusermenu is null")

        list_menu = app_user_menu.locator(".list-menu").last
        menu_limits = list_menu.locator(".list-menu-item").last

        menu_limits.click()
        self._page.wait_for_timeout(400)

        limits = self._frame.locator("app-game-limits ul>li>span").all()
        self.minimum_bet = float((limits[0].text_content()).split(" ")[0] or "0")
        self.maximum_bet = float((limits[1].text_content()).split(" ")[0] or "0")
        self.maximum_win_for_one_bet = float((limits[2].text_content()).split(" ")[0] or "0")

        button_close = self._frame.locator("ngb-modal-window")
        button_close.click()

