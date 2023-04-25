import abc
from typing import Union
from enum import Enum
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page, Locator


class Control(Enum):
    Control1 = 1
    Control2 = 2


class AbstractControlBase(abc.ABC):
    @abc.abstractmethod
    def init(self):
        ...

    @abc.abstractmethod
    def set_auto_cash_out(self, multiplier, control):
        ...

    @abc.abstractmethod
    def update_amount(self, amount, control):
        ...

    @abc.abstractmethod
    def bet(self, amount, multiplier, control):
        ...


class AbstractGameBase(abc.ABC):
    def __init__(self, url: str):
        self.playwright: Union[sync_playwright, None] = None
        self._browser: Union[Browser, None] = None
        self._context: Union[BrowserContext, None] = None
        self._page: Union[Page, None] = None
        self._app_game: Union[Locator, None] = None
        self._history_game: Union[Locator, None] = None
        self._balance_element: Union[Locator, None] = None
        self._controls: Union[AbstractControlBase, None] = None
        self.minimum_bet: int = 0
        self.maximum_bet: int = 0
        self.maximum_win_for_one_bet: int = 0
        self.url: str = url
        self.multipliers: list[float] = []
        self.balance: int = 0

    @abc.abstractmethod
    def _click(self, element: any):
        ...

    @abc.abstractmethod
    def _login(self):
        ...

    @abc.abstractmethod
    def open(self):
        ...

    @abc.abstractmethod
    def close(self):
        ...

    @abc.abstractmethod
    def read_game_limits(self):
        ...

    @abc.abstractmethod
    def read_balance(self) -> float:
        ...

    @abc.abstractmethod
    def read_multipliers(self):
        ...

    @abc.abstractmethod
    def bet(self, amount: float, multiplier: float, control: Control):
        ...

    @abc.abstractmethod
    def wait_next_game(self):
        ...
