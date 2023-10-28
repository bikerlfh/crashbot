# Internal
from apps.game.bots.bot_strategy import BotStrategy
from apps.game.games.constants import GameType
from apps.game.games.game_base import GameBase
from apps.game.models import Bet, Multiplier
from apps.globals import GlobalVars
from apps.gui.gui_events import SendEventToGUI
from apps.utils.local_storage import LocalStorage

local_storage = LocalStorage()


class GameStrategy(GameBase, configuration=GameType.STRATEGY.value):
    bot: BotStrategy
    """
    This game no uses the AI. Only use strategy to bet.
    """

    def _initialize_bot(self, *, bot_name: str):
        self.bot = BotStrategy(
            bot_name=bot_name,
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
        self.multipliers_to_save.append(Multiplier(multiplier))
        self.request_save_multipliers()
        # remove the first multiplier
        self.multipliers = self.multipliers[1:]
        SendEventToGUI.send_multipliers([multiplier])

    async def wait_next_game(self):
        """
        Wait for the next game to start
        override the base method to not save customer balance
        """
        SendEventToGUI.log.info(_("waiting for the next game"))  # noqa
        await self.game_page.wait_next_game()
        self.balance = await self.read_balance_to_aviator()
        # TODO implement create manual bets
        self.bot.update_balance(self.balance)
        self.add_multiplier(self.game_page.multipliers[-1])
        self.bets = []

    def get_next_bet(self) -> list[Bet]:
        auto_play = GlobalVars.get_auto_play()
        bets = self.bot.get_next_bet(
            multiplier_positions=self.multiplier_positions,
            auto_play=auto_play,
        )
        if auto_play:
            self.bets = bets
        elif bets:
            _possible_bets = [
                dict(amount=bet.amount, multiplier=bet.multiplier)
                for bet in bets
            ]
            for bet in reversed(_possible_bets):
                SendEventToGUI.log.info(f"possible bet: {bet}")
        return self.bets
