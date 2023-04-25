from typing import Optional
from enum import Enum
from dataclasses import dataclass
from apps.scrappers.game_base import AbstractGameBase
from apps.scrappers.aviator.aviator_demo import AviatorDemo
from apps.scrappers.aviator.aviator_bet_play import AviatorBetPlay
from apps.scrappers.aviator.aviator_one_win import AviatorOneWin


class WSEvent(str, Enum):
    VERIFY = "verify"
    LOGIN = "login"
    START_BOT = "startBot"
    AUTO_PLAY = "autoPlay"
    CLOSE_GAME = "closeGame"
    SET_MAX_AMOUNT_TO_BET = "setMaxAmountToBet"
    # events from server
    LOG = "log"
    UPDATE_BALANCE = "update_balance"
    ERROR = "error"
    EXCEPTION = "exception"


@dataclass
class HomeBet:
    id: int
    name: str
    min_bet: float
    max_bet: float
    url: str
    game_page: AbstractGameBase.__class__
    amount_multiple: Optional[float] = None

    def get_game_page(self) -> AbstractGameBase:
        return self.game_page(self.url)


HomeBets: list[HomeBet] = [
    HomeBet(
        id=1,
        name="demo",
        min_bet=1,
        max_bet=100,
        url="https://www.spribe.co/games/aviator",
        game_page=AviatorDemo,
    ),
    HomeBet(
        id=2,
        name="Bet Play",
        min_bet=100,
        max_bet=50000,
        url="https://betplay.com.co/slots",
        game_page=AviatorBetPlay,
    ),
    HomeBet(
        id=3,
        name="One Win",
        min_bet=500,
        max_bet=500000,
        url="https://www.spribe.co/games/aviator",
        game_page=AviatorOneWin,
    ),
    HomeBet(
        id=4,
        name="Rivalo",
        min_bet=500,
        max_bet=500000,
        url="https://www.rivalo.co",
        game_page=AviatorOneWin,
    ),
]


class BotType(Enum):
    AGGRESSIVE = "aggressive"
    TIGHT = "tight"
    LOOSE = "loose"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

    @classmethod
    def to_list(cls):
        return [key.value for key in cls]
