# Standard Library
import json
from enum import Enum

# Libraries
from localStoragePy import localStoragePy

# Internal
from apps.utils.patterns.singleton import Singleton


class LocalStorage(metaclass=Singleton):
    class LocalStorageKeys(Enum):
        TOKEN = "token"
        REFRESH = "refresh"
        CUSTOMER_ID = "customer_id"
        HOME_BETS = "home_bets"
        LAST_INITIAL_BALANCE = "last_initial_balance"

    def __init__(self):
        self.local_storage = localStoragePy("co.crashbot.local", "json")

    def get(self, key: str):
        return self.local_storage.getItem(key)

    def set(self, key: str, value: any):
        self.local_storage.setItem(key, value)

    def remove(self, key: str):
        self.local_storage.removeItem(key)

    def clear(self):
        self.local_storage.clear()

    def set_token(self, token: str):
        self.set(LocalStorage.LocalStorageKeys.TOKEN.value, token)

    def get_token(self):
        return self.get(LocalStorage.LocalStorageKeys.TOKEN.value)

    def set_refresh(self, refresh: str):
        self.set(LocalStorage.LocalStorageKeys.REFRESH.value, refresh)

    def get_refresh(self):
        return self.get(LocalStorage.LocalStorageKeys.REFRESH.value)

    def set_customer_id(self, customer_id: int):
        self.set(LocalStorage.LocalStorageKeys.CUSTOMER_ID.value, customer_id)

    def get_customer_id(self) -> int:
        customer_id = self.get(LocalStorage.LocalStorageKeys.CUSTOMER_ID.value)
        return int(customer_id) if customer_id else None

    def set_home_bets(self, home_bets: list[dict[str, any]]):
        self.set(LocalStorage.LocalStorageKeys.HOME_BETS.value, json.dumps(home_bets))

    def get_home_bets(self) -> list[dict[str, any]]:
        """
        :return: list[dict(
            id: int,
            name: str,
            url: str,
            min_bet: float,
            max_bet: float,
        )]
        """
        home_bets = self.get(LocalStorage.LocalStorageKeys.HOME_BETS.value)
        if home_bets:
            home_bets = json.loads(home_bets)
        return home_bets if home_bets else []

    def set_last_initial_balance(self, *, home_bet_id: int, balance: float):
        data = self.get(LocalStorage.LocalStorageKeys.LAST_INITIAL_BALANCE.value) or {}
        data[str(home_bet_id)] = balance
        self.set(
            LocalStorage.LocalStorageKeys.LAST_INITIAL_BALANCE.value, json.dumps(data)
        )

    def get_last_initial_balance(
        self,
        *,
        home_bet_id: int,
    ) -> float | None:
        data = self.get(LocalStorage.LocalStorageKeys.LAST_INITIAL_BALANCE.value)
        data = json.loads(data) if data else {}
        last_balance = data.get(str(home_bet_id), None)
        return float(last_balance) if last_balance else None
