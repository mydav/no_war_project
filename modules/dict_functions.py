import os
from copy import deepcopy
from modules.text_functions import no_probely
import json
from modules.encoding_funcs import deep_encode
from modules.find_functions import found_atLeastOne
from modules.list_functions import clear_list
from modules_23.numbers_functions import my_int
from modules_23.dict_functions import *

from modules.logging_functions import get_logger

logger = get_logger(__name__)


def add_defaults(dct1, dct2):
    try:
        dct = deepcopy(dct1)
    except Exception as er:
        logger.debug("can not deepcopy in add_defaults")
        dct = dct1

    for k, v in dct2.items():
        if k not in dct:
            dct[k] = v
    # dct1.update(dct2)
    return dct


def add_defaults_py2(
    task, default, keys_float=[], keys_int=[], want_int=True
):  # , perezapisj=0
    """ф-я в py2"""
    r = {}
    for k in task:
        r[k] = task[k]

    for k in default:
        v_default = default[k]

        #        if perezapisj:
        #            v = v_default
        #        else:
        v = task.get(k, v_default)
        if type(v) in [type(10), type(0.1)]:
            pass
        else:
            if want_int and str_is_int(v):
                try:
                    v = int(v)
                except Exception as er:
                    pass

        if k in keys_float:
            try:
                v = float(v)
            except Exception as er:
                pass

        if k in keys_int:
            try:
                v = int(v)
            except Exception as er:
                pass

        r[k] = v

    return r


def hitro_dict(dct, default_key="dct"):
    # хитрословарь - ф-я может получать как текст так и словарь, но нам нужно именно словарь
    # print type(dct)
    # if type(dct)==type('str') or type(dct)==type(u'u'):
    if type(dct) != type({}):
        task = {
            default_key: dct,
        }
    else:
        task = dct
    # print task
    return task


class Bunch(object):
    """get dict, and use d.x instead of d['x']
    source: http://stackoverflow.com/questions/18090672/convert-dictionary-entries-into-variables-python"""

    def __init__(self, adict):
        self.__dict__.update(adict)

    def __repr__(self):
        return f"<B:{self.__dict__}>"


def get_dict_with_new_keys(abb_dict, tpl="s:[key]"):
    info = {}
    for k in abb_dict:
        k_new = tpl.replace("[key]", str(k))
        v = abb_dict[k]
        info[k_new] = v
    return info


def obj_to_json(obj={}):
    return json.dumps(obj)


def obj_from_json(html="", encoding="utf-8", debug=True, want_retry=True):

    htmls = [html]
    if want_retry:
        html2 = html
        # бинарные нужно в текст
        if not isinstance(html, str):
            html2 = html2.decode("utf-8")
        htmls.append(
            html2.replace("'", '"')
        )  # решаю JSONDecodeError('Expecting property name enclosed in double quote

    json_answer = None
    for html in htmls:
        try:
            json_answer = json.loads(html)
            break
        except Exception as er:
            if debug:
                logger.error(f"{er=}")

    if json_answer is None:
        json_answer = {
            "error": "ERROR_NOT_JSON",
            "body": html,
        }

    if encoding:
        json_answer = deep_encode(json_answer, encoding)
    return json_answer


def prepare_dict_value(
    selection={},
    default_dct={},
    keys_int=None,
    keys_int_parts=None,
    keys_float=None,
    keys_float_parts=None,
    keys_list=None,
    keys_list_part=None,
    keys_str=None,
):
    """Часто при загрузке с екселя нужно определенно обработать словарь"""
    selection = add_defaults(selection, default_dct)
    keys_list = keys_list if keys_list is not None else {}
    keys_str = keys_str if keys_str is not None else {}
    keys_list_part = keys_list_part if keys_list_part is not None else {}

    for key, value in selection.items():
        if value is None:
            continue

        if keys_float_parts:
            want_float = found_atLeastOne(keys_float_parts, key)
        else:
            want_float = False
        if ((keys_float and key in keys_float) or want_float) and isinstance(
            value, str
        ):
            try:
                value = float(value)
            except Exception as er:
                value = ""

        if keys_str and key in keys_str:
            value = str(value)

        if keys_int_parts:
            want_int = found_atLeastOne(keys_int_parts, key)
        else:
            want_int = False
        # print(want_int, key)
        # if want_int:
        # print(type(value), value)
        # wait_for_ok()
        if ((keys_int and key in keys_int) or want_int) and isinstance(
            value, str
        ):
            value = my_int(value)
        # print('%s want_int %s, value %s' % (key, want_int, value))

        list_delim = keys_list.get(key, None)
        if not list_delim:
            for k, v in keys_list_part.items():
                # print(k, key, k in key)
                if k in key:
                    list_delim = v
                    break

        if list_delim is not None and isinstance(value, str):
            value = clear_list(value.split(list_delim))

        selection[key] = value
        # wait_for_ok(selection)

    return selection


if __name__ == "__main__":
    special = "obj_from_json"

    if special == "obj_from_json":
        html = '{"weight": 25.1}'
        html = "{'weight': 25.1}"
        html = """{'sr': 9, 'vr': '515', 'cs': 2, 'st': 1, 'mi': 'missing_stake', 'mv': '', 'bt': [{'ob': [], 'ms': 0.0, 'er': True, 'ra': 0.0, 'rp': 0.0, 'bt': 1, 'od': '22/1', 'fi': 112425394, 'pt': [{'pi': 396693716}], 'sr': 2}, {'ob': [], 'ms': 0.0, 'er': True, 'ra': 0.0, 'rp': 0.0, 'bt': 1, 'od': '28/1', 'fi': 112425394, 'pt': [{'pi': 396693709}], 'sr': 2}]}"""
        html = """{'sr': 9, 'vr': '515'}"""
        html = b"""{'sr': 9, 'vr': '515'}"""
        r = obj_from_json(html)
        print(f"{r=}")
