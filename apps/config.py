# Standard Library
import os
from enum import Enum

# Internal
from apps.utils.patterns.singleton import Singleton

CONFIG_FILE_PATH = "conf.ini"


class Config(metaclass=Singleton):
    class ConfigVar(str, Enum):
        API_URL = "API_URL"
        WS_URL = "WS_URL"
        ALLOWED_LOG_CODES_TO_SHOW = "ALLOWED_LOG_CODES_TO_SHOW"
        MAX_AMOUNT_HOME_BET_PERCENTAGE = "MAX_AMOUNT_HOME_BET_PERCENTAGE"
        MAX_AMOUNT_BALANCE_PERCENTAGE = "MAX_AMOUNT_BALANCE_PERCENTAGE"
        NUMBER_OF_MULTIPLIERS_IN_BAR_GRAPH = (
            "NUMBER_OF_MULTIPLIERS_IN_BAR_GRAPH"
        )
        MULTIPLIERS_TO_SHOW_LAST_POSITION = "MULTIPLIERS_TO_SHOW_LAST_POSITION"
        LANGUAGE = "LANGUAGE"
        IGNORE_DB_LOGS = "IGNORE_DB_LOGS"

    def __init__(self):
        self.config_file = CONFIG_FILE_PATH
        self.API_URL = "https://probetsai.com"
        self.WS_URL = "ws://probetsai.com:5000/ws/bot/"
        self.ALLOWED_LOG_CODES_TO_SHOW = [
            "info",
            "success",
            "warning",
            "error",
            # "debug",
        ]
        self.MAX_AMOUNT_HOME_BET_PERCENTAGE = 0.5
        self.MAX_AMOUNT_BALANCE_PERCENTAGE = 0.005
        self.NUMBER_OF_MULTIPLIERS_IN_BAR_GRAPH = 30
        self.MULTIPLIERS_TO_SHOW_LAST_POSITION = []
        self.LANGUAGE = "en"
        self.IGNORE_DB_LOGS = True
        self._ALLOWED_LANGUAGES = ["en", "es"]
        self.read_config()

    def __create_config(self):
        config_dir = os.path.dirname(self.config_file)
        if config_dir and not os.path.exists(config_dir):
            os.makedirs(config_dir)
        if not os.path.exists(self.config_file):
            self.write_config()

    def read_config(self):
        if not os.path.exists(self.config_file):
            self.__create_config()
        with open(self.config_file, "r") as file:
            config = {}
            for line in file:
                if line.startswith("#"):
                    continue
                variable, value = line.strip().split("=")
                match variable:
                    case self.ConfigVar.API_URL:
                        self.API_URL = value
                    case self.ConfigVar.WS_URL:
                        self.WS_URL = value
                    case self.ConfigVar.ALLOWED_LOG_CODES_TO_SHOW:
                        self.ALLOWED_LOG_CODES_TO_SHOW = value.split(",")
                    case self.ConfigVar.MAX_AMOUNT_HOME_BET_PERCENTAGE:
                        self.MAX_AMOUNT_HOME_BET_PERCENTAGE = float(value)
                    case self.ConfigVar.MAX_AMOUNT_BALANCE_PERCENTAGE:
                        self.MAX_AMOUNT_BALANCE_PERCENTAGE = float(value)
                    case self.ConfigVar.NUMBER_OF_MULTIPLIERS_IN_BAR_GRAPH:
                        self.NUMBER_OF_MULTIPLIERS_IN_BAR_GRAPH = int(value)
                    case self.ConfigVar.MULTIPLIERS_TO_SHOW_LAST_POSITION:
                        self.MULTIPLIERS_TO_SHOW_LAST_POSITION = [
                            int(i) for i in value.split(",")
                        ]
                    case self.ConfigVar.LANGUAGE:
                        self.LANGUAGE = value
                        if value not in self._ALLOWED_LANGUAGES:
                            self.LANGUAGE = self._ALLOWED_LANGUAGES[0]
                    case self.ConfigVar.IGNORE_DB_LOGS:
                        self.IGNORE_DB_LOGS = bool(int(value))
            return config

    def write_config(self):
        with open(self.config_file, "w") as file:
            file.write("# Default configuration\n")
            # file.write(f"API_URL={self.API_URL}\n")
            # file.write(f"WS_URL={self.WS_URL}\n")
            file.write(f"LANGUAGE={self.LANGUAGE}\n")
            file.write(
                f"NUMBER_OF_MULTIPLIERS_IN_BAR_GRAPH="
                f"{self.NUMBER_OF_MULTIPLIERS_IN_BAR_GRAPH}\n"
            )
            # file.write(
            #   f'ALLOWED_LOG_CODES_TO_SHOW={",".join(self.ALLOWED_LOG_CODES_TO_SHOW)}\n'
            # )
            # file.write(
            #     f"MAX_AMOUNT_HOME_BET_PERCENTAGE={self.MAX_AMOUNT_HOME_BET_PERCENTAGE}\n"
            # )
            # file.write(
            #     f"MAX_AMOUNT_BALANCE_PERCENTAGE={self.MAX_AMOUNT_BALANCE_PERCENTAGE}\n"
            # )
