#!/usr/bin/python
# -*- coding: utf-8 -*-

from hashlib import md5
import re
from modules.encoding_funcs import *
from modules.find_functions import *
import sys
from chardet import detect as chardet_detect
from modules_23.text_functions import *

logger = get_logger(__name__)


def to_hash(text, sposob="md5"):
    """перевести текст в хеш"""
    try:  # нужно для utf
        text = str(text)
    except Exception as er:
        er = f"to_hash: error str {er}"
        print(er)
        logger.error(er)
        pass
    if sposob == "md5":
        # return md5.new(text).hexdigest()
        encoded = text.encode()
        result = md5(encoded)
        h = result.hexdigest()
        # print(f"{h=}, {text=}")
        return h

    # elif sposob == 'crc32':
    #     return str(abs(crc32(text)))
    else:
        raise Exception(f"unknown {sposob=}")


def my_symbols(text, good=".0123456789"):
    text = str(text)
    r = []
    for x in text:
        if x in good:
            r.append(x)
    r = "".join(r)
    return r


def parse_settings_from_text(text="", delim="|", var_delim="="):
    """
        text = "from=hello world|more=1|more2=2"
        parse_settings_from_text(text) ->
            {'from': 'hello world', 'more': '1', 'more2': '2'}
    """
    fun = "parse_settings_from_text"
    items = [_ for _ in text.split(delim) if _.strip()]
    r = {}
    for item in items:
        parts = item.split(var_delim)
        if len(parts) != 2:
            logger.error(f"{fun} ERROR: {item=} with not 2 {parts=}")
            continue
        r[parts[0]] = parts[1]
    return r


def found_atLeastOne(phrases=[], p=""):
    for phrase in phrases:
        if phrase in p:
            return True
        else:
            # print 'no phrase %s in page' % phrase
            pass
    return False


def found_all(phrases=[], p=""):
    for phrase in phrases:
        if phrase not in p:
            return False
    return True


def remove_empty_lines(
    text, delim="\n", return_delim="\n", trim_line: bool = True
):
    """убираем пустые строчки с текста"""
    body = []
    items = text.split(delim)
    for item in items:
        # item = item.strip()
        if item.strip() == "":
            continue
        if trim_line:
            item = item.strip()
        body.append(item)
    return return_delim.join(body)


def find_from_to_all(from_text, to_text, text):
    """получаем шаблон из от, до и - все возможные"""
    i_want = []
    items = text.split(from_text)[1:]
    for item in items:
        found = find_from_to_one("nahposhuk", to_text, item)
        #        uni( found )
        i_want.append(found)
    return i_want


def do_lower_utf8(text):
    return text.lower()


def do_lower(text, ch="1251"):
    """делаем все в нижнем регистре"""
    return text.lower()


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


def text_to_charset(
    text, to_charset="cp1251", charset="", errors="ignore", otladka=False
):
    logger.debug("text_to_charset not working in py3")
    return text

    if text == "":
        return text

    repl_charset = {"utf8": "utf-8", "cp-1251": "cp1251"}
    logger.debug("text=%s" % text)
    text = str(text)
    if otladka:
        logger.debug("[from:|%s| to:|%s|" % (charset, to_charset))
    if charset == "":
        charset = chardet_detect(text)["encoding"]
        if otladka:
            logger.debug("detected:|%s|" % charset)
        # ~ if charset in ['ISO-8859-2']:
        # ~ charset = 'utf8'

    if charset == None:
        return text
        pass
        if otladka:
            logger.debug("ups, charset None")
            return text

    charset = do_lower(charset)
    to_charset = do_lower(to_charset)
    charset = no_probely(charset, repl_charset)
    to_charset = no_probely(to_charset, repl_charset)

    if otladka:
        logger.debug(charset)
    if charset != None and charset != to_charset:
        if otladka:
            logger.debug("to_charset %s" % to_charset)
        try:
            text = unicode(text, charset, errors)
            text = text.encode(to_charset, errors)
        except Exception as err:
            logger.error("error %s" % err)
    #        text = unicode(text, charset)
    #        text = text.encode(to_charset, 'xmlcharrefreplace')
    else:
        if otladka:
            logger.debug("do not need encoding")

    return text


def no_probely_tupo(*args, **kwargs):
    kwargs["mode_replace"] = "one_by_one"
    return no_probely(*args, **kwargs)


def calculate_functions_in_text(phrase="", fun_txt="", fun=None):
    """
    замена текстовой ф-ии с аргументами на ее значение
    """
    repl = {}
    delim = "{%s(" % fun_txt  # '{score_handicap('
    parts = phrase.split(delim)
    for part in parts[1:]:
        args = find_from_to_one("nahposhuk", ")}", part)
        value = fun(args)
        repl["{%s(%s)}" % (fun_txt, args)] = value
    phrase = no_probely(phrase, repl)
    return phrase


if __name__ == "__main__":
    t = 1
    if t:
        f = r"s:\!kyxa\!code\!documentation\py4seo\advanced\08\dor_minimum\forted\temp\markets_КиберФутбол.txt"
        f = text_to_charset(f)
        logger.debug(f)
        os._exit(0)

    from pprint import pprint

    logging.basicConfig(
        format="%(filename)s[:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s",
        level=logging.DEBUG,
    )

    special = "to_hash"
    special = "parse_settings_from_text"
    special = "no_probely"

    if special == "parse_settings_from_text":
        text = "from=hello world|more=1|more2=2"
        pprint(parse_settings_from_text(text))

    elif special == "to_hash":
        key = "hello привет"
        print(to_hash(key))

    if special == "no_probely":
        body = "Hello"

        body = b"" b"Hello big world" b""

        body = b"<h1>Hello</h1>"
        replaces = {
            # "Hello": "Привет",
            b"Hello": "Привет",
            # b"Hello": "Привет".encode("utf8"),
        }
        print(body)
        print(replaces)

        body = no_probely(body, replaces)
        print("\n" * 3, "RESULT:", body)
