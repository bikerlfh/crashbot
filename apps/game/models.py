# Standard Library
import random
import string
from dataclasses import dataclass
from typing import Optional

# Internal
from apps.gui.gui_events import SendEventToGUI


class Multiplier:
    def __init__(self, multiplier: float):
        self.multiplier = multiplier
        self.category = 1 if multiplier < 2 else 2


class Bet:
    def __init__(
        self,
        amount: float,
        multiplier: float,
        bet_type: Optional[str] = None,
        prediction: Optional[float] = None,
    ):
        # generate external_id with random string of 32 chars
        self.external_id = self.__generate_external_id()
        self.amount = amount
        self.multiplier = multiplier
        self.prediction = prediction or self.multiplier
        self.multiplier_result = None
        self.profit = 0
        self.bet_type = bet_type

    def __str__(self):
        return f"{self.amount} * {self.multiplier}"

    def __generate_external_id(self):
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=16))

    def evaluate(self, multiplier_result: float):
        self.multiplier_result = multiplier_result
        if multiplier_result > self.multiplier:
            self.profit += self.amount * (self.multiplier - 1)
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
    in_average_prediction_of_model: bool

    @staticmethod
    def _show_percentage(value: float) -> str:
        return f"{round(value * 100, 2)}%"

    def print_data(self) -> None:
        SendEventToGUI.log.success(
            f"{_('prediction')}: {self.prediction_round} - " # noqa
            f"{_('probability')}: {self._show_percentage(self.probability)}" # noqa
        )
        SendEventToGUI.log.info(
            f"CatPer: {self._show_percentage(self.category_percentage)} - "
            f"AvgModel: {self._show_percentage(self.average_prediction_of_model)}"
        )
        SendEventToGUI.log.debug(
            f"InCatPer: {self.in_category_percentage} - "
            f"InAvgModel: {self.in_average_prediction_of_model}"
        )
