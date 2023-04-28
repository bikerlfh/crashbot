# Standard Library
import random


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
    The Kelly formula is a formula used to determine the optimal fraction of one's capital to bet on a given bet.
    The formula is: f* = (bp - q) / b
    :param b: is the ratio of net gains to net losses (i.e., net gains per unit bet),
    :param p: is the probability of winning the bet, and
    :param q: is the probability of losing the bet (q = 1 - p).
    :param capital: is the amount of money you have to bet.
    example: kelly_formula(2, 0.6, 1000)
    """
    f = (b * p - (1 - p)) / b
    return round(capital * f, 2)


def adaptive_kelly_formula(b: float, p: float, R: float, capital: float) -> float:
    """
    The Adaptive Kelly formula is a formula used to determine the optimal fraction of one's capital to bet on a given bet.
    The formula is: f* = (bp - q) / b * (1 + R)
    :param b: is the ratio of net gains to net losses (i.e., net gains per unit bet),
    :param p: is the probability of winning the bet, and
    :param q: is the probability of losing the bet (q = 1 - p).
    :param R: is a risk factor that varies with the volatility of the market,
    :param capital: is the amount of money you have to bet.
    example: kelly_formula(2, 0.6, 0.1, 1000)
    """
    f = ((b * p - (1 - p)) / b) * (1 + R)
    return round(capital * f, 2)
