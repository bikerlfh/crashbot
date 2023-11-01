# Standard Library
from datetime import datetime

# Internal
from apps.utils.patterns.singleton import Singleton


class SessionTime(metaclass=Singleton):
    """
    Class to get session time
    """

    def __init__(self):
        self.start_time = datetime.now()

    @property
    def duration(self):
        now = datetime.now()
        duration = now - self.start_time
        return duration

    @property
    def seconds(self):
        return self.duration.seconds

    def every(self, *, seconds: int):
        return self.seconds % seconds == 0
