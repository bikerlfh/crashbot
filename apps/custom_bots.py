"""
this file contains the logic to load custom bots
"""
# Standard Library
import json
import os

# Internal
from apps.api.models import Bot
from apps.constants import BotType


def _validate_conditions(conditions: list[dict]) -> bool:
    invalid_values = False
    i = 1
    for condition in conditions:
        if not isinstance(condition, dict):
            return False
        fields_ = [
            "id",
            "condition_on",
            "condition_on_value",
            # "condition_on_value_2",
            "actions",
        ]

        if not all(key in condition for key in fields_):
            invalid_values = True
        if not isinstance(condition["id"], int):
            print(f"{i} :: invalid id for condition")
            invalid_values = True
        if not isinstance(condition["condition_on"], str):
            print(f"{i} :: invalid condition_on for condition")
            invalid_values = True
        if not isinstance(condition["condition_on_value"], (int, float)):
            print(f"{i} :: invalid condition_on_value for condition")
            invalid_values = True
        if "condition_on_value_2" in condition:
            condition_on_value_2 = condition["condition_on_value_2"]
            if condition_on_value_2 is not None and not isinstance(
                condition_on_value_2, (int, float)
            ):
                print(f"{i} :: invalid condition_on_value_2 for condition")
                invalid_values = True
        if not isinstance(condition["actions"], list):
            print(f"{i} :: invalid actions for condition")
            invalid_values = True
        actions = condition["actions"]
        if not all(isinstance(action, dict) for action in actions):
            print(f"{i} :: invalid actions for condition")
            invalid_values = True
        if not all(
            set(action.keys()) == {"condition_action", "action_value"}
            for action in actions
        ):
            print(f"{i} :: invalid actions for condition")
            invalid_values = True
        i += 1
    return invalid_values


def read_custom_bots() -> list[Bot]:
    """
    read custom bots from file
    """
    # validate if file exists
    custom_bots_file = "custom_bots.json"
    if not os.path.exists(custom_bots_file):
        print("custom bots: file not found")
        return []
    print("loading custom bots")
    # read json file
    with open(custom_bots_file, "r") as file:
        data = json.load(file)
    # validate if data is a list
    if not isinstance(data, list):
        print("custom bots: invalid data")
        return []
    # validate if data is a list of dicts
    if not all(isinstance(item, dict) for item in data):
        print("custom bots: invalid data")
        return []
    # validate if data is a list of dicts with the required keys
    required_keys = [
        "name",
        "bot_type",
        "risk_factor",
        "min_multiplier_to_bet",
        "min_multiplier_to_recover_losses",
        "min_probability_to_bet",
        "min_category_percentage_to_bet",
        "max_recovery_percentage_on_max_bet",
        "min_average_model_prediction",
        "stop_loss_percentage",
        "take_profit_percentage",
        "conditions",
    ]
    if not all(set(item.keys()) == set(required_keys) for item in data):
        print("custom bots: invalid keys")
        return []
    # validate if data is a list of dicts with the required keys and values
    invalid_values = False
    for item in data:
        if not isinstance(item["name"], str):
            print("custom bots: invalid name")
            invalid_values = True
        if item["bot_type"] not in BotType.to_list():
            print("custom bots: invalid bot_type")
            invalid_values = True
        if not isinstance(item["risk_factor"], float):
            print("custom bots: invalid risk_factor")
            invalid_values = True
        if not isinstance(item["min_multiplier_to_bet"], float):
            print("custom bots: invalid min_multiplier_to_bet")
            invalid_values = True
        if not isinstance(item["min_multiplier_to_recover_losses"], float):
            print("custom bots: invalid min_multiplier_to_recover_losses")
            invalid_values = True
        if not isinstance(item["min_probability_to_bet"], float):
            print("custom bots: invalid min_probability_to_bet")
            invalid_values = True
        if not isinstance(item["min_category_percentage_to_bet"], float):
            print("custom bots: invalid min_category_percentage_to_bet")
            invalid_values = True
        if not isinstance(item["max_recovery_percentage_on_max_bet"], float):
            print("custom bots: invalid max_recovery_percentage_on_max_bet")
            invalid_values = True
        if not isinstance(item["min_average_model_prediction"], float):
            print("custom bots: invalid min_average_model_prediction")
            invalid_values = True
        if not isinstance(item["stop_loss_percentage"], float):
            print("custom bots: invalid stop_loss_percentage")
            invalid_values = True
        if not isinstance(item["take_profit_percentage"], float):
            print("custom bots: invalid take_profit_percentage")
            invalid_values = True
        if not isinstance(item["conditions"], list):
            print("custom bots: invalid conditions")
            invalid_values = True
        invalid_conditions = _validate_conditions(item["conditions"])
        if invalid_values or invalid_conditions:
            return []

    # create custom bots
    custom_bots = []
    i = -1
    for item in data:
        custom_bots.append(
            Bot(
                id=i,
                name=item["name"],
                bot_type=item["bot_type"],
                risk_factor=item["risk_factor"],
                min_multiplier_to_bet=item["min_multiplier_to_bet"],
                min_multiplier_to_recover_losses=item[
                    "min_multiplier_to_recover_losses"
                ],
                min_probability_to_bet=item["min_probability_to_bet"],
                min_category_percentage_to_bet=item[
                    "min_category_percentage_to_bet"
                ],
                max_recovery_percentage_on_max_bet=item[
                    "max_recovery_percentage_on_max_bet"
                ],
                min_average_model_prediction=item[
                    "min_average_model_prediction"
                ],
                stop_loss_percentage=item["stop_loss_percentage"],
                take_profit_percentage=item["take_profit_percentage"],
                conditions=item["conditions"],
            )
        )
        i -= 1
    print(f"{len(custom_bots)} custom bots loaded")
    return custom_bots
