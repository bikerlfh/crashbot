from typing import Optional
from dataclasses import dataclass


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


@dataclass
class BotStrategy:
    number_of_bets: int
    profit_percentage: float
    min_amount_percentage_to_bet: float
    profit_percentage_to_bet: float
    others: dict


class Bot:
    def __init__(
        self,
        id: int,
        bot_type: str,
        risk_factor: float,
        min_multiplier_to_bet: float,
        min_multiplier_to_recover_losses: float,
        min_probability_to_bet: float,
        min_category_percentage_to_bet: float,
        min_category_percentage_value_in_live_to_bet: float,
        min_average_prediction_model_in_live_to_bet: float,
        stop_loss_percentage: float,
        take_profit_percentage: float,
        strategies: list[dict[str, any]],
    ):
        self.id = id
        self.bot_type = bot_type
        self.risk_factor = risk_factor
        self.min_multiplier_to_bet = min_multiplier_to_bet
        self.min_multiplier_to_recover_losses = min_multiplier_to_recover_losses
        self.min_probability_to_bet = min_probability_to_bet
        self.min_category_percentage_to_bet = min_category_percentage_to_bet
        self.min_category_percentage_value_in_live_to_bet = min_category_percentage_value_in_live_to_bet
        self.min_average_prediction_model_in_live_to_bet = min_average_prediction_model_in_live_to_bet
        self.stop_loss_percentage = stop_loss_percentage
        self.take_profit_percentage = take_profit_percentage
        self.strategies = [BotStrategy(**strategy) for strategy in strategies]



