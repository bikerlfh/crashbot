import abc


class AbstractControlBase(abc.ABC):
    @abc.abstractmethod
    def init(self):
        ...

    @abc.abstractmethod
    def set_auto_cash_out(self, multiplier, control):
        ...

    @abc.abstractmethod
    def update_amount(self, amount, control):
        ...

    @abc.abstractmethod
    def bet(self, amount, multiplier, control):
        ...


class AbstractGameBase(abc.ABC):

    @abc.abstractmethod
    def _click(self, element: any):
        ...

    @abc.abstractmethod
    def _login(self):
        ...

    @abc.abstractmethod
    def open(self):
        ...

    @abc.abstractmethod
    def close(self):
        ...

    @abc.abstractmethod
    def read_game_limits(self):
        ...

    @abc.abstractmethod
    def read_balance(self) -> float:
        ...

    @abc.abstractmethod
    def read_multipliers(self):
        ...

    @abc.abstractmethod
    def bet(self, amount: float, multiplier: float, control: AbstractControlBase):
        ...

    @abc.abstractmethod
    def wait_next_game(self):
        ...