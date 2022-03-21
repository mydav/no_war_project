from modules.my_types import *
from modules_23.minimum_important_functions import *
from modules.logging_functions import get_logger
from modules.list_functions import clear_list
from modules.text_functions import find_from_to_one
from modules.time_functions import get_human_time

logger = get_logger(__name__)


def compare_two_cookies(kuka_1, kuka_2, max_length_diff: int = 0):
    """
    :param kuka_1:
    :param kuka_2:
    :return:
    """
    errors = []
    while True:
        # name_1 = kuka_1["name"]
        # name_2 = kuka_2["name"]
        # if name_1 != name_2:
        #     errors.append(f"name: {name_1} != {name_2}")

        keys_skip = clear_list(
            """
        HttpOnly
	# SameSite
	# Secure
	# domain
	expires
	# name
	# path
	value
	value_length
	vars
        """
        )
        for k in kuka_1.keys():
            if k in keys_skip:
                continue
            v_1 = kuka_1[k]
            v_2 = kuka_2[k]
            if v_1 != v_2:
                errors.append(f"{k=}: {v_1} != {v_2}")

        # разница в длинне - есть?
        value_length_1 = kuka_1["value_length"]
        value_length_2 = kuka_2["value_length"]
        length_diff = (1.0 * value_length_1 / value_length_2) * 100
        if length_diff > (100 + max_length_diff) or length_diff < (
            100 - max_length_diff
        ):
            errors.append(
                f"{length_diff=} for {value_length_1=}, {value_length_2=}"
            )

        break

    res = {"status": "equals"}
    if errors:
        res["error"] = errors
        res["status"] = "not_equals"
    return res


def update_cookieString(text="", new_cookies={}, skipping=[]) -> str:
    old_cookies = parse_cookieString_to_dict(text)
    for k, v in new_cookies.items():
        if k in skipping:
            continue
        if 1 or k in old_cookies:
            old_cookies[k] = v
    cookies_str = convert_cookiesDict_to_str(old_cookies)
    return cookies_str


def parse_cookieString_to_dict(
    text="pstk=CE51140EC5F4DDF6B0AB69FCFCB59866000003; aps03=lng=1&tzi=4&ct=171&cst=0&cg=4; aaat=di=45b0d8bb-f457-4316-9299-6796404712d6&am=0&at=2259874e-74db-4b40-bb93-20c4b9daf391&ts=03-02-2022 11:53:39&v=2; usdi=uqid=D4DC5BDB-FF56-4DB9-B783-2F1319841BE1; session=processform=0; __cf_bm=caKPqPfoSfKmx3lStwg1_pJPbPE11OsxZaFwZuleT0c-1643897487-0-AZ2qszjbAkt2w3o3EvU7HC+F0XPx/dq/eiYds5VPJgWTLF8oGn9cZC9s9EPTeo5wrsZKW6Gir7zV5MUHnrH5Tn+0WX3B5Ph7RD25RJhrBr+jFUSGWauhD58kYOUvxBnVMs8oEl1jmFkwW2MPzVvv/r0fX0Lk8/oNy9FLQ/38QBTL",
):
    kuka = text.split("Cookie: ")[-1]
    items = kuka.split("; ")
    res = OrderedDict()
    for item in items:
        k = find_from_to_one("nahposhuk", "=", item)
        v = find_from_to_one("=", "nahposhuk", item)
        res[k] = v
    return res


def parse_setCookieLine(
    text="Set-Cookie: __cf_bm=h16SewoRGLLuUeSCXzrsJIMy93BWgYaFAW.nJQcXFio-1643823681-0-ARnkpPf0zpVg3q6NOpxBJ/5b+3TMGIK8UkNhYCEAZ6CX77VXn8y6G003qrWTiA4w8gyHA9o+CqbkGdxQzsIuJQk=; path=/; expires=Wed, 02-Feb-22 18:11:21 GMT; domain=.bet365.es; HttpOnly; Secure; SameSite=None != __cf_bm=wtYt8jFVAGNpNsO8W02Lfdty5jmBwDJmBltjhWAEaYw-1643823602-0-AafmRhzISEPRqJpSmD9VYQVWJiJ4qd6yKvhmDIhUVjdq3LlTfagPpn/FioZCb/KYNpEYb8EVJPlcRkKiPbnpRRQ=; path=/; expires=Wed, 02-Feb-22 18:10:02 GMT; domain=.bet365.es; HttpOnly; Secure; SameSite=None",
):
    kuka = text.split("Set-Cookie: ")[-1]
    name = find_from_to_one("nahposhuk", "=", kuka).strip()
    value = find_from_to_one(f"{name}=", "; ", kuka)
    # if not value:
    #     value = find_from_to_one(f"{name}=", "; Path=", kuka)
    if not value:
        m = f"empty value in {kuka=}"
        raise ValueError(m)

    vars = find_from_to_one(f"{name}={value};", "nahposhuk", kuka).strip()
    res = {
        "name": name,
        "value": value,
        "value_length": len(value),
        "vars": vars,
    }

    items = vars.split("; ")
    for item in items:
        parts = item.split("=")
        if len(parts) == 2:
            k, v = parts
        else:
            k = item
            v = ""
        res[k] = v

    return res


def parse_all_headers_from_text(*args, **kwargs):
    kwargs["bad_keys"] = []
    kwargs["bad_starts"] = "#"
    return parse_headers_from_text(*args, **kwargs)


def parse_headers_from_text(
    text, bad_starts=":#", want_strip=True, bad_keys=["host", "GET https"]
) -> OrderedDict:
    if isinstance(text, dict):
        return text

    response_content = None
    delimiter_content = "___________response_content___________"
    if delimiter_content in text:
        parts = text.split(delimiter_content)
        if len(parts) != 2:
            raise ValueError(f"content has {len(parts)=} != 2")

        text, response_content = parts

    headers = OrderedDict()
    items = clear_list(text)

    cookies = []
    for item in items:
        if want_strip:
            item = item.strip()
        if item[0] in bad_starts:
            continue
        key = find_from_to_one("nahposhuk", ":", item)
        if key == "" or (key.lower() in bad_keys) or key in bad_keys:
            continue
        value = find_from_to_one(":", "nahposhuk", item).strip()

        if key.lower() in ["set-cookie"]:
            kuka = parse_setCookieLine(value)
            cookies.append(kuka)
            continue

        headers[key] = value
    if cookies:
        headers["set_cookies"] = cookies

    if response_content is not None:
        headers["response_content"] = response_content
    return headers


def convert_headers_from_dict_to_txt(headers={}):
    return "\n".join(["%s: %s" % (k, v) for k, v in headers.items()])


def format_headers(d: dict):
    """
    input:
        x -> 1
        y -> 2

    r:
        x: 1
        y: 2
    """
    return "\n".join("%s: %s" % (k, v) for k, v in d.items())


def explore_cookies(cookies, name=""):
    # logger.debug(f"explore_cookies: { len(cookies)} cookies")
    # for c in cookies:
    #     logger.debug(f"  cookie {c.name}: {c.value}")

    lines = []
    for num, kuka in enumerate(cookies, 1):
        line = f"       {num}/{len(cookies)} name={kuka.name}: at {kuka.domain}, expires {get_human_time(kuka.expires)}, value='{kuka.value}'"
        lines.append(line)
    lines = "\n".join(lines)
    logger.debug(f"explore_cookies {name}: {len(cookies)} cookies:\n{lines}")


def convert_cookiesDict_to_str(cookies):
    return "; ".join([f"{k}={v}" for k, v in cookies.items()])


def convert_cookies_to_str(cookies):
    return "; ".join([f"{c.name}={c.value}" for c in cookies])


def update_headers(headers, update_with: dict = None):
    if update_with == "empty_pirxt":
        update_with = {
            "PIRXTcSdwp-b": "",
            "PIRXTcSdwp-a": "",
            "PIRXTcSdwp-d": "",
            "PIRXTcSdwp-f": "",
            "PIRXTcSdwp-z": "",
            "PIRXTcSdwp-c": "",
        }
    headers.update(update_with)


if __name__ == "__main__":
    from modules import *

    special = "parse_setCookieLine"
    special = "format_headers"
    special = "parse_cookieString_to_dict"
    special = "parse_headers_from_text"
    special = "update_cookieString"

    if special == "update_cookieString":
        text = "pstk=CE51140EC5F4DDF6B0AB69FCFCB59866000003; aps03=lng=1&tzi=4&ct=171&cst=0&cg=4; aaat=di=45b0d8bb-f457-4316-9299-6796404712d6&am=0&at=2259874e-74db-4b40-bb93-20c4b9daf391&ts=03-02-2022 11:53:39&v=2; usdi=uqid=D4DC5BDB-FF56-4DB9-B783-2F1319841BE1; session=processform=0; __cf_bm=caKPqPfoSfKmx3lStwg1_pJPbPE11OsxZaFwZuleT0c-1643897487-0-AZ2qszjbAkt2w3o3EvU7HC+F0XPx/dq/eiYds5VPJgWTLF8oGn9cZC9s9EPTeo5wrsZKW6Gir7zV5MUHnrH5Tn+0WX3B5Ph7RD25RJhrBr+jFUSGWauhD58kYOUvxBnVMs8oEl1jmFkwW2MPzVvv/r0fX0Lk8/oNy9FLQ/38QBTL"
        dct = {
            "pstk": "2222",
            "new_cookie": "some_new_cookie",
        }
        cookies = update_cookieString(text, new_cookies=dct)
        logger.info(f"{cookies=}")

    elif special == "format_headers":
        formated = format_headers(
            {"host": "bet365.com", "cookie": "some cookie"}
        )
        logger.info(formated)
        text_to_file(formated, "temp/formated.txt")

    elif special == "parse_cookieString_to_dict":
        items = clear_list(
            """
            Cookie: pstk=CE51140EC5F4DDF6B0AB69FCFCB59866000003; aps03=lng=1&tzi=4&ct=171&cst=0&cg=4; aaat=di=45b0d8bb-f457-4316-9299-6796404712d6&am=0&at=2259874e-74db-4b40-bb93-20c4b9daf391&ts=03-02-2022 11:53:39&v=2; usdi=uqid=D4DC5BDB-FF56-4DB9-B783-2F1319841BE1; session=processform=0; __cf_bm=caKPqPfoSfKmx3lStwg1_pJPbPE11OsxZaFwZuleT0c-1643897487-0-AZ2qszjbAkt2w3o3EvU7HC+F0XPx/dq/eiYds5VPJgWTLF8oGn9cZC9s9EPTeo5wrsZKW6Gir7zV5MUHnrH5Tn+0WX3B5Ph7RD25RJhrBr+jFUSGWauhD58kYOUvxBnVMs8oEl1jmFkwW2MPzVvv/r0fX0Lk8/oNy9FLQ/38QBTL
            """,
            bad_starts="#",
        )
        cookies = []
        for txt in items:
            logger.debug(f"{txt=}")
            cookie = parse_cookieString_to_dict(txt)
            cookies.append(cookie)

            show_dict(cookie)

    elif special == "parse_setCookieLine":
        items = clear_list(
            """
            Set-Cookie: __cf_bm=h16SewoRGLLuUeSCXzrsJIMy93BWgYaFAW.nJQcXFio-1643823681-0-ARnkpPf0zpVg3q6NOpxBJ/5b+3TMGIK8UkNhYCEAZ6CX77VXn8y6G003qrWTiA4w8gyHA9o+CqbkGdxQzsIuJQk=; path=/; expires=Wed, 02-Feb-22 18:11:21 GMT; domain=.bet365.es; HttpOnly; Secure; SameSite=None
            Set-Cookie: __cf_bm=wtYt8jFVAGNpNsO8W02Lfdty5jmBwDJmBltjhWAEaYw-1643823602-0-AafmRhzISEPRqJpSmD9VYQVWJiJ4qd6yKvhmDIhUVjdq3LlTfagPpn/FioZCb/KYNpEYb8EVJPlcRkKiPbnpRRQ=; path=/; expires=Wed, 02-Feb-22 18:10:02 GMT; domain=.bet365.es; HttpOnly; Secure; SameSite=None
            # Set-Cookie: pstk=4D8C8F24155E5D54B213F858C674C58C000003; Path=/; Expires=Thu, 10 Feb 2022 06:19:31 GMT; Domain=.bet365.com

            """,
            bad_starts="#",
        )
        cookies = []
        for txt in items:
            logger.debug(f"{txt=}")
            cookie = parse_setCookieLine(txt)
            cookies.append(cookie)

            show_dict(cookie)

        if len(cookies) == 2:
            compared = compare_two_cookies(cookies[0], cookies[1])
            logger.debug(f"{compared=}")

    elif special == "parse_headers_from_text":
        text = """
    User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64; rv:56.0) Gecko/20100101 Firefox/56.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
    Accept-Language: en-US,en;q=0.5
    Accept-Encoding: gzip, deflate
    Cookie: sesid=dncs0t-odxdk*y_rgkfp-u0mcnbq0vbw-t^vaxemivhucnbn_t*vfqbn_t*vfqbn; _ym_visorc_27984774=w
    Connection: keep-alive
    Upgrade-Insecure-Requests: 1
    Cache-Control: max-age=0
    Set-Cookie: pstk=4D8C8F24155E5D54B213F858C674C58C000003; Path=/; Expires=Thu, 10 Feb 2022 06:19:31 GMT; Domain=.bet365.com
    set-cookie: small=4D8C8F24155E5D54B213F858C674C58C000003; path=/; Expires=Thu, 10 Feb 2022 06:19:31 GMT; Domain=.bet365.com
    set-cookie: aaat=di=ae360759-83d8-427f-9f8d-94320753c76e&am=0&at=1658787a-adf7-424a-b4cf-7dcca313b238&ts=03-02-2022 14:20:40&v=2; domain=.bet365.es; expires=Tue, 03-Feb-2032 14:20:40 GMT; path=/; secure
            """

        t = 0
        if t:
            f = r"s:\!kyxa\!code\!small_scripts\data\step_compare_edit_and_resend_REPEAT\browser_request_response.txt"
            text = text_from_file(f)

        headers = parse_headers_from_text(text)
        show_dict(headers)

    else:
        logger.critical(f"unknown {special=}")
