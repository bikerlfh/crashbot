# Standard Library
from typing import List, Optional

# Internal
from apps.api import services as api_services
from apps.api.models import MultiplierPositions
from apps.constants import BotType
from apps.game.bots.helpers import BotConditionHelper
from apps.game import utils as game_utils
from apps.game.models import Bet, PredictionData
from apps.game.prediction_core import PredictionCore
from apps.globals import GlobalVars
from apps.gui.gui_events import SendEventToGUI
from apps.utils import graphs as utils_graphs


class BotBase:
    """
    The BotBase has the logic for all bots
    """

    BOT_TYPE: BotType = BotType.LOOSE
    RISK_FACTOR: float = 0.1  # 0.1 = 10%
    MIN_MULTIPLIER_TO_BET: float = 1.5
    MIN_MULTIPLIER_TO_RECOVER_LOSSES: float = 2.0
    MIN_PROBABILITY_TO_BET: float = 0.5
    # use to calculate the recovery amount to bet
    MAX_RECOVERY_PERCENTAGE_ON_MAX_BET: float = 0.5  # 0.5 = 50%
    MIN_CATEGORY_PERCENTAGE_TO_BET: float = 0.8  # 0.8 = 80%
    MIN_AVERAGE_MODEL_PREDICTION: float = 0.8  # 0.8 = 80%
    STOP_LOSS_PERCENTAGE: float = 0
    TAKE_PROFIT_PERCENTAGE: float = 0

    # minimum value to determine if the game is bullish or bearish
    MINIMUM_VALUE_TO_DETERMINE_BULLISH_GAME = 0.31
    # if True, the bot will ignore the model PROBABILITY_TO_BET and MIN_AVERAGE_MODEL_PREDICTION
    IGNORE_MODEL = False
    is_bullish_game: bool = False

    MAX_MULTIPLIERS_IN_MEMORY: int = 50

    amount_multiple: Optional[float] = None
    initial_balance: float = 0
    balance: float = 0
    stop_loss: float = 0
    take_profit: float = 0
    minimum_bet: float
    maximum_bet: float
    bets: List[Bet] = []
    amounts_lost: List[float] = []
    multipliers: List[float] = []

    _max_amount_to_bet: float = 0
    _min_amount_to_bet: float = 0

    multiplier_positions: MultiplierPositions = None
    bot_condition_helper: BotConditionHelper = None

    def __init__(
        self,
        bot_type: BotType,
        minimum_bet: float = 0,
        maximum_bet: float = 0,
        amount_multiple: Optional[float] = None,
    ):
        self._custom_bot = GlobalVars.get_custom_bot_selected()
        self.BOT_TYPE = bot_type
        self.minimum_bet = minimum_bet
        self.maximum_bet = maximum_bet
        self.amount_multiple = amount_multiple

    def initialize(self, *, balance: float, multipliers: list[float]):
        self.initial_balance = balance
        self.balance = balance
        self.multipliers = multipliers
        bot_data = api_services.get_bots(bot_type=self.BOT_TYPE.value)
        if len(bot_data) == 0:
            SendEventToGUI.exception("No bot data found")
            raise ValueError("No bot data found")
        bot = bot_data[0]
        if self._custom_bot:
            bot = self._custom_bot
        # initialize the conditions
        self.bot_condition_helper = BotConditionHelper(
            bot_conditions=bot.conditions,
            min_multiplier_to_bet=bot.min_multiplier_to_bet,
            min_multiplier_to_recover_losses=bot.min_multiplier_to_recover_losses,
        )
        SendEventToGUI.log.info(f"Bot {bot.name} loaded")
        self.MIN_CATEGORY_PERCENTAGE_TO_BET = (
            bot.min_category_percentage_to_bet
        )
        self.MIN_AVERAGE_MODEL_PREDICTION = bot.min_average_model_prediction
        self.RISK_FACTOR = bot.risk_factor
        self.MIN_MULTIPLIER_TO_BET = bot.min_multiplier_to_bet
        self.MIN_MULTIPLIER_TO_RECOVER_LOSSES = (
            bot.min_multiplier_to_recover_losses
        )
        self.MIN_PROBABILITY_TO_BET = bot.min_probability_to_bet
        self.MAX_RECOVERY_PERCENTAGE_ON_MAX_BET = (
            bot.max_recovery_percentage_on_max_bet
        )
        self.STOP_LOSS_PERCENTAGE = bot.stop_loss_percentage
        self.TAKE_PROFIT_PERCENTAGE = bot.take_profit_percentage
        self.stop_loss = round(
            self.initial_balance * self.STOP_LOSS_PERCENTAGE, 2
        )
        self.take_profit = round(
            self.initial_balance * self.TAKE_PROFIT_PERCENTAGE, 2
        )
        SendEventToGUI.log.info(_("Bot initialized"))  # noqa
        SendEventToGUI.log.info(
            f"{_('Bot type')}: {self.BOT_TYPE.value}"  # noqa
        )  # noqa
        SendEventToGUI.log.info(
            f"{_('Bot risk factor')}: {self.RISK_FACTOR}"  # noqa
        )
        SendEventToGUI.log.info(
            f"{_('Bot min multiplier to bet')}: {self.MIN_MULTIPLIER_TO_BET}"  # noqa
        )
        SendEventToGUI.log.info(
            f"{_('Bot min multiplier to recover losses')}: "  # noqa
            f"{self.MIN_MULTIPLIER_TO_RECOVER_LOSSES}"
        )
        SendEventToGUI.log.info(
            f"{_('Bot min category percentage to bet')}: "  # noqa
            f"{self.MIN_CATEGORY_PERCENTAGE_TO_BET}"
        )
        SendEventToGUI.log.debug(
            f"{_('Bot min average model prediction')}: "  # noqa
            f"{self.MIN_AVERAGE_MODEL_PREDICTION}"
        )
        SendEventToGUI.log.info(f"{_('Stop Loss')}: {self.stop_loss}")  # noqa
        SendEventToGUI.log.info(
            f"{_('Take Profit')}: {self.take_profit}"  # noqa
        )
        SendEventToGUI.log.debug(
            f"{_('Bot conditions count')}: {len(self.bot_condition_helper.bot_conditions)}"  # noqa
        )

    def validate_bet_amount(self, amount: float) -> float:
        # if amount < minimumBet, set amount = minimumBet
        final_amount = max(amount, self.minimum_bet)
        # get the min amount between amount, maximumBet and balance
        final_amount = min(final_amount, self.maximum_bet, self.balance)
        final_amount = round(final_amount, 0)
        if self.amount_multiple:
            final_amount = game_utils.format_number_to_multiple(
                amount, self.amount_multiple
            )
        return final_amount

    def add_multiplier(self, multiplier: float):
        self.multipliers.append(multiplier)
        # remove the first multiplier
        if len(self.multipliers) > self.MAX_MULTIPLIERS_IN_MEMORY:
            self.multipliers = self.multipliers[1:]
        self.is_bullish_game = self.determine_bullish_game()
        SendEventToGUI.log.debug(f"Is bullish game: {self.is_bullish_game}")

    def add_loss(self, amount: float):
        self.amounts_lost.append(amount)

    def remove_loss(self, amount: float):
        total_loss = amount
        for i in range(len(self.amounts_lost) - 1, -1, -1):
            if self.amounts_lost[i] > total_loss:
                self.amounts_lost[i] -= total_loss
                break
            total_loss -= self.amounts_lost[i]
            self.amounts_lost.pop()

    def reset_losses(self):
        self.amounts_lost = []

    def determine_bullish_game(self) -> bool:
        y_coordinates = utils_graphs.convert_multipliers_to_coordinate(
            self.multipliers
        )
        slope, _ = utils_graphs.calculate_slope_linear_regression(
            y_coordinates
        )
        return slope >= self.MINIMUM_VALUE_TO_DETERMINE_BULLISH_GAME

    def get_last_lost_amount(self) -> float:
        """
        Get the last lost amount
        if there are more than 4 lost amounts, return the average
        :return:
        """
        if len(self.amounts_lost) > 4:
            average = sum(self.amounts_lost) / len(self.amounts_lost)
            return average
        if len(self.amounts_lost) == 0:
            return 0
        return max(self.amounts_lost)

    def set_max_amount_to_bet(
        self,
        *,
        amount: float,
        user_change: bool = False
    ):
        """
        Set the max amount to bet
        :param amount: amount to bet
        :param user_change: if the user changed the amount
        :return: None
        """
        self.bot_condition_helper.set_bet_amount(
            bet_amount=amount,
            user_change=user_change
        )
        self._max_amount_to_bet = round(amount * 0.7, 0)
        if self._max_amount_to_bet > self.balance:
            SendEventToGUI.log.debug(
                f"maxAmountToBet is greater than balance({self.balance})"
            )
            SendEventToGUI.log.debug("setting maxAmountToBet to balance")
            self._max_amount_to_bet = 0
        self._min_amount_to_bet = round(self._max_amount_to_bet * 0.3, 0)
        if self.amount_multiple:
            self._max_amount_to_bet = game_utils.format_number_to_multiple(
                self._max_amount_to_bet, self.amount_multiple
            )
            self._min_amount_to_bet = game_utils.format_number_to_multiple(
                self._min_amount_to_bet, self.amount_multiple
            )
        total = self._max_amount_to_bet + self._min_amount_to_bet
        if total < amount:
            self._max_amount_to_bet += amount - total
        SendEventToGUI.log.success(
            f"{_('Min bet amount')}: {self._min_amount_to_bet}"  # noqa
        )
        SendEventToGUI.log.success(
            f"{_('Max bet amount')}: {self._max_amount_to_bet}"  # noqa
        )

    def _execute_conditions(self, result_last_game: bool):
        """
        Evaluate the conditions to bet
        :param result_last_game: True if the last game was a win
        :return: None
        """
        bet_amount, multiplier, self.IGNORE_MODEL = (
            self.bot_condition_helper.evaluate_conditions(
                result_last_game=result_last_game,
                profit=self.get_profit()
            )
        )
        self.set_max_amount_to_bet(amount=bet_amount)
        if result_last_game:
            self.MIN_MULTIPLIER_TO_BET = multiplier
        else:
            self.MIN_MULTIPLIER_TO_RECOVER_LOSSES = multiplier
        SendEventToGUI.log.debug(f"evaluate_conditions :: bet_amount {bet_amount}")
        SendEventToGUI.log.debug(f"evaluate_conditions :: multiplier {multiplier}")

    def evaluate_bets(self, multiplier_result: float):
        total_amount = 0
        result_last_game = False
        for bet in self.bets:
            profit = bet.evaluate(multiplier_result)
            if profit < 0:
                self.add_loss(bet.amount)
            else:
                total_amount += profit
        if total_amount > 0:
            result_last_game = True
            self.remove_loss(total_amount)
        self.bets = []
        self._execute_conditions(
            result_last_game=result_last_game
        )

    def get_number_of_bets(self):
        """
        Number of maximum bets that the bot can hold
        @return {number} the number of bets
        """
        return int(self.balance // self.maximum_bet)

    def get_profit(self):
        return round(self.balance - self.initial_balance, 2)

    def get_profit_percent(self):
        return self.get_profit() / self.initial_balance

    def in_stop_loss(self) -> bool:
        profit = self.get_profit()
        return profit < 0 and abs(profit) >= self.stop_loss

    def in_take_profit(self) -> bool:
        profit = self.get_profit()
        return profit >= self.take_profit

    def update_balance(self, balance: float):
        self.balance = balance
        SendEventToGUI.balance(self.balance)

    def get_prediction_data(
        self, prediction: PredictionCore
    ) -> PredictionData:
        category_percentage = prediction.get_category_percentage()
        category_percentage_value_in_live = (
            prediction.get_category_percentage_value_in_live()
        )
        average_predictions_of_model = prediction.average_predictions_of_model
        in_category_percentage = (
            category_percentage >= self.MIN_CATEGORY_PERCENTAGE_TO_BET
        )
        in_average_prediction_of_model = (
            average_predictions_of_model >= self.MIN_AVERAGE_MODEL_PREDICTION
        )
        prediction_data = PredictionData(
            prediction_value=prediction.get_prediction_value(),
            prediction_round=prediction.get_prediction_round_value(),
            probability=prediction.get_probability_value(),
            category_percentage=category_percentage,
            category_percentage_value_in_live=category_percentage_value_in_live, # noqa
            average_prediction_of_model=average_predictions_of_model,
            in_category_percentage=in_category_percentage,
            in_average_prediction_of_model=in_average_prediction_of_model,
        )
        return prediction_data

    def predict_next_multiplier(self) -> tuple[float, float]:
        """
        Get the next prediction value
        @return range of the next multiplier
        """
        multiplier, percentage = game_utils.predict_next_multiplier(
            data=self.multiplier_positions,
            last_multipliers=self.multipliers,
            use_all_time=True,
        )
        if multiplier <= 2:
            return 2, 2
        min_ = round(multiplier * (1 - percentage), 2)
        return min_, multiplier

    @staticmethod
    def calculate_recovery_amount(
        amount_lost: float, multiplier: float
    ) -> float:
        """
        * calculate the amount to recover the losses
        * @param {number} profit the profit of bot
        * @param {number} multiplier the multiplier
        * @return {number} the amount to recover the losses
        """
        return abs(amount_lost) / (multiplier - 1)

    def get_bet_recovery_amount(
        self, multiplier: float, probability: float
    ) -> float:
        """
        * adjust the bet recovery amount
        * @param {number} amount the amount to recover the losses
        * @param {number} multiplier the multiplier
        """
        profit = self.get_profit()
        amount_to_recover_losses = self.calculate_recovery_amount(
            profit, multiplier
        )
        # calculate the amount to bet to recover last amount loss
        last_amount_loss = self.calculate_recovery_amount(
            self.get_last_lost_amount(), multiplier
        )
        # calculates the maximum amount allowed to recover in a single bet
        max_recovery_amount = (
            self.maximum_bet * self.MAX_RECOVERY_PERCENTAGE_ON_MAX_BET
        )  # 50% of maximum bet (this can be a parameter of the bot)
        amount = min(
            amount_to_recover_losses, max_recovery_amount, self.balance
        )
        amount = last_amount_loss if amount >= max_recovery_amount else amount
        kelly_amount = game_utils.adaptive_kelly_formula(
            multiplier, probability, self.RISK_FACTOR, amount
        )
        return max(amount, kelly_amount)

    def generate_recovery_bets(
        self, multiplier: float, probability: float
    ) -> List[Bet]:
        bets: List[Bet] = []
        profit = self.get_profit()
        if profit >= 0 or multiplier < self.MIN_MULTIPLIER_TO_RECOVER_LOSSES:
            return []

        amount = self.get_bet_recovery_amount(
            multiplier, probability
        )
        amount = self.validate_bet_amount(amount)
        if multiplier >= 2:
            amount = round(amount / 1.5, 0)
            if self.amount_multiple:
                amount = game_utils.format_number_to_multiple(
                    amount, self.amount_multiple
                )
            multiplier1 = round((multiplier / 2) * 1.5, 2)
            bets.append(Bet(amount, multiplier1))
            bets.append(Bet(amount, multiplier1))
        else:
            bets.append(Bet(amount, multiplier))

        return [b for b in bets if b.amount > 0]

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
                return []

            if not prediction_data.in_average_prediction_of_model:
                return []
            if prediction_data.probability < self.MIN_PROBABILITY_TO_BET:
                SendEventToGUI.log.debug(_("Probability is too low"))  # noqa
                return []
        # CATEGORY 1
        if prediction_data.prediction_round == 1:
            return self.generate_bets(prediction_data)
        # CATEGORY 2 and 3
        return self.generate_bets(prediction_data)
