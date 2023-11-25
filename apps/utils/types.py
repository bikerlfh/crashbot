class PercentageNumber:
    def __init__(self, value: float):
        self.value = value

    def is_valid(self) -> bool:
        return 0 <= self.value <= 1
