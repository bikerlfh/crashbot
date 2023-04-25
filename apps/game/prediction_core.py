from typing import Dict
from apps.api.models import Prediction

# from ws.gui_events import send_event_to_gui


class PredictionCore:
    def __init__(self, *, id: int, average_predictions: float):
        self.id = id
        self.average_predictions_of_model = average_predictions
        self.prediction_values = []
        self.prediction_rounds = []
        self.probability_values = []
        self.multiplier_results = []
        self.category_percentages = {
            1: None,
            2: None,
            3: None,
        }
        self.category_percentages_values_in_live = {
            1: None,
            2: None,
            3: None,
        }

    def add_prediction(
        self,
        prediction: float,
        prediction_round: int,
        probability: float,
        average_predictions: float,
        category_percentage: float = 0,
    ):
        self.prediction_values.append(prediction)
        self.prediction_rounds.append(prediction_round)
        self.probability_values.append(probability)
        self.average_predictions_of_model = average_predictions
        if self.category_percentages[prediction_round] is None:
            self.category_percentages[prediction_round] = category_percentage  # NOQA
        if self.category_percentages_values_in_live[prediction_round] is None:
            self.category_percentages_values_in_live[
                prediction_round
            ] = category_percentage  # NOQA
        # sendEventToGUI.log.debug("---------------------- PredictionCore: addPrediction ----------------------")
        # sendEventToGUI.log.debug(f"Model ID: {self.id}")
        # sendEventToGUI.log.debug(f"Added prediction: {prediction}({prediction_round}) - probability: {probability}")

    def add_multiplier_result(self, multiplier: float):
        self.multiplier_results.append(multiplier)
        self.calculate_average_model_prediction()
        self.calculate_category_percentages()

    def calculate_category_percentages(self):
        # send_event_to_gui.log.debug("------------- PredictionCore: calculateCategoryPercentages -------------")
        # send_event_to_gui.log.debug(f"Model ID: {self.id}")
        # send_event_to_gui.log.debug(f"Prediction Rounds: {self.prediction_rounds}")
        # send_event_to_gui.log.debug(f"Prediction Values: {self.prediction_values}")
        # send_event_to_gui.log.debug(f"Multiplier Results: {self.multiplier_results}")
        round_multiplier = 0
        value_round = 0
        value = 0
        for i in range(1, 3):
            count_i = 0
            count = 0
            count_values = 0
            for j in range(len(self.prediction_rounds)):
                value_round = self.prediction_rounds[j]
                value = self.prediction_values[j]
                if value_round == i:
                    count_i += 1
                    round_multiplier = round(self.multiplier_results[j], 0)
                    round_multiplier = 2 if round_multiplier >= 2 else round_multiplier
                    if value_round == round_multiplier:
                        count += 1
                    if value <= self.multiplier_results[j]:
                        count_values += 1
            if count == 0 or count_i == 0:
                continue
            self.category_percentages[i] = round(count / count_i, 2)  # NOQA
            self.category_percentages_values_in_live[i] = round(
                count_values / count_i, 2
            )  # NOQA
            # send_event_to_gui.log.debug(f"Category {i}: {self.category_percentages[i]}")
            # send_event_to_gui.log.debug(f"Category {i} Values: {self.category_percentages_values_in_live[i]}")

    def calculate_average_model_prediction(self):
        # send_event_to_gui.log.debug("------------- PredictionCore: calculateAverageModelPrediction -------------")
        correct_values_count = 0
        round_multiplier = 0
        for i in range(len(self.multiplier_results)):
            round_multiplier = round(self.multiplier_results[i], 0)
            round_multiplier = 2 if round_multiplier >= 2 else round_multiplier
            if self.prediction_rounds[i] == round_multiplier:
                correct_values_count += 1
        self.average_predictions_of_model = round(
            correct_values_count / len(self.multiplier_results), 2
        )
        # send_event_to_gui.log.debug(f"Model ID: {self.id}")
        # send_event_to_gui.log.debug(f"Prediction Rounds: {self.prediction_rounds}")
        # send_event_to_gui.log.debug(f"Multiplier Results: {self.multiplier_results}")
        # send_event_to_gui.log.debug(f"Correct Values: {correct_values_count}")
        # send_event_to_gui.log.debug(f"Count Multiplier Results: {len(self.multiplier_results)}")
        # send_event_to_gui.log.debug(f"Average Predictions: {self.average_predictions_of_model})")

    def get_prediction_value(self) -> int:
        return self.prediction_values[-1]

    def get_prediction_round_value(self) -> int:
        return self.prediction_rounds[-1]

    def get_probability_value(self) -> float:
        return self.probability_values[-1]

    def get_category_percentage(self) -> float:
        return self.category_percentages.get(self.get_prediction_round_value(), 0)

    def get_category_percentage_value_in_live(self) -> float:
        return self.category_percentages_values_in_live.get(
            self.get_prediction_round_value(), 0
        )


class PredictionModel:
    __instance = None
    predictions = []
    MAX_RESULTS_TO_EVALUATE = 18

    def __init__(self):
        if not PredictionModel.__instance:
            PredictionModel.__instance = self

    @staticmethod
    def get_instance():
        if not PredictionModel.__instance:
            PredictionModel.__instance = PredictionModel()
        return PredictionModel.__instance

    def add_predictions(self, predictions: list[Prediction]):
        # send_event_to_gui.log.debug("----------------- PredictionModel: addPredictions ------------------")
        # send_event_to_gui.log.debug(f"Count Predictions: {len(self.predictions)}")
        new_predictions = []
        for prediction in predictions:
            prediction_ = next(
                (item for item in self.predictions if item.id == prediction.id), None
            )
            if not prediction_:
                prediction_ = PredictionCore(
                    id=prediction.id,
                    average_predictions=prediction.average_predictions
                )
                # send_event_to_gui.log.debug(f"New PredictionCore: {prediction.id}")
            prediction_.add_prediction(
                prediction.prediction,
                prediction.prediction_round,
                prediction.probability,
                prediction.average_predictions,
                prediction.category_percentage,
            )
            new_predictions.append(prediction_)
        self.predictions = new_predictions
        # send_event_to_gui.log.debug(f"Next Count Predictions: {len(self.predictions)}")
        # self.predictions = [obj for obj in self.predictions if obj.id in [item.id for item in predictions]]

    def add_multiplier_result(self, multiplier: float):
        for prediction in self.predictions:
            if len(prediction.multiplier_results) < len(prediction.prediction_rounds):
                prediction.add_multiplier_result(multiplier)

    def evaluate_models(self, min_bot_average_prediction_model: float):
        # send_event_to_gui.log.debug("----------------- PredictionModel: evaluateModels ------------------")
        # send_event_to_gui.log.debug(f"Count Prediction: {len(self.predictions)}")
        self.predictions = [
            p
            for p in self.predictions
            if p.average_predictions_of_model > min_bot_average_prediction_model
            or len(p.multiplier_results) < self.MAX_RESULTS_TO_EVALUATE
        ]
        # send_event_to_gui.log.debug(f"Next Count Prediction: {len(self.predictions)}")

    def get_best_prediction(self) -> PredictionCore | None:
        if not self.predictions:
            return None
        best_prediction = self.predictions[0]
        for pre in self.predictions:
            if (
                pre.average_predictions_of_model
                > best_prediction.average_predictions_of_model
            ):
                best_prediction = pre
        # send_event_to_gui.log.debug("----------------- PredictionModel: getBestPrediction ------------------")
        # send_event_to_gui.log.debug(f"Model ID: {best_prediction.id}")
        return best_prediction
