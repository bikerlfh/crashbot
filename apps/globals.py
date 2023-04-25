"""
globals variables
use globals().get('auto_play') to get value
use globals().setdefault('auto_play', False) to set value
"""

from typing import Callable

auto_play = False
max_amount_to_bet = 0


add_log: Callable = None
