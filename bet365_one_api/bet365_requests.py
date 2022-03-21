#!/usr/bin/python
# -*- coding: utf-8 -*-
from bet365_one_api.bet365_helper import *
from my_requests.requests_helper import *

# from cloudflare_requests.cloudscraper_helper import *

logger = get_logger(__name__)


def prepare_headers_for_bet365_placebet(
    session_headers="",
    pirxt_headers="",
    nst_headers="",
    min_browser_headers=None,
    fixed_headers="",
    final_process_func: callable = None,
):
    """
    есть сессия с браузера, есть пирхты заготовленные и база
    :param session_headers:
    :param pirxt_headers:
    :return:
    """
    if min_browser_headers is None:
        min_browser_headers = """
Host: www.bet365.com
User-Agent: [user_agent]
Accept: */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Referer: https://www.bet365.com/
Content-type: application/x-www-form-urlencoded
Origin: https://www.bet365.com
Connection: keep-alive
        """.strip()

    headers_list = [
        pirxt_headers,
        min_browser_headers,
        nst_headers,
        fixed_headers,
        session_headers,
    ]
    headers_list = [_ for _ in headers_list if _]
    # logger.debug(f"{headers_list=}")
    text_headers = "\n\n".join(headers_list)

    text_headers = text_headers.replace("Content-type:", "Content-Type:")

    if final_process_func:
        text_headers = final_process_func(text_headers)

    text_headers = text_headers.replace(
        "[user_agent]", get_nonempty_useragent()
    )

    headers = parse_headers_from_text(text_headers)
    return headers


def get_text_headers_like_in_browser(user_agent=None):
    user_agent = get_nonempty_useragent()

    text_headers_like_browser_later = """
        # Host: members.bet365.com
    User-Agent: [user_agent]
    # Accept: */*
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
    Accept-Language: en-US,en;q=0.5
    Accept-Encoding: gzip, deflate, br
    Content-type: application/x-www-form-urlencoded
    # Referer: https://www.bet365.com/
    # Content-Length: 194
    # Origin: https://www.bet365.com
    Connection: keep-alive
    Upgrade-Insecure-Requests: 1
        """

    text_headers_like_browser = """
    User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Connection: keep-alive
# Cookie: pstk=E6DBF2551024D98C89499A79001BC532000003; rmbs=3; aaat=di=26bd48d8-61a2-4f83-a6aa-bef167d80f13&am=0&at=449ed0d5-247e-45bb-8838-7203429a90e7&ts=02-02-2022 15:16:24&v=2; aps03=ao=1&cf=E&cg=4&cst=0&ct=171&hd=Y&lng=1&oty=2&tt=2&tzi=4
Upgrade-Insecure-Requests: 1
Sec-Fetch-Dest: document
Sec-Fetch-Mode: navigate
Sec-Fetch-Site: none
    """
    repl = {
        "[user_agent]": user_agent,
    }

    text_headers_like_browser = com_to_es(
        no_probely_one(text_headers_like_browser, repl)
    )
    return text_headers_like_browser


def convert_gzipBytes_to_str(data="", enc="utf-8"):
    bites = data
    # if not isinstance(bites, bytes):
    #     bites = bites.encode(enc, 'ignore') # bytes
    logger.debug(f"{type(bites)} {bites=}")

    # answer = zlib.decompress(bites)  # equivalent to gzdecompress()
    answer = gzip.decompress(bites)
    return answer.decode()


if __name__ == "__main__":
    special = "convert_gzipBytes_to_str"

    if special == "convert_gzipBytes_to_str":
        f = r"s:\!kyxa\!code\!documentation\py4seo\advanced\08\dor_minimum\bet365_one_api\temp\response_content.pickled"
        t = 1
        if t:
            data = obj_from_file(f)
            logger.debug(f"{type(data)} {data=}")

        f = r"s:\!kyxa\!code\!documentation\py4seo\advanced\08\dor_minimum\bet365_one_api\temp\response.pickled"
        f = r"s:\!kyxa\!code\!documentation\py4seo\advanced\08\dor_minimum\bet365_one_api\temp\response_content.pickled"
        data = obj_from_file(f)
        logger.debug(f"{type(data)} {data=}")
        answer = convert_gzipBytes_to_str(data)
        logger.info(f"{answer=}")
        os._exit(0)

    proxy = "node-gb-3.astroproxy.com:10463"
    proxy = "node-uk-3.astroproxy.com:10381"  # 78
    proxy = "node-uk-2.astroproxy.com:10381"  # 100
    proxy = ""

    login = "demo_login"
    # login = "demo_login"

    login_id = "112"  # порезка
    login_id = "77"  #
    domain = "com"

    t = 1
    if t:
        domain = "es"
        login_id = "118"  # spain

    proxy, login, password = get_proxy_login_password_for_bet365(
        special=login_id
    )

    session_from = "only_requests"
    session_from = "requests"
    want_check_bet365_access = True

    cookie = ""
    cookie = "aaat=di=9eb72229-4e13-4ebe-b3f1-7d875a193033&am=0&at=0970101f-7ce5-4a2c-b4a4-bff146d8e0f5&un=Philipp49Hgd&ts=28-01-2022 10:57:08&v=2; pstk=51A6E23BD91F3898A8C39623E8BC8C14000004; qBvrxRyB=AzvwVKB-AQAAOBdnGzs9KY1vzrI-zxoaPQI8GD7XiVjhNfB7-lNcbZBK7PNgAVIbYGGucqIfwH8AAEB3AAAAAA|1|1|366a7acd5afdc01cca30f75930284c3baed6e118; aps03=lng=1&tzi=1&ct=197&cst=0&cg=2; session=processform=0; usdi=uqid=C15A05D2-5887-40CA-AF0D-B012F7E90970"

    t = 1
    if t:
        session_from = "cloudscraper"
        want_check_bet365_access = False

    if session_from == "only_requests":
        session = requests.Session()
        proxy = proxy.split("/")[-1]
        proxies = {
            "http": proxy,
            "https": proxy,
        }
        logger.debug(f"setup {proxies=}")
        session.proxies = proxies

    else:
        session = get_bet365_session(
            login=login,
            proxy=proxy,
            session_from=session_from,
            want_check_bet365_access=want_check_bet365_access,
        )

    if cookie:
        logger.warning(f"adding to session {cookie=}")
        session.headers["Cookie"] = cookie
        # wait_for_ok()

    url = "https://google.com"
    url = "https://bet365.es"
    url = "https://httpbin.org/"
    url = "https://bet365.com/"
    url = "https://bet365.com"
    data = ""

    want_post = True
    want_post = False
    if want_post:
        url = "https://httpbin.org/post"
        data = {
            "eventType": "AAS_PORTAL_START",
            "data": {"uid": "hfe3hf45huf33545", "aid": "1", "vid": "1"},
        }
        data = json.dumps(data)

    r = request_with_requests_html(session, url=url, data=data)
    # r = session.get(url)
    logger.info(f"{r=}")
