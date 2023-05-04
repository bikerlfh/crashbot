# Standard Library
import abc
import random
from enum import Enum
from typing import Union

# Libraries
from playwright.sync_api import (
    Browser,
    BrowserContext,
    Locator,
    Page,
    sync_playwright,
)

# Internal
from apps.game.models import Bet


class Control(Enum):
    Control1 = 1
    Control2 = 2


class AbstractControlBase(abc.ABC):
    @staticmethod
    def _random_delay() -> int:
        return random.randint(15, 50)

    @abc.abstractmethod
    async def init(self):
        ...

    @abc.abstractmethod
    async def set_auto_cash_out(self, multiplier, control):
        ...

    @abc.abstractmethod
    async def update_amount(self, amount, control):
        ...

    @abc.abstractmethod
    async def bet(self, amount, multiplier, control):
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

    @staticmethod
    def _format_multiplier(multiplier: str) -> float:
        return float(multiplier.replace(r"/\s / g", "").replace("x", ""))

    @abc.abstractmethod
    async def _click(self, element: any):
        ...

    @abc.abstractmethod
    async def _login(self):
        ...

    @abc.abstractmethod
    async def open(self):
        ...

    @abc.abstractmethod
    async def close(self):
        ...

    @abc.abstractmethod
    async def read_game_limits(self):
        ...

    @abc.abstractmethod
    async def read_balance(self) -> float:
        ...

    @abc.abstractmethod
    async def read_multipliers(self):
        ...

    @abc.abstractmethod
    async def bet(self, bets: list[Bet]):
        ...

    @abc.abstractmethod
    async def wait_next_game(self):
        ...
