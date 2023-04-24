from typing import Optional
from dataclasses import dataclass
from enum import Enum
import random
import string


class BotType(Enum):
    AGGRESSIVE = "aggressive"
    TIGHT = "tight"
    LOOSE = "loose"


class Multiplier:
    def __init__(self, multiplier: float):
        self.multiplier = multiplier
        self.category = 1 if multiplier < 2 else 2


class Bet:
    def __init__(
        self, amount: float, multiplier: float, prediction: Optional[float] = None
    ):
        # generate external_id with random string of 32 chars
        self.external_id = self.__generate_external_id()
        self.amount = amount
        self.multiplier = multiplier
        self.prediction = prediction or self.multiplier
        self.multiplierResult = None
        self.profit = 0

    def __generate_external_id(self):
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=16))

    def evaluate(self, multiplier_result: float):
        self.multiplierResult = multiplier_result
        if multiplier_result > self.multiplier:
            self.profit += self.amount * (self.multiplierResult - 1)
        else:
            self.profit -= self.amount
        return round(self.profit, 2)


@dataclass
class PredictionData:
    prediction_value: float
    prediction_round: float
    probability: float
    category_percentage: float
    category_percentage_value_in_live: float
    average_prediction_of_model: float
    in_category_percentage: bool
    in_category_percentage_value_in_live: bool
    in_average_prediction_of_model: bool

    def print_data(self) -> None:
        print(f"Prediction Value: {self.prediction_value}")
        print(f"Prediction Round: {self.prediction_round}")
        print(f"Probability: {self.probability}")
        print(f"Category Percentage: {self.category_percentage}")
        print(
            f"Category Percentage Value In Live: {self.category_percentage_value_in_live}"
        )
        print(f"Average Prediction Of Model: {self.average_prediction_of_model}")
        print(f"In Category Percentage: {self.in_category_percentage}")
        print(
            f"In Category Percentage Value In Live: {self.in_category_percentage_value_in_live}"
        )
        print(f"In Average Prediction Of Model: {self.in_average_prediction_of_model}")
