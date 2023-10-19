# Standard Library
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

# Internal
from apps.constants import BetType


@dataclass
class HomeBetModel:
    id: int
    name: str
    url: str
    min_bet: float
    max_bet: float


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
class PlanData:
    name: str
    with_ai: bool
    start_dt: datetime
    end_dt: datetime
    is_active: bool


@dataclass
class CustomerData:
    customer_id: int
    home_bets: list[HomeBetModel]
    plan: PlanData


@dataclass
class Positions:
    count: int
    positions: dict[int, int]


@dataclass
class MultiplierPositions:
    all_time: dict[int, Positions]
    today: dict[int, Positions]
