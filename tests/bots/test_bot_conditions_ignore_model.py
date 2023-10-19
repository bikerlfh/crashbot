# Libraries
import pytest

# Internal
from apps.api.models import BotCondition, BotConditionAction
from apps.game.bots.constants import ConditionAction, ConditionON
from apps.game.bots.helpers import BotConditionHelper


class TestBotConditionsIgnoreModel:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.conditions = [
            BotCondition(
                id=1,
                condition_on=ConditionON.EVERY_LOSS,
                condition_on_value=1,
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
                condition_on=ConditionON.EVERY_LOSS,
                condition_on_value=1,
                actions=[
                    BotConditionAction(
                        condition_action=ConditionAction.IGNORE_MODEL,
                        action_value=1,
                    )
                ],
                others={},
            ),
            BotCondition(
                id=4,
                condition_on=ConditionON.EVERY_WIN,
                condition_on_value=1,
                actions=[
                    BotConditionAction(
                        condition_action=ConditionAction.RESET_MULTIPLIER,
                        action_value=0.0,
                    ),
                    BotConditionAction(
                        condition_action=ConditionAction.IGNORE_MODEL,
                        action_value=0.0,
                    ),
                ],
                others={},
            ),
        ]

    def test_ignore_model(self):
        helper = BotConditionHelper(
            bot_conditions=self.conditions,
            min_multiplier_to_bet=2,
            min_multiplier_to_recover_losses=2,
            multipliers=[1.0, 1.5, 2.0, 2.5],
        )
        helper.set_bet_amount(bet_amount=2000, user_change=True)
        helper.current_bet_amount = 5000
        helper.current_multiplier = 2.5
        helper.last_games = []
        bet_amount, multiplier, ignore_model = helper.evaluate_conditions(
            result_last_game=False,
            profit=0.01,
            multiplier_result=2.5,
        )
        assert bet_amount == 2000
        assert multiplier == 2.5
        assert ignore_model is True

    def test_not_ignore_model(self):
        helper = BotConditionHelper(
            bot_conditions=self.conditions,
            min_multiplier_to_bet=2,
            min_multiplier_to_recover_losses=2,
            multipliers=[1.0, 1.5, 2.0, 2.5],
        )
        helper.set_bet_amount(bet_amount=2000, user_change=True)
        helper.current_bet_amount = 5000
        helper.current_multiplier = 2.5
        helper.last_games = [False, False, False]
        bet_amount, multiplier, ignore_model = helper.evaluate_conditions(
            result_last_game=True,
            profit=0.01,
            multiplier_result=2.5,
        )
        assert bet_amount == 5000
        assert multiplier == 2
        assert ignore_model is False
