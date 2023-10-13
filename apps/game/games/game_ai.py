# Standard Library
from typing import Optional

# Internal
from apps.api import services as api_services
from apps.constants import BotType, HomeBet
from apps.game.bots.bot_ai import BotAI
from apps.game.games.constants import GameType
from apps.game.games.game_base import GameBase
from apps.game.models import Bet
from apps.game.prediction_core import PredictionCore, PredictionModel
from apps.globals import GlobalVars
from apps.gui.gui_events import SendEventToGUI
from apps.utils.local_storage import LocalStorage

local_storage = LocalStorage()


class GameAI(GameBase, configuration=GameType.AI.value):
    """
    this game uses the AI model from backend
    """

    _prediction_model: PredictionModel

    def __init__(
        self,
        *,
        home_bet: HomeBet,
        bot_type: BotType,
        **kwargs,
    ):
        super().__init__(home_bet=home_bet, bot_type=bot_type)
        self._prediction_model: PredictionModel = (
            PredictionModel.get_instance()
        )

    def _initialize_bot(self, *, bot_type: BotType):
        self.bot = BotAI(
            bot_type=bot_type,
            minimum_bet=self.minimum_bet,
            maximum_bet=self.maximum_bet,
            amount_multiple=self.home_bet.amount_multiple,
        )

    def request_get_prediction(self) -> Optional[PredictionCore]:
        """
        Get the prediction from the database
        """
        multipliers = [item.multiplier for item in self.multipliers]
        try:
            predictions = api_services.request_prediction(
                home_bet_id=self.home_bet.id, multipliers=multipliers
            )
        except Exception as e:
            SendEventToGUI.log.debug(
                f"{_('Error in request_get_prediction')}: {e}"  # noqa
            )
            return None
        self._prediction_model.add_predictions(predictions)
        return self._prediction_model.get_best_prediction()

    def add_multiplier(self, multiplier: float) -> None:
        """
        Add a new multiplier and update the multipliers
        """
        self._prediction_model.add_multiplier_result(multiplier)
        super().add_multiplier(multiplier)

    def get_next_bet(self) -> list[Bet]:
        """
        Get the next bet from the prediction
        """
        self._prediction_model.evaluate_models(
            self.bot.MIN_AVERAGE_MODEL_PREDICTION
        )
        prediction = self.request_get_prediction()
        if prediction is None:
            SendEventToGUI.log.warning(_("No prediction found"))  # noqa
            return []
        bets = self.bot.get_next_bet(
            prediction=prediction,
            multiplier_positions=self.multiplier_positions,
        )
        if GlobalVars.get_auto_play():
            self.bets = bets
        elif bets:
            _possible_bets = [
                dict(multiplier=bet.multiplier, amount=bet.amount)
                for bet in bets
            ]
            SendEventToGUI.log.debug(f"possible bets: " f"{_possible_bets}")
        return self.bets
