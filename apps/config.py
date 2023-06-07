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

    def __init__(self):
        self.config_file = CONFIG_FILE_PATH
        self.API_URL = "http://127.0.0.1:8000"
        self.WS_URL = "ws://127.0.0.1:8000"
        self.ALLOWED_LOG_CODES_TO_SHOW = [
            "info",
            "success",
            "warning",
            "error",
            "debug",
        ]
        self.MAX_AMOUNT_HOME_BET_PERCENTAGE = 0.5
        self.MAX_AMOUNT_BALANCE_PERCENTAGE = 0.005
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
            return config

    def write_config(self):
        with open(self.config_file, "w") as file:
            file.write("# Default configuration\n")
            file.write(f"API_URL={self.API_URL}\n")
            file.write(f"WS_URL={self.WS_URL}\n")
            file.write(
                f'ALLOWED_LOG_CODES_TO_SHOW={",".join(self.ALLOWED_LOG_CODES_TO_SHOW)}\n'
            )
            file.write(
                f"MAX_AMOUNT_HOME_BET_PERCENTAGE={self.MAX_AMOUNT_HOME_BET_PERCENTAGE}\n"
            )
            file.write(
                f"MAX_AMOUNT_BALANCE_PERCENTAGE={self.MAX_AMOUNT_BALANCE_PERCENTAGE}\n"
            )
