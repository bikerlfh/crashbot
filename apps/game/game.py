from typing import Optional
from apps.game.models import Multiplier, Bet, BotType
from apps.api import services as api_services
from apps.constants import HomeBet
from apps.game.prediction_core import PredictionModel, PredictionCore

# from ws.client import WebSocketClient
from apps.scrappers.aviator.aviator import Aviator
from apps.scrappers.aviator.bet_control import Control
from apps.api.models import BetData
from apps.utils.datetime import sleep_now
from apps.game.bots import Bot, BotStatic

# from ws.gui_events import sendEventToGUI
from apps import globals


class Game:
    MAX_MULTIPLIERS_TO_SAVE: int = 10
    aviator_page: Aviator
    minimum_bet: float = 0
    maximum_bet: float = 0
    maximum_win_for_one_bet: float = 0
    _prediction_model: PredictionModel
    # _ws_client: Optional[WebSocketClient] = None
    initialized: bool = False
    # automatic betting
    bot: Bot | BotStatic
    home_bet: HomeBet
    initial_balance: float = 0
    balance: float = 0
    multipliers: list[Multiplier] = []
    multipliers_to_save: list[float] = []
    bets: list[Bet] = []

    def __init__(
        self,
        *,
        home_bet: HomeBet,
        bot_type: BotType,
        use_bot_static: Optional[bool] = False,
    ):
        # TODO: add correct customerId
        self.home_bet: home_bet = home_bet
        self.aviator_page: Aviator = self.home_bet.get_aviator_page()
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
        # globals.home_betId = self.home_bet.id

    # def ws_on_message(self, event):
    #     """
    #     Handle the websocket messages to create bets
    #     """
    #     try:
    #         data = json.loads(event.data)
    #         home_bet_id = data.get("home_bet_id", None)
    #         min_multiplier = data.get("min_multiplier", None)
    #         max_multiplier = data.get("max_multiplier", None)
    #         chat_id = data.get("chat_id", None)
    #         others = data.get("others", None)
    #         if not all([home_bet_id, min_multiplier, max_multiplier]):
    #             # sendEventToGUI.log.debug(f"socketOnMessage: data incomplete {json.dumps(data)}")
    #             return
    #         if home_bet_id != self.home_bet.id:
    #             # the home bet of the bet is not the same as the current home bet
    #             return
    #         # TODO: fix this. Amount should be calculated from the multiplier
    #         # amount = self.calculate_amount_bet(min_multiplier)
    #         amount = self.bot.validate_bet_amount(round(self.balance * 0.1))
    #         amount2 = self.bot.validate_bet_amount(round(amount / 3))
    #         self.bets.append(Bet(amount, min_multiplier))
    #         self.bets.append(Bet(amount2, max_multiplier))
    #         self.send_bets_to_aviator(self.bets).then(lambda: None).catch(lambda error: self.bets.clear())
    #     except Exception as error:
    #         # sendEventToGUI.log.error(f"socketOnMessage: {error}")

    def initialize(self):
        """
        Init the game
        - init the websocket
        - Open the browser
        """
        # NOTE: activate when the websocket is ready
        # sendLogToGUI("connecting to websocket.....")
        # self._ws_client = WebSocketClient.getInstance()
        # self._ws_client.setOnMessage(self.ws_on_message.bind(self))
        # sendEventToGUI.log.info("opening home bet.....")
        self.aviator_page.open()
        # sendEventToGUI.log.debug("reading the player's balance.....")
        self.initial_balance = self.aviator_page.balance
        self.balance = self.initial_balance
        # sendEventToGUI.balance(self.balance)
        # sendEventToGUI.log.debug("loading the player.....")
        self.multipliers_to_save = self.aviator_page.multipliers
        self.multipliers = list(
            map(lambda item: Multiplier(item), self.multipliers_to_save)
        )
        self.request_save_multipliers()
        self.bot.initialize(self.initial_balance)
        self.initialized = True
        # sendEventToGUI.log.success("Game initialized")

    def close(self):
        self.aviator_page.close()
        # TODO: clean all variables
        self.initialized = False

    def read_balance_to_aviator(self):
        """
        Read the balance from the Aviator
        """
        return self.aviator_page.read_balance() or 0

    def request_save_multipliers(self):
        """
        Save the multipliers in the database
        """
        if len(self.multipliers_to_save) < self.MAX_MULTIPLIERS_TO_SAVE:
            return
        # sendEventToGUI.log.debug("saving multipliers.....")
        try:
            api_services.add_multipliers(
                home_bet_id=self.home_bet.id, multipliers=self.multipliers_to_save
            )
            self.multipliers_to_save = []
            # sendEventToGUI.log.debug(f"multipliers saved: {response.data.multipliers}")
        except Exception as error:
            # sendEventToGUI.log.debug(f"error in requestSaveMultipliers: {error}")
            print(f"error in requestSaveMultipliers: {error}")

    def request_save_bets(self, bets):
        """
        Save the bets in the database
        """
        if not bets:
            return
        bets_to_save = [
            BetData(
                bet.external_id,
                bet.prediction,
                bet.multiplier,
                round(bet.amount, 2),
                bet.multiplier_result,
            )
            for bet in bets
        ]
        # sendEventToGUI.log.debug("saving bets.....")
        try:
            api_services.create_bets(
                home_bet_id=self.home_bet.id,
                balance=round(self.balance, 2),
                bets=bets_to_save,
            )
            # sendEventToGUI.log.debug(f"bets saved: [{response.data.bet_ids}]")
        except Exception as error:
            # sendEventToGUI.log.debug(f"Error in requestSaveBets: {error}")
            print(f"Error in requestSaveBets: {error}")

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
            # sendEventToGUI.log.debug(f"Error in request_get_prediction: {e}")
            return None
        self._prediction_model.add_predictions(predictions)
        return self._prediction_model.get_best_prediction()

    def wait_next_game(self):
        """
        Wait for the next game to start
        """
        self.aviator_page.wait_next_game()
        self.balance = self.read_balance_to_aviator()
        self.bot.update_balance(self.balance)
        self.add_multiplier(self.aviator_page.multipliers[-1])
        self.bets = []

    def send_bets_to_aviator(self, bets: list[Bet]):
        """
        Send the bets to the Aviator
        """
        if not bets:
            return
        for index, bet in enumerate(bets):
            control = Control.Control1 if index == 0 else Control.Control2
            # sendEventToGUI.log.info(f"Sending bet to aviator {bet.amount} * {bet.multiplier} control: {control}")
            self.aviator_page.bet(bet.amount, bet.multiplier, control)
            sleep_now(1000)

    def play(self):
        if not self.initialized:
            # sendEventToGUI.log.error("The game is not initialized")
            return
        while self.initialized:
            self.wait_next_game()
            self.get_next_bet()
            if globals.auto_play:
                self.send_bets_to_aviator(self.bets)
            # sendEventToGUI.log.info("***************************************")

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
        self.multipliers_to_save.append(multiplier)
        self.request_save_bets(self.bets)
        self.request_save_multipliers()
        # remove the first multiplier
        self.multipliers = self.multipliers[1:]

    def get_next_bet(self) -> list[Bet]:
        """
        Get the next bet from the prediction
        """
        self._prediction_model.evaluate_models(
            self.bot.MIN_AVERAGE_PREDICTION_MODEL_IN_LIVE_TO_BET
        )
        prediction = self.request_get_prediction()
        if prediction is None:
            # send_event_to_GUI.log.warning("No prediction found")
            return []
        self.bets = self.bot.get_next_bet(prediction)
        return self.bets
