# Standard Library
from typing import Optional

# Internal
from apps.api.models import MultiplierPositions
from apps.constants import BotType
from apps.game import utils as game_utils
from apps.game.bots.bot_base import BotBase
from apps.game.bots.helpers import BotConditionHelper
from apps.game.models import Bet, PredictionData
from apps.game.prediction_core import PredictionCore
from apps.globals import GlobalVars
from apps.gui.gui_events import SendEventToGUI


class Bot(BotBase):
    """
    The Bot class is a class used to determine the
    optimal fraction of one's capital to bet on a given bet.
    """

    def set_max_amount_to_bet(
        self,
        *,
        amount: float,
        user_change: bool = False
    ):
        pass


class BotStatic(BotBase):
    """
    The BotStatic class is a class used to determine
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

    def __init__(
        self,
        bot_type: BotType,
        minimum_bet: float = 0,
        maximum_bet: float = 0,
        amount_multiple: float = None,
    ):
        """
        @param bot_type: BotType bot type
        @param minimum_bet: float minimum bet allowed by home bet
        @param maximum_bet: float maximum bet allowed by home bet
        @param amount_multiple: float
        """
        super().__init__(bot_type, minimum_bet, maximum_bet, amount_multiple)
        self._initial_balance = 0

    def initialize(self, *, balance: float, multipliers: list[float]):
        super().initialize(balance=balance, multipliers=multipliers)
        self._initial_balance = balance
        self.set_max_amount_to_bet(
            amount=GlobalVars.get_max_amount_to_bet(),
            user_change=True
        )

    def update_balance(self, balance: float):
        if balance > self.initial_balance:
            self.initial_balance = balance
        super().update_balance(balance)

    def get_real_profit(self) -> float:
        return self.balance - self._initial_balance

    """def evaluate_bets(self, multiplier_result: float):
        total_amount = 0
        for bet in self.bets:
            profit = bet.evaluate(multiplier_result)
            if profit < 0:
                self.add_loss(bet.amount)
            else:
                total_amount += profit
        if total_amount > 0:
            self.remove_loss(total_amount)
        self.bets = []"""

    def get_bet_recovery_amount(
        self, multiplier: float, probability: float
    ) -> float:
        """
        Adjust the bet recovery amount.
        :param multiplier: The multiplier.
        :param probability: The probability.
        :return: The bet recovery amount.
        """
        profit = self.get_profit()
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
        """
        kelly_amount = game_utils.adaptive_kelly_formula(
            multiplier,
            probability,
            self.RISK_FACTOR,
            amount
        )
        """
        amount = round(max(amount, self.minimum_bet), 2)
        return amount

    def generate_recovery_bets(
        self, multiplier: float, probability: float
    ) -> list[Bet]:
        """
        Generate recovery bets.
        :param multiplier: The multiplier.
        :param probability: The probability.
        :return: The recovery bets.
        """
        if multiplier < self.MIN_MULTIPLIER_TO_RECOVER_LOSSES:
            SendEventToGUI.log.warning(
                _( # noqa
                    "multiplier is less than min multiplier to recovery losses"
                )
            )
            return []
        SendEventToGUI.log.debug(_("generating recovery bets"))  # noqa
        bets = []
        amount = self.get_bet_recovery_amount(
            multiplier, probability
        )
        amount = self.validate_bet_amount(amount)
        bets.append(Bet(amount, multiplier))
        return list(filter(lambda b: b.amount > 0, bets))

    def generate_bets(
        self, prediction_data: PredictionData
    ) -> list[Bet]:
        """
        Generate bets.
        :param prediction_data: The prediction data.
        :return: The bets.
        """
        self.bets = []
        profit = self.get_profit()
        second_multiplier = 2
        min_multiplier, max_multiplier = self.predict_next_multiplier()
        SendEventToGUI.log.debug(
            f"second multiplier**: {min_multiplier} - {max_multiplier}"
        )
        category_percentage = prediction_data.category_percentage
        SendEventToGUI.log.debug(f"Amount Lost: {self.amounts_lost}")
        if profit < 0 and abs(profit) >= self.minimum_bet:
            # always the multiplier to recover losses is 1.95
            self.bets = self.generate_recovery_bets(
                self.MIN_MULTIPLIER_TO_RECOVER_LOSSES,
                category_percentage,
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
        profit_percentage = self.get_profit_percent()
        if profit_percentage > 0 or self.is_bullish_game:
            SendEventToGUI.log.debug(
                "generate_bets :: profit_percentage > 0 or is_bullish_game"
            )
            max_bet_kelly_amount = game_utils.adaptive_kelly_formula(
                self.MIN_MULTIPLIER_TO_BET,
                category_percentage,
                self.RISK_FACTOR,
                self._max_amount_to_bet,
            )
            min_bet_kelly_amount = game_utils.adaptive_kelly_formula(
                second_multiplier,
                category_percentage,
                self.RISK_FACTOR,
                self._min_amount_to_bet,
            )
            self.bets.append(
                Bet(
                    max(max_bet_kelly_amount, self._max_amount_to_bet),
                    self.MIN_MULTIPLIER_TO_BET,
                )
            )
            self.bets.append(
                Bet(
                    max(min_bet_kelly_amount, self._min_amount_to_bet),
                    second_multiplier,
                )
            )
        else:
            self.bets.append(
                Bet(self._max_amount_to_bet, self.MIN_MULTIPLIER_TO_BET)
            )
            self.bets.append(Bet(self._min_amount_to_bet, second_multiplier))
        self.bets = list(filter(lambda b: b.amount > 0, self.bets))
        return self.bets

    def get_next_bet(
        self,
        *,
        prediction: PredictionCore,
        multiplier_positions: Optional[MultiplierPositions] = None,
    ) -> list[Bet]:
        """
        Get the next bet.
        :param prediction: The prediction core.
        :param multiplier_positions: The multiplier positions.
        :return: The next bet.
        """
        if prediction is None:
            return []
        self.multiplier_positions = multiplier_positions
        profit = self.get_profit()
        if profit >= 0:
            self.reset_losses()
        prediction_data = self.get_prediction_data(prediction)
        SendEventToGUI.log.debug(f"profit: {profit}")
        prediction_data.print_data()
        if self.in_stop_loss():
            SendEventToGUI.log.warning(_("Stop loss reached"))  # noqa
            return []
        if self.in_take_profit():
            SendEventToGUI.log.success(_("Take profit reached"))  # noqa
            return []
        if not self.IGNORE_MODEL:
            if not prediction_data.in_category_percentage:
                SendEventToGUI.log.warning(
                    _("Prediction value is not in category percentage") # noqa
                )
                return []
            if prediction_data.probability < self.MIN_PROBABILITY_TO_BET:
                SendEventToGUI.log.debug("Probability is too low")
                return []
        # CATEGORY 1 not bet
        if prediction_data.prediction_round == 1:
            SendEventToGUI.log.debug("Prediction round is 1")
            return []
        # CATEGORY 2
        return self.generate_bets(prediction_data)
