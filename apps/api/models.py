# Standard Library
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

# Internal
from apps.constants import BetType


@dataclass
class LimitModel:
    max_bet: float
    min_bet: float
    amount_multiple: float


@dataclass
class HomeBetModel:
    id: int
    name: str
    url: str
    limits: dict[str, LimitModel]

    def __post_init__(self):
        limits_ = {}
        for key in self.limits.keys():
            value = self.limits[key]
            if isinstance(self.limits[key], dict):
                value = LimitModel(**value)  # noqa
            limits_.update({key: value})
        self.limits = limits_

    def _get_limits(self) -> LimitModel:
        # Internal
        from apps.globals import GlobalVars

        currency = GlobalVars.get_currency()
        if not currency:
            currency = list(self.limits.keys())[0]
        return self.limits[currency]

    @property
    def min_bet(self) -> float:
        return self._get_limits().min_bet

    @property
    def max_bet(self) -> float:
        return self._get_limits().max_bet

    @property
    def amount_multiple(self) -> float:
        return self._get_limits().amount_multiple


@dataclass
class Prediction:
    id: int
    prediction: float
    prediction_round: int
    probability: float
    average_predictions: float
    category_percentage: float


@dataclass
class BetData:
    external_id: str
    prediction: float
    multiplier: float
    amount: float
    multiplier_result: Optional[float] = None
    bet_type: Optional[str] = BetType.AUTOMATIC.value


@dataclass
class BotConditionAction:
    condition_action: str
    action_value: float


@dataclass
class BotCondition:
    id: int
    condition_on: str
    condition_on_value: float
    actions: list[BotConditionAction]
    others: dict
    condition_on_value_2: Optional[float] = None

    def __post_init__(self):
        self.actions = [
            BotConditionAction(**action)
            if isinstance(action, dict)
            else action
            for action in self.actions  # noqa
        ]


class Bot:
    def __init__(
        self,
        id: int,
        name: str,
        bot_type: str,
        number_of_min_bets_allowed_in_bank: int,
        risk_factor: float,
        min_multiplier_to_bet: float,
        min_multiplier_to_recover_losses: float,
        min_probability_to_bet: float,
        min_category_percentage_to_bet: float,
        max_recovery_percentage_on_max_bet: float,
        min_average_model_prediction: float,
        stop_loss_percentage: float,
        take_profit_percentage: float,
        conditions: list[dict[str, any]],
        **__kwargs,
    ):
        self.id = id
        self.name = name
        self.bot_type = bot_type
        self.number_of_min_bets_allowed_in_bank = (
            number_of_min_bets_allowed_in_bank
        )
        self.risk_factor = risk_factor
        self.min_multiplier_to_bet = min_multiplier_to_bet
        self.min_multiplier_to_recover_losses = (
            min_multiplier_to_recover_losses
        )
        self.min_probability_to_bet = min_probability_to_bet
        self.min_category_percentage_to_bet = min_category_percentage_to_bet
        self.max_recovery_percentage_on_max_bet = (
            max_recovery_percentage_on_max_bet
        )
        self.min_average_model_prediction = min_average_model_prediction
        self.stop_loss_percentage = stop_loss_percentage
        self.take_profit_percentage = take_profit_percentage
        self.conditions = [
            BotCondition(**condition) for condition in conditions
        ]


@dataclass
class CrashApp:
    version: str
    home_bet_game_id: int
    home_bets: list[HomeBetModel]

    def __post_init__(self):
        self.home_bets = [
            HomeBetModel(**home_bet) for home_bet in self.home_bets  # noqa
        ]


@dataclass
class PlanData:
    name: str
    with_ai: bool
    start_dt: datetime
    end_dt: datetime
    is_active: bool
    crash_app: CrashApp

    def __post_init__(self):
        if isinstance(self.crash_app, dict):
            self.crash_app = CrashApp(**self.crash_app)  # noqa


@dataclass
class CustomerData:
    customer_id: int
    plan: PlanData

    def __post_init__(self):
        if isinstance(self.plan, dict):
            self.plan = PlanData(**self.plan)


@dataclass
class CustomerLiveData:
    allowed_to_save_multiplier: bool


@dataclass
class Positions:
    count: int
    positions: dict[int, int]


@dataclass
class MultiplierPositions:
    all_time: dict[int, Positions]
    today: dict[int, Positions]


@dataclass
class Multiplier:
    multiplier: float
    multiplier_dt: datetime

    def __dict__(self):
        multiplier_dt = self.multiplier_dt.strftime("%Y-%m-%d %H:%M:%S")
        return dict(
            multiplier=self.multiplier,
            multiplier_dt=multiplier_dt,
        )
