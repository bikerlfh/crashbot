# Standard Library
import abc

# Internal
from apps.api import services as api_services
from apps.api.models import BetData, MultiplierPositions
from apps.game.bookmakers.home_bet import HomeBet
from apps.game.bots.bot_base import BotBase
from apps.game.models import Bet, Multiplier
from apps.globals import GlobalVars
from apps.gui.gui_events import SendEventToGUI
from apps.scrappers.game_base import AbstractCrashGameBase
from apps.utils.local_storage import LocalStorage
from apps.utils.patterns.factory import ConfigurationFactory

local_storage = LocalStorage()


class GameBase(abc.ABC, ConfigurationFactory):
    """
    To implement a new Game you need to create
    a new class with a configuration.
    The new class needs be imported in the
    file apps/game/games/__init__.py
    """

    MAX_MULTIPLIERS_TO_SAVE: int = 10
    game_page: AbstractCrashGameBase
    minimum_bet: float = 0
    maximum_bet: float = 0
    maximum_win_for_one_bet: float = 0
    initialized: bool = False
    # automatic betting
    customer_id: int = 0
    bot: BotBase
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
        bot_name: str,
        **kwargs,
    ):
        self.customer_id = local_storage.get_customer_id()
        self.home_bet = home_bet
        self.game_page = self.home_bet.get_crash_game()
        self.minimum_bet: float = home_bet.min_bet
        self.maximum_bet: float = home_bet.max_bet

        self._initialize_bot(bot_name=bot_name)
        self.maximum_win_for_one_bet: float = self.maximum_bet * 100

    @abc.abstractmethod
    def _initialize_bot(self, *, bot_name: str):
        ...

    async def initialize(self):
        """
        Init the game
        - init the websocket
        - Open the browser
        """
        SendEventToGUI.log.info(_("opening home bet"))  # noqa
        await self.game_page.open()
        SendEventToGUI.log.info(_("reading the player's balance"))  # noqa
        self.initial_balance = self.game_page.balance
        self.balance = self.initial_balance
        last_balance = local_storage.get_last_initial_balance(
            home_bet_id=self.home_bet.id
        )
        if last_balance and last_balance > self.initial_balance:
            self.initial_balance = last_balance
            SendEventToGUI.log.debug(
                f"Update the initial balance from"
                f" local storage {self.initial_balance}"
            )
        SendEventToGUI.balance(self.balance)
        SendEventToGUI.log.debug("loading the player")
        self.multipliers_to_save = self.game_page.multipliers
        SendEventToGUI.send_multipliers(self.multipliers_to_save)
        self.multipliers = list(
            map(lambda item: Multiplier(item), self.multipliers_to_save)
        )
        self.bot.initialize(
            balance=self.initial_balance,
            multipliers=self.multipliers_to_save,
        )
        self.initialized = True
        self.request_save_multipliers()
        self.request_save_customer_balance()
        SendEventToGUI.log.success(_("Game initialized"))  # noqa
        SendEventToGUI.game_loaded(True)
        self.bot.show_last_position_of_multipliers()

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
            # SendEventToGUI.log.debug("multiplier positions received")
        except Exception as error:
            SendEventToGUI.log.debug(
                f"Error in requestMultiplierPositions: {error}"
            )

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
            # SendEventToGUI.log.debug("multipliers saved")
            self.request_multiplier_positions()
        except Exception as error:
            SendEventToGUI.log.debug(
                f"error in requestSaveMultipliers: {error}"
            )

    def request_save_customer_balance(self):
        """
        Save the customer's balance in the database
        """
        # SendEventToGUI.log.debug("saving balance")
        try:
            api_services.update_customer_balance(
                customer_id=self.customer_id,
                home_bet_id=self.home_bet.id,
                balance=round(self.balance, 2),
            )
            # SendEventToGUI.log.debug("balance saved")
        except Exception as error:
            SendEventToGUI.log.debug(
                f"Error in request_save_customer_balance :: bet :: {error}"
            )

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
        # SendEventToGUI.log.debug(_("saving bets"))  # noqa
        try:
            api_services.create_bets(
                home_bet_id=self.home_bet.id,
                bets=bets_to_save,
            )
            # SendEventToGUI.log.debug(_("bets saved"))  # noqa
        except Exception as error:
            SendEventToGUI.log.debug(
                f"{_('Error in requestSaveBets')} :: {error}"  # noqa
            )

    async def wait_next_game(self):
        """
        Wait for the next game to start
        """
        SendEventToGUI.log.info(_("waiting for the next game"))  # noqa
        await self.game_page.wait_next_game()
        balance = await self.read_balance_to_aviator()
        if balance != self.balance:
            self.balance = balance
            self.request_save_customer_balance()
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

    def evaluate_bets(self, multiplier: float) -> None:
        """
        Evaluate the bets and update the balance
        """
        for bet in self.bets:
            profit = bet.evaluate(multiplier)
            self.balance += profit
        self.bot.evaluate_bets(multiplier)

    def add_multiplier(self, multiplier: float) -> None:
        """
        Add a new multiplier and update the multipliers
        """
        self.evaluate_bets(multiplier)
        self.multipliers.append(Multiplier(multiplier))
        self.bot.add_multiplier(multiplier)
        self.multipliers_to_save.append(multiplier)
        self.request_save_bets()
        self.request_save_multipliers()
        # remove the first multiplier
        self.multipliers = self.multipliers[1:]
        SendEventToGUI.send_multipliers([multiplier])

    async def play(self):
        while self.initialized:
            await self.wait_next_game()
            self.get_next_bet()
            await self.send_bets_to_aviator()
            SendEventToGUI.log.info(
                "*****************************************"
            )
            self.bot.show_last_position_of_multipliers()
        SendEventToGUI.log.error(_("The game is not initialized"))  # noqa

    @abc.abstractmethod
    def get_next_bet(self) -> list[Bet]:
        ...
