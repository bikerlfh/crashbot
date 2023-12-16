# Standard Library
from typing import Optional

# Internal
from apps.api.models import MultiplierPositions
from apps.game import utils as game_utils
from apps.game.bots.bot_base import BotBase
from apps.game.models import Bet, PredictionData
from apps.game.prediction_core import PredictionCore
from apps.gui.gui_events import SendEventToGUI


class BotStrategy(BotBase):
    """
    NOTE: don't use this directly
    The BotStrategy class is a class used to determine
    the optimal fraction of one's capital to bet on a given bet.
    This Bot is used to bet in the game, it's necessary
    that the customer select the two amount to bet (max and min).
    In control 1, the bot will bet the max amount of
    money that the customer selects.
    In control 2, the bot will bet the min amount of
    money that the customer selects.
    The min amount of bet should be less than the max
    amount of bet / 3 example: max bet = 300, min bet = 300/3 = 100.
    """

    def generate_bets(
        self, prediction_data: Optional[PredictionData] = None
    ) -> list[Bet]:
        """
        Generate bets.
        :param prediction_data: The prediction data.
        :return: The bets.
        """
        self.bets = []
        profit = self.profit_last_balance
        second_multiplier = 2
        min_multiplier, max_multiplier = self.predict_next_multiplier()
        if self.amounts_lost:
            SendEventToGUI.log.debug(f"Amount Lost: {self.amounts_lost}")
        if (
            profit < 0
            and abs(profit) >= self.minimum_bet
            and self.RECOVERY_LOSSES
        ):
            self.bets = self.generate_recovery_bets(
                self.MIN_MULTIPLIER_TO_RECOVER_LOSSES
            )
            return self.bets
        if self.MIN_MULTIPLIER_TO_BET == 0:
            return []
        # get the possible next second multiplier
        if min_multiplier > second_multiplier:
            second_multiplier = game_utils.generate_random_multiplier(
                min_multiplier, max_multiplier
            )
            SendEventToGUI.log.debug(
                f"second multiplier: {min_multiplier} - "
                f"{max_multiplier} = {second_multiplier}"
            )
        if self.MAKE_SECOND_BET:
            self.bets.append(
                Bet(self._max_amount_to_bet, self.MIN_MULTIPLIER_TO_BET)
            )
            if second_multiplier == self.MIN_MULTIPLIER_TO_BET:
                second_multiplier += 0.2
            self.bets.append(Bet(self._min_amount_to_bet, second_multiplier))
        else:
            self.bets.append(Bet(self._bet_amount, self.MIN_MULTIPLIER_TO_BET))
        self.bets = list(filter(lambda b: b.amount > 0, self.bets))
        return self.bets

    def get_next_bet(
        self,
        *,
        prediction: Optional[PredictionCore] = None,
        multiplier_positions: Optional[MultiplierPositions] = None,
        auto_play: Optional[bool] = False,
    ) -> list[Bet]:
        """
        Get the next bet.
        :param prediction: The prediction core.
        :param multiplier_positions: The multiplier positions.
        :param auto_play: The auto bet.
        :return: The next bet.
        """
        self.auto_play = auto_play
        self.multiplier_positions = multiplier_positions
        profit = self.profit_last_balance
        if profit >= 0:
            self.reset_losses()
        if self.in_stop_loss():
            SendEventToGUI.log.warning(_("Stop loss reached"))  # noqa
            return []
        if self.in_take_profit():
            SendEventToGUI.log.success(_("Take profit reached"))  # noqa
            return []
        return self.generate_bets()
