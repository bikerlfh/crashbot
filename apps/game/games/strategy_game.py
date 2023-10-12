from apps.game.models import Bet
from apps.utils.local_storage import LocalStorage
from apps.game.models import Bet, Multiplier

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

    def add_multiplier(self, multiplier: float) -> None:
        """
        Add a new multiplier and update the multipliers
        """
        self.evaluate_bets(multiplier)
        self.multipliers.append(Multiplier(multiplier))
        self.bot.add_multiplier(multiplier)
        self.multipliers_to_save.append(multiplier)
        self.request_save_multipliers()
        # remove the first multiplier
        self.multipliers = self.multipliers[1:]
        SendEventToGUI.send_multipliers([multiplier])

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
