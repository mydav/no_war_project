# !/usr/bin/python
# -*- coding: utf-8 -*-

from math import ceil as math_ceil
from math import floor as math_floor


def round_decimals_down(number=22.555, decimals=1):
    """
    Returns a value rounded down to a specific number of decimal places.
    """
    if not isinstance(decimals, int):
        raise TypeError("decimal places must be an integer")
    elif decimals < 0:
        raise ValueError("decimal places has to be 0 or more")
    elif decimals == 0:
        return math_floor(number)

    factor = 10 ** decimals
    return math_floor(number * factor) / factor


def calc_max_stake_from_odds_and_max_win(odds=41, max_win=30, stake=None):
    """stake * odds = max_win"""
    max_stake = round_decimals_down(1.0 * max_win / odds, 2)
    if stake is not None:
        max_stake = min(stake, max_stake)
    return max_stake


def round_stavka(num, divisor):
    """
    Я могу округливать и к целым, и к float
    на входе округление
        и целые round_to == int (0, 1, 2...)
        и флоа: 0.1, 0.2
    """
    fun_round = round
    # fun_round = round_decimals_down
    int_divisor = divisor
    if isinstance(divisor, float) or divisor in [0]:
        int_divisor = int(10 * divisor)
    return round_stavka_int(num, int_divisor, fun_round=fun_round)


def round_stavka_int(stake, round_to=0, fun_round=round):
    """
    на входе округление round_to == int (0, 1, 2...)
    """
    # fun_round = round_decimals_down
    stake = fun_round(stake, round_to)
    if round_to in [0]:
        stake = int(stake)
    return stake


def round_down_int(num, divisor):
    """
    (19,10)=10
    (19,5)=15
    (10,10)=10
    """
    # logger.debug('round_down_int %s, divisor %s' % (num, divisor))
    return num - (num % divisor)


def round_decimals_up(number=22.555, decimals=1):
    """
    Returns a value rounded up to a specific number of decimal places.
    https://kodify.net/python/math/round-decimals/
    """
    if not isinstance(decimals, int):
        raise TypeError("decimal places must be an integer")
    elif decimals < 0:
        raise ValueError("decimal places has to be 0 or more")
    elif decimals == 0:
        return math_ceil(number)

    factor = 10 ** decimals
    return math_ceil(number * factor) / factor


if __name__ == "__main__":
    special = "round_decimals_down"
    special = "calc_max_stake_from_odds_and_max_win"

    if special == "calc_max_stake_from_odds_and_max_win":
        max_stake = calc_max_stake_from_odds_and_max_win(26, 11, 3)
        print("max_stake=%s" % max_stake)

    elif special == "round_decimals_down":
        values = [
            1.2,
            1.259,
            1.251,
        ]
        for value in values:
            rounded = round_decimals_down(value, 2)
            print("value=%s, rounded=%s" % (value, rounded))
