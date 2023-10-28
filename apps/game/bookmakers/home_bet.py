# Internal
from apps.api.models import HomeBetModel
from apps.scrappers.aviator.aviator_base import AviatorBase


class HomeBet(HomeBetModel):
    def get_crash_game(self) -> AviatorBase:
        return AviatorBase(
            configuration=self.id,
            url=self.url,
        )
