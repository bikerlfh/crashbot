# Internal
from apps.api.models import HomeBetModel
from apps.game.bookmakers.constants import BookmakerIDS
from apps.scrappers.aviator.aviator_base import AviatorBase
from apps.scrappers.constants import CrashGame
from apps.scrappers.game_base import AbstractCrashGameBase
from apps.scrappers.to_the_moon.to_the_moon_base import ToTheMoonBase


class HomeBet(HomeBetModel):
    def get_crash_game(
        self, *, crash_game: CrashGame
    ) -> AbstractCrashGameBase:
        id_ = self.id
        if id_ not in BookmakerIDS.values():
            id_ = BookmakerIDS.DEFAULT.value
        match crash_game:
            case CrashGame.AVIATOR:
                return AviatorBase(
                    configuration=id_,
                    url=self.url,
                )
            case CrashGame.TO_THE_MOON:
                return ToTheMoonBase(
                    configuration=id_,
                    url=self.url,
                )
