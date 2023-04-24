from typing import Optional
from dataclasses import dataclass
from apps.scrappers.aviator.aviator import Aviator
from apps.scrappers.aviator.aviator_demo import AviatorDemo
from apps.scrappers.aviator.aviator_bet_play import AviatorBetPlay
from apps.scrappers.aviator.aviator_one_win import AviatorOneWin


@dataclass
class HomeBet:
    id: int
    min_bet: float
    max_bet: float
    url: str
    aviator_page: Aviator.__class__
    amount_multiple: Optional[float] = None


HomeBets: list[HomeBet] = [
    HomeBet(
        id=1,
        min_bet=0.1,
        max_bet=100,
        url="https://www.spribe.co/games/aviator",
        aviator_page=AviatorDemo,
    ),
    HomeBet(
        id=2,
        min_bet=100,
        max_bet=50000,
        url= "https://betplay.com.co/slots",
        aviator_page=AviatorBetPlay,
    ),
    HomeBet(
        id=3,
        min_bet=500,
        max_bet=500000,
        url= "https://www.spribe.co/games/aviator",
        aviator_page=AviatorOneWin,
    )
]