"""
this file contains the logic to load custom bots
"""
# Standard Library
import json
import os

# Internal
from apps.api.models import Bot
from apps.constants import BotType


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
        if invalid_values:
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
                strategies=[],
            )
        )
        i -= 1
    return custom_bots
