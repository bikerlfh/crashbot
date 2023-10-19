# Standard Library
import copy
from typing import Optional

# Internal
from apps.api.models import BotCondition
from apps.game.bots.constants import ConditionAction, ConditionON


class BotConditionHelper:
    _priority_conditions = [
        ConditionON.PROFIT_LESS_THAN,
        ConditionON.PROFIT_GREATER_THAN,
        ConditionON.STREAK_N_MULTIPLIER_LESS_THAN,
        ConditionON.STREAK_N_MULTIPLIER_GREATER_THAN,
        ConditionON.EVERY_WIN,
        ConditionON.EVERY_LOSS,
        ConditionON.STREAK_WINS,
        ConditionON.STREAK_LOSSES,
    ]

    def __init__(
        self,
        *,
        bot_conditions: list[BotCondition],
        min_multiplier_to_bet: float,
        min_multiplier_to_recover_losses: float,
        multipliers: list[float],
    ):
        self.bot_conditions = bot_conditions
        self.bot_conditions = sorted(
            self.bot_conditions,
            key=lambda x: (
                x.condition_on_value,
                x.condition_on_value_2 if x.condition_on_value_2 else 0.0,
            ),
        )
        # valid conditions of the round
        self.valid_conditions: list[BotCondition] = []
        self.MIN_MULTIPLIER_TO_BET = copy.copy(min_multiplier_to_bet)
        self.MIN_MULTIPLIER_TO_RECOVER_LOSSES = copy.copy(
            min_multiplier_to_recover_losses
        )
        self.multipliers = copy.copy(multipliers)
        self.current_multiplier = copy.copy(min_multiplier_to_bet)
        self.initial_bet_amount = 0.0
        self.current_bet_amount = 0.0
        self.profit = 0.0
        self.last_games: list[bool] = []

    def set_bet_amount(self, *, bet_amount: float, user_change: bool = False):
        """
        Set the bet amount
        :param bet_amount: bet amount
        :param user_change: if the user change the bet amount
        :return: None
        """
        if not user_change:
            return
        self.initial_bet_amount = bet_amount
        self.current_bet_amount = bet_amount

    def add_last_game(self, last_game: bool):
        self.last_games.append(last_game)

    def set_profit(self, profit: float):
        self.profit = profit

    def calculate_streak(self, outcome: bool):
        streak = 0
        for game in reversed(self.last_games):
            if game == outcome:
                streak += 1
            else:
                break
        return streak

    def calculate_multiplier_streak(
        self, *, multiplier: float, count_multipliers: float, is_less: bool
    ) -> bool:
        streak = 0
        for value in reversed(self.multipliers):
            if (is_less and value < multiplier) or (
                not is_less and value > multiplier
            ):
                streak += 1
                continue
            break
        return streak >= count_multipliers

    def _check_conditions(self) -> list[BotCondition]:
        """
        Check if the conditions are valid
        :return: list of valid conditions
        """
        _conditions = []

        def _add_valid_condition(new_condition: BotCondition):
            _condition_on = ConditionON(new_condition.condition_on)
            if _condition_on in [c.condition_on for c in _conditions]:
                filter_conditions = filter(
                    lambda x: x.condition_on == _condition_on.value,
                    _conditions,
                )
                for _condition in filter_conditions:
                    if (
                        new_condition.condition_on_value_2 is not None
                        and _condition.condition_on_value_2 is not None
                    ):
                        is_same_value = (
                            _condition.condition_on_value
                            == new_condition.condition_on_value
                        )
                        is_value_2_less = (
                            _condition.condition_on_value_2
                            < new_condition.condition_on_value_2
                        )
                        if is_same_value and is_value_2_less:
                            _conditions.remove(_condition)
                            continue
                    is_value_less = (
                        _condition.condition_on_value
                        < new_condition.condition_on_value
                    )
                    if is_value_less:
                        _conditions.remove(_condition)
            _conditions.append(new_condition)

        for condition in self.bot_conditions:
            condition_on = ConditionON(condition.condition_on)
            condition_on_value = condition.condition_on_value
            condition_on_value_2 = condition.condition_on_value_2
            match condition_on:
                case ConditionON.EVERY_WIN:
                    if self.last_games and self.last_games[-1]:
                        _add_valid_condition(condition)
                case ConditionON.EVERY_LOSS:
                    if self.last_games and not self.last_games[-1]:
                        _add_valid_condition(condition)
                case ConditionON.STREAK_WINS:
                    if self.calculate_streak(True) >= int(condition_on_value):
                        _add_valid_condition(condition)
                case ConditionON.STREAK_LOSSES:
                    if self.calculate_streak(False) >= int(condition_on_value):
                        _add_valid_condition(condition)
                case ConditionON.PROFIT_GREATER_THAN:
                    if self.profit > condition_on_value:
                        _add_valid_condition(condition)
                case ConditionON.PROFIT_LESS_THAN:
                    if self.profit < condition_on_value:
                        _add_valid_condition(condition)
                case ConditionON.STREAK_N_MULTIPLIER_LESS_THAN:
                    in_streak = self.calculate_multiplier_streak(
                        multiplier=condition_on_value_2,
                        count_multipliers=condition_on_value,
                        is_less=True,
                    )
                    if in_streak:
                        _add_valid_condition(condition)
                case ConditionON.STREAK_N_MULTIPLIER_GREATER_THAN:
                    in_streak = self.calculate_multiplier_streak(
                        multiplier=condition_on_value_2,
                        count_multipliers=condition_on_value,
                        is_less=False,
                    )
                    if in_streak:
                        _add_valid_condition(condition)
        _conditions = sorted(
            _conditions,
            key=lambda x: self._priority_conditions.index(
                ConditionON(x.condition_on)
            ),
            reverse=True,
        )
        actions = []
        streak_wins = list(
            filter(
                lambda x: x.condition_on == ConditionON.STREAK_WINS.value,
                _conditions,
            )
        )
        for streak_win in streak_wins:
            actions += streak_win.actions
        streak_losses = list(
            filter(
                lambda x: x.condition_on == ConditionON.STREAK_LOSSES.value,
                _conditions,
            )
        )
        for streak_loss in streak_losses:
            actions += streak_loss.actions
        if streak_wins or streak_losses:
            every_conditions = list(
                filter(
                    lambda x: x.condition_on
                    in [
                        ConditionON.EVERY_WIN.value,
                        ConditionON.EVERY_LOSS.value,
                    ],
                    _conditions,
                )
            )
            for action in actions:
                for every_condition in every_conditions:
                    _actions = [
                        action.condition_action
                        for action in every_condition.actions
                    ]
                    if action.condition_action in _actions:
                        # remove the action from the every condition
                        every_condition.actions = list(
                            filter(
                                lambda x: x.condition_action
                                != action.condition_action,
                                every_condition.actions,
                            )
                        )
            for every_condition in every_conditions:
                if not every_condition.actions:
                    _conditions.remove(every_condition)
        return _conditions

    def evaluate_conditions(
        self,
        *,
        multiplier_result: float,
        profit: float,
        result_last_game: Optional[bool] = None,
    ) -> tuple[float, float, bool]:
        """
        Evaluate the conditions and return the new bet amount and multiplier
        :param result_last_game: True if the last game was a win,
            False if it was a loss
        :param multiplier_result: multiplier of the last game
        :param profit: profit of the last game
        :return: tuple(bet_amount, multiplier, ignore_model)
        """
        self.multipliers.append(multiplier_result)
        if result_last_game is not None:
            self.add_last_game(result_last_game)
        self.profit = profit
        self.valid_conditions = self._check_conditions()
        ignore_model = False
        for condition in self.valid_conditions:
            for action in condition.actions:
                condition_action = action.condition_action
                action_value = action.action_value
                match condition_action:
                    case ConditionAction.INCREASE_BET_AMOUNT:
                        self.current_bet_amount += (
                            self.current_bet_amount * action_value
                        )
                    case ConditionAction.DECREASE_BET_AMOUNT:
                        self.current_bet_amount -= (
                            self.current_bet_amount * action_value
                        )
                    case ConditionAction.RESET_BET_AMOUNT:
                        self.current_bet_amount = self.initial_bet_amount
                    case ConditionAction.UPDATE_MULTIPLIER:
                        self.current_multiplier = action_value
                    case ConditionAction.RESET_MULTIPLIER:
                        if self.profit >= 0:
                            self.current_multiplier = (
                                self.MIN_MULTIPLIER_TO_BET
                            )
                        else:
                            self.current_multiplier = (
                                self.MIN_MULTIPLIER_TO_RECOVER_LOSSES
                            )
                    case ConditionAction.IGNORE_MODEL:
                        ignore_model = bool(action_value)
                    case ConditionAction.MAKE_BET:
                        _make_bet = bool(action_value)
                        if not _make_bet:
                            return 0.0, 0.0, ignore_model
        return self.current_bet_amount, self.current_multiplier, ignore_model
