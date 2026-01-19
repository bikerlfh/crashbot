"""
contain functions to help with graphs
"""

# Standard Library
from typing import Optional

# Libraries
import numpy as np


def convert_multipliers_to_coordinate(
    multipliers: list[float], last_y_coordinates: Optional[list[int]] = None
) -> list[int]:
    """
    convert multipliers to Y coordinate
    :param multipliers: list of multipliers
    :param last_y_coordinates: list of last Y coordinates
        (only if you want to continue the list)
    :return: list of Y coordinates
    """
    y = last_y_coordinates or []
    for multiplier in multipliers:
        value = 1 if multiplier >= 2 else -1
        last_value = 0 if len(y) == 0 else y[-1]
        value_ = last_value + value
        y.append(value_)
    return y


def calculate_slope_linear_regression(
    y: list[float], len_window: Optional[int] = -11
) -> tuple[float, float]:
    """
    calculate the slope of the linear regression
    using to know if a graph is going up or down
    :param y: is the list of values to calculate the slope
    :param len_window: is the length of the window to calculate the slope
    :return: tuple the slope and the intercept
    """
    if not y:
        return -1, 0
    len_window = abs(len_window) * -1
    if len(y) > len_window:
        y = y[len_window:]
    x = np.arange(len(y))
    # Calculate the slope of the linear regression
    coefficients = np.polyfit(x, y, 1)
    slope = coefficients[0]
    intercept = coefficients[1]
    return float(slope), intercept
