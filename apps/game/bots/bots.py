# Internal
from apps.api.models import BotStrategy
from apps.constants import BotType
from apps.game.bots.bot_base import BotBase
from apps.game.models import Bet, PredictionData
from apps.game.prediction_core import PredictionCore
from apps.game.utils import adaptive_kelly_formula
from apps.globals import GlobalVars
from apps.gui.gui_events import SendEventToGUI


class Bot(BotBase):
    """
    The Bot class is a class used to determine the optimal fraction of one's capital to bet on a given bet.
    """

    def __init__(
        self,
        bot_type: BotType,
        minimum_bet: float = 0,
        maximum_bet: float = 0,
        amount_multiple: float = None,
    ):
        super().__init__(bot_type, minimum_bet, maximum_bet, amount_multiple)

    def initialize(self, balance: float):
        super().initialize(balance)

    def set_max_amount_to_bet(self, amount: float):
        # # SendEventToGUI.log.info("this bot not allowed to set max_amount_to_bet.")
        pass


class BotStatic(BotBase):
    """
    The BotStatic class is a class used to determine the optimal fraction of one's capital to bet on a given bet.
    This Bot is used to bet in the game, it's necessary that the customer select the two amount to bet (max and min).
    In control 1, the bot will bet the max amount of money that the customer selects.
    In control 2, the bot will bet the min amount of money that the customer selects.
    The min amount of bet should be less than the max amount of bet / 3 example: max bet = 300, min bet = 300/3 = 100.
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

    def initialize(self, balance: float):
        # SendEventToGUI.log.debug("initializing bot static")
        super().initialize(balance)
        self._initial_balance = balance
        self.set_max_amount_to_bet(GlobalVars.get_max_amount_to_bet())

    def update_balance(self, balance: float):
        if balance > self.initial_balance:
            self.initial_balance = balance
        super().update_balance(balance)

    def evaluate_bets(self, multiplier_result: float):
        total_amount = 0
        for bet in self.bets:
            profit = bet.evaluate(multiplier_result)
            if profit < 0:
                self.add_loss(bet.amount)
            else:
                total_amount += profit
        if total_amount > 0:
            self.remove_loss(total_amount)
        self.bets = []

    def get_bet_recovery_amount(
        self, multiplier: float, probability: float, strategy: BotStrategy
    ) -> float:
        """
        Adjust the bet recovery amount.
        :param multiplier: The multiplier.
        :param probability: The probability.
        :param strategy: The bot strategy.
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
        # amount = last_amount_loss if amount >= max_recovery_amount else amount
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
        # kelly_amount = adaptive_kelly_formula(multiplier, probability, self.RISK_FACTOR, amount)
        amount = round(max(amount, self.minimum_bet), 2)
        SendEventToGUI.log.debug(
            f"BotStatic :: get_bet_recovery_amount {amount}"
        )
        return amount

    def generate_recovery_bets(
        self, multiplier: float, probability: float, strategy: BotStrategy
    ) -> list[Bet]:
        """
        Generate recovery bets.
        :param multiplier: The multiplier.
        :param probability: The probability.
        :param strategy: The bot strategy.
        :return: The recovery bets.
        """
        if multiplier < self.MIN_MULTIPLIER_TO_RECOVER_LOSSES:
            SendEventToGUI.log.warning(
                f"multiplier is less than "
                f"{self.MIN_MULTIPLIER_TO_RECOVER_LOSSES}, no recovery bets"
            )
            return []
        SendEventToGUI.log.debug("generating recovery bets")
        bets = []
        amount = self.get_bet_recovery_amount(
            multiplier, probability, strategy
        )
        amount = self.validate_bet_amount(amount)
        bets.append(Bet(amount, multiplier))
        return list(filter(lambda b: b.amount > 0, bets))

    def generate_bets(
        self, prediction_data: PredictionData, strategy: BotStrategy
    ) -> list[Bet]:
        """
        Generate bets.
        :param prediction_data: The prediction data.
        :param strategy: The bot strategy.
        :return: The bets.
        """
        self.bets = []
        profit = self.get_profit()
        category_percentage = prediction_data.category_percentage
        SendEventToGUI.log.debug(f"Amount Lost: {self.amounts_lost}")
        if profit < 0 and abs(profit) >= self.minimum_bet:
            # always the multiplier to recover losses is 1.95
            self.bets = self.generate_recovery_bets(
                self.MIN_MULTIPLIER_TO_RECOVER_LOSSES,
                category_percentage,
                strategy,
            )
            return self.bets
        # to category 2
        # if the profit is greater than 10% of the initial balance
        profit_percentage = self.get_profit_percent()
        if profit_percentage > 0.10:
            SendEventToGUI.log.debug(
                "generate_bets :: profit_percentage > 0.10"
            )
            max_bet_kelly_amount = adaptive_kelly_formula(
                1.95,
                category_percentage,
                self.RISK_FACTOR,
                self._max_amount_to_bet,
            )
            min_bet_kelly_amount = adaptive_kelly_formula(
                2,
                category_percentage,
                self.RISK_FACTOR,
                self._min_amount_to_bet,
            )
            self.bets.append(
                Bet(max(max_bet_kelly_amount, self._max_amount_to_bet), 1.95)
            )
            self.bets.append(
                Bet(max(min_bet_kelly_amount, self._min_amount_to_bet), 2)
            )
        else:
            self.bets.append(Bet(self._max_amount_to_bet, 1.95))
            self.bets.append(Bet(self._min_amount_to_bet, 2))
        self.bets = list(filter(lambda b: b.amount > 0, self.bets))
        SendEventToGUI.log.debug(f"bot bets: {self.bets}")
        return self.bets

    def get_next_bet(self, prediction: PredictionCore) -> list[Bet]:
        """
        Get the next bet.
        :param prediction: The prediction core.
        :return: The next bet.
        """
        if prediction is None:
            return []
        profit = self.get_profit()
        if profit >= 0:
            self.reset_losses()
        prediction_data = self.get_prediction_data(prediction)
        number_of_bet = self.get_number_of_bets()
        strategy = self.get_strategy(number_of_bet)
        if not strategy:
            SendEventToGUI.log.warning(
                f"No strategy found for profit "
                f"percentage: {self.get_profit_percent()}"
            )
            return []
        SendEventToGUI.log.debug(f"profit: {profit}")
        prediction_data.print_data()
        if self.in_stop_loss():
            SendEventToGUI.log.warning("Stop loss reached")
            return []
        if self.in_take_profit():
            SendEventToGUI.log.success("Take profit reached")
            return []
        if not prediction_data.in_category_percentage:
            SendEventToGUI.log.warning(
                "Prediction value is not in category percentage"
            )
            return []
        if prediction_data.prediction_value < self.MIN_MULTIPLIER_TO_BET:
            SendEventToGUI.log.warning("Prediction value is too low")
            return []
        if prediction_data.probability < self.MIN_PROBABILITY_TO_BET:
            SendEventToGUI.log.debug("Probability is too low")
            return []
        # CATEGORY 1 not bet
        if prediction_data.prediction_round == 1:
            SendEventToGUI.log.debug("Prediction round is 1")
            return []
        # CATEGORY 2
        return self.generate_bets(prediction_data, strategy)
