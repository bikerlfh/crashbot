# Internal
from apps.api.models import HomeBetModel
from apps.game.bookmakers.constants import BookmakerIDS
from apps.scrappers.aviator.aviator_base import AviatorBase


class HomeBet(HomeBetModel):
    def get_crash_game(self) -> AviatorBase:
        id_ = self.id
        if id_ not in BookmakerIDS.values():
            id_ = BookmakerIDS.DEFAULT.value
        return AviatorBase(
            configuration=id_,
            url=self.url,
        )
