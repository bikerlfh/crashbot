# Internal
from apps.scrappers.aviator.aviator_base import AviatorBase


class HomeBet:
    def __init__(
        self,
        *,
        id: int,
        name: int,
        min_bet: float,
        max_bet: float,
        url: str,
        amount_multiple: float,
    ):
        self.id = id
        self.name = name
        self.min_bet = min_bet
        self.max_bet = max_bet
        self.url = url
        self.amount_multiple = amount_multiple

    def get_crash_game(self) -> AviatorBase:
        return AviatorBase(
            configuration=self.id,
            url=self.url,
        )
