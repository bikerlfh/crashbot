import os

from cryptography.fernet import Fernet

from apps.services.constants import DATA_FILE_PATH
from apps.utils.patterns.singleton import Singleton


class Encrypt(Singleton):
    FILE_KEY_PATH: str
    KEY_ENCRYPTED: str

    def __init__(self):
        self.FILE_KEY_PATH = f"{DATA_FILE_PATH}/mykey.key"
        self.KEY_ENCRYPTED = self.get_key_encrypted()

    def generate_key_encrypted(self) -> str:
        """
        Generate key encrypted
        :return: str
        """
        exists = os.path.isdir(DATA_FILE_PATH)
        if not exists:
            os.mkdir(DATA_FILE_PATH)
        key = Fernet.generate_key()
        with open(self.FILE_KEY_PATH, "wb") as my_key:
            my_key.write(key)
        return key

    def get_key_encrypted(self) -> str:
        """
        Get key encrypted
        :return: str
        """
        exists = os.path.isfile(self.FILE_KEY_PATH)
        if not exists:
            return self.generate_key_encrypted()
        with open(self.FILE_KEY_PATH, "rb") as mykey:
            key = mykey.read()
        return key

    def encrypt(self, data: str) -> str:
        """
        Encrypt data
        :param data: data
        :return: str
        """
        fernet = Fernet(self.KEY_ENCRYPTED)
        return fernet.encrypt(data.encode()).decode()

    def decrypt(self, data: str) -> str:
        """
        Decrypt data
        :param data: data
        :return: str
        """
        fernet = Fernet(self.KEY_ENCRYPTED)
        return fernet.decrypt(data.encode()).decode()
