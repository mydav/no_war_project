import numpy as np


def srednee(items):
    # m = sum(items) / len(items)
    return np.mean(items)


def variance_2(items):
    m = srednee(items)
    # calculate variance using a list comprehension
    varRes = sum([(xi - m) ** 2 for xi in items]) / len(items)
    return varRes


def variance(items):
    """Дисперсия"""
    variance = np.var(items)
    return variance


def std(items, ddof=0):
    return np.std(items, ddof=ddof)


def calculate_percent_excel(cnt, suma, round_do=3):
    """-100 == -100%
    """
    percent = calculate_percent(cnt, suma, round_do)
    znak = 1
    if suma < 0:
        znak = -1
    # print(f"    {percent=} {znak=}")
    return znak * percent


def calculate_percent_int(cnt=1, suma=3):
    return calculate_percent(cnt=cnt, suma=suma, round_to=0)


def calculate_percent(cnt=1, suma=3, round_to=3):
    if not suma:
        return 0.0

    percent = 100.0 * cnt / suma
    if round_to == 0:
        percent = int(percent)
    else:
        percent = round(percent, round_to)
    return percent


if __name__ == "__main__":
    special = "test_statistic_funcs"
    special = "calculate_percent"

    if special == "calculate_percent":
        fun = calculate_percent
        fun = calculate_percent_excel
        tasks = [
            (1, 3),
            (-1, 3),
            (-1, -3),
            (1, -3),
        ]
        for x, y in tasks:
            print(f"{x}/{y} = {fun(x, y)}")

    elif special == "test_statistic_funcs":
        list_of_items = [
            [1, 2, 3, 4, 2],
            [1, 1, 1, 1, 100],
            [1, 1, 1, 1, 4],
        ]
        for items in list_of_items:
            print(
                variance(items), variance_2(items), srednee(items), std(items)
            )

"""
Есть либа?
    https://docs.python.org/3/library/statistics.html#statistics.pvariance
"""
