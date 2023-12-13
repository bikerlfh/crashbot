# Standard Library
from typing import Optional

# Internal
from apps.api.models import MultiplierPositions
from apps.game import utils as game_utils
from apps.game.bots.bot_base import BotBase
from apps.game.models import Bet, PredictionData
from apps.game.prediction_core import PredictionCore
from apps.gui.gui_events import SendEventToGUI


class BotAI(BotBase):
    """
    The BotAI class is a class used to determine
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

    def _show_bot_info(self):
        SendEventToGUI.log.info(
            f"{_('Only bullish games')}: {self.ONLY_BULLISH_GAMES}"  # noqa
        )
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
        SendEventToGUI.log.info(_("Bot initialized"))  # noqa
        SendEventToGUI.log.warning(f"{_('Bot')}: {self.BOT_NAME}")  # noqa

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
        category_percentage = prediction_data.category_percentage
        SendEventToGUI.log.debug(f"Amount Lost: {self.amounts_lost}")
        if profit < 0 and abs(profit) >= self.minimum_bet:
            # always the multiplier to recover losses is 1.95
            self.bets = self.generate_recovery_bets(
                self.MIN_MULTIPLIER_TO_RECOVER_LOSSES,
                category_percentage,
            )
            return self.bets
        if self.MIN_MULTIPLIER_TO_BET == 0:
            return []
        # to category 2
        # if the profit is greater than 10% of the initial balance
        # get the possible next second multiplier
        if min_multiplier > second_multiplier:
            second_multiplier = game_utils.generate_random_multiplier(
                min_multiplier, max_multiplier
            )
            SendEventToGUI.log.debug(f"Second multiplier: {second_multiplier}")
        if second_multiplier == self.MIN_MULTIPLIER_TO_BET:
            second_multiplier += 0.2
        profit_percentage = self.profit_percent_last_balance
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
        elif self.MAKE_SECOND_BET:
            self.bets.append(
                Bet(self._max_amount_to_bet, self.MIN_MULTIPLIER_TO_BET)
            )
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
        if prediction is None:
            return []
        prediction_data = self.get_prediction_data(prediction)
        SendEventToGUI.log.debug(f"profit: {profit}")
        prediction_data.print_data()
        if not self.IGNORE_MODEL:
            if not prediction_data.in_category_percentage:
                SendEventToGUI.log.warning(
                    _("Prediction value is not in category percentage")  # noqa
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
