#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import gzip

from modules import *

from modules_23.my_forms import get_prepared_request
from bet365_one_api.bet365_parse_answer_tip import is_fiddler_error
from bet365_one_api.bet365_requests import *
from bet365_one_api.bet365_helper import *
from cloudflare_requests.cloudscraper_helper import *

logger = get_logger(__name__)


def get_bet365_session(
    proxy="",
    proxies=None,
    session_from: Literal["cloudscraper", "requests"] = "cloudscraper",
    login="",
    domain="",
    want_cache: bool = None,
    want_check_bet365_access: bool = None,
):
    user_agent = get_nonempty_useragent()
    sess_attributes = {
        "keep_alive": False,
        "timeout": (10, 10),
        "headers": {"User-Agent": user_agent},
    }

    # прокси добавляю
    if proxies is None:
        proxy = proxy.split("/")[-1]
        if proxy and proxy not in ["no", "-"]:
            proxy = f"http://{proxy}"
            proxies = {
                "http": proxy,
                "https": proxy,
                # "http"  : self.http_proxy,
                # "https" : self.https_proxy,
                # "ftp"   : self.ftp_proxy
            }

    if proxies:
        logger.warning(f"add to sess_attributes {proxies=}")
        sess_attributes["proxies"] = proxies

    if session_from == "cloudscraper":
        my_os = detect_os()
        f_cache = (
            pathlib.Path(__file__).parent
            # pathlib.Path(__name__).parent
            / "temp"
            / "!cloudscraper_sessions"
            / f"{login}_{domain}__{my_os}.session".replace("__windows", "")
        ).resolve()
        logger.debug(f"{f_cache=}")
        # wait_for_ok()

        session = get_cached_bet365_session_for_cloudflare(
            want_cache=want_cache,
            f_cache=f_cache,
            domain=domain,
            want_check_bet365_access=want_check_bet365_access,
            sess_attributes=sess_attributes,
        )
    elif session_from == "requests":
        session = requests.Session()
    else:
        logger.critical(f"unknown {session_from=}")
        os._exit(0)

    # все атрибуты прописываем
    setup_session_attributes_to_session(session, sess_attributes)

    logger.debug(
        f" +{session=}, {session_from=}, {len(session.cookies)} cookies:"
    )
    explore_cookies(session.cookies, "session.cookies:")
    # wait_for_ok()
    return session


def check_session_on_bet365_cloudflare_access(session=None, domain="com"):
    if session is not None:
        urls = ["main", "refreshslip", "placebet"]
        logger.debug(f"check important {urls=}")
        for url in urls:
            check_session_on_refreshslip(
                session, url=url, domain=domain
            )  # если не пройдет - сессия отвалится


def check_session_on_refreshslip(session, domain="com", url="refreshslip"):

    if url == "refreshslip":
        url = "https://www.bet365.com/BetsWebAPI/refreshslip"
    elif url == "placebet":
        url = "https://www.bet365.com/BetsWebAPI/placebet"
    elif url == "main":
        url = "https://www.bet365.com/"

    url_refreshslip = get_bet365url_in_domain(url, domain)
    logger.debug(f"check_session_on_refreshslip {domain=} {url_refreshslip=}")

    response = download_url_with_session(session, url_refreshslip)
    if response is not None:
        success = check_cloudflare_status(response.text)
    else:
        success = "response error"
    logger.info(f"  + refreshslip check: {success=}")
    if success not in ["solved"]:
        m = f"not solved"
        logger.critical(m)
        inform_critical(m)
        os._exit(0)


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
