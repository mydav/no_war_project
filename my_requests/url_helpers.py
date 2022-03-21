# -*- coding: utf-8 -*-

# import httplib
import socket

# from modules.find_functions import *
# from modules.file_functions import *
from modules.text_functions import *


def idna_to_domen(domen):
    """ convert idna to domen:utf8 .rf """
    fun = "domen_to_idna"
    try:
        # r = domen.decode('utf-8', 'ignore').encode('idna', 'ignore')
        r = domen.decode("idna", "ignore").encode("utf-8")
    except Exception as er:
        logger.error("er %s" % (fun, er))
        r = domen
    return r


def domen_to_idna(domen):
    """ convert domen:utf8 like .rf to idna"""
    fun = "domen_to_idna"
    if isinstance(domen, str):
        r = domen
    else:
        try:
            r = domen.decode("utf-8", "ignore").encode("idna")
        except Exception as er:
            logger.error("error %s: %s" % (fun, er))
            r = domen
    return r


def url_to_idna(url):
    """ convert url:utf8 like .rf to idna"""
    fun = "url_to_idna"
    # logger.debug("[%s: '%s'" % (fun, url))
    domen = get_domen_from_url(url)
    # logger.debug('domen[%s]' % domen)
    domen_idna = domen_to_idna(domen)
    url = url.replace(domen, domen_idna)
    # logger.debug('+%s]' % url)
    return url


def split_subdomain_domain(url=""):
    domainSubdomain = get_url_without_http_from_uDomain(url)
    parts = domainSubdomain.split(".")
    # logger.debug('domain_subdomain %s, parts %s' % (domainSubdomain, parts))
    subdomain = ""
    domain = ".".join(parts[-2:])
    if len(parts) > 2:
        subdomain = parts[0]
    return subdomain, domain


def get_url_with_http_from_uDomain(url="sub.domain.com"):
    url_http = url
    if url_http.find("http://") == -1:
        url_http = "http://%s/" % url_http
    return url_http


def get_url_without_http_from_uDomain(url="sub.domain.com"):
    url_no_http = url.replace("http://", "").replace("/", "")
    # wait_for_ok(url_no_http)
    return url_no_http


def get_domen_from_poddomen(poddomen):
    """из названия поддомена вырываем домен"""
    return ".".join(poddomen.split(".")[-2:])


def get_dir_from_url(poddomen):
    """из названия поддомена вырываем домен"""
    return "/".join(poddomen.split("/")[:-1]) + "/"


def get_good_url(url, remove_vars=False):
    """из строки c урлом отбрасываем www и хттп
	http://www.vitaminov.net/rus-drugsafety-0-0-6352.html -> vitaminov.net/rus-drugsafety-0-0-6352.html"""
    url = url.strip()
    url = url.lower()
    bad = ["http://", "www."]
    for b in bad:
        url = url.replace(b, "")
    if remove_vars:
        if url.find("?") != -1:
            url = find_from_to_one("nahposhuk", "?", url)

    return url


def get_domen_from_url(url, want_www=True):
    """из строки достает сам домен, без www и хттп
	http://www.vitaminov.net/rus-drugsafety-0-0-6352.html -> vitaminov.net"""
    more = {}
    if type(want_www) == type(True):
        more["want_www"] = want_www
    else:
        more = want_www

    want_www = more.get("want_www", True)
    want_port = more.get("want_port", True)

    url = url.strip()
    url = url.lower()
    bad = ["http://", "https://"]
    for b in bad:
        url = url.replace(b, "")

    url = url.split("/")[0]

    if not want_www and url.find("www.") == 0:
        url = url[4:]

    if not want_port:
        url = url.split(":")[0]  # убираем порт

    return url


def url_without_port(url):
    """урл без порта"""  # http://domen:80/...#удаляем порт с урла
    domen2 = get_domen_from_url(url, {"want_port": 1})
    domen3 = get_domen_from_url(url, {"want_port": 0})
    # 	domen3 = domen2.split(':')[0]
    # 	logger.debug('%s %s' % (domen3, domen2))
    if domen3 != domen2:
        after = find_from_to_one(domen2, "nahposhuk", url)
        do = find_from_to_one("nahposhuk", domen2, url)
        url_new = "%s%s%s" % (do, domen3, after)
        # 		domen2 = domen3
        # print 'url_new: ', url_new
        url = url_new
    return url


def get_vars_from_url(url, spliter="&", want_lower=False):
    """получает урл, и возвращает словарь из переменных с этого урла
	http://forum.onthewheels.ru/viewtopic.php?pid=218&utm_source=direct_click_sergijko ->
	{pid:218, utm_source:direct_click_sergijko}"""
    rezult = {}
    if want_lower:
        url = url.lower()
    # if len(url)>0 and url[0] in ['?']:
    # url = find_from_to_one('?', 'nahposhuk', url)

    if url.find("?") == -1:
        return rezult

    url = find_from_to_one("?", "nahposhuk", url)

    items = url.split(spliter)
    # show_list(items)
    for item in items:
        try:
            # var, val = item.split('=')
            var = find_from_to_one("nahposhuk", "=", item)
            val = find_from_to_one("=", "nahposhuk", item)
            rezult[var] = val
        except Exception as er:
            logger.error("error: %s" % er)
    return rezult


def get_settings_from_args(args=""):
    """
		получаю настройки с аргументов
	"""
    if not args:
        args = "".join(sys.argv[1:])

    # args = 'addurl_selenium ?spec_task=change_passwords_all??f_settings=setting_change_passwords_all.txt'
    # args = 'mozg.py ?spec_task=check_tunel??spec_tunel='

    logger.debug("args: %s" % args)

    settings_args = get_vars_from_url(args, "??")

    settings_args["args"] = args
    return settings_args


def remove_sessions_from_url(task):
    """убиваем сессии с урлов. Т.е. находм все потенциальные сессии в урле - и рубаем их
all_possible - это все возможные потенциальные сессии"""

    url = task["u"]
    check_names = task.get("check_names", 0)
    tip = task.get("tip", "all_possible")
    session_names = "phpsessid sid highlight".split(" ")

    r = url

    if tip == "all_possible":
        repl = {}
        vars = get_vars_from_url(url)
        for k, v in vars.iteritems():
            if v.find("#") != -1:
                v = find_from_to_one("nahposhuk", "#", v)

            is_session = False
            if can_be_session(v):
                is_session = True
            elif check_names and k.lower() in [session_names]:
                is_session = True

            if is_session:
                line = "%s=%s" % (k, v)
                repl[line] = ""

        # wait_for_ok()
        if repl != {}:
            # show_dict(repl)
            # for k, v
            ##wait_for_ok()
            # pass
            r = no_probely(r, repl)

            repl2 = [["&&", "&"], ["?&", "?"], ["&#", "#"]]
            r = no_probely(r, repl2)

            after = ""
            if r.find("#") != -1:
                after = "#" + find_from_to_one("#", "nahposhuk", r)
                r = find_from_to_one("nahposhuk", "#", r)
            r = url_del_bad_ends(r)
            r = r + after

        # r = remove_vars_from_url (url, parts)
    return r


def can_be_session(v):
    """проверяем может ли быть это значением сессии
	http://softtime.ru/forum/read.php?id_forum=1&id_theme=62185 - о длинне сессии"""

    # сессия может быть только такой длинны
    # if len(v) not in [32, 26, 22, 40, 27]:#это все возможные
    if len(v) not in [
        32,
        26,
    ]:  # но чтобы случайно не накоцать хорошие переменные в сайтах - ограничил до самых распространенных
        return False

    # сессия может быть только с таких символов
    good_symbols = "1234567890qwertyuioplkjhgfdsazxcvbnm"
    if my_symbols(v, good_symbols) != v:
        return False

    # и обязательно должны быть и цифры, и буквы
    good_symbols = "1234567890"
    if my_symbols(v, good_symbols) == "":
        return False

    good_symbols = "qwertyuioplkjhgfdsazxcvbnm"
    if my_symbols(v, good_symbols) == "":
        return False

    return True


def remove_vars_from_url(url, parts="PHPSESSID phpsessid sid"):
    if isinstance(parts, str):
        bads = parts.split(" ")
    else:
        bads = parts

    after = ""
    if url.find("#") != -1:
        after = "#" + find_from_to_one("#", "nahposhuk", url)
        url = find_from_to_one("nahposhuk", "#", url)

    new_url = url
    for bad in bads:
        start = "?"
        if new_url.find("%s%s=" % (start, bad)) != -1:
            value = find_from_to_one(
                "%s%s=" % (start, bad), "nahposhuk", new_url
            )
            if value.find("&") != -1:
                value = find_from_to_one("nahposhuk", "&", value)
            new_url = new_url.replace(
                "%s%s=%s" % (start, bad, value), "?"
            ).replace("?&", "?")

        start = "&"
        if new_url.find("%s%s=" % (start, bad)) != -1:
            value = find_from_to_one(
                "%s%s=" % (start, bad), "nahposhuk", new_url
            )
            if value.find("&") != -1:
                value = find_from_to_one("nahposhuk", "&", value)
            new_url = new_url.replace(
                "%s%s=%s" % (start, bad, value), ""
            )  # .replace('?&', '?')

    new_url = url_del_bad_ends(new_url)
    new_url = new_url + after

    return new_url


def url_del_bad_ends(url):
    """подчисточка урла - удаляем грязь с конца"""
    new_url = url
    lasts = ["?", "&"]
    while True:
        if len(new_url) > 0 and new_url[-1] in lasts:
            new_url = new_url[:-1]
        else:
            break
    return new_url


def remove_www(url):
    parts = url.split(".")
    if parts[0] == "www":
        return ".".join(parts[1:])
    return url


def url_abs(url_otn, url_part, otl=False):
    """получает урл с которого парсим, относительный урл от него и выдает абсолютный урл"""
    # 	получаю на сколько уровней следует поднятся вверх
    # 	if url_part=='/':
    # 		return url_otn
    if (
        url_part.lower().find("http://") == 0
        or url_part.lower().find("https://") == 0
        or url_part.lower().find("javascript:") == 0
    ):  # если это абсолютный урл
        return url_part

    elif url_part.lower().find("//") == 0:
        rash = url_otn.split("/")[0]
        return "%s%s" % (rash, url_part)

    # 	else:
    # 		return url_good(url_part)

    url_otn = url_good(url_otn, min=False, no_www=False)
    # print url_otn
    # wait_for_ok()

    # x/ad.hm to x/
    url_otn_dir = url_otn.split("/")
    url_otn_dir = "/".join(url_otn_dir[:-1]) + "/"
    # print url_otn_dir
    # show_list(url_otn_dir)
    # wait_for_ok()

    # 	if (otl) print "<hr><br>ищу пути: url_otn || $url_part<br>";
    if url_part.find("./") == 0:
        # 		if ($otl) print 'от ./';
        url_part = url_part[2:]
        res = url_otn_dir + url_part

    elif url_part.find("/") == 0:  # если от корня считаем
        # 		if ($otl) print 'от корня';
        url_part = url_part[1:]
        all_parts_of_url_otn = url_otn.split("/")
        need_parts = all_parts_of_url_otn[:3]
        url_otn = "/".join(need_parts)
        res = url_otn + "/" + url_part

    else:
        all_parts_of_url_part = url_part.split("../")

        levels_up = len(all_parts_of_url_part) - 1
        # 		if ($otl) echo "<br>", $levels_up, " уровней для обреза ";
        # print 'levels_up', levels_up
        if levels_up > 0:
            url_part = url_part.replace("../", "")
            all_parts_of_url_otn = url_otn.split("/")
            # 			if ($otl) oecho ($all_parts_of_url_otn, '', 1);
            need_parts = all_parts_of_url_otn[
                0 : max(len(all_parts_of_url_otn) - levels_up - 1, 3)
            ]
            url_otn = "/".join(need_parts)
            res = url_otn + "/" + url_part
        else:
            res = url_otn_dir + url_part
    # //	oecho ($all_parts_of_url_part, 'разбил дополнительный урл', 1);
    # //	print "<BR>$res";
    res = res.replace("http:///", "/")
    return res


def url_good(url, min=False, no_www=False):
    """получаем урл, и делаем его с http и без www"""
    if no_www:
        url = url.replace("www.", "")
    # url = url.replace('http://', '')
    if min:
        parts = url.split("/")
        last_part = parts[-1]
        if last_part != "":
            url = "/".join(parts[0 : len(parts) - 1])

    if url.find("http") != 0 and url.find("ftp") != 0:
        url = "http://" + (url + "/").replace("//", "/")
    return url


def url_base(url):
    """получаем самый базовый урл"""
    # 	url = url.replace('www.', '')
    url = url.replace("http://", "")

    parts = url.split("/")
    last_part = parts[0]
    url = "http://" + last_part + "/"
    return url
