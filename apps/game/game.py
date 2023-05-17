# Standard Library
from typing import Optional

# Internal
from apps.api import services as api_services
from apps.api.models import BetData, MultiplierPositions
from apps.constants import BotType, HomeBet
from apps.game.bots.bots import Bot, BotStatic
from apps.game.models import Bet, Multiplier
from apps.game.prediction_core import PredictionCore, PredictionModel
from apps.globals import GlobalVars
from apps.gui.gui_events import SendEventToGUI
from apps.scrappers.game_base import AbstractGameBase


class Game:
    MAX_MULTIPLIERS_TO_SAVE: int = 10
    game_page: AbstractGameBase
    minimum_bet: float = 0
    maximum_bet: float = 0
    maximum_win_for_one_bet: float = 0
    _prediction_model: PredictionModel
    initialized: bool = False
    # automatic betting
    bot: Bot | BotStatic
    home_bet: HomeBet
    initial_balance: float = 0
    balance: float = 0
    multipliers: list[Multiplier] = []
    multipliers_to_save: list[float] = []
    bets: list[Bet] = []

    multiplier_positions: MultiplierPositions = None

    def __init__(
        self,
        *,
        home_bet: HomeBet,
        bot_type: BotType,
        use_bot_static: Optional[bool] = True,
    ):
        # TODO: add correct customerId
        self.home_bet: home_bet = home_bet
        self.game_page = self.home_bet.get_game_page()
        self.minimum_bet: float = home_bet.min_bet
        self.maximum_bet: float = home_bet.max_bet
        if not use_bot_static:
            self.bot: Bot = Bot(bot_type, self.minimum_bet, self.maximum_bet)
        else:
            self.bot: BotStatic = BotStatic(
                bot_type, self.minimum_bet, self.maximum_bet
            )
        self.maximum_win_for_one_bet: float = self.maximum_bet * 100
        self._prediction_model: PredictionModel = PredictionModel.get_instance()

    async def initialize(self):
        """
        Init the game
        - init the websocket
        - Open the browser
        """
        SendEventToGUI.log.info("opening home bet.....")
        await self.game_page.open()
        SendEventToGUI.log.debug("reading the player's balance.....")
        self.initial_balance = self.game_page.balance
        self.balance = self.initial_balance
        SendEventToGUI.balance(self.balance)
        SendEventToGUI.log.debug("loading the player.....")
        self.multipliers_to_save = self.game_page.multipliers
        SendEventToGUI.send_multipliers(self.multipliers_to_save)
        self.multipliers = list(
            map(lambda item: Multiplier(item), self.multipliers_to_save)
        )
        self.bot.initialize(
            balance=self.initial_balance,
            multipliers=self.multipliers_to_save,
        )
        self.request_save_multipliers()
        self.initialized = True
        SendEventToGUI.log.success("Game initialized")
        SendEventToGUI.game_loaded(True)

    async def close(self):
        await self.game_page.close()
        # TODO: clean all variables
        self.initialized = False

    async def read_balance_to_aviator(self):
        """
        Read the balance from the Aviator
        """
        return await self.game_page.read_balance() or 0

    def request_multiplier_positions(self):
        """
        Get the multiplier positions from the database
        """
        try:
            self.multiplier_positions = api_services.get_multiplier_positions(
                home_bet_id=self.home_bet.id
            )
            SendEventToGUI.log.debug(f"multiplier positions received")
        except Exception as error:
            SendEventToGUI.log.debug(f"Error in requestMultiplierPositions: {error}")

    def request_save_multipliers(self):
        """
        Save the multipliers in the database
        """
        # TODO fix this
        if not GlobalVars.get_allowed_to_save_multipliers():
            return
        if len(self.multipliers_to_save) < self.MAX_MULTIPLIERS_TO_SAVE:
            return
        try:
            api_services.add_multipliers(
                home_bet_id=self.home_bet.id,
                multipliers=self.multipliers_to_save,
            )
            self.multipliers_to_save = []
            SendEventToGUI.log.debug(f"multipliers saved")
            self.request_multiplier_positions()
        except Exception as error:
            SendEventToGUI.log.debug(f"error in requestSaveMultipliers: {error}")

    def request_save_bets(self):
        """
        Save the bets in the database
        """
        if not self.bets:
            return
        bets_to_save = [
            BetData(
                bet.external_id,
                bet.prediction,
                bet.multiplier,
                round(bet.amount, 2),
                bet.multiplier_result,
            )
            for bet in self.bets
        ]
        SendEventToGUI.log.debug("saving bets.....")
        try:
            api_services.create_bets(
                home_bet_id=self.home_bet.id,
                balance=round(self.balance, 2),
                bets=bets_to_save,
            )
            SendEventToGUI.log.debug(f"bets saved")
        except Exception as error:
            SendEventToGUI.log.debug(f"Error in requestSaveBets :: bet: {error}")

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
            SendEventToGUI.log.debug(f"Error in request_get_prediction: {e}")
            return None
        self._prediction_model.add_predictions(predictions)
        return self._prediction_model.get_best_prediction()

    async def wait_next_game(self):
        """
        Wait for the next game to start
        """
        SendEventToGUI.log.info("waiting for the next game.....")
        await self.game_page.wait_next_game()
        self.balance = await self.read_balance_to_aviator()
        # TODO implement create manual bets
        self.bot.update_balance(self.balance)
        self.add_multiplier(self.game_page.multipliers[-1])
        self.bets = []

    async def send_bets_to_aviator(self):
        """
        Send the bets to the Aviator
        """
        if not self.bets:
            return
        await self.game_page.bet(
            bets=self.bets, use_auto_cash_out=GlobalVars.get_auto_cash_out()
        )

    async def play(self):
        while self.initialized:
            await self.wait_next_game()
            self.get_next_bet()
            await self.send_bets_to_aviator()
            SendEventToGUI.log.info("***************************************")
        SendEventToGUI.log.error("The game is not initialized")

    def evaluate_bets(self, multiplier: float) -> None:
        """
        Evaluate the bets and update the balance
        """
        if not self.bets:
            return
        for bet in self.bets:
            profit = bet.evaluate(multiplier)
            self.balance += profit
        self.bot.evaluate_bets(multiplier)

    def add_multiplier(self, multiplier: float) -> None:
        """
        Add a new multiplier and update the multipliers
        """
        self._prediction_model.add_multiplier_result(multiplier)
        self.evaluate_bets(multiplier)
        self.multipliers.append(Multiplier(multiplier))
        self.bot.add_multiplier(multiplier)
        self.multipliers_to_save.append(multiplier)
        self.request_save_bets()
        self.request_save_multipliers()
        # remove the first multiplier
        self.multipliers = self.multipliers[1:]
        SendEventToGUI.send_multipliers([multiplier])

    def get_next_bet(self) -> list[Bet]:
        """
        Get the next bet from the prediction
        """
        self._prediction_model.evaluate_models(self.bot.MIN_AVERAGE_MODEL_PREDICTION)
        prediction = self.request_get_prediction()
        if prediction is None:
            SendEventToGUI.log.warning("No prediction found")
            return []
        bets = self.bot.get_next_bet(
            prediction=prediction,
            multiplier_positions=self.multiplier_positions,
        )
        if GlobalVars.get_auto_play():
            self.bets = bets
        elif bets:
            SendEventToGUI.log.debug(
                f"possible bets: " f"{[str(vars(bet)) for bet in bets]}"
            )
        return self.bets
