#!/usr/bin/python
# -*- coding: utf-8 -*-

# from modules_23.minimum_important_functions import *
import re
from modules.logging_functions import get_logger
from modules_23.minimum_important_functions_00 import get_python_version

logger = get_logger(__name__)


def no_probely_pusto(text, replaces={}, one=False, ignore_case=False):
    """то же что и no_probely, но если замена пустая - значит не заменяем ничего"""
    if replaces == {}:
        replaces = "pusto"
    return no_probely(
        text, replaces=replaces, one=one, ignore_case=ignore_case
    )


def no_probely_one(*args, **kwargs):
    kwargs["one"] = True
    return no_probely(*args, **kwargs)


def no_probely_multi(text, replaces="", limit_multi=3, *args, **kwargs):
    kwargs["limit_multi"] = limit_multi
    return no_probely(text, replaces, *args, **kwargs)


def no_probely_tupo(*args, **kwargs):
    kwargs["mode_replace"] = "one_by_one"
    return no_probely(*args, **kwargs)


def no_probely_py2(
    text,
    replaces="",
    one=False,
    ignore_case=False,
    limit=3,
    mode_replace="clever",
    limit_multi=1,
):
    """убивает много проблелов, и делает их минимальное количество

    # mode_replace = 'one_by_one_tupo'
    """
    #    print 'ignore_case: ', ignore_case
    #    debug = True

    if isinstance(text, int) or isinstance(text, long):
        text = str(text)

    text = text.strip()
    if replaces == "pusto":
        return text
    #        replaces=[]
    elif replaces == "":
        replaces = [
            (" ", " "),
            ("\t", " "),
            ("\n\n", "\n"),
            ("\n\r\n", "\n"),
            ("  ", " "),
        ]  #
        replaces = [
            ("\t", " "),
            ("\n\n", "\n"),
            ("\n\r\n", "\n"),
            ("  ", " "),
        ]  #
        limit = 5000
    # print replaces
    if type(replaces) == list:
        replaces_list = replaces[:]

    if type(replaces) != list:
        keys = replaces.keys()
        keys = sorted(keys, cmp=sort_len)
        replaces_list = [[k, replaces[k]] for k in keys]

    for limit_multi_now in range(limit_multi):
        for x, y in replaces_list:
            # x = str(bad)
            # y = str(replaces[bad])
            # x = bad
            # y = replaces[bad]
            x = str(x)
            y = str(y)
            i = 0
            if mode_replace == "one_by_one_tupo":
                while x in text:
                    i += 1
                    text = text.replace(x, y)

                    if one or i > limit:
                        break

                if debug:
                    logger.debug(
                        "replace `%s` to `%s`, final=`%s`" % (x, y, text)
                    )
                continue

            else:
                #            logger.debug(str([x, find_umno(text, x, ignore_case)]))
                while find_umno(text, x, ignore_case) != -1:
                    i += 1
                    if ignore_case:
                        text = ireplace(text, x, y)
                    else:
                        text = text.replace(x, y)
                    if one or i > limit:
                        break
    return text


def no_probely(
    text,
    replaces="",
    one=False,
    ignore_case=False,
    limit=3,
    want_check_type=True,
    limit_multi=1,
):
    """убивает много проблелов, и делает их минимальное количество"""
    fun = "no_probely"

    if want_check_type:
        if not isinstance(type, str):
            text = str(text)

    text = text.strip()

    if replaces == "pusto":
        return text
    #        replaces=[]

    elif replaces == "":
        replaces = [
            (" ", " "),
            ("\t", " "),
            ("\n\n", "\n"),
            ("\n\r\n", "\n"),
            ("  ", " "),
        ]  #
        replaces = [
            ("\t", " "),
            ("\n\n", "\n"),
            ("\n\r\n", "\n"),
            ("  ", " "),
        ]  #
        limit = 5000

    # print(f'replaces: {replaces}')
    # нужно чтобы был полюбе список, поэтому с словаря делаем список
    if isinstance(replaces, dict):
        keys = list(replaces.keys())
        keys.sort(key=lambda item: (-len(item), item))  # сначала длинные

        replaces_list = []
        for bad in keys:
            good = replaces[bad]
            replaces_list.append([bad, good])
        replaces = replaces_list[:]

    # print(replaces)

    if not isinstance(replaces, list):
        m = "no_probely ERROR: unknown type"
        logger.error(m)
        wait_for_ok(m)

    # print('is list')
    for limit_multi_now in range(limit_multi):
        for bad, good in replaces:
            bad = str(bad)
            good = str(good)
            # print(bad, good)
            i = 0
            try:
                while find_umno(text, bad, ignore_case) != -1:
                    i += 1
                    if ignore_case:
                        text = ireplace(text, bad, good)
                    else:
                        text = text.replace(bad, good)

                    if one or i >= limit:
                        break

            except Exception as er:
                print("ERROR %s: %s" % (fun, er))
                continue

    text = text.strip()

    return text


def no_probely_dct(dct_json, repl, enc="utf8"):
    for k in dct_json:
        v = dct_json[k]
        v = no_probely(v, repl)
        if enc != "":
            v = text_to_charset(v, enc, "cp1251")
        dct_json[k] = v
    return dct_json


def find_umno(text, ot, ignore_case=False):
    if ignore_case == False:
        return text.find(ot)
    else:
        return ifind(text, ot)


def ifind_last(text, ot, coding="cp1251"):
    #    поиск последнего символа вне зависимости от регистра
    poses = []
    last_pos = -1
    while True:
        t1 = ifind(text, ot, coding)
        #        print t1
        if t1 == -1:
            break

        poses.append(t1)
        last_pos = sum(poses)
        #        print 'last_pos: ', last_pos
        text = text[last_pos:]
    return last_pos


def ifind(text, ot):
    """Поиск вне зависимости от регистра
    """
    # ignorecase-find

    #    return re.search(re.escape(ot), re.escape(text), re.IGNORECASE)
    #    return re.match(re.escape(ot), re.escape(text), re.IGNORECASE)
    #    return re.search(re.escape(ot), re.escape(text), re.UNICODE|re.I|re.M|re.DOTALL|re.IGNORECASE)
    #    return re.search(re.escape(ot), re.escape(text), re.UNICODE|re.I|re.M|re.DOTALL|re.IGNORECASE)

    text1 = text.lower()
    ot1 = ot.lower()
    return text1.find(ot1)


def ireplace(text, old, new):
    """регистро-независимая замена - отсюда http://stackoverflow.com/questions/787842/case-insensitivity-in-python-strings
    но работает только с англ."""
    if False:
        return re.sub(
            r"(?i)" + re.escape("hippo"), lambda m: new, text
        )  # не заработало на

    # If you're only doing a single replace, or want to save lines of code, it's more efficient to use a single substitution with re.sub and the (?i) flag: re.sub('(?i)' + re.escape('hippo'), 'giraffe', 'I want a hIPpo for my birthday') –  Derrick Coetzee Nov 24 '11 at 1:04

    # 	http://stackoverflow.com/questions/919056/python-case-insensitive-replace
    insensitive_hippo = re.compile(re.escape(old), re.IGNORECASE)
    return insensitive_hippo.sub(new, text)


def sort_len(x, y):
    #    print x, y
    #    print len(x), len(y)
    return len(y) - len(x)


def filename(text_start, allow_slashes=True, only_bukvi=False):
    """транслитерируем"""
    slash = ""
    if allow_slashes:
        slash = "\/"

    LettersFrom = "абвгдезиклмнопрстуфыэйхё"
    LettersTo = "abvgdeziklmnoprstufyejhe"
    Consonant = "бвгджзйклмнпрстфхцчшщ"
    Vowel = "аеёиоуыэюя"
    BiLetters = {
        "ж": "zh",
        "ц": "ts",
        "ч": "ch",
        "ш": "sh",
        "щ": "sch",
        "ю": "ju",
        "я": "ja",
    }
    znaki = [
        ("ь", ""),
        ("ъ", "j"),
        (" ", "-"),
    ]
    odnoznakovie = [
        ("jj", "j"),
        ("  ", " "),
        ("__", "_"),
        ("--", "-"),
    ]  # эти по 2 буквы подряд нельзя
    #    ne_start_stop = ['-', '_'] #с этих нельзя начинаться-заканчиваться

    all_znaki = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890абвгдезиклмнопрстуфыэйхёбвгджзйклмнпрстфхцчшщжцчшщюя- _&@%/."

    text = strtolower(text_start)
    #    text = do_lower(text_start)

    for znak in text:
        #        print znak
        if znak not in all_znaki:
            if only_bukvi:
                text = text.replace(znak, "")
            else:
                text = text.replace(znak, "-")

    for (x, y) in znaki:
        text = text.replace(x, y)
    #    //transliterating
    text = strtr(text, (LettersFrom, LettersTo))
    text = strtr(text, BiLetters)

    for (double, one) in odnoznakovie:
        while text.find(double) != -1:
            text = text.replace(double, one)

    #    try:
    #        if text[0] in ne_start_stop:
    #            text = text[1:]
    #        if text[-1] in ne_start_stop:
    #            text = text[:-1]
    #    except:
    #        uni(text_start)

    #    text = preg_replace("/j{2,}/", "j", text)
    #
    #    text = preg_replace("/[^".slash."0-9a-z_\-]+/", "", text)

    return text


def strtolower_py3(text):
    return text.lower()


def strtolower_py2(text):
    """переводит текст в нижний регистр - ибо встроенная ф-я с русским не работает"""
    big_small = {
        "А": "а",
        "Б": "б",
        "В": "в",
        "Г": "г",
        "Д": "д",
        "Е": "е",
        "Ё": "ё",
        "Ж": "ж",
        "З": "з",
        "И": "и",
        "Й": "й",
        "К": "к",
        "Л": "л",
        "М": "м",
        "Н": "н",
        "О": "о",
        "Р": "р",
        "П": "п",
        "С": "с",
        "Т": "т",
        "У": "у",
        "Ф": "ф",
        "Х": "х",
        "Ц": "ц",
        "Ч": "ч",
        "Ш": "ш",
        "Щ": "щ",
        "Ъ": "ъ",
        "Ь": "ь",
        "Ы": "ы",
        "Э": "э",
        "Ю": "ю",
        "Я": "я ",
    }

    for bukva in big_small.keys():
        text = text.replace(bukva, big_small[bukva])
    return text


def strtr(text, replace_pairs):

    """Эта функция возвращает строку str, в которой каждое вхождение любого символа из перечисленных в from заменено на соответствующий символ из строки to
    Ф-Я НЕ ПРОВЕРЕНА!"""
    zamenjaem = {}
    t = type(replace_pairs)

    if t == tuple:  # значит получили 2 строчки текста
        old, neww = replace_pairs
        # print len(old), len(neww)
        for i in range(len(old)):
            zamenjaem[old[i]] = neww[i]
    elif t == dict:  # а иначе сразу получаем словарь
        zamenjaem = replace_pairs
    else:
        logger.debug("%s %s" % (t, replace_pairs))
        logger.error("CAN'NT REPLACE - UNKNOWN TYPE")
        return ""

    for was in zamenjaem:
        text = text.replace(was, zamenjaem[was])
    return text


# version dependency
if get_python_version() >= 3:
    strtolower = strtolower_py3
else:
    strtolower = strtolower_py2


if __name__ == "__main__":
    name = "12314 1234 /1234 .раз"
    logger.debug(filename(name))
