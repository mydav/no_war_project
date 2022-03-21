import requests
import gzip

from modules import *

from modules_23.my_forms import get_prepared_request
from bet365_one_api.bet365_parse_answer_tip import is_fiddler_error
from my_requests.parse_response import *


def request_with_requests_html(*args, **kwargs):
    kwargs["want_json"] = False
    return request_with_requests(*args, **kwargs)


def request_with_requests(
    session=None,
    want_json=True,
    debug=False,
    want_add_cookie_from_session: bool = True,
    want_delete_bad_headers: bool = True,
    want_save_unknown_cloudflare_status_page: bool = True,
    want_headers_in_order: bool = True,  # хочу хедеры в том же порядке?
    want_cloudflare_status: bool = False,  # хочу статус клаудфлара проверить?
    **kwargs,
):
    fun = "request_with_requests"
    if debug:
        logger.debug(fun)
    t_start = time.time()

    response = None
    post_error = ""  # краткая ошибка, для меня
    post_error_raw = ""  # реальная пост-ошибка

    replaying = kwargs.pop("replaying", None)
    if replaying:
        logger.debug(f"have {replaying=}")
        kwargs["url"] = replaying.url
        kwargs["headers"] = replaying.headers
        kwargs["data"] = replaying.data
    # wait_for_ok()

    if kwargs.get("data") not in ["", None]:
        func = session.post
    else:
        func = session.get

    # приходится удалять юзерагент, а то всё время с клаудфларным конфликтую?
    if 1 and want_delete_bad_headers and not want_headers_in_order:
        to_delete = [
            "User-Agent",
            # "Cookie",
        ]
        headers = kwargs.get("headers", {})
        for key in to_delete:
            if key in headers:
                # logger.debug(
                #     f"{key=} in session = {session.headers.get(key)}"
                # )
                session_value = session.headers.get(key)
                if (
                    session_value is not None and session_value != headers[key]
                ):  # удаляю только если у сессии этого нет
                    logger.warning(
                        f"""deleted from headers {key}={headers[key]}, because have another {session_value=}"""
                    )
                    del kwargs["headers"][key]
        # wait_for_ok("deleted")

    user_agent = getattr(session, "my_user_agent", None)
    if user_agent:
        logger.warning(f"use fixed {session.my_user_agent=}")
        session.headers["User-Agent"] = user_agent
        # wait_for_ok()

    headers = kwargs.get("headers", {})
    if 1 and want_add_cookie_from_session:
        cookie = getattr(session, "cookie", None)
        # try:
        #     cookie = getattr(session, "cookie", None)
        # except Exception as er:
        #     cookie = None
        if cookie:
            headers["Cookie"] = cookie
            logger.warning(f"session has {cookie=}, adding to request")
            # wait_for_ok()

    # удаляю ненужные хедеры
    to_delete = ["set_cookie"]
    for k in to_delete:
        if k in headers:
            del headers[k]

    old_session_headers = None
    if want_headers_in_order and headers:
        old_session_headers = session.headers
        session.headers = headers
        logger.debug(
            f"want_headers_in_order, so new session headers={pretty_dict(session.headers)}, old session_headers={pretty_dict(old_session_headers)}"
        )
        kwargs["headers"] = {}
    else:
        kwargs["headers"] = headers

    if debug:
        logger.debug(f"func_name={func.__name__}, {kwargs=}")

    # response = func(**kwargs)
    try:
        response = func(**kwargs)
    except Exception as er:
        # logger.debug(f"{er.__dict__=} {er.__class__=}")
        post_error_raw = str(er)

    if old_session_headers is not None:  # возврат хедеров
        session.headers = old_session_headers

    post_error = post_error_raw
    if debug:
        logger.debug(f"{response=}")
        # logger.debug(f"{response.request=}")

    if post_error:
        logger.error(f"{post_error=}")

    if is_fiddler_error(post_error):
        logger.critical("fiddler_error")
        inform_critical("fiddler_error")

    t_raw = time.time()
    raw_request = get_prepared_request(
        response, t_start=t_start, request_error=post_error
    )

    t_to_json = time.time()

    json_answer = None
    text = None

    if want_json:  # and not post_error:
        try:
            json_answer = response.json()
            logger.debug(f"{json_answer=}")
        except Exception as er:
            logger.warning(f"answer not json {er=}")

    if json_answer is None:
        text = get_response_text(response)
        if text is not None:
            title = find_from_to_one("<title>", "</title>", text).strip()
            logger.debug(
                f".text not JSON, text with {title=}, text={text[:200]}..."
            )
    # wait_for_ok(f"request done? {json_answer=} {text=}")

    cloudflare_status = None
    if text is not None and want_cloudflare_status:
        cloudflare_status = check_cloudflare_status(text)
        logger.debug(f"{cloudflare_status=}")

        if "Proxy: Unknown error, contact administrator" in text:
            post_error = "unknown_proxy_error"
            logger.error(f"{post_error=} with proxy {session.proxies}")

        elif cloudflare_status in [
            "cloudflare_captcha",
            "cloudflare_block",
        ]:
            post_error = cloudflare_status

        elif cloudflare_status in [
            "solved",
        ]:
            pass

        else:
            if want_save_unknown_cloudflare_status_page:
                f_unknown = pathlib.Path(
                    f"temp/!unknown_post_errors/{response.status_code}_{to_hash(text)}.html"
                ).resolve()
                text_to_file(text, f_unknown)
                logger.warning(
                    f"unknown cloudflare status, saved to analyze to {f_unknown}"
                )

    t = 0
    if t:
        show_dict(response.headers)
        logger.debug(response.headers["Location"])
        logger.debug(response.text)
        wait_for_ok(f"{post_error=}")

    if (
        "User-Agent in request differs from that defined in the session"
        in post_error
    ):
        t = 1
        if t:
            logger.critical(post_error)
            logger.debug(f"""kwargs: {pretty_dict(kwargs.get("headers"))}""")

            logger.debug(f"session: {pretty_dict(session.headers)}")

            logger.debug(
                f"""session user_agent = {session.headers.get("User-Agent")}"""
            )
            logger.debug(
                f"""request user_agent = {kwargs["headers"].get("User-Agent")}"""
            )
            logger.critical(post_error)
            inform_critical(post_error)

    elif "HTTPConnectionPool(host='localhost', port=80)" in post_error:
        post_error = "bot_ip"

    elif "Error: You CANNOT solve a challenge request on a POST" in post_error:
        post_error = "cloudflare_on_post_impossible"

    elif (
        "Cannot connect to proxy." in post_error
    ):  # HTTPSConnectionPool(host='members.bet365.com', port=443): Max retries exceeded with url: /lp/default.aspx (Caused by ProxyError('Cannot connect to proxy.', OSError(0, 'Error')))
        post_error = "connection_proxy_error"

    elif response and response.headers.get("Location") == "http://localhost":
        post_error = "bot_ip"
        # wait_for_ok(post_error)

    elif response and response.text == "{}":
        post_error = "pstk_not_logined"

    if post_error:
        logger.error(f"{post_error=}")

    if (
        post_error_raw and post_error != post_error_raw
    ):  # если краткая ошибка сходится с общей - значит какой-то глюк, краткая это минимально возможная
        m = f"{post_error=} != {post_error_raw=}"
        logger.warning(m)
        # inform_critical(m)

    t_end = time.time()
    duration_total = round(t_end - t_start, 3)
    duration_post = round(t_raw - t_start, 3)
    duration_raw = round(t_to_json - t_raw, 3)
    duration_to_json = round(t_end - t_to_json, 3)
    duration_details = [
        f"total {duration_total} = post {duration_post} + raw {duration_raw} + to_json {duration_to_json}"
    ]
    # wait_for_ok(duration_details)
    _ = {
        "duration": duration_total,
        "error": post_error,
        "error_raw": post_error_raw,
        "response": response,
        "raw_request": raw_request,
        "json": json_answer,
        "duration_details": duration_details,
    }
    logger.debug(f"   +{fun} in {duration_total} seconds]")
    return _


def get_etag(session, url=""):
    etag = None
    try:
        response = session.head(url)
        etag = response.headers["etag"]
    except Exception as er:
        logger.error(er)
    return etag
