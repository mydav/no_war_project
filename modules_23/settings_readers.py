#!/usr/bin/python
# -*- coding: utf-8 -*-

from modules_23.minimum_important_functions import *
import os

# from modules.find_functions import find_from_to_one
# from modules.logging_functions import get_logger

logger = get_logger(__name__)


def get_dict_from_txt(f_in):
    """получает файлик с такими строчками:
    name = 'narkis913zagibalov'
    и возвращает словарь обычный
    """
    rezult = {}
    #    lines = text
    lines = text_from_file(f_in).strip()
    lines = lines.split("\n")
    new_code = []
    for line in lines:
        if line.strip() == "":
            continue
        #        logger.debug(line)
        #        line = line.replace('=', ':')
        (x, y) = line.split("=")
        x = x.strip()
        y = y.strip()
        new_code.append("'%s':%s" % (x, y))
    new_code = "{" + ",\n".join(new_code) + "}"
    #    logger.debug('new_code %s' % new_code)
    return eval(new_code)


def put_settings_to_text(task={"dct": "", "f": ""}):
    delim = task.get("delim", "=")
    dct = task["dct"]
    f = task.get("f", "")

    keys = list(dct.keys())
    keys.sort()

    lines = []
    for k in keys:
        v = dct[k]
        line = delim.join(map(str, [k, v]))
        lines.append(line)
    rez = "\n".join(lines)
    if f == "":
        return rez
    text_to_file(rez, f)


def get_settings_from_txt_and_my_txt_files(files=[]):
    settings_from_files = {}
    for f_settings in files:
        f_settings = os.path.abspath(f_settings)
        logger.debug(f"get settings from {f_settings}")
        if not os.path.isfile(f_settings):
            logger.warning(f"{f_settings=} not exists")
            continue
        settings_text = text_from_file(f_settings)
        settings_from_file = get_settings_from_txt_and_my_txt(settings_text)

        settings_from_files = add_defaults(
            settings_from_file, settings_from_files
        )
    return settings_from_files


def get_settings_from_txt_and_my_txt(text=""):
    dct1 = get_settings_from_my_txt(text)
    dct2 = get_settings_from_text(text)
    dct1.update(dct2)
    if "" in dct1:
        del dct1[""]
    return dct1


def get_settings_from_my_txt(text):
    """получаем текст вида <x>значение<y> и берет автоматом все значения"""
    otl = 1
    otl = 0

    obrezka = "<obrezaluss>"  # все что после этого - игнорим

    # text = text.strip()
    # lines = text.split('\n')
    rezult = {}
    text = text.replace("\r", "\n")
    text = "\n" + text + "\n"

    if text.find(obrezka) != -1:
        text = find_from_to_one("nahposhuk", obrezka, text)

    items = text.split("\n<")[1:]
    # items = text.split('\r<')[1:]
    if otl:
        logger.debug("%s items" % len(items))
        show_list(items)
    for item in items:
        k = find_from_to_one("nahposhuk", ">", item)
        if otl:
            logger.debug("key %s" % k)
        k_start = "\n<%s>" % k

        # k_start = '<%s>' % k
        #        k_end = '</%s>\n' % k
        k_end = "</%s>" % k
        if text.find(k_end) != -1:
            #            logger.debug('    %s' % k)
            v = find_from_to_one(k_start, k_end, text)
            rezult[k] = v
    return rezult


def get_settings_from_text(text, delim="="):
    text = text.strip()
    lines = text.split("\n")
    # show_list(lines)
    rezult = {}
    section = ""
    for line in lines:
        if line.strip() == "":
            continue
        # logger.debug(line)
        #        line = line.replace('=', ':')
        # секции могу организовывать
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1].strip()
            rezult[section] = {}
            continue

        k = find_from_to_one("nahposhuk", delim, line).strip()
        v = find_from_to_one(delim, "nahposhuk", line).strip()

        if section == "":
            searching_in = rezult
        else:
            searching_in = rezult[section]

        if k in searching_in:
            continue

        searching_in[k] = v
    return rezult


def get_settings_from_txt(f_in, delim="="):
    """получает файлик с такими строчками:
    name = 'narkis913zagibalov'
    и возвращает словарь обычный
    """
    rezult = {}
    if not file_exists(f_in):
        return rezult
    return get_settings_from_text(text_from_file(f_in), delim)


if __name__ == "__main__":
    f = r"s:\!kyxa\!code\bet365_valuebets\settings_vilki.txt"
    settings = get_settings_from_txt_and_my_txt(f)
    logger.debug("settings=%s" % settings)
