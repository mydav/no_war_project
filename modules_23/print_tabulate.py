#!/usr/bin/python
# -*- coding: utf-8 -*-

from tabulate import tabulate
from modules.logging_functions import *

logger = get_logger(__name__)


def print_my_tabulate(*args, **kwargs):
    """
        печатаем
        в консоль некоторые символы не умеют передаваться, тогда хоть криво но вывожу
    """
    fun = "print_my_tabulate"
    debug = True
    debug = False
    if debug:
        # print 'lst:', lst
        print("args: %s" % args)
        print("kwargs: %s" % kwargs)

    # сначала переводим в печатный вид

    t = 1
    t = 0
    if t:
        args = list(args)
        lst = args[0]
        lst = lst_to_tabulate(lst)
        args[0] = lst

        args = tuple(args)

    # print lst
    # wait_for_ok()
    # txt = my_tabulate(*args, **kwargs)
    # print txt

    if debug:
        print("new args %s, new kwargs %s" % (args, kwargs))

    try:
        txt = my_tabulate(*args, **kwargs)
        print(txt)
    except Exception as er:
        # txt = my_tabulate(lst, to_utf8=1)
        # print txt
        logger.error(er)
        logger.warning("%s error, but print even somethig" % fun)
        lst = args[0]
        for _ in lst:
            print(_)
        # print(lst)
        # show_list(lst)
        txt = str(lst)

    # wait_for_ok()
    return txt


def lst_to_tabulate(lst=[[]]):
    return lst
    # lst = lst_to_unicode(lst, 'charset', 'cp1251')
    lst = lst_to_unicode(lst, "charset", "cp866")
    # wait_for_ok(lst)

    lst = lst_to_unicode(lst, "unicode", "cp866")
    # wait_for_ok(lst)
    return lst


def lst_to_unicode(lst=[[]], spec_task="unicode", charset="utf8"):
    """
        для таб-списка нужен уникод. Делаем
        spec_task='unicode'
        spec_task='charset'
    """
    fun = "lst_to_unicode"
    lst_new = []
    for line in lst:
        line_good = []
        for item in line:
            if spec_task == "charset":
                if type(item) == type("str"):
                    try:
                        # item = item.encode(charset, 'ignore')
                        # item = item.encode(charset)#, errors='replace')
                        item = item.encode(charset, "replace")
                    except Exception as er:
                        logger.error("%s ERROR %s" % (fun, er))
                        pass

            elif spec_task == "unicode":
                if type(item) == type("str"):

                    try:
                        # item = item.decode(charset, 'ignore')
                        # item = item.decode(charset, errors='replace')
                        item = item.decode(charset, "replace")
                    except Exception as er:
                        logger.error("%s ERROR" % fun, er)
                        pass
                    # print str(item)
                    # print item, type(item)
                    # wait_for_ok()

                    # try:
                    #    item = do_unicode(item)
                    # except Exception, er:
                    #    pass
                    # print '    ', type(item)

            line_good.append(item)
        lst_new.append(line_good)
    lst = lst_new[:]
    return lst


def my_tabulate(lines0, tablefmt="orgtbl"):
    return tabulate(lines0, tablefmt=tablefmt)

    fun = "my_tabulate"
    charset = "cp1251"
    charset = "cp866"
    # print len(lines),

    lines = lst_to_tabulate(lines0)
    # lines = lines0[:]

    txt = tabulate(lines, tablefmt=tablefmt)
    return txt

    # wait_for_ok('my_tabulate1+')
    try:
        # txt = txt.decode('cp1251', 'ignore')
        txt = txt.encode(charset, "ignore")
    except Exception as er:
        logger.error(er)
    # print len(txt)
    # wait_for_ok(fun)
    return txt


def my_tabulate_split(lst=[], to_utf8=0, split_rounds=0):
    """красиво вывожу табличку
        split_round - разбивать табличку по раундам?
    """
    fun = "my_tabulate_split"
    tablefmt = "orgtbl"
    tablefmt = "fancy_grid"

    if not split_rounds:
        pass
    else:
        delim_line = ["*" * 3] * len(
            lst[0]
        )  # добавляю эту строку перед каждым новым раундом

        lst_new = []
        last_pround = "preflop"
        for line in lst:
            pround = line[0]
            if pround != last_pround:
                lst_new.append(delim_line)
                last_pround = pround
            lst_new.append(line)
        lst = lst_new[:]

    try:
        answer_txt = tabulate(lst, tablefmt=tablefmt)
    except Exception as er:
        logger.error("    error %s: %s" % (fun, er))
        answer_txt = "error in %s" % (fun) + str(lst)

    # answers_txt.append(v)

    # answer_txt = '\n'.join(answers_txt)

    if to_utf8:
        answer_txt = answer_txt.encode("utf-8")
    return answer_txt


def my_tabulate_list_of_dicts(data=[], keys=[], titles=[], tablefmt="orgtbl"):
    lst = []
    if len(data) == len(titles):
        row = [""] + titles
        lst.append(row)

    if not keys:
        keys = data[0].keys()
        keys.sort()

    for k in keys:
        row = [k]
        for dct in data:
            row.append(dct.get(k, ""))
        lst.append(row)

    # show_list(lst)
    print_my_tabulate(lst, tablefmt=tablefmt)


if __name__ == "__main__":
    lines = [
        [1, 2],
        [3, 4],
        ["привет", "hello"],
    ]
    print_my_tabulate(lines)
    # print(my_tabulate(lines))
    # print(tabulate(lines))
    t = 0
    t = 1
    if t:
        charset = "cp1251"
        charset = "utf8"
        log = [
            [u"estará aquí", "Traducción", "inglés",],
            ["1", u"2", "3",],
            [4, 5, 6],
        ]
        tablefmt = "fancy_grid"
        tablefmt = "orgtbl"

        print_my_tabulate(log)

        print_my_tabulate(log, tablefmt=tablefmt)
        # wait_for_ok()

        t = 1
        if t:
            # spec_task = 'charset'
            # log = lst_to_unicode(log, spec_task, charset)
            log = lst_to_tabulate(log)

            # for k in log:
            #    print type(k),
            #    print str(k)
            #    print k

            print("log1: %s" % log)

            print(tabulate(log))
            print(my_tabulate(log))

        coupons = [
            {
                "status": True,
                "return": 97.91,
                "title": "Under (0.5)",
                "odds": 1.417,
                "stake": 69.1,
                "button_text": "None",
                "teams": "Al Zawraa v Al Shorta Baghdad",
                "market": "Asian Goal Line (O/U 0.5) - 90 Mins",
                "error": "",
                "footer_messages_short": "[]",
                "balance": "",
                "footer_message_short": "None",
                "footer_message": "",
            },
            {
                "status": True,
                "return": 100.42,
                "title": "Over",
                "odds": 3.25,
                "stake": 30.9,
                "button_text": "None",
                "teams": "Al Zawra'a v Al Shorta SC",
                "market": "Match Goals",
                "error": "",
                "footer_messages_short": "[]",
                "balance": "",
                "footer_message_short": "None",
                "footer_message": "",
            },
        ]
        keys = [
            "title",
            "market",
            "teams",
            "odds",
        ]
        my_tabulate_list_of_dicts(coupons, keys=keys, titles=[1, 2])
        os._exit(0)
