# pyarmor options: no-spp-mode
# -*- coding: utf-8 -*-

import os

from colorama import init as init_colorama
from colorama import deinit as deinit_colorama
from colorama import Fore, Back, Style
import logging

inited_colorama = False


def init_colorama_once(*args, **kwargs):
    global inited_colorama
    if not inited_colorama:
        # print("init colorama")
        init_colorama(*args, **kwargs)
        inited_colorama = True

    else:
        print("     colorama already inited")


# def init_colorama_once(*args, **kwargs):
#     init_colorama(*args, **kwargs)


def color_text(text="", fg="blue", bg=""):
    """fg - текст
    bg - фон
    """
    end = MyColors.END
    fg = color_to_foreground(fg)
    bg = color_to_background(bg)
    # text_unicode = text_to_unicode_for_color(text)
    text_unicode = text
    return bg + fg + text_unicode + end

    try:
        return bg + text_unicode
    except Exception as er:
        return text_unicode


def return_with_color_old(*args, **kwargs):
    kwargs["mode_return"] = "return"
    return print_with_color(*args, **kwargs)


def print_with_color(text="", color="", end="", mode_return="print", **kwargs):
    # Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
    # Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
    # Style: DIM, NORMAL, BRIGHT, RESET_ALL
    fun = "print_with_color"
    bg = color_to_background(color)

    # нужно тут инициацию, чтобы при прерывании можно было смотреть номер строки
    text_unicode = None
    t = 0
    t = 1
    if t:
        init_colorama(autoreset=True)
        print_polube_for_color(
            text_unicode, text, bg, end=end, mode_return="print", **kwargs
        )
        deinit_colorama()


def print_polube_for_color(
    text_unicode="", text="", bg="", end="", mode_return="", **kwargs
):
    fun = "print_polube_for_color"
    if text_unicode is None:
        text_unicode = text_to_unicode_for_color(text)

    if not mode_return:
        mode_return = "print"

    # if type(text_unicode) not in [u'', 'str']:
    #     text_unicode = str(text_unicode)

    r = ""
    if mode_return != "print":
        try:
            return bg + text_unicode
        except Exception as er:
            return text_unicode

    try:
        if end == "":
            print(bg + text_unicode)
        else:
            print(bg + text_unicode),
    except Exception as er:
        try:
            str_text = str(text)
            print(bg + str_text)
        except Exception as er:
            logging.error("             ERROR %s, print normal %s" % (fun, er))
            print("         unable to print with color")


def print_h1(text="", **kwargs):
    return print_with_color(text, "h1", **kwargs)


def print_h2(text=""):
    print_with_color(text, "h2")


def print_h3(text=""):
    print_with_color(text, "h3")


def print_yes(text=""):
    print_with_color(text, "yes")


def print_no(text=""):
    print_with_color(text, "no")


def print_warning(text=""):
    print_with_color(text, "warning")


def print_error(text=""):
    print_with_color(text, "red")


def print_success(text=""):
    print_with_color(text, "green")


def print_info(text=""):
    print_with_color(text, "info")


def print_debug(text=""):
    print_with_color(text, "debug")


def color_to_foreground(color="", default=""):
    if isinstance(color, str):
        color_upper = color.upper()
        color = getattr(Fore, color_upper, default)
    return color


def color_to_background(color="", default=""):
    if color in ["yes", "success", "green"]:
        bg = Back.GREEN

    elif color in ["no", "red", "error"]:
        bg = Back.RED

    elif color in ["h1", "info"]:
        bg = Back.BLUE

    elif color in ["h2", "yellow", "warning"]:
        bg = Back.YELLOW

    elif color in ["debug"]:
        bg = Back.WHITE
    else:
        color_upper = color.upper()
        bg = getattr(Back, color_upper, default)
    return bg


def text_to_unicode_for_color(value=""):
    if isinstance(value, bytes):  # unicode Не работает?
        return value
    try:
        r = value.decode("utf8", "ignore")
    except Exception as er:
        # t, er = sys.exc_info()[:2]
        # print(er)
        # except Exception, er:
        r = value
    return r


class MyColors:
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    DARKCYAN = "\033[36m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


init_colorama_once(autoreset=True)

# print("+print_colored")

if __name__ == "__main__":
    # os._exit(0)

    try:
        1 / 0
    except Exception as er:
        print(er)

    init_colorama_once(autoreset=True)
    t = 0
    t = 1
    if t:
        t = "я крутой текст"
        t1 = color_text(t, "black", "blue")
        t2 = color_text(t, "red")
        t3 = color_text("finished printing", "green")
        t4 = color_text("default color")
        lst = [t1, t2, t3]
        # print ' '.join(list(map(str, lst)))
        print("%s %s %s %s" % (t1, t2, t3, t4))
        message = (
            Fore.RED
            + "красный текст"
            + Back.GREEN
            + "and with a green background"
            + Back.BLUE
            + "and blue"
            + Back.RESET
            + "NORMAL"
        )
        print(message)

        init_colorama_once(autoreset=True)
        message = "UPDATED: %s" % message
        print(message)
        os._exit(0)

    t = 1
    t = 0
    if t:
        t = "normal %s blue % yellow normal" % (Back.BLUE, Back.YELLOW)
        print(t)
        os._exit(0)

    t = 1
    t = 0
    if t:
        print_warning(["1", 2, "Желтый"])
        r = print_h1("h1", end=",")
        print("r=", r)
        print_warning("warning")
        print_error("error")
        # os._exit(0)

    t = 1
    t = 0
    if t:
        print("colorama test:")
        fun_to_arg = [
            [print_h1, "текст h1"],
            [print_h2, "h2"],
            [print_h3, "h3"],
            [print_yes, "yes"],
            [print_no, "no"],
        ]
        print_h1("тест h1")
        print_h2("test h2")
        print_h3("test h3")

        for fun, arg in fun_to_arg:
            fun(arg)
        # print('тест')
        # uni('тест')
        # uni2('тест')

        # wait_for_ok()

    t = 0
    t = 1
    if t:
        colors_lines = ""

        init_colorama_once(autoreset=True)
        message = (
            Fore.RED
            + "красный текст"
            + Back.GREEN
            + "and with a green background"
            + Back.BLUE
            + "and blue"
            + Back.RESET
            + "NORMAL"
        )
        print(message)
        os._exit(0)
        print(
            Fore.RED
            + "some red text"
            + Back.GREEN
            + "and with a green background"
            + Back.BLUE
            + "and blue"
            + Back.RESET
            + "NORMAL"
        )
        # os._exit(0)

        print(Back.GREEN + "and with a green background")
        print(Back.RED + "and with a green background")
        print(Style.DIM + "and in dim text")
        print(Fore.RED + "some red text")
        print("automatically back to default color again")
        print(Style.RESET_ALL)
        print("back to normal now")
        print(Style.BRIGHT + Fore.RED + "some bright red text")

        print(MyColors.BOLD + MyColors.RED + "Hello World !" + MyColors.END)
        print("\033[1m  Your Name  \033[0m")
        print("\033[1m" + "Hello")
        print("\033[1;37mciao!")

        start = "\033[1m"
        end = "\033[0;0m"
        print("The" + start + "text" + end + " is bold.")

    t = 0
    t = 1
    if t:
        from termcolor import colored

        print(colored("Hello", "green"))
        print(colored("Hello", attrs=["bold"]))

        from termcolor import cprint

        cprint("Hello temcolor", "green", attrs=["bold"], file=sys.stderr)
        # wait_for_ok()

    t = 1
    if t:
        import ctypes

        # Constants from the Windows API
        STD_OUTPUT_HANDLE = -11
        FOREGROUND_RED = 0x0004  # text color contains red.

        def get_csbi_attributes(handle):
            # Based on IPython's winconsole.py, written by Alexander Belchenko
            import struct

            csbi = ctypes.create_string_buffer(22)
            res = ctypes.windll.kernel32.GetConsoleScreenBufferInfo(
                handle, csbi
            )
            # assert res

            (
                bufx,
                bufy,
                curx,
                cury,
                wattr,
                left,
                top,
                right,
                bottom,
                maxx,
                maxy,
            ) = struct.unpack("hhhhHhhhhhh", csbi.raw)
            return wattr

        handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
        reset = get_csbi_attributes(handle)

        ctypes.windll.kernel32.SetConsoleTextAttribute(handle, FOREGROUND_RED)
        print("Cherry on top")
        ctypes.windll.kernel32.SetConsoleTextAttribute(handle, reset)

    t = 1
    if t:
        print("-" * 100 + "icolor")
        from icolor import cformat  # there is also cprint

        print(
            cformat(
                """This is #RED;a red string, partially with a #xBLUE;blue background
        This is \x1b[31ma red string, partially with a \x1b[44mblue background\x1b[0m"""
            )
        )

    # from blessings import Terminal

    # t = Terminal()

    # print(t.bold('Hi there!'))
    # print(t.bold_red_on_bright_green('It hurts my eyes!'))

    # wait_for_ok()

"""
в винде работает простейшее print_h1 print_yes print_no

https://stackoverflow.com/questions/287871/how-to-print-colored-text-to-the-terminal/3332860#3332860
"""
