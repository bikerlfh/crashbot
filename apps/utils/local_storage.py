from localStoragePy import localStoragePy
from apps.utils.patterns.singleton import Singleton


class LocalStorage(metaclass=Singleton):
    def __init__(self):
        self.local_storage = localStoragePy('co.crashbot.local', 'json')

    def get(self, key: str):
        return self.local_storage.getItem(key)

    def set(self, key: str, value: any):
        self.local_storage.setItem(key, value)

    def remove(self, key: str):
        self.local_storage.removeItem(key)

    def clear(self):
        self.local_storage.clear()
