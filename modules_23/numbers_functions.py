# -*- coding: utf-8 -*-

import re

# from modules_23.minimum_important_functions import *
# from modules_23.minimum_important_functions import get_logger, find_from_to_one

from modules.logging_functions import get_logger
from modules.find_functions import find_from_to_one

logger = get_logger(__name__)


def have_one_symbol(name, good_symbols):
    # есть ли хоть один символ в имени из нужных
    # name = name.lower()
    good = 0
    for b in name:
        if b in good_symbols:
            good = 1
            break
    return good


def have_bad_symbol(name, good_symbols):
    # есть ли плохий символ в имени
    # name = name.lower()
    bad = 0
    # wait_for_ok('have_bad_symbol for "%s" ' % name)
    if type(name) not in [type([]), type("str")]:
        name = str(name)
    for b in name:
        if b not in good_symbols:
            # logger.debug('%s not in %s' % (b, good_symbols))
            bad = 1
            break
        else:
            pass
            # logger.debug('    %s in %s' % (b, good_symbols))
    return bad


def str_is_int(v):
    """проверяем - строка это число или нет. На 0 начинаться не может. На + может"""
    t = 1
    if t:
        try:
            # if str(int(str(v))) == str(v):
            t = str(int(v))
            while True:
                if t[0] in ["+"]:
                    t = t[1:]
                    continue
                break
            # logger.debug('v %s, t %s, strv %s' % (v, t, str(v)))
            if t == str(v) or "+" + t == str(v):
                return True
            else:
                return False
        except Exception as er:
            return False

    else:
        # t = 0
        # if t:
        try:
            v1 = str(v)
        except Exception as er:
            return False
        try:
            v1 = int(v1)
        except Exception as er:
            v1 = "asldfjasldfjlsadjflsajfas;lfdj"
            pass
        if str(v) == str(v1):
            return True
    return False


def only_cifry(v="", cifry="0123456789"):
    # проверяем значение только из цифр или нет (может начинаться на 0)
    # wait_for_ok('only_cifry')
    return not have_bad_symbol(v, cifry)


def str_is_float(v="", almost=0):
    if almost:
        cifry = ",+-.0123456789"
    else:
        cifry = "+-.0123456789"
    v0 = str(v).strip()
    if v0 == "":
        return 0

    if v in ["-", "+"]:
        return 0

    is_only_cifry = only_cifry(v, cifry=cifry)
    # wait_for_ok(is_only_cifry)
    if is_only_cifry:
        return 1
    return 0


def to_str_float(value=0.1, str_format="%.1f"):
    """
        переводим флоат в строчечный формат (обычно эксельке надо)
    """
    r = value
    if type(value) in [type(0.1)]:
        r = str_format % value

    elif str_is_int(value):
        pass

    else:
        v = str_to_float(value, None)
        if v != None:
            r = str_format % v
    return r


is_int = only_cifry


def replace_numbers_to_nonumber(value=""):
    allowed = [
        "12",
        "1",
        "2",
        "",
        None,
    ]
    if value in allowed:
        return value

    exp = r"[0-9\.)(]+"
    exp = r"[0-9\.]+"
    t = re.sub(exp, "*", value)  # Only non-alphanumeric
    # t = t.replace("(#)", "#")
    return t


def floats_almost_equals(v1=0, v2=0, max_diff=0.00001, with_diff=0):
    """
        проверяем - значения почти равны?
        а то 0.0000001 и 0 они же равні
    """
    diff = abs(v1 - v2)
    if diff <= max_diff:
        return 1

    if with_diff:
        return diff

    return 0


def str_to_float(v, default=False):
    """
        получаем строку, и ее в флоат
    """
    v0 = my_symbols(v, "+-.,1234567890")

    if v0.count(".") == 1 and v0.count(",") == 1:  # $1,011.50
        v0 = v0.replace(",", "")

    v0 = v0.replace(",", ".").replace("+", "")
    try:
        v0 = float(v0)
    except Exception as er:
        v0 = default

    return v0


def my_symbols(text, good=".0123456789"):
    text = str(text)
    r = []
    for x in text:
        if x in good:
            r.append(x)
    r = "".join(r)
    return r


def str_is_int(v):
    """проверяем - строка это число или нет. На 0 начинаться не может. На + может"""
    t = 1
    if t:
        try:
            # if str(int(str(v))) == str(v):
            t = str(int(v))
            while True:
                if t[0] in ["+"]:
                    t = t[1:]
                    continue
                break
            # logger.debug('v %s, t %s, strv %s' % (v, t, str(v)))
            if t == str(v) or "+" + t == str(v):
                return True
            else:
                return False
        except Exception as er:
            return False

    else:
        # t = 0
        # if t:
        try:
            v1 = str(v)
        except Exception as er:
            return False
        try:
            v1 = int(v1)
        except Exception as er:
            v1 = "asldfjasldfjlsadjflsajfas;lfdj"
            pass
        if str(v) == str(v1):
            return True
    return False


def my_int(text, on_empty=None):
    text = str(text).strip()
    "екселька вместо 1 выдает 1.0"
    text = rstrip_dotzero(text)
    # logger.debug('text=%s' % text)
    good = "0123456789"
    r = []
    for x in text:
        if x in good:
            r.append(x)
        # logger.debug('my_int=%s' % r)
    r = "".join(r)
    if r == "":
        r = on_empty
    else:
        r = int(r)
    return r


def rstrip_dotzero(text=""):
    if isinstance(text, str) and text.endswith(".0"):
        text = text[:-2]
    return text


def cut_zeros_after_dot(value=""):
    """
    обрубаем нули в конце
        0.001 0.001
        0.01001000 0.01001
        0.20 0.2
        3 3
        1.15 1.15
        10.0 10
        4. 4

    """
    v = str(value)
    v = v.strip()

    dot_symbol = "."
    if not dot_symbol in v:
        dot_symbol = ","
    if not dot_symbol in v:
        return v

    parts = v.split(dot_symbol)
    after_dot = parts[-1]

    good_symbols = []
    # after_dot.reverse()

    found_zero = 1
    for i in range(len(after_dot)):
        pos = len(after_dot) - i - 1
        symbol = after_dot[pos]
        if symbol in ["0"] and found_zero:
            found_zero = 1
            continue

        found_zero = 0
        good_symbols.append(symbol)
        found_zero = 0

    if len(good_symbols) > 0:
        good_symbols.reverse()

        after_dot = "".join(good_symbols)

        value = "%s%s%s" % (parts[0], dot_symbol, after_dot)
    else:
        value = parts[0]

    return value


def float_without_zero(f=1.0):
    """
        удаляем из флоата нули после точки
        2.0 -> 2
    """
    t = str(f)
    if t.find(".") != -1:
        last = find_from_to_one(".", "nahposhuk", t)

        remove_last = 1
        for symb in last:
            if symb != "0":
                remove_last = 0
                break

        if remove_last:
            t = find_from_to_one("nahposhuk", ".", t)
    return t


def replace_numbers_to_nonumber(value=""):
    allowed = [
        "12",
        "1",
        "2",
        "",
        None,
    ]
    if value in allowed:
        return value

    exp = r"[0-9\.)(]+"
    exp = r"[0-9\.]+"
    t = re.sub(exp, "*", value)  # Only non-alphanumeric
    # t = t.replace("(#)", "#")
    return t


def value_with_znak(
    value="1", option="znak", want_only_minus_znak=False, debug=False
):
    fun = "value_with_znak"
    raw_value = value
    znak0 = value[0]
    if znak0 in ["+", "-"]:
        bez_znaka = value[1:]
    else:
        znak0 = "+"
        bez_znaka = value

    if option == "minus_znak":
        if znak0 == "+":
            new_znak = "-"
        elif znak0 == "-":
            new_znak = "+"
    elif option == "plus_znak":
        if znak0 == "+":
            new_znak = "+"
        elif znak0 == "-":
            new_znak = "-"
    elif option == "znak":
        new_znak = znak0

    else:
        wait_for_ok("ERROR %s - unknown option %s" % (fun, option))

    value = new_znak + bez_znaka
    if bez_znaka == "0":  # Ф1(0)
        value = bez_znaka

    if want_only_minus_znak and value[0] in ["+"]:
        value = value[1:]

    if 0 and debug:
        logger.debug(
            "value=%s from raw_value=%s: znak0=%s, bez_znaka=%s, new_znak=%s for options %s"
            % (value, raw_value, znak0, bez_znaka, new_znak, options)
        )
    return value
    # wait_for_ok(value)


if __name__ == "__main__":
    from modules import *

    special = "rounded"
    special = "value_with_znak"
    special = "float_without_zero"
    special = "str_to_float"

    if special == "value_with_znak":
        items = clear_list(
            """
        0
        0.5
        +0.5
        -0.5
        """
        )
        options = ["plus_znak", "minus_znak", "znak"]
        for item in items:
            logger.debug(item)
            for option in options:
                with_znak = value_with_znak(item, option)
                logger.debug(
                    " {with_znak} from {item} for {option}".format(**locals())
                )

    elif special == "rounded":
        numbers = [
            [19.5, 10, 10],
            [19.5, 5, 15],
            [10.55, 10, 10],
            [10.55, 1, 10],
            [10.55, 0.1, 10.5],
            [10.555, 0.2, 10.55],
            [10.55, 0, 10],
            [10.55, 1, 10],
        ]
        for item in numbers:
            number, divisor, expected = item
            rounded_up = round_decimals_up(number, 1)
            rounded_down = round_decimals_down(number, 1)
            res = round_stavka(number, divisor)
            logger.debug(
                "%s (up=%s, down=%s) from item %s"
                % (res, rounded_up, rounded_down, item)
            )
            if res != expected:
                logger.error("   ERROR %s!=%s expected" % (res, expected))

    if special == "float_without_zero":
        tests = [
            "0.001",
            "0.01001000",
            "0.20",
            "3",
            "1.15",
            "10.0",
            "4.",
        ]
        for bet in tests:
            # cuted = cut_zeros_after_dot(bet)
            # cuted = txtfloat_del_zeros(bet)
            cuted = float_without_zero(bet)
            logger.info("    %s %s" % (bet, cuted))

    elif special == "str_to_float":
        tests = [
            # '-23,4',
            # '+23,4',
            # '+23.a4',
            # '_23.a4',
            # '0',
            # 'hrenj',
            # 'hrenj1',
            "$1,011.50",
        ]
        for t in tests:
            res = str_to_float(t)
            logger.info("%s        %s" % (t, res))
    else:
        logger.error("unknown special %s" % special)
