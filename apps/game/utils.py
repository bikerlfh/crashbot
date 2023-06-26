# Standard Library
import copy
import random
from typing import Optional

# Internal
from apps.api.models import MultiplierPositions


def generate_random_multiplier(min_: float, max_: float) -> float:
    random_num = random.uniform(min_, max_)
    value = round(random_num, 2)
    return value


def format_number_to_multiple(num: float, multiple: float) -> float:
    """
    :param num: is the number to format
    :param multiple: is the multiple to format the number
    example: format_number_to_multiple(1.2345, 100)
    """
    return round(num / multiple) * multiple


def kelly_formula(b: float, p: float, capital: float) -> float:
    """
    The Kelly formula is a formula used to determine the
    optimal fraction of one's capital to bet on a given bet.
    The formula is: f* = (bp - q) / b
    :param b: is the ratio of net gains to net losses
        (i.e., net gains per unit bet),
    :param p: is the probability of winning the bet, and
    :param q: is the probability of losing the bet (q = 1 - p).
    :param capital: is the amount of money you have to bet.
    example: kelly_formula(2, 0.6, 1000)
    """
    f = (b * p - (1 - p)) / b
    return round(capital * f, 2)


def adaptive_kelly_formula(
    b: float, p: float, R: float, capital: float
) -> float:
    """
    The Adaptive Kelly formula is a formula used to determine
    the optimal fraction of one's capital to bet on a given bet.
    The formula is: f* = (bp - q) / b * (1 + R)
    :param b: is the ratio of net gains to net losses
        (i.e., net gains per unit bet),
    :param p: is the probability of winning the bet, and
    :param q: is the probability of losing the bet (q = 1 - p).
    :param R: is a risk factor that varies with the volatility of the market,
    :param capital: is the amount of money you have to bet.
    example: kelly_formula(2, 0.6, 0.1, 1000)
    """
    f = ((b * p - (1 - p)) / b) * (1 + R)
    return round(capital * f, 2)


def predict_next_multiplier(
    *,
    data: MultiplierPositions,
    last_multipliers: list[float],
    use_all_time: Optional[bool] = True
) -> tuple[int, float]:
    """
    predict the next multiplier range.
    this is a basic prediction, it will be improved in the future.
    :param data: data from backend
    :param last_multipliers:
    :param use_all_time: if True, use all_time data, else use today data
    :return: tuple(next_value, percentage)
    """

    def _get_last_position_multiplier(multiplier_: int) -> int:
        multi = copy.copy(last_multipliers)
        multi.reverse()
        for i in range(len(multi)):
            if multi[i] >= multiplier_:
                return i + 1
        return -1

    if not last_multipliers or not data:
        return 0, 0
    data_ = data.all_time if use_all_time else data.today
    max_value = (0, 0)
    for key in reversed(data_):
        values = data_[key]
        multiplier = int(key)
        if multiplier < 2:
            continue
        index_ = _get_last_position_multiplier(multiplier)
        if index_ < 0:
            continue
        count = int(values.count)
        positions = values.positions
        for position, position_count in positions.items():
            position_ = int(position)
            if index_ > position_:
                percentage = round(position_count / count, 2)
                if max_value[1] < percentage:
                    max_value = (multiplier, percentage)
    return max_value
