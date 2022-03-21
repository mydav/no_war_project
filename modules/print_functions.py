# pyarmor options: no-spp-mode
# -*- coding: utf-8 -*-

from pprint import pprint
import os, sys
from io import StringIO
from contextlib import redirect_stdout
import sys
from json import dumps as json_dumps
from modules.logging_functions import get_logger

# print("print_functions start")
logger = get_logger(__name__)
# print(f"print_functions {logger=}")


class Capturing(list):
    """
    https://stackoverflow.com/questions/16571150/how-to-capture-stdout-output-from-a-python-function-call
    """

    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio  # free up some memory
        sys.stdout = self._stdout


def get_printed_result(func, *args, **kwargs):
    """
    https://stackoverflow.com/questions/521532/how-do-i-get-pythons-pprint-to-return-a-string-instead-of-printing

    Еще можно:
        https://stackoverflow.com/questions/24277488/in-python-how-to-capture-the-stdout-from-a-c-shared-library-to-a-variable/29834357
    """
    f = StringIO()
    # f = sys.stdout
    with redirect_stdout(f):
        run_function_with_args_and_kwargs(func, *args, **kwargs)
    out = f.getvalue()
    return out


def get_printed_result_list(func, *args, **kwargs):
    """
    https://stackoverflow.com/questions/521532/how-do-i-get-pythons-pprint-to-return-a-string-instead-of-printing
    """
    with Capturing() as output:
        r = run_function_with_args_and_kwargs(func, args, kwargs)
    # output = output[0]
    # output = str(output)
    print(f"{type(output)}, {output=}")
    return output


def run_function_with_args_and_kwargs(func, *args, **kwargs):
    debug = True
    debug = False

    if debug:
        print(
            f"{func=} {args=} {type(args)=} {dir(args)=} {kwargs=} {type(kwargs)=} {dir(kwargs)=}"
        )
    r = func(*args, **kwargs)

    if debug:
        print(f"{r=}")
    return r


def get_printed_result_as_html(func, *args, **kwargs):
    """
    получаем результат любой ф-ии
    """
    r = get_printed_result(func, *args, **kwargs)
    r = prepare_text_for_html(r)
    return r


def pprint_to_html(obj: None) -> str:
    """
    https://stackoverflow.com/questions/521532/how-do-i-get-pythons-pprint-to-return-a-string-instead-of-printing
    """
    return get_printed_result_as_html(pprint, obj)


def pprint_to_html_old(obj: None) -> str:
    """
    https://stackoverflow.com/questions/521532/how-do-i-get-pythons-pprint-to-return-a-string-instead-of-printing
    """
    s = StringIO()
    pprint(obj, s)
    r = s.getvalue()  # displays the string

    r = prepare_text_for_html(r)
    return r


def prepare_text_for_html(r):
    r = r.replace("\n", "<br>")
    r = f"<pre>{r}</pre>"
    return r


def pretty(d, indent=0):
    if isinstance(d, str):
        print(f'"{d}"')

    elif isinstance(d, list) or isinstance(d, tuple):
        i = 0
        for value in d:
            i += 1
            tabs = "\t" * (indent)
            print(f"{tabs}{i}/{len(d)}", end=" ")
            pretty(value, indent + 1)
    else:

        if isinstance(d, dict):
            for key, value in d.items():
                print("\t" * indent + str(key))
                if isinstance(value, dict):
                    pretty(value, indent + 1)
                else:
                    print("\t" * (indent + 1) + str(value))
        else:
            tabs = "\t" * (indent)
            duzhki = ""
            if isinstance(d, str):
                duzhki = '"'
            print("\t" * indent + f"{duzhki}{d}{duzhki}")


def print_pretty(mess={}):
    # print(1)
    pretty(mess)
    # print(2)


def wait_pretty(mess={}):
    print_pretty(mess)
    wait_for_ok()


def show_dict_new(dct, indent=1):
    pretty(dct, indent=indent)


def pretty_dict(dct, name=""):
    if name:
        logger.debug(f"{type(dct)} {name}:")
    try:
        return json_dumps(dct, indent=4)
    except Exception as er:
        return f"{dct=}"


def show_dict(dct, otstyp="\t", good_keys=False, max_length=5000, bad_keys=[]):
    fun = "show_dict"
    keys = list(dct.keys())
    keys.sort()
    if good_keys == False:
        good_keys = keys[:]

    if type(otstyp) == type(2):
        otstyp = otstyp * "\t"

    # print(good_keys)

    for k in good_keys:
        if k not in dct or k in bad_keys:
            continue

        value = dct[k]
        print(otstyp + str(k), end="")
        # print(f"{k=} {type(value) == list}")
        if not type(value) == list:
            try:
                v = str(value)
                if len(v) > max_length:
                    v = "too_long"

                v = "\n" + otstyp * 2 + v
                if len(v) > max_length:
                    v = "too_long"
                # uni(v)
                print(v)
            except Exception as er:
                print(f"{fun} error: {er}")
        else:
            if value == []:
                print(f"{otstyp*3}, []")
            else:
                print()
                show_list(value, otstyp * 3, 1)


def wait_for_ok(
    start_mess="сделай что должен и ВВЕДИ '1'",
    good_answer=["ok", "1", 1],
    repeat_mess="введи 1, если готов продолжать",
):
    """ждем пока введут правильные значения"""
    print(f"`{start_mess}`, waiting - check")
    while True:
        otvet = input()
        if otvet in good_answer:
            break
        else:
            print("\t" + repeat_mess)


def show_list(lst, otstyp="\t", want_print=1):
    rez = []
    for i, k in enumerate(lst, 1):
        # print(k)
        m = f"{otstyp}{i}/{len(lst)}\t{k}"
        rez.append(m)
    # print(rez)

    if want_print:
        for _ in rez:
            print(_)
    else:
        rez = "\n".join(rez)
        return rez


def Show_step(s, otstyp_size=2):
    try:
        otstyp = "\t" * otstyp_size

        if otstyp_size == 0:
            for i in range(8):
                print("*" * i * 3)

        print("\n", otstyp, "_" * 30)
        print(otstyp, end="")
        # uni(s, 1)
        print(s)
        print(otstyp, "_" * 30, "\n")

        if otstyp_size == 0:
            for i in range(7, 0, -1):
                print("*" * i * 3)
    except:
        print(s)


def print_otstup(m="", cnt=3):
    otstup = "\n" * cnt
    print(otstup + str(m))


def flush():
    sys.stdout.flush()


if __name__ == "__main__":
    special = "capturing"
    special = "pprint_to_html"
    special = "show_step"
    special = "show_dict"

    if special == "show_step":
        Show_step("Ура!")

    elif special == "capturing":
        with Capturing() as output:
            print("hello world")

        print("displays on screen")

        with Capturing(output) as output:  # note the constructor argument
            print("hello world2")

        print("done")
        print("output:", output)

    if special == "pprint_to_html":
        people = [
            {"first": "Brian", "last": "Kernighan"},
            {"first": "Dennis", "last": "Richie"},
        ]

        obj = {
            "1": 2,
            "3": ["4", 5],
            "people": people,
        }
        pprint(obj)
        print("-" * 10)

        html = pprint_to_html(obj)
        print(html)
        # html = pprint_to_html_old(obj)
        # print(html)

    if special == "show_dict":
        t = 1
        if t:
            dct = {
                "item": 1,
                "lst1": [1, 2],
            }
            show_dict(dct)
            show_dict_new(dct)
            os._exit(0)

        t = 1
        if t:
            polja = [
                {1: 2},
                {3: 4},
            ]
            show_list(polja)
            os._exit(0)

        t = 1
        t = 0
        if t:
            pretty(
                [[0, 1], ["a", 1], {1: 1, 2: "2",},]
            )
        t = 1
        t = 0
        if t:
            wait_for_ok("good")
