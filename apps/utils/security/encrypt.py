# Standard Library
import base64
import hashlib
from typing import Optional

# Libraries
import machineid
from cryptography.fernet import Fernet

# Internal
from apps.utils.patterns.singleton import Singleton


class FernetHandler(metaclass=Singleton):
    KEY_ENCRYPTED: bytes

    def __init__(self, key: Optional[str] = None):
        if not key:
            key = machineid.hashed_id(machineid.id())[:32]
        self.KEY_ENCRYPTED = base64.urlsafe_b64encode(key.encode())

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


def md5(text: str) -> str:
    try:
        _md5 = hashlib.md5()
        _md5.update(text.encode("utf-8"))
        hash_md5 = _md5.hexdigest()
        return hash_md5
    except Exception as e:
        return str(e)
