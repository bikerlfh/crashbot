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

    def get_real_profit(self) -> float:
        return self.balance - self.initial_balance

    def get_bet_recovery_amount(
        self, multiplier: float, probability: Optional[float] = None
    ) -> float:
        """
        Adjust the bet recovery amount.
        :param multiplier: The multiplier.
        :param probability: The probability.
        :return: The bet recovery amount.
        """
        profit = self.profit_last_balance
        # NOTE: no use minBet by strategy
        # min_bet = self.balance * strategy.min_amount_percentage_to_bet
        amount_to_recover_losses = self.calculate_recovery_amount(
            profit, multiplier
        )
        if amount_to_recover_losses < self.minimum_bet:
            return self.minimum_bet
        # calculate the amount to bet to recover last amount loss
        last_amount_loss = self.calculate_recovery_amount(
            self.get_last_lost_amount(), multiplier
        )
        # calculates the maximum amount allowed to recover in a single bet
        max_recovery_amount = (
            self.maximum_bet * self.MAX_RECOVERY_PERCENTAGE_ON_MAX_BET
        )
        amount = min(
            amount_to_recover_losses, max_recovery_amount, self.balance
        )
        amount = max(amount, self.minimum_bet)
        # validation of new balance after bet recovery with the stop loss
        possible_loss = abs(profit) + amount
        if possible_loss >= self.stop_loss:
            amount = min(round(amount * 0.5, 2), last_amount_loss)
            SendEventToGUI.log.debug(
                f"get_bet_recovery_amount ::"
                f"possible_loss >= self.stop_loss"
                f"({possible_loss} >= {self.stop_loss}) ::"
                f"new amount={amount}"
            )
        amount = round(max(amount, self.minimum_bet), 2)
        return amount

    def generate_recovery_bets(
        self, multiplier: float, probability: Optional[float] = None
    ) -> list[Bet]:
        """
        Generate recovery bets.
        :param multiplier: The multiplier.
        :param probability: The probability.
        :return: The recovery bets.
        """
        if multiplier < self.MIN_MULTIPLIER_TO_RECOVER_LOSSES:
            SendEventToGUI.log.warning(
                _(  # noqa
                    "multiplier is less than min multiplier to recovery losses"
                )
            )
            return []
        if self.MIN_MULTIPLIER_TO_RECOVER_LOSSES == 0:
            SendEventToGUI.log.debug(
                _("min multiplier to recovery losses is 0")  # noqa
            )
            return []
        SendEventToGUI.log.debug(_("generating recovery bets"))  # noqa
        bets = []
        amount = self.get_bet_recovery_amount(multiplier)
        amount = self.validate_bet_amount(amount)
        bets.append(Bet(amount, multiplier))
        return list(filter(lambda b: b.amount > 0, bets))

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
        SendEventToGUI.log.debug(
            f"second multiplier**: {min_multiplier} - {max_multiplier}"
        )
        SendEventToGUI.log.debug(f"Amount Lost: {self.amounts_lost}")
        if profit < 0 and abs(profit) >= self.minimum_bet:
            # always the multiplier to recover losses is 1.95
            self.bets = self.generate_recovery_bets(
                self.MIN_MULTIPLIER_TO_RECOVER_LOSSES
            )
            return self.bets
        # to category 2
        # if the profit is greater than 10% of the initial balance
        # get the possible next second multiplier
        if min_multiplier > second_multiplier:
            second_multiplier = game_utils.generate_random_multiplier(
                min_multiplier, max_multiplier
            )
            SendEventToGUI.log.debug(f"Second multiplier: {second_multiplier}")
        self.bets.append(
            Bet(self._max_amount_to_bet, self.MIN_MULTIPLIER_TO_BET)
        )
        if second_multiplier == self.MIN_MULTIPLIER_TO_BET:
            second_multiplier += 0.2
        self.bets.append(Bet(self._min_amount_to_bet, second_multiplier))
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
