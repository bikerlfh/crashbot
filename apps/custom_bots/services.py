"""
this file contains the logic to load custom bots
"""
# Standard Library
import os

# Internal
from apps.api.models import Bot
from apps.custom_bots.handlers import CustomBotsEncryptHandler


def read_custom_bots(custom_bots_path: str) -> list[Bot]:
    """
    read custom bots from file
    @param custom_bots_path: path to custom bots folder
    """
    # validate if file exists
    if not os.path.exists(custom_bots_path):
        return []
    print("loading custom bots")
    bots_handler = CustomBotsEncryptHandler(custom_bots_path)
    custom_bots = bots_handler.load_all()
    print(f"bots loaded: {[bot.name for bot in custom_bots]}")
    return custom_bots
