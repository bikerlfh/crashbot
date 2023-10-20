# Internal
from apps.api.models import BotCondition, BotConditionAction
from apps.game.bots.constants import ConditionAction, ConditionON
from apps.game.bots.helpers import BotConditionHelper


class TestBotConditionMakeBet:
    def test_no_make_bet(self):
        conditions = [
            BotCondition(
                id=1,
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
                id=3,
                condition_on=ConditionON.STREAK_N_MULTIPLIER_LESS_THAN,
                condition_on_value=5.0,
                condition_on_value_2=1.99,
                actions=[
                    BotConditionAction(
                        condition_action=ConditionAction.MAKE_BET,
                        action_value=0,
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
        bet_amount, multiplier, ignore_model = helper.evaluate_conditions(
            result_last_game=True,
            multiplier_result=1.6,
            profit=0.0,
        )
        assert bet_amount == 0
        assert multiplier == 0
        assert ignore_model is False

    def test_no_make_bet_2(self):
        conditions = [
            BotCondition(
                id=1,
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
                id=3,
                condition_on=ConditionON.STREAK_N_MULTIPLIER_LESS_THAN,
                condition_on_value=5.0,
                condition_on_value_2=1.99,
                actions=[
                    BotConditionAction(
                        condition_action=ConditionAction.MAKE_BET,
                        action_value=0,
                    )
                ],
                others={},
            ),
        ]
        helper = BotConditionHelper(
            bot_conditions=conditions,
            min_multiplier_to_bet=2,
            min_multiplier_to_recover_losses=2,
            multipliers=[1.0, 1.0, 1.5, 1.6, 1],
        )
        helper.initial_bet_amount = 1000
        helper.current_bet_amount = 2000
        helper.last_games = [False, False, False, False]
        bet_amount, multiplier, ignore_model = helper.evaluate_conditions(
            result_last_game=False,
            multiplier_result=1.6,
            profit=0.0,
        )
        assert bet_amount == 0
        assert multiplier == 0
        assert ignore_model is False

        bet_amount, multiplier, ignore_model = helper.evaluate_conditions(
            result_last_game=True,
            multiplier_result=3.4,
            profit=0.0,
        )
        assert bet_amount == 1000
        assert multiplier == 2
        assert ignore_model is False

    def test_make_bet_after_no_bet(self):
        conditions = [
            BotCondition(
                id=1,
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
                id=3,
                condition_on=ConditionON.STREAK_N_MULTIPLIER_LESS_THAN,
                condition_on_value=5.0,
                condition_on_value_2=1.99,
                actions=[
                    BotConditionAction(
                        condition_action=ConditionAction.MAKE_BET,
                        action_value=0,
                    )
                ],
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
            result_last_game=True,
            multiplier_result=2.6,
            profit=0.0,
        )
        assert bet_amount == 1000
        assert multiplier == 2
        assert ignore_model is False

    def test_make_bet_after_no_bet_2(self):
        conditions = [
            BotCondition(
                id=1,
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
                id=3,
                condition_on=ConditionON.STREAK_N_MULTIPLIER_LESS_THAN,
                condition_on_value=5.0,
                condition_on_value_2=1.99,
                actions=[
                    BotConditionAction(
                        condition_action=ConditionAction.MAKE_BET,
                        action_value=0,
                    )
                ],
                others={},
            ),
        ]
        helper = BotConditionHelper(
            bot_conditions=conditions,
            min_multiplier_to_bet=2,
            min_multiplier_to_recover_losses=2,
            multipliers=[1.0, 1.0, 1.5, 1.6, 1.7, 2.5],
        )
        helper.initial_bet_amount = 1000
        helper.current_bet_amount = 2000
        helper.last_games = [False, False, False, False]
        bet_amount, multiplier, ignore_model = helper.evaluate_conditions(
            result_last_game=False,
            multiplier_result=1.54,
            profit=0.0,
        )
        assert bet_amount == 2000
        assert multiplier == 2
        assert ignore_model is False
