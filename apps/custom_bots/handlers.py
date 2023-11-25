# Standard Library
import json
import os

# Internal
from apps.api.models import Bot
from apps.utils.security.encrypt import FernetHandler


class CustomBotsEncryptHandler:
    BOT_EXTENSION = ".bot"

    def __init__(self, path: str):
        self.path = path
        self._key = "fc8c9c896d8545b18282ebb19c67ac30"
        self._fernet = FernetHandler(key=self._key)

    def save(self, bot: Bot):
        bot_path = f"{self.path}/{bot.name}{self.BOT_EXTENSION}"
        cipher_text = self._fernet.encrypt(json.dumps(bot.dict()))
        with open(bot_path, "wb") as file:
            file.write(cipher_text.encode())

    def remove(self, bot: Bot):
        bot_path = f"{self.path}/{bot.name}{self.BOT_EXTENSION}"
        os.remove(bot_path)

    def load(self, bot_path: str) -> Bot:
        with open(bot_path, "rb") as file:
            cipher_text = file.read()
        data = json.loads(self._fernet.decrypt(cipher_text.decode()))
        bot = Bot(**data)
        return bot

    def load_all(self) -> list[Bot]:
        if not os.path.exists(self.path):
            return []
        bots = []
        for file_name in os.listdir(self.path):
            if not file_name.endswith(self.BOT_EXTENSION):
                continue
            bot_path = f"{self.path}/{file_name}"
            bot = self.load(bot_path)
            bots.append(bot)
        bots = sorted(bots, key=lambda x: x.id, reverse=True)
        return bots

    def convert_json_to_encrypted(self) -> list[Bot]:
        bots = []
        i = -1
        for file_name in os.listdir(self.path):
            if not file_name.endswith(".json"):
                continue
            bot_path = f"{self.path}/{file_name}"
            with open(bot_path, "r") as file:
                data = json.load(file)
                if isinstance(data, list):
                    data = data[0]
            bot = Bot(id=i, **data)
            self.save(bot)
            bots.append(bot)
            i -= 1
        return bots
