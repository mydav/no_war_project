from modules import *
from my_requests.parse_response import *


def setup_session_attributes_to_session(session, sess_attributes):
    logger.debug(
        f"[setup_session_attributes_to_session: sess_attributes={pretty_dict(sess_attributes)} {session=} {getattr(session, 'user_agent', None)=} {getattr(session, 'headers', None)=}"
    )

    logger.debug(f" {pretty_dict(session.headers, 'session.headers')}")

    for k, v in sess_attributes.items():
        if k == "headers":
            for key, value in v.items():
                if key == "User-Agent" and not value:
                    pass
                else:
                    logger.debug(f"    add to session.headers: {key}={value}")
                    session.headers[key] = value
        # elif k == "User-Agent" and v:
        #     session.headers["User-Agent"] = v
        else:
            setattr(session, k, v)

    if not session.headers["User-Agent"]:
        logger.warning(f"   delete empty User-Agent")
        del session.headers["User-Agent"]

    t = 0
    if t:
        logger.warning(
            f"{session.headers['User-Agent']=}, {session.user_agent=}"
        )
        wait_for_ok(f"{session.headers=}")


def get_useragent_in_domain(headers="", domain="com"):
    headers = add_useragent(headers)
    headers = get_bet365url_in_domain(headers, domain=domain)
    return headers


def get_bet365url_in_domain(url, domain="com"):
    """если надо - могу заменить под конкретный испанский сайт"""
    url = url.replace("bet365.es", "bet365.com")
    return url.replace("bet365.com", f"bet365.{domain}").replace(
        "[domain]", f"{domain}"
    )


def get_random_bet365_url(domain="com"):
    rand_num = randint(1, 1000)
    url = f"https://www.bet365.es/BetsWebAPI/refreshslip?{rand_num}"
    url = f"https://www.bet365.es/BetsWebAPI/refreshslip"
    url = f"https://www.bet365.[domain]/"
    url = f"https://www.bet365.[domain]/?{rand_num}_{get_human_time()}".replace(
        " ", "-"
    )
    url = get_bet365url_in_domain(url, domain)

    return url


def com_to_es(url):
    """если надо - могу заменить под конкретный испанский сайт"""
    return url
    return url.replace(".com", ".es")


def com_to_es_polube(url):
    """если надо - могу заменить под конкретный испанский сайт"""
    return url.replace(".com", ".es")


def com_to_es_no(url):
    """если надо - могу заменить под конкретный испанский сайт"""
    return url


def add_useragent(headers: str = "", user_agent=None):
    """
    User-Agent: [user_agent]
    ...
    """
    user_agent = get_nonempty_useragent(user_agent)
    return headers.replace("[user_agent]", user_agent)


def get_saved_cookie(files=None):
    if files is None:
        files = [
            pathlib.Path(__file__).parent / "data" / "cookie_headers.txt",
        ]
    cookie = text_from_file(files)
    if cookie is not None:
        cookie = cookie.replace("Cookie: ", "").strip()
    logger.debug(f"{cookie=} from {files=}")
    return cookie


def get_saved_token(files=None):
    """получить сохраненный токен"""
    if files is None:
        files = [
            pathlib.Path(__file__).parent / "data" / "nst_headers.txt",
        ]
    token = text_from_file(files)
    if token is not None:
        token = token.replace("X-Net-Sync-Term:", "").strip()
    logger.debug(f"{token=} from {files=}")
    return token


def get_saved_pirxts(files=None):
    if files is None:
        files = [
            "c:\pirxt_headers.txt",
            pathlib.Path(__file__).parent / "data" / "pirxt_headers.txt",
        ]

    pirxts_saved = text_from_file(files)
    logger.debug(f"{pirxts_saved=} from {files=}")
    return pirxts_saved


def get_nonempty_useragent(user_agent=None):
    if not user_agent:
        # user_agent = "Mozilla/5.0 (Android 8.0.0; Mobile; rv:62.0) Gecko/62.0 Firefox/62.0"
        user_agent = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0"
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"  # real user agent of firefox
        user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36"  # с линукса хром
        user_agent = ""
        user_agent = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0"  # линукса фаерфокс
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 Edg/98.0.1108.56"  # George
        user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36"  # это с helheim
    return user_agent
