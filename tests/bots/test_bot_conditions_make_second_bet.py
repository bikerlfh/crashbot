# Internal
from apps.api.models import BotCondition, BotConditionAction
from apps.game.bots.constants import ConditionAction, ConditionON
from apps.game.bots.helpers import BotConditionHelper


class TestBotConditionMakeSecondBet:
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
                    BotConditionAction(
                        condition_action=ConditionAction.MAKE_SECOND_BET,
                        action_value=0,
                    ),
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
            multiplier_result=1.6,
            profit=0.0,
        )
        bet_amount = result_.bet_amount
        multiplier = result_.multiplier
        ignore_model = result_.ignore_model
        make_second_bet = result_.make_second_bet
        assert bet_amount == 1000
        assert multiplier == 2
        assert ignore_model is False
        assert make_second_bet is False
