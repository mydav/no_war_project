from urllib.parse import quote as urllib_quote
from urllib.parse import unquote_plus as urllib_unquote_plus
from modules.text_functions import find_from_to_one
import sys


def quote(key: str, plus: bool = True):
    r = urllib_quote(key)
    if plus:
        r = r.replace("%2B", "+").replace("%20", "+").replace("/", "%2F")
    return r


def unquote(key: str):
    """
    encodedStr = 'Hell%C3%B6%20W%C3%B6rld%40Python'
    unquote(encodedStr)
        'Hellö Wörld@Python'
    """
    return urllib_unquote_plus(key)  # also with +


def ahref(url: str = "", anchor: str = None, target: bool = False):
    if url is None:
        return ""

    if not anchor:
        anchor = url

    target_line = ""
    if target:
        target_line = " target=_blank"
    href = f'<a href="{url}"{target_line}>{anchor}</a>'
    return href


def get_folder_from_url(url: str) -> str:
    parts = url.split("/")

    is_root_domain = len(parts) == 3  # http://domain.com

    if url[-1] == "/" or is_root_domain:  # значит это папка /folder/
        external_folder = url
    else:
        external_folder = "/".join(parts[:-1]) + "/"
    return external_folder


def get_domain_from_url(url: str) -> str:
    parts = url.split("/")
    domain = "/".join(parts[:3])
    return domain


def get_vars_from_url(url, spliter="&", want_lower=False):
    fun = "get_vars_from_url"
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
    # print 'url_0', url

    items = url.split(spliter)
    # show_list(items)
    for item in items:
        try:
            # var, val = item.split('=')
            var = find_from_to_one("nahposhuk", "=", item)
            val = find_from_to_one("=", "nahposhuk", item)
            rezult[var] = val
        except Exception as er:
            pass
            print(f"error {fun}: {er=}")
    #            print url
    #            wait_for_ok()
    return rezult


def get_settings_from_args(args=""):
    """
        получаю настройки с аргументов
    """
    if not args:
        args = "".join(sys.argv[1:])

    # args = 'addurl_selenium ?spec_task=change_passwords_all??f_settings=setting_change_passwords_all.txt'
    # args = 'mozg.py ?spec_task=check_tunel??spec_tunel='

    t = 1
    t = 0
    if t:
        args = (
            "addurl_selenium.py ?spec_task=gmail_before_change_password??login=%s??password=%s??phone=%s??proxy_change_password=%s"
            % (login, password, phone, proxie)
        )

    print(f"{args=}")
    settings_args = get_vars_from_url(args, "??")

    settings_args["args"] = args
    print(f"{settings_args=}")
    return settings_args


if __name__ == "__main__":
    from modules.list_functions import clear_list

    special = "unquote"
    special = "quote"
    special = "get_folder_from_url"
    special = "get_settings_from_args"

    if special == "get_settings_from_args":
        args = "main ?var1=1??var2=2"
        args = get_settings_from_args(args)
        print(f"{args=}")

    elif special == "get_folder_from_url":
        urls = [
            "http://google.com",
            "http://google.com/",
            "http://google.com/1/",
            "http://google.com/1/?x=2",
        ]
        for url in urls:
            folder = get_folder_from_url(url)
            domain = get_domain_from_url(url)
            print(f"{url=}, {folder=} {domain=}")

    if special == "unquote":
        strings = """
    Hell%C3%B6%20W%C3%B6rld%40Python
    hello+world%20and you
    """
        keys = clear_list(strings)
        for key in keys:
            unquoted = unquote(key)
            print(f"{unquoted}, {key=}")

    if special == "quote":
        strings = """
    hello world+and you/a?
    """
        keys = clear_list(strings)
        for key in keys:
            quoted = quote(key)
            print(f"{quoted=} from {key=}")
