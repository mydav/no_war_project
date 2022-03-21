# pyarmor options: no-spp-mode
# -*- coding: utf-8 -*-

# import six
from tabulate import tabulate
from modules.logging_functions import *

logger = get_logger(__name__)


def obj_to_utf8(obj):
    # txt = str(dct)
    # txt = []
    #    {k:v.encode('utf-8') if isinstance(v, basestring) else v for k,v in d.items()}
    # txt = str(dct)
    # txt = repr(dct)

    # if type(obj)==type(u''):

    def get_lapka(k):
        if type(k) in [type(1), type(0.1), type(True), type({})]:
            return ""
        return '"'

    final_list = []
    t = 0
    t = 1

    if t:
        if type(obj) in [type("str"), type("str")]:
            pass

        elif type(obj) in [type(u"str")]:
            obj = to_utf8_string(obj)
        elif type(obj) in [type(3), type(0.3), type(True)]:
            obj = str(obj)

        elif type(obj) == type([]):
            lst = []
            for k in obj:
                # logger.debug('key=%s' % k)
                lapka = get_lapka(k)
                v = obj_to_utf8(k)
                # logger.debug('v=%s' % v)
                v_new = "%s%s%s" % (lapka, v, lapka)

                lst.append(v_new)

            # logger.debug('lst=%s' % lst)
            lst = ", ".join(lst)
            obj = "[%s]" % lst

            # obj = ', '
        elif type(obj) == type({}):
            lst = []
            for k, v in obj.items():
                lapka = get_lapka(k)
                k = obj_to_utf8(k)
                k_new = "%s%s%s" % (lapka, k, lapka)

                lapka = get_lapka(v)
                v = obj_to_utf8(v)
                v_new = "%s%s%s" % (lapka, v, lapka)

                lst.append("%s:%s" % (k_new, v_new))
            lst = ", ".join(lst)
            obj = "{%s}" % lst
        #    {k:v.encode('utf-8') if isinstance(v, basestring) else v

        else:
            obj = str(obj)

    final_list.append(obj)

    txt = "".join(final_list)
    # logger.debug('final: %s' %s txt)

    t = 0
    if t:
        logger.debug(txt)
        logger.debug("\n" * 10 + "-" * 10)
        uni(txt)

        logger.debug("\n" * 10 + "-" * 10)
        uni2(txt)

        txt = text_to_charset(txt, "utf8")
        logger.debug(txt)
        uni(txt)
        uni2(txt)

    return txt


# def to_utf8_string(val):
#     if not isinstance(val, basestring):
#         return str(val)
#     if not isinstance(val, str):
#         val = val.encode("utf8")
#     return val


# def do_unicode(txt, charset="utf8"):
#     # сделать длинну текста такую, как я вижу
#     txt = unicode(txt, charset)
#     return txt


def unicode_encode(txt, charset="utf8"):
    # вернуть текст с уникода в читабельный
    # logger.debug(type(txt))
    if type(txt) == type(u""):
        txt = txt.encode(charset, "ignore")
    return txt


def deep_encode(obj, encoding="utf-8"):
    if isinstance(obj, unicode):
        return obj.encode(encoding)
    elif isinstance(obj, dict):
        return {
            deep_encode(key, encoding): deep_encode(value, encoding)
            for key, value in obj.items()
        }
    elif isinstance(obj, list):
        return [deep_encode(item, encoding) for item in obj]
    else:
        return obj


def see(txt, charset="utf8"):
    return do_unicode(txt, charset)


def see_to_norm(txt, charset="utf8"):
    return unicode_encode(txt, charset)


def see_to_norm_dct(r, charset="utf8"):
    # получаем словарь, и конвертим его с уникода
    r2 = {}
    for k in r:
        v = r[k]

        if type(k) == type(u""):
            k = see_to_norm(k, charset)

        if type(v) == type(u""):
            v = see_to_norm(v, charset)

        r2[k] = v

    return r2


def unicode_to_text(html, encoding="utf-8"):
    # return six.text_type(html, encoding)
    # # ...
    # if isinstance(html, unicode):
    #     html = html.encode(encoding)
    return html


if __name__ == "__main__":
    obj = {1: 2, "hello": b"world"}
    v = obj_to_utf8(obj)
    logger.info(v)

    data = u"oppa"
    txt = unicode_to_text(data)
    logger.debug("%s - new %s %s" % (type(data), type(txt), txt))
