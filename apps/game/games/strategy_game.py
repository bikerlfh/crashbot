from apps.game.models import Bet
from apps.utils.local_storage import LocalStorage

from apps.game.games.base_game import BaseGame
from apps.game.bots.bot_strategy import StrategyBot
from apps.globals import GlobalVars
from apps.gui.gui_events import SendEventToGUI
from apps.constants import BotType
from apps.game.games.constants import GameType

local_storage = LocalStorage()


class StrategyGame(BaseGame, configuration=GameType.STRATEGY.value):
    bot: StrategyBot
    """
    This game no uses the AI. Only use strategy to bet.
    """

    def _initialize_bot(self, *, bot_type: BotType):
        self.bot = StrategyBot(
            bot_type=bot_type,
            minimum_bet=self.minimum_bet,
            maximum_bet=self.maximum_bet,
            amount_multiple=self.home_bet.amount_multiple,
        )

    def get_next_bet(self) -> list[Bet]:
        bets = self.bot.get_next_bet(
            multiplier_positions=self.multiplier_positions,
        )
        if GlobalVars.get_auto_play():
            self.bets = bets
        elif bets:
            _possible_bets = [
                dict(multiplier=bet.multiplier, amount=bet.amount)
                for bet in bets
            ]
            SendEventToGUI.log.debug(f"possible bets: " f"{_possible_bets}")
        return self.bets
