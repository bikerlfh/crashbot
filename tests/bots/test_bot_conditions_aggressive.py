# Libraries
import pytest

# Internal
from apps.api.models import BotCondition, BotConditionAction
from apps.game.bots.constants import ConditionAction, ConditionON
from apps.game.bots.helpers import BotConditionHelper


class TestBotConditionsAggressive:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.conditions = [
            BotCondition(
                id=1,
                condition_on=ConditionON.EVERY_LOSS,
                condition_on_value=1,
                condition_on_value_2=None,
                actions=[
                    BotConditionAction(
                        condition_action=ConditionAction.RESET_BET_AMOUNT,
                        action_value=0,
                    ),
                    BotConditionAction(
                        condition_action=ConditionAction.UPDATE_MULTIPLIER,
                        action_value=2.5,
                    ),
                ],
                others={},
            ),
            BotCondition(
                id=3,
                condition_on=ConditionON.STREAK_LOSSES,
                condition_on_value=5,
                condition_on_value_2=None,
                actions=[
                    BotConditionAction(
                        condition_action=ConditionAction.UPDATE_MULTIPLIER,
                        action_value=2.7,
                    )
                ],
                others={},
            ),
            BotCondition(
                id=4,
                condition_on=ConditionON.STREAK_LOSSES,
                condition_on_value=8,
                condition_on_value_2=None,
                actions=[
                    BotConditionAction(
                        condition_action=ConditionAction.UPDATE_MULTIPLIER,
                        action_value=3.2,
                    )
                ],
                others={},
            ),
            BotCondition(
                id=5,
                condition_on=ConditionON.EVERY_WIN,
                condition_on_value=1,
                condition_on_value_2=None,
                actions=[
                    BotConditionAction(
                        condition_action=ConditionAction.RESET_MULTIPLIER,
                        action_value=0,
                    )
                ],
                others={},
            ),
            BotCondition(
                id=6,
                condition_on=ConditionON.STREAK_WINS,
                condition_on_value=5,
                condition_on_value_2=None,
                actions=[
                    BotConditionAction(
                        condition_action=ConditionAction.INCREASE_BET_AMOUNT,
                        action_value=0.33,
                    )
                ],
                others={},
            ),
        ]

    def test_win_last_game(self):
        helper = BotConditionHelper(
            bot_conditions=self.conditions,
            min_multiplier_to_bet=2,
            min_multiplier_to_recover_losses=2,
            multipliers=[1.0, 1.5, 2.0, 2.5],
        )
        helper.current_bet_amount = 2000
        helper.current_multiplier = 2.5
        helper.last_games = []
        result_ = helper.evaluate_conditions(
            result_last_game=True,
            multiplier_result=2.5,
            profit=0.01,
        )
        bet_amount = result_.bet_amount
        multiplier = result_.multiplier
        ignore_model = result_.ignore_model
        assert bet_amount == 2000
        assert multiplier == 2
        assert ignore_model is False

    def test_first_game(self):
        helper = BotConditionHelper(
            bot_conditions=self.conditions,
            min_multiplier_to_bet=2,
            min_multiplier_to_recover_losses=2,
            multipliers=[1.0, 1.5, 2.0, 2.5],
        )
        helper.current_bet_amount = 2000
        helper.current_multiplier = 2.5
        helper.last_games = []
        result_ = helper.evaluate_conditions(
            result_last_game=True,
            multiplier_result=2.5,
            profit=0.01,
        )
        bet_amount = result_.bet_amount
        multiplier = result_.multiplier
        ignore_model = result_.ignore_model
        assert bet_amount == 2000
        assert multiplier == 2
        assert ignore_model is False

    def test_streak_wins(self):
        helper = BotConditionHelper(
            bot_conditions=self.conditions,
            min_multiplier_to_bet=2,
            min_multiplier_to_recover_losses=2,
            multipliers=[1.0, 1.5, 2.0, 2.5],
        )
        helper.current_bet_amount = 2000
        helper.current_multiplier = 2.5
        helper.last_games = [True, True, True, True]
        result_ = helper.evaluate_conditions(
            result_last_game=True,
            multiplier_result=2.5,
            profit=0.1,
        )
        bet_amount = result_.bet_amount
        multiplier = result_.multiplier
        ignore_model = result_.ignore_model
        assert bet_amount == 2000 * (1 + 0.33)
        assert multiplier == 2
        assert ignore_model is False

    def test_loss_last_game(self):
        helper = BotConditionHelper(
            bot_conditions=self.conditions,
            min_multiplier_to_bet=2,
            min_multiplier_to_recover_losses=2,
            multipliers=[1.0, 1.5, 2.0, 2.5],
        )
        helper.initial_bet_amount = 1000
        helper.current_bet_amount = 2000
        helper.last_games = [False]
        result_ = helper.evaluate_conditions(
            result_last_game=False,
            profit=0.0,
            multiplier_result=2.5,
        )
        bet_amount = result_.bet_amount
        multiplier = result_.multiplier
        ignore_model = result_.ignore_model
        assert bet_amount == 1000
        assert multiplier == 2.5
        assert ignore_model is False

    def test_streak_5_losses(self):
        helper = BotConditionHelper(
            bot_conditions=self.conditions,
            min_multiplier_to_bet=2,
            min_multiplier_to_recover_losses=2,
            multipliers=[1.0, 1.5, 2.0, 2.5],
        )
        helper.initial_bet_amount = 1000
        helper.current_bet_amount = 2000
        helper.last_games = [False, False, False, False]
        result_ = helper.evaluate_conditions(
            result_last_game=False,
            multiplier_result=2.5,
            profit=0.0,
        )
        bet_amount = result_.bet_amount
        multiplier = result_.multiplier
        ignore_model = result_.ignore_model
        assert bet_amount == 1000
        assert multiplier == 2.7
        assert ignore_model is False

    def test_streak_8_losses(self):
        helper = BotConditionHelper(
            bot_conditions=self.conditions,
            min_multiplier_to_bet=2,
            min_multiplier_to_recover_losses=2,
            multipliers=[1.0, 1.5, 2.0, 2.5],
        )
        helper.initial_bet_amount = 1000
        helper.current_bet_amount = 2000
        helper.last_games = [False, False, False, False, False, False, False]
        result_ = helper.evaluate_conditions(
            result_last_game=False,
            multiplier_result=2.5,
            profit=0.0,
        )
        bet_amount = result_.bet_amount
        multiplier = result_.multiplier
        ignore_model = result_.ignore_model
        assert bet_amount == 1000
        assert multiplier == 3.2
        assert ignore_model is False

    def test_streak_n_multiplier_less_than(self):
        conditions = self.conditions
        conditions.append(
            BotCondition(
                id=7,
                condition_on=ConditionON.STREAK_N_MULTIPLIER_LESS_THAN,
                condition_on_value=5.0,
                condition_on_value_2=2.0,
                actions=[
                    BotConditionAction(
                        condition_action=ConditionAction.MAKE_BET,
                        action_value=0,
                    )
                ],
                others={},
            )
        )
        helper = BotConditionHelper(
            bot_conditions=conditions,
            min_multiplier_to_bet=2,
            min_multiplier_to_recover_losses=2,
            multipliers=[1.0, 1.0, 1.0, 1.0],
        )
        helper.initial_bet_amount = 1000
        helper.current_bet_amount = 2000
        helper.last_games = [False, True]
        result_ = helper.evaluate_conditions(
            result_last_game=False,
            multiplier_result=1.5,
            profit=0.0,
        )
        bet_amount = result_.bet_amount
        multiplier = result_.multiplier
        ignore_model = result_.ignore_model
        assert bet_amount == 0
        assert multiplier == 0
        assert ignore_model is False

    def test_streak_n_multiplier_less_than_2(self):
        conditions = self.conditions
        conditions += [
            BotCondition(
                id=7,
                condition_on=ConditionON.STREAK_N_MULTIPLIER_LESS_THAN,
                condition_on_value=10.0,
                condition_on_value_2=2.0,
                actions=[
                    BotConditionAction(
                        condition_action=ConditionAction.MAKE_BET,
                        action_value=1,
                    )
                ],
                others={},
            ),
            BotCondition(
                id=8,
                condition_on=ConditionON.STREAK_N_MULTIPLIER_LESS_THAN,
                condition_on_value=10.0,
                condition_on_value_2=2.0,
                actions=[
                    BotConditionAction(
                        condition_action=ConditionAction.INCREASE_BET_AMOUNT,
                        action_value=0.5,
                    )
                ],
                others={},
            ),
        ]
        helper = BotConditionHelper(
            bot_conditions=conditions,
            min_multiplier_to_bet=2,
            min_multiplier_to_recover_losses=2,
            multipliers=[1, 1, 1, 1, 1, 1, 1, 1, 1, 1.99],
        )
        helper.initial_bet_amount = 1000
        helper.current_bet_amount = 2000
        helper.last_games = []
        result_ = helper.evaluate_conditions(
            result_last_game=False,
            multiplier_result=1.84,
            profit=0.0,
        )
        bet_amount = result_.bet_amount
        multiplier = result_.multiplier
        ignore_model = result_.ignore_model
        _bet_amount = helper.initial_bet_amount * (1 + 0.5)
        assert bet_amount == _bet_amount
        assert multiplier == 2.5
        assert ignore_model is False

    def test_streak_n_multiplier_greater_than(self):
        conditions = self.conditions
        conditions.append(
            BotCondition(
                id=7,
                condition_on=ConditionON.STREAK_N_MULTIPLIER_GREATER_THAN,
                condition_on_value=3.0,
                condition_on_value_2=2.0,
                actions=[
                    BotConditionAction(
                        condition_action=ConditionAction.MAKE_BET,
                        action_value=0,
                    )
                ],
                others={},
            )
        )
        helper = BotConditionHelper(
            bot_conditions=conditions,
            min_multiplier_to_bet=2,
            min_multiplier_to_recover_losses=2,
            multipliers=[1.0, 1.0, 4.0, 5.0],
        )
        helper.initial_bet_amount = 1000
        helper.current_bet_amount = 2000
        helper.last_games = [False, True]
        result_ = helper.evaluate_conditions(
            result_last_game=True,
            multiplier_result=6.5,
            profit=0.0,
        )
        bet_amount = result_.bet_amount
        multiplier = result_.multiplier
        ignore_model = result_.ignore_model
        assert bet_amount == 0
        assert multiplier == 0
        assert ignore_model is False

    def test_example_streak_4(self):
        conditions = [
            BotCondition(
                id=1,
                condition_on=ConditionON.EVERY_LOSS,
                condition_on_value=1,
                condition_on_value_2=None,
                actions=[
                    BotConditionAction(
                        condition_action=ConditionAction.RESET_BET_AMOUNT,
                        action_value=0,
                    ),
                    BotConditionAction(
                        condition_action=ConditionAction.UPDATE_MULTIPLIER,
                        action_value=2.0,
                    ),
                ],
                others={},
            ),
            BotCondition(
                id=3,
                condition_on=ConditionON.STREAK_LOSSES,
                condition_on_value=4,
                condition_on_value_2=None,
                actions=[
                    BotConditionAction(
                        condition_action=ConditionAction.UPDATE_MULTIPLIER,
                        action_value=2.3,
                    )
                ],
                others={},
            ),
            BotCondition(
                id=4,
                condition_on=ConditionON.STREAK_LOSSES,
                condition_on_value=5,
                condition_on_value_2=None,
                actions=[
                    BotConditionAction(
                        condition_action=ConditionAction.UPDATE_MULTIPLIER,
                        action_value=2.5,
                    )
                ],
                others={},
            ),
            BotCondition(
                id=5,
                condition_on=ConditionON.STREAK_LOSSES,
                condition_on_value=8,
                condition_on_value_2=None,
                actions=[
                    BotConditionAction(
                        condition_action=ConditionAction.UPDATE_MULTIPLIER,
                        action_value=3.0,
                    )
                ],
                others={},
            ),
            BotCondition(
                id=6,
                condition_on=ConditionON.EVERY_WIN,
                condition_on_value=1,
                condition_on_value_2=None,
                actions=[
                    BotConditionAction(
                        condition_action=ConditionAction.RESET_MULTIPLIER,
                        action_value=0,
                    )
                ],
                others={},
            ),
            BotCondition(
                id=6,
                condition_on=ConditionON.STREAK_WINS,
                condition_on_value=5,
                condition_on_value_2=None,
                actions=[
                    BotConditionAction(
                        condition_action=ConditionAction.INCREASE_BET_AMOUNT,
                        action_value=0.33,
                    )
                ],
                others={},
            ),
        ]
        helper = BotConditionHelper(
            bot_conditions=conditions,
            min_multiplier_to_bet=2,
            min_multiplier_to_recover_losses=2,
            multipliers=[1.0, 1.0, 1.5],
        )
        helper.initial_bet_amount = 1000
        helper.current_bet_amount = 2000
        helper.last_games = [False, False, False]
        result_ = helper.evaluate_conditions(
            result_last_game=False,
            multiplier_result=1.6,
            profit=0.0,
        )
        bet_amount = result_.bet_amount
        multiplier = result_.multiplier
        ignore_model = result_.ignore_model
        assert bet_amount == 1000
        assert multiplier == 2.3
        assert ignore_model is False

    def test_example_streak_4_with_win(self):
        conditions = [
            BotCondition(
                id=1,
                condition_on=ConditionON.EVERY_LOSS,
                condition_on_value=1,
                condition_on_value_2=None,
                actions=[
                    BotConditionAction(
                        condition_action=ConditionAction.RESET_BET_AMOUNT,
                        action_value=0,
                    ),
                    BotConditionAction(
                        condition_action=ConditionAction.UPDATE_MULTIPLIER,
                        action_value=2.0,
                    ),
                ],
                others={},
            ),
            BotCondition(
                id=3,
                condition_on=ConditionON.STREAK_LOSSES,
                condition_on_value=4,
                condition_on_value_2=None,
                actions=[
                    BotConditionAction(
                        condition_action=ConditionAction.UPDATE_MULTIPLIER,
                        action_value=2.3,
                    )
                ],
                others={},
            ),
            BotCondition(
                id=4,
                condition_on=ConditionON.STREAK_LOSSES,
                condition_on_value=5,
                condition_on_value_2=None,
                actions=[
                    BotConditionAction(
                        condition_action=ConditionAction.UPDATE_MULTIPLIER,
                        action_value=2.5,
                    )
                ],
                others={},
            ),
            BotCondition(
                id=5,
                condition_on=ConditionON.STREAK_LOSSES,
                condition_on_value=8,
                condition_on_value_2=None,
                actions=[
                    BotConditionAction(
                        condition_action=ConditionAction.UPDATE_MULTIPLIER,
                        action_value=3.0,
                    )
                ],
                others={},
            ),
            BotCondition(
                id=6,
                condition_on=ConditionON.EVERY_WIN,
                condition_on_value=1,
                condition_on_value_2=None,
                actions=[
                    BotConditionAction(
                        condition_action=ConditionAction.RESET_MULTIPLIER,
                        action_value=0,
                    )
                ],
                others={},
            ),
            BotCondition(
                id=6,
                condition_on=ConditionON.EVERY_WIN,
                condition_on_value=1,
                condition_on_value_2=None,
                actions=[
                    BotConditionAction(
                        condition_action=ConditionAction.RESET_BET_AMOUNT,
                        action_value=0,
                    )
                ],
                others={},
            ),
            BotCondition(
                id=6,
                condition_on=ConditionON.STREAK_WINS,
                condition_on_value=5,
                condition_on_value_2=None,
                actions=[
                    BotConditionAction(
                        condition_action=ConditionAction.INCREASE_BET_AMOUNT,
                        action_value=0.33,
                    )
                ],
                others={},
            ),
        ]
        helper = BotConditionHelper(
            bot_conditions=conditions,
            min_multiplier_to_bet=2,
            min_multiplier_to_recover_losses=2,
            multipliers=[1.0, 1.0, 1.5, 1.6],
        )
        helper.initial_bet_amount = 1000
        helper.current_bet_amount = 2000
        helper.last_games = [False, False, False, False]
        result_ = helper.evaluate_conditions(
            result_last_game=True,
            multiplier_result=2.6,
            profit=0.0,
        )
        bet_amount = result_.bet_amount
        multiplier = result_.multiplier
        ignore_model = result_.ignore_model
        assert bet_amount == 1000
        assert multiplier == 2
        assert ignore_model is False

    def test_example_two_loss_no_next(self):
        conditions = [
            BotCondition(
                id=6,
                condition_on=ConditionON.EVERY_WIN,
                condition_on_value=1,
                condition_on_value_2=None,
                actions=[
                    BotConditionAction(
                        condition_action=ConditionAction.RESET_MULTIPLIER,
                        action_value=0,
                    ),
                    BotConditionAction(
                        condition_action=ConditionAction.RESET_BET_AMOUNT,
                        action_value=0,
                    ),
                ],
                others={},
            ),
            BotCondition(
                id=1,
                condition_on=ConditionON.EVERY_LOSS,
                condition_on_value=1,
                condition_on_value_2=None,
                actions=[
                    BotConditionAction(
                        condition_action=ConditionAction.RESET_BET_AMOUNT,
                        action_value=0,
                    ),
                    BotConditionAction(
                        condition_action=ConditionAction.UPDATE_MULTIPLIER,
                        action_value=1.5,
                    ),
                ],
                others={},
            ),
            BotCondition(
                id=3,
                condition_on=ConditionON.STREAK_LOSSES,
                condition_on_value=2,
                condition_on_value_2=None,
                actions=[
                    BotConditionAction(
                        condition_action=ConditionAction.UPDATE_MULTIPLIER,
                        action_value=2.3,
                    )
                ],
                others={},
            ),
        ]
        helper = BotConditionHelper(
            bot_conditions=conditions,
            min_multiplier_to_bet=2,
            min_multiplier_to_recover_losses=2,
            multipliers=[1.0, 1.0, 1.5, 1.6],
        )
        helper.initial_bet_amount = 1000
        helper.current_bet_amount = 2000
        helper.last_games = [False, False, False, False]
        result_ = helper.evaluate_conditions(
            result_last_game=False,
            multiplier_result=1,
            profit=0.0,
        )
        bet_amount = result_.bet_amount
        multiplier = result_.multiplier
        ignore_model = result_.ignore_model
        assert bet_amount == 1000
        assert multiplier == 2.3
        assert ignore_model is False

    def test_example_two_loss_no_next_2(self):
        conditions = [
            BotCondition(
                id=6,
                condition_on=ConditionON.EVERY_WIN,
                condition_on_value=1,
                condition_on_value_2=None,
                actions=[
                    BotConditionAction(
                        condition_action=ConditionAction.RESET_MULTIPLIER,
                        action_value=0,
                    ),
                    BotConditionAction(
                        condition_action=ConditionAction.RESET_BET_AMOUNT,
                        action_value=0,
                    ),
                ],
                others={},
            ),
            BotCondition(
                id=1,
                condition_on=ConditionON.EVERY_LOSS,
                condition_on_value=1,
                condition_on_value_2=None,
                actions=[
                    BotConditionAction(
                        condition_action=ConditionAction.RESET_BET_AMOUNT,
                        action_value=0,
                    ),
                    BotConditionAction(
                        condition_action=ConditionAction.UPDATE_MULTIPLIER,
                        action_value=1.5,
                    ),
                ],
                others={},
            ),
            BotCondition(
                id=3,
                condition_on=ConditionON.STREAK_LOSSES,
                condition_on_value=2,
                condition_on_value_2=None,
                actions=[
                    BotConditionAction(
                        condition_action=ConditionAction.UPDATE_MULTIPLIER,
                        action_value=2.3,
                    )
                ],
                others={},
            ),
        ]
        helper = BotConditionHelper(
            bot_conditions=conditions,
            min_multiplier_to_bet=2,
            min_multiplier_to_recover_losses=2,
            multipliers=[1.0, 1.0, 1.5, 1.6],
        )
        helper.initial_bet_amount = 1000
        helper.current_bet_amount = 2000
        helper.last_games = [
            False,
            False,
            False,
            False,
            True,
            False,
            False,
            True,
        ]
        result_ = helper.evaluate_conditions(
            result_last_game=False,
            multiplier_result=1,
            profit=0.0,
        )
        bet_amount = result_.bet_amount
        multiplier = result_.multiplier
        ignore_model = result_.ignore_model
        assert bet_amount == 1000
        assert multiplier == 1.5
        assert ignore_model is False

    def test_example_two_loss_no_next_3(self):
        conditions = [
            BotCondition(
                id=6,
                condition_on=ConditionON.EVERY_WIN,
                condition_on_value=1,
                condition_on_value_2=None,
                actions=[
                    BotConditionAction(
                        condition_action=ConditionAction.RESET_MULTIPLIER,
                        action_value=0,
                    ),
                    BotConditionAction(
                        condition_action=ConditionAction.RESET_BET_AMOUNT,
                        action_value=0,
                    ),
                ],
                others={},
            ),
            BotCondition(
                id=1,
                condition_on=ConditionON.EVERY_LOSS,
                condition_on_value=1,
                condition_on_value_2=None,
                actions=[
                    BotConditionAction(
                        condition_action=ConditionAction.RESET_BET_AMOUNT,
                        action_value=0,
                    ),
                    BotConditionAction(
                        condition_action=ConditionAction.UPDATE_MULTIPLIER,
                        action_value=1.5,
                    ),
                ],
                others={},
            ),
            BotCondition(
                id=3,
                condition_on=ConditionON.STREAK_LOSSES,
                condition_on_value=2,
                condition_on_value_2=None,
                actions=[
                    BotConditionAction(
                        condition_action=ConditionAction.UPDATE_MULTIPLIER,
                        action_value=2.3,
                    )
                ],
                others={},
            ),
        ]
        helper = BotConditionHelper(
            bot_conditions=conditions,
            min_multiplier_to_bet=2,
            min_multiplier_to_recover_losses=2,
            multipliers=[1.0, 1.0, 1.5, 1.6],
        )
        helper.initial_bet_amount = 1000
        helper.current_bet_amount = 2000
        helper.last_games = []
        result_ = helper.evaluate_conditions(
            result_last_game=False,
            multiplier_result=1,
            profit=0.0,
        )
        bet_amount = result_.bet_amount
        multiplier = result_.multiplier
        ignore_model = result_.ignore_model
        assert bet_amount == 1000
        assert multiplier == 1.5
        assert ignore_model is False

        result_ = helper.evaluate_conditions(
            result_last_game=False,
            multiplier_result=1,
            profit=0.0,
        )
        bet_amount = result_.bet_amount
        multiplier = result_.multiplier
        ignore_model = result_.ignore_model
        assert bet_amount == 1000
        assert multiplier == 2.3
        assert ignore_model is False

        result_ = helper.evaluate_conditions(
            result_last_game=True,
            multiplier_result=1,
            profit=0.0,
        )
        bet_amount = result_.bet_amount
        multiplier = result_.multiplier
        ignore_model = result_.ignore_model
        assert bet_amount == 1000
        assert multiplier == 2
        assert ignore_model is False

        result_ = helper.evaluate_conditions(
            result_last_game=False,
            multiplier_result=1.9,
            profit=0.0,
        )
        bet_amount = result_.bet_amount
        multiplier = result_.multiplier
        ignore_model = result_.ignore_model
        assert bet_amount == 1000
        assert multiplier == 1.5
        assert ignore_model is False
