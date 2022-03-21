import random, os
from modules.type_functions import is_int
from random import shuffle
import logging

logger = logging.getLogger(__name__)


def random_elements(lst, num):
    """получает список и число случайных елементов из него, которое нужно вернуть"""
    if num > len(lst):
        num = len(lst)
    if type(lst) == str:
        new_lst = [i for i in lst]
    else:
        new_lst = lst
    shuffle(new_lst)
    return new_lst[:num]


def random_element(lst):
    """получает список и возвращает один случайный елемент из него"""
    return random_elements(lst, 1)[0]


def my_randint(do=10000, ot=0, otl=0):
    """
        включаем все точки
    """
    if ot > do:
        ot, do = do, ot

    r = random.SystemRandom()
    value = r.randint(ot, do)

    if otl:
        print(f"my_randint={value} (ot {ot}, do {do})")
    return value


# adding new functions
def randint(ot=0, do=10000):
    return my_randint(do, ot)


def get_random_value_in_range(value="", special="value", otl=0):
    """
        20      20
        "20"    20
        20-40 рандом от 20 до 40, все включительно

        рейнджи - для точек включительно
    """
    found = None
    found_range = []
    while True:
        # 2
        if isinstance(value, int):
            found = value
            found_range = [found, found]
            break

        if isinstance(value, str):
            parts = value.split("-")
            # "2-4"
            if len(parts) == 2:
                ot, do = parts
                found_range = [seconds_from_str(ot), seconds_from_str(do)]
                found = my_randint(found_range[0], found_range[1])
                break

            # "2"
            elif len(parts) == 1:
                found = seconds_from_str(value)
                found_range = [found, found]
                break

            else:
                logger.error("unknown len for value {value}, parts {parts}")

        else:
            logger("unknown type for value {value}, type {type(value)}")

    if otl:
        print(
            f"for value {value}: found_range {found_range}, found value in range {found}"
        )

    if special == "value":
        return found

    elif special == "range":
        return found_range

    else:
        logger.error(f'ERROR: unknown special "{special}"')


def prepare_random_range(value="", ot=0, do=10000000, special="str_value"):
    """
    special str_value вернет текстовое представление полное
    special ot_do вернет [ot, do]
    """
    found = value
    ot_found = ot
    do_found = do
    if isinstance(value, int):
        ot_found = do_found = value

    elif isinstance(value, str):
        t = value.strip()

        # 2- to <=2
        if t[-1] in ["-"]:
            do_found = t[:-1]
            t = "<=" + t[:-1]

        # 1-2
        parts = t.split("-")
        if len(parts) == 2 and is_int(parts[0]) and is_int(parts[1]):
            ot_found = parts[0]
            do_found = parts[1]
            pass

        # >=2
        elif t[:2] in [">="]:
            ot_found = t[2:]
            found = f"{ot_found}-{do}"

        # >2
        elif t[:1] in [">"]:
            ot_found = int(t[1:]) + 1
            found = f"{ot_found}-{do}"

        # 2+
        elif t[-1] in ["+"]:
            ot_found = t[:-1]
            found = f"{ot_found}-{do}"

        # <=2
        elif t[:2] in ["<="]:
            do_found = t[2:]
            found = f"{ot}-{do_found}"

        # <2
        elif t[:1] in ["<"]:
            do_found = int(t[1:]) - 1
            found = f"{ot}-{do_found}"

        # "66"
        elif is_int(value):
            ot_found = do_found = value
            pass

        else:
            logger.error(f'todo "{value}"')

    else:
        tip = type(value)
        logger.error("ERROR: unknown type {tip}")

    ot_found = int(ot_found)
    do_found = int(do_found)

    if special == "str_value":
        return found

    elif special == "ot_do":
        return [ot_found, do_found]
    else:
        logger.error(f"unknown special {special}")


def rand_from_txt(t):
    if type(t) == type(""):
        if t.find("-") == -1:
            return int(t)
        x, y = t.split("-")
        r = randint(int(x), int(y))
        return r

    return t


def seconds_from_str(s):
    if isinstance(s, str):
        s = s.lower().strip()
        s = s.replace("s", "*1")  # seconds
        s = s.replace("m", "*60")  # minutes
        s = s.replace("h", "*60*60")  # hours
        s = s.replace("d", "*60*60*24")  # hours
        s = eval(s)

    return int(float(s))


if __name__ == "__main__":
    from modules import *

    special = "nah"
    special = "seconds_from_str"

    if special == "seconds_from_str":
        items = clear_list(
            """
        10
        100
        10h
        10d
        """
        )
        for item in items:
            seconds = seconds_from_str(item)
            print("item=%s seconds=%s" % (item, seconds))

    t = 1
    t = 0
    if t:
        t = "10-30"
        wait_random_seconds(t)
        os._exit(0)

    if t:
        checking = [
            99,
            "99",
            "1-2",
            ">2",
            ">=2",
            "2+",
            "<2",
            "<=2",
            "2-",
        ]

        special = "str_value"
        special = "ot_do"
        for check in checking:
            r = prepare_random_range(check, special=special)
            print(f"checking {check}, result {r}")
        os._exit(0)

    t = 1
    if t:
        for i in range(100):
            checking = [
                # 99,
                # "99",
                # "1-3",
                # "1-1",
                # "1-100",
                # "1-2",
                "0-3",
            ]
            for check in checking:
                r = get_random_value_in_range(check)
                print(f"checking {check}, result {r}")
