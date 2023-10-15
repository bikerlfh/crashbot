# Internal
from apps.api.models import BotCondition
from apps.game.bots.constants import ConditionAction, ConditionON
from apps.game.bots.helpers import BotConditionHelper


class TestBotConditionsStreakNMultiplierLessThan:
    def test_example_streak_10_multiplier_less_10(self):
        conditions = [
            BotCondition(
                id=1,
                condition_on=ConditionON.EVERY_WIN,
                condition_on_value=1,
                condition_on_value_2=None,
                condition_action=ConditionAction.RESET_MULTIPLIER,
                action_value=0,
                others={},
            ),
            BotCondition(
                id=2,
                condition_on=ConditionON.EVERY_WIN,
                condition_on_value=1,
                condition_on_value_2=None,
                condition_action=ConditionAction.RESET_BET_AMOUNT,
                action_value=0,
                others={},
            ),
            BotCondition(
                id=3,
                condition_on=ConditionON.STREAK_N_MULTIPLIER_LESS_THAN,
                condition_on_value=10.0,
                condition_on_value_2=10.0,
                condition_action=ConditionAction.UPDATE_MULTIPLIER,
                action_value=10.0,
                others={},
            ),
        ]
        helper = BotConditionHelper(
            bot_conditions=conditions,
            min_multiplier_to_bet=2,
            min_multiplier_to_recover_losses=2,
            multipliers=[1.0, 1.0, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 5.0],
        )
        helper.initial_bet_amount = 1000
        helper.current_bet_amount = 2000
        helper.last_games = [False, False, False, False]
        bet_amount, multiplier, ignore_model = helper.evaluate_conditions(
            result_last_game=True,
            multiplier_result=2.6,
            profit=0.0,
        )
        assert bet_amount == 1000
        assert multiplier == 10
        assert ignore_model is False

    def test_example_streak_10_multiplier_less_10_win_to_11(self):
        conditions = [
            BotCondition(
                id=1,
                condition_on=ConditionON.EVERY_WIN,
                condition_on_value=1,
                condition_on_value_2=None,
                condition_action=ConditionAction.RESET_MULTIPLIER,
                action_value=0,
                others={},
            ),
            BotCondition(
                id=2,
                condition_on=ConditionON.EVERY_WIN,
                condition_on_value=1,
                condition_on_value_2=None,
                condition_action=ConditionAction.RESET_BET_AMOUNT,
                action_value=0,
                others={},
            ),
            BotCondition(
                id=3,
                condition_on=ConditionON.STREAK_N_MULTIPLIER_LESS_THAN,
                condition_on_value=10.0,
                condition_on_value_2=10.0,
                condition_action=ConditionAction.UPDATE_MULTIPLIER,
                action_value=10.0,
                others={},
            ),
        ]
        helper = BotConditionHelper(
            bot_conditions=conditions,
            min_multiplier_to_bet=2,
            min_multiplier_to_recover_losses=2,
            multipliers=[1.0, 1.0, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 5.0, 2.6],
        )
        helper.initial_bet_amount = 1000
        helper.current_bet_amount = 2000
        helper.last_games = [False, False, False, False]
        bet_amount, multiplier, ignore_model = helper.evaluate_conditions(
            result_last_game=True,
            multiplier_result=12.6,
            profit=0.0,
        )
        assert bet_amount == 1000
        assert multiplier == 2
        assert ignore_model is False

    def test_example_streak_multiplier_less_same(self):
        """
        Test streak 10 multiplier less than 10
        in the configuration we have 2 condition with the same streak
        :return:
        """
        conditions = [
            BotCondition(
                id=1,
                condition_on=ConditionON.EVERY_WIN,
                condition_on_value=1,
                condition_on_value_2=None,
                condition_action=ConditionAction.RESET_MULTIPLIER,
                action_value=0,
                others={},
            ),
            BotCondition(
                id=2,
                condition_on=ConditionON.EVERY_WIN,
                condition_on_value=1,
                condition_on_value_2=None,
                condition_action=ConditionAction.RESET_BET_AMOUNT,
                action_value=0,
                others={},
            ),
            BotCondition(
                id=3,
                condition_on=ConditionON.STREAK_N_MULTIPLIER_LESS_THAN,
                condition_on_value=10.0,
                condition_on_value_2=10.0,
                condition_action=ConditionAction.UPDATE_MULTIPLIER,
                action_value=10.0,
                others={},
            ),
            BotCondition(
                id=4,
                condition_on=ConditionON.STREAK_N_MULTIPLIER_LESS_THAN,
                condition_on_value=10.0,
                condition_on_value_2=5.0,
                condition_action=ConditionAction.UPDATE_MULTIPLIER,
                action_value=5.0,
                others={},
            ),
        ]
        helper = BotConditionHelper(
            bot_conditions=conditions,
            min_multiplier_to_bet=2,
            min_multiplier_to_recover_losses=2,
            multipliers=[1.0, 1.0, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.0, 2.6],
        )
        helper.initial_bet_amount = 1000
        helper.current_bet_amount = 2000
        helper.last_games = [False, False, False, False]
        bet_amount, multiplier, ignore_model = helper.evaluate_conditions(
            result_last_game=True,
            multiplier_result=1.6,
            profit=0.0,
        )
        assert bet_amount == 1000
        assert multiplier == 10
        assert ignore_model is False

    def test_example_streak_multiplier_less_same_2(self):
        """
        Test streak 10 multiplier less than 10
        in the configuration we have 2 condition with different same streak
        :return:
        """
        conditions = [
            BotCondition(
                id=1,
                condition_on=ConditionON.EVERY_WIN,
                condition_on_value=1,
                condition_on_value_2=None,
                condition_action=ConditionAction.RESET_MULTIPLIER,
                action_value=0,
                others={},
            ),
            BotCondition(
                id=2,
                condition_on=ConditionON.EVERY_WIN,
                condition_on_value=1,
                condition_on_value_2=None,
                condition_action=ConditionAction.RESET_BET_AMOUNT,
                action_value=0,
                others={},
            ),
            BotCondition(
                id=3,
                condition_on=ConditionON.STREAK_N_MULTIPLIER_LESS_THAN,
                condition_on_value=10.0,
                condition_on_value_2=10.0,
                condition_action=ConditionAction.UPDATE_MULTIPLIER,
                action_value=10.0,
                others={},
            ),
            BotCondition(
                id=4,
                condition_on=ConditionON.STREAK_N_MULTIPLIER_LESS_THAN,
                condition_on_value=5.0,
                condition_on_value_2=5.0,
                condition_action=ConditionAction.UPDATE_MULTIPLIER,
                action_value=5.0,
                others={},
            ),
        ]
        helper = BotConditionHelper(
            bot_conditions=conditions,
            min_multiplier_to_bet=2,
            min_multiplier_to_recover_losses=2,
            multipliers=[1.0, 1.0, 1.5, 1.6, 1.7],
        )
        helper.initial_bet_amount = 1000
        helper.current_bet_amount = 2000
        helper.last_games = [False, False, False, False]
        bet_amount, multiplier, ignore_model = helper.evaluate_conditions(
            result_last_game=False,
            multiplier_result=1.6,
            profit=0.0,
        )
        assert bet_amount == 2000
        assert multiplier == 5
        assert ignore_model is False

    def test_example_streak_multiplier_less(self):
        """
        Test streak 10 multiplier less than 10
        in the configuration we have 2 condition with different same streak
        :return:
        """
        conditions = [
            BotCondition(
                id=1,
                condition_on=ConditionON.STREAK_N_MULTIPLIER_LESS_THAN,
                condition_on_value=4.0,
                condition_on_value_2=2.0,
                condition_action=ConditionAction.UPDATE_MULTIPLIER,
                action_value=2.0,
                others={},
            ),
            BotCondition(
                id=2,
                condition_on=ConditionON.STREAK_N_MULTIPLIER_LESS_THAN,
                condition_on_value=5.0,
                condition_on_value_2=5.0,
                condition_action=ConditionAction.UPDATE_MULTIPLIER,
                action_value=5.0,
                others={},
            ),
            BotCondition(
                id=2,
                condition_on=ConditionON.STREAK_N_MULTIPLIER_LESS_THAN,
                condition_on_value=7.0,
                condition_on_value_2=7.0,
                condition_action=ConditionAction.UPDATE_MULTIPLIER,
                action_value=7.0,
                others={},
            ),
            BotCondition(
                id=3,
                condition_on=ConditionON.STREAK_N_MULTIPLIER_LESS_THAN,
                condition_on_value=19.0,
                condition_on_value_2=10.0,
                condition_action=ConditionAction.UPDATE_MULTIPLIER,
                action_value=10.0,
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
        helper.last_games = [False, False, False, False]
        bet_amount, multiplier, ignore_model = helper.evaluate_conditions(
            result_last_game=False,
            multiplier_result=1.6,
            profit=0.0,
        )
        assert bet_amount == 2000
        assert multiplier == 2
        assert ignore_model is False

    def test_example_streak_multiplier_less_1(self):
        """
        Test streak 10 multiplier less than 10
        in the configuration we have 2 condition with different same streak
        :return:
        """
        conditions = [
            BotCondition(
                id=1,
                condition_on=ConditionON.STREAK_N_MULTIPLIER_LESS_THAN,
                condition_on_value=4.0,
                condition_on_value_2=2.0,
                condition_action=ConditionAction.UPDATE_MULTIPLIER,
                action_value=2.0,
                others={},
            ),
            BotCondition(
                id=2,
                condition_on=ConditionON.STREAK_N_MULTIPLIER_LESS_THAN,
                condition_on_value=5.0,
                condition_on_value_2=5.0,
                condition_action=ConditionAction.UPDATE_MULTIPLIER,
                action_value=5.0,
                others={},
            ),
            BotCondition(
                id=2,
                condition_on=ConditionON.STREAK_N_MULTIPLIER_LESS_THAN,
                condition_on_value=7.0,
                condition_on_value_2=7.0,
                condition_action=ConditionAction.UPDATE_MULTIPLIER,
                action_value=7.0,
                others={},
            ),
            BotCondition(
                id=3,
                condition_on=ConditionON.STREAK_N_MULTIPLIER_LESS_THAN,
                condition_on_value=19.0,
                condition_on_value_2=10.0,
                condition_action=ConditionAction.UPDATE_MULTIPLIER,
                action_value=10.0,
                others={},
            ),
        ]
        helper = BotConditionHelper(
            bot_conditions=conditions,
            min_multiplier_to_bet=2,
            min_multiplier_to_recover_losses=2,
            multipliers=[1.0, 1.0, 1.5, 1.4, 1.45],
        )
        helper.initial_bet_amount = 1000
        helper.current_bet_amount = 2000
        helper.last_games = [False, False, False, False]
        bet_amount, multiplier, ignore_model = helper.evaluate_conditions(
            result_last_game=False,
            multiplier_result=1.6,
            profit=0.0,
        )
        assert bet_amount == 2000
        assert multiplier == 5
        assert ignore_model is False

    def test_example_streak_multiplier_less_2(self):
        """
        Test streak 10 multiplier less than 10
        in the configuration we have 2 condition with different same streak
        :return:
        """
        conditions = [
            BotCondition(
                id=1,
                condition_on=ConditionON.STREAK_N_MULTIPLIER_LESS_THAN,
                condition_on_value=4.0,
                condition_on_value_2=2.0,
                condition_action=ConditionAction.UPDATE_MULTIPLIER,
                action_value=2.0,
                others={},
            ),
            BotCondition(
                id=2,
                condition_on=ConditionON.STREAK_N_MULTIPLIER_LESS_THAN,
                condition_on_value=5.0,
                condition_on_value_2=5.0,
                condition_action=ConditionAction.UPDATE_MULTIPLIER,
                action_value=5.0,
                others={},
            ),
            BotCondition(
                id=2,
                condition_on=ConditionON.STREAK_N_MULTIPLIER_LESS_THAN,
                condition_on_value=7.0,
                condition_on_value_2=7.0,
                condition_action=ConditionAction.UPDATE_MULTIPLIER,
                action_value=7.0,
                others={},
            ),
            BotCondition(
                id=3,
                condition_on=ConditionON.STREAK_N_MULTIPLIER_LESS_THAN,
                condition_on_value=19.0,
                condition_on_value_2=10.0,
                condition_action=ConditionAction.UPDATE_MULTIPLIER,
                action_value=10.0,
                others={},
            ),
        ]
        helper = BotConditionHelper(
            bot_conditions=conditions,
            min_multiplier_to_bet=2,
            min_multiplier_to_recover_losses=2,
            multipliers=[1.0, 1.0, 1.5, 1.4, 1.45, 1, 1, 1.2],
        )
        helper.initial_bet_amount = 1000
        helper.current_bet_amount = 2000
        helper.last_games = [False, False, False, False]
        bet_amount, multiplier, ignore_model = helper.evaluate_conditions(
            result_last_game=False,
            multiplier_result=1.6,
            profit=0.0,
        )
        assert bet_amount == 2000
        assert multiplier == 7
        assert ignore_model is False
