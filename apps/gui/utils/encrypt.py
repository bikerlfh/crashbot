# Standard Library
import os

# Libraries
import base64
import machineid
from cryptography.fernet import Fernet

# Internal
# from apps.gui.constants import DATA_FILE_PATH
from apps.utils.patterns.singleton import Singleton


class Encrypt(metaclass=Singleton):
    KEY_ENCRYPTED: bytes

    def __init__(self):
        self.KEY_ENCRYPTED = base64.urlsafe_b64encode(
            machineid.hashed_id(machineid.id())[:32].encode()
        )

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
