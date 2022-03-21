#!/usr/bin/python
# -*- coding: utf-8 -*-

from bet365_one_api.bet365_session import *
from bet365_one_api.bet365_parse_answer_tip import parse_answer_tip

logger = get_logger(__name__)


def login_with_pstk_from_members(
    pstk="", login="", password="", session=None, domain="com", cookie=None
):
    """
    логин через members
    """
    fun = "login_with_pstk"
    logger.debug(f"[{fun}: {pstk=} {login}:{password}")
    url = "https://members.bet365.es/lp/default.aspx"
    post_data = "__EVENTTARGET=ctl00%24Main%24login%24lkSbmt&__EVENTARGUMENT=&__VIEWSTATE=%2FwEPDwULLTE2NjY0NzYzMDhkZKlsKnSQzLaZ0S6f%2BreYVFyl%2FzhU&__VIEWSTATEGENERATOR=06128CC4&__PREVIOUSPAGE=kgVR20NQOHcp9njXh_2B3A07c5V8PCfeIpTL-mv41mBaq6NOBbH3u98HBUCVjwsyhFmtJEwAWH7JPLTIgI8me8hoQO81&__EVENTVALIDATION=%2FwEdAAl5uTDPov%2BRwGYbIQ3PnF9wMjNLWSq8HM0dtMNnBYhaWbTxPJ7qpGKFbNi06jUk2%2FVsf5Il2PWmaG79t2vZO%2FDvTXlrpyncbOf%2Fs%2BHAx2PewTUWfQnCJSI9rkN4Zu3xXNGJirSoHMHoH15HqCioukYg4MaMebzjBKQd6dN%2BNXS54jC1oNjRUUdSjCH2Hfz3CEBxz4LeO7NylrjFgNYlNco2JRqCBA%3D%3D&baseId=ctl00&showValidIcons=True&showInvalidIcons=True&showHelpTips=True&hdnBaseControl=ctl00_Main_login&txtUserName=maricasapo&txtPassword=Sapo1010&txtTKN=3D07CD9D8C284B098D8DF6C2FCEEE830000003&txtType=77&txtSTKN=&txtDeepLink=https%3A%2F%2Fmembers.bet365.es%2F%3Fem%3D1%26handler%3Drdapi%26lng%3D3%26prdid%3D1%26txtLCNOVR%3DES&platform=1&ctl00%24Main%24login%24UserName=maricasapo&ctl00%24Main%24login%24Password=Sapo1010&ctl00%24Main%24login%24hdClientStateBag=&ctl00%24hdRunHostCheck=0&ctl00%24hdMembersHostUrl=https%3A%2F%2Fmembers.bet365.es%2Fmembers%2Fservices%2Fhost%3FMicrosite%3DMembers%26ptqs%3D%252fhe%252flogin%252fdefault.aspx%253fhostedBy%253dMEMBERS_HOST%2526prdid%253d1%26DisplayMode%3DDesktop%26prdid%3D1%26DWTYPE%3D%26hostedtimeout%3D1"
    post_data = post_data.replace("maricasapo", login).replace(
        "Sapo1010", password
    )
    if pstk:
        post_data = post_data.replace(
            "3D07CD9D8C284B098D8DF6C2FCEEE830000003", pstk
        )
    else:
        logger.warning("pstk is empty, so use default value")

    text_headers = """
Host: members.bet365.es
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Referer: https://members.bet365.es/he/login/?hostedBy=MEMBERS_HOST&prdid=1
Content-Type: application/x-www-form-urlencoded
Content-Length: 1288
Origin: https://members.bet365.es
Connection: keep-alive
# Cookie: __cf_bm=4Vs7.ZcG0BMATEd3b88k4FDRh1n2mvC63vE3rO7.JLI-1644406918-0-AXJEAAOFJlC+IciLiO8+qEkMW1wm1Yu+NyncMxNRPgTafQ3jgAxrxoF5zjb9lK+s6uW3HCVVaYqVIeHPqyHg8i8JFQNU1ASTv9LUgcqCrkhG6kE2e1uyQ3k0CwD9j/YBxybfkyq0vwC9PgiW1NsWPZ795PKuhPitp/w18cs+Ow5G; aps03=cf=N&cg=4&cst=0&ct=171&gb=1&hd=N&lng=3&oty=2&tzi=4; pstk=3D07CD9D8C284B098D8DF6C2FCEEE830000003; gstk=3D07CD9D8C284B098D8DF6C2FCEEE830000003; rmbs=3; session=processform=0; platform=1
Upgrade-Insecure-Requests: 1
        """
    if cookie:
        text_headers = f"{text_headers}\nCookie: {cookie}"

    text_headers = get_bet365url_in_domain(text_headers, domain)
    url = get_bet365url_in_domain(url, domain)

    headers = parse_headers_from_text(text_headers)
    logger.debug(f"headers: {pretty_dict(headers)}")
    # session.headers["User-Agent"] = headers["User-Agent"]

    kwargs = {
        "url": url,
        "headers": headers,
        "data": post_data,
    }

    # wait_for_ok(session)
    r_response = request_with_requests_html(
        session=session, debug=True, **kwargs
    )
    error = r_response.get("error")
    response = r_response["response"]
    if error:
        logger.warning(f"login {error=}")
        return r_response

    session_cookies = session.cookies.get_dict()
    logger.debug(f"session_cookies={pretty_dict(session_cookies)}")
    pstk = session_cookies.get("pstk")
    if not pstk or not pstk.endswith("00004"):
        logger.critical(f"  -not logined, {pstk=}]")
        logger.debug(f"html={get_response_text(response)}")
        # os._exit(0)
    else:
        logger.info(f"    +logined, {pstk=}]")

    # analyze_response(r_response)
    return r_response
    # response = r_response["response"]


def keep_pstk_alive(
    pstk="",
    r_login=None,
    seconds_sleep=60,
    domain="com",
    max_steps=0,
    session=None,
    name: str = "",
):
    """держим чтобы живая сессия была"""
    fun = "keep_pstk_alive"

    error = 0
    t_start = time.time()
    step = 0
    while True:
        step += 1
        duration = time.time() - t_start
        logger.debug2(
            f"{fun} {step=} duration {get_human_duration(duration)} for {pstk=}"
        )

        result = get_last_action_time(
            pstk, info=r_login, domain=domain, session=session
        )
        logger.info(f"get_last_action_time {result=}")

        seconds = result.get("seconds")
        if seconds == -1:
            error = "pstk_not_logined"
            break

        result = set_last_action_time(
            pstk, info=r_login, domain=domain, session=session
        )
        logger.info(f"set_last_action_time {result=}")

        result = get_last_action_time(
            pstk, info=r_login, domain=domain, session=session
        )
        logger.info(f"get_last_action_time {result=}")

        logger.debug1(
            f"     +{fun} {step=} {get_human_time()}: duration {get_human_duration(duration)} for {pstk=} {name=}"
        )

        if max_steps and step >= max_steps:
            break

        sleep_(seconds_sleep)

    if error:
        logger.error(f"finished, {error=}")
        return api_error(error, duration=duration)


def get_balance_with_pstk(
    pstk="", info={}, login="", domain="com", session=None
):
    """получить баланс с pstk"""
    # pstk = ""
    url = get_bet365url_in_domain(
        f"https://www.bet365.com/balancedataapi/pullbalance?rn=[microseconds]&y=jsn",
        domain,
    )
    headers_txt = get_useragent_in_domain(
        f"""
Accept: */*
Host: www.bet365.com
User-Agent: [user_agent]
Cookie: pstk={pstk}
""",
        domain,
    )
    # logger.debug(f"{headers_txt=}")
    # wait_for_ok(f"good headers?")
    headers = parse_headers_from_text(headers_txt)
    microseconds = int(
        (datetime.datetime.utcnow().timestamp() - 60 * 60 * 0) * 1000
    )
    url = url.replace("[microseconds]", str(microseconds))
    # wait_for_ok(url)

    if not session:
        session = get_bet365_session(proxy="", login=login, domain=domain)
    # session = info.get("session")

    kwargs = {
        "url": url,
        "headers": headers,
        "allow_redirects": False,
    }
    t_start_request = time.time()
    step = 0
    while True:
        step += 1
        duration = time.time() - t_start_request
        if duration > 60 * 20:
            m = "check, may be bad proxy"
            logger.critical(m)
            inform_critical(m)

        r = request_with_requests_html(session, **kwargs)
        logger.debug(
            f"""  + {step=} ({duration:0f} seconds from start), durations {r["duration_details"]}"""
        )
        # show_dict(r)
        break

    response = r["response"]
    error = r.get("error")

    if error:
        logger.error(f"request {error=}")
        return api_error(error)

    elif response is None:
        logger.error(f"wrong response {response=}")
        return api_error(error)

    html = response.text

    if html == "$0.00$$$$$$$$$":
        error = "pirxt_not_logined"
        logger.error(f"{error=}")
        return api_error(error)

    else:
        # logger.debug(f"{html=}")
        try:
            balance = float(clear_list(html.split("$"))[0])
            logger.debug(f"{balance=}")
            return api_success(balance=balance)
        except Exception as er:
            error = "html_is_not_with_balance"
            logger.error(f"{error=}: {er=} for {html=}")
            return api_error(error)


def check_max_logins_with_pstk(
    pstk="", info={}, login="", domain="com", session=None
):
    """проверяю - возможно макс логинов вылезло
    загадочный __RequestVerificationToken не разгадал
              "url": "https://members.bet365.com/members/services/notifications/process?em=1&prdid=1",

    """
    # pstk = ""
    url = f"https://members.bet365.com/members/services/Notifications/Process?prdid=1"
    url_start = f"https://members.bet365.com/members/services/notifications/process?em=1&prdid=1"

    if not session:
        if info:
            logger.debug(f"get prepared session")
            session = info.get("session")

            headers_txt = f"""
    {headers_txt}
    Cookie: {info["cookie"]}
    """
            # headers = prepare_headers_for_bet365_placebet(
            #     min_browser_headers=headers_txt,
            #     # fixed_headers=f"""{get_text_headers_like_in_browser()}\nCookie: {info["cookie"]}\n""",
            #     # fixed_headers=f"""Cookie: {info["cookie"]}\n""",
            # )
            headers = parse_headers_from_text(headers_txt)
            if 1:
                show_dict(headers)
        else:
            logger.debug(f"creating new session")
            session = get_bet365_session(proxy="", login=login)

    t = 1
    if t:
        response = session.get(url_start)
        html = get_response_text(response)
        # logger.debug(f"{html=}")

        RequestVerificationToken = find_from_to_one(
            'name="__RequestVerificationToken" type="hidden" value="',
            '"',
            html,
        )
        logger.debug(f"{RequestVerificationToken=}")
        if not RequestVerificationToken:
            """
            сессию сразу разлогинило?
            CRITICAL:root:inform_critical 2022-02-08 14:28:50: no RequestVerificationToken in html="<html><body><script>function receiveMessage(event) {window.parent.postMessage(JSON.stringify({message:'IFRAME_COMPLETE', loginStateChanged: 0, sessionTerminated: 1}), '*');}window.addEventListener('message', receiveMessage, false);window.parent.postMessage(JSON.stringify({message: 'IFRAME_LOADED'}), '*');</script></body></html>"
            """
            if "sessionTerminated: 1}" in html:
                m = "no RequestVerificationToken - session terminated?"
            else:
                m = f"no RequestVerificationToken in {html=}"
            logger.critical(m)
            inform_critical(m)

        # os._exit(0)

    headers_txt = get_useragent_in_domain(
        f"""
Host: members.bet365.com
User-Agent: [user_agent]
Accept: */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Referer: https://members.bet365.com/members/services/notifications/process?em=1&prdid=1
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
__RequestVerificationToken: [token]
X-Requested-With: XMLHttpRequest
Content-Length: 73
Origin: https://members.bet365.com
Connection: keep-alive
# Cookie: qBvrxRyA=AxQJlmR-AQAAzf9t-7-XSOCLrmz15v6I5L7mh1WCle5E3TvQCizRRnUsS6hXAVGTvLucuL5iwH8AAEB3AAAAAA|1|1|0dcf714799755ba2ecfdc762d7211dbde18c88be; aps03=lng=1&tzi=1&ct=197&cst=0&cg=2; aaat=di=0b824179-66cd-4298-9bab-be5bbea3b427&am=0&at=b10183a1-9c6a-4ea3-a955-eeb066b51417&un=Kwashiorkor&ts=18-01-2022 12:20:57&v=2; usdi=uqid=D2F67A3A-30D2-4DFD-8A32-3765CCF34022; pstk=E9045A08B6E07C6E9541E51F708D514D000004; session=processform=0; __RequestVerificationToken_L21lbWJlcnMvc2VydmljZXMvTm90aWZpY2F0aW9ucw2=8aC72IZtlMY7s_jck64rl9pxN0DFyRWYb6BuGgRUKo0V5fW_FflBwE8yzxb1KNVFalnECd9GcYk33l9qN2OWotA6e6I1
""",
        domain=domain,
    ).replace("[token]", RequestVerificationToken)
    post_data = "notificationType=0&requestType=2&payload=&viewModelTypeName=BaseViewModel"

    headers = parse_headers_from_text(headers_txt)

    kwargs = {
        "url": url,
        "headers": headers,
        "data": post_data,
        "allow_redirects": False,
    }
    t_start_request = time.time()
    step = 0
    while True:
        step += 1
        duration = time.time() - t_start_request
        if duration > 60 * 20:
            m = "check, may be bad proxy"
            logger.critical(m)
            inform_critical(m)

        r = request_with_requests_html(session, **kwargs)
        logger.debug(
            f"""  + {step=} ({duration:0f} seconds from start), durations {r["duration_details"]}"""
        )
        # show_dict(r)
        break

    response = r["response"]
    if response is None:
        html = ""
    else:
        html = response.text

    status = None
    details = None
    if (
        "You have reached the maximum number of log ins allowed in a day"
        in html
    ):
        error = "reached_maximum_logins"
        logger.warning(f"{error=}")
        return api_error(error)

    elif "<h2>Object moved to" in html:
        error = "wrong_request"
        logger.error(f"{error=}")
        return api_error(error)

    elif 'data-val-required="The NotificationType field is required."' in html:
        status = "success"
        details = "max_logins not reached"

    else:
        logger.debug(f"{html=}")
    return api_success(status=status, details=details)


def get_last_action_time(
    pstk="", info={}, login="", domain="com", session=None
):
    """проверяю - когда были последние действия
    """
    # pstk = ""
    fun = "get_last_action_time"
    url = get_bet365url_in_domain(
        f"https://www.bet365.com/sessionactivityapi/getlastactiontime", domain
    )
    headers_txt = get_useragent_in_domain(
        f"""
Host: www.bet365.com
User-Agent: [user_agent]
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Connection: keep-alive
Cookie: pstk=[pstk]
Upgrade-Insecure-Requests: 1
Cache-Control: max-age=0
""",
        domain=domain,
    )

    headers_txt = headers_txt.replace("[pstk]", pstk)

    if not session:
        if info:
            logger.debug(f"get prepared session")
            session = info.get("session")

        else:
            logger.debug(f"creating new session")
            session = get_bet365_session(proxy="", login=login, domain=domain)

    headers = parse_headers_from_text(headers_txt)

    kwargs = {
        "url": url,
        "headers": headers,
        "allow_redirects": False,
        "want_save_unknown_cloudflare_status_page": False,
    }
    t_start_request = time.time()
    step = 0
    while True:
        step += 1
        duration = time.time() - t_start_request
        if duration > 60 * 20:
            m = "check, may be bad proxy"
            logger.critical(m)
            inform_critical(m)

        r = request_with_requests_html(session, **kwargs)
        logger.debug(
            f"""  + {step=} ({duration:0f} seconds from start), durations {r["duration_details"]}"""
        )
        # show_dict(r)
        break
        get_human_time()

    response = r["response"]
    if response is None:
        html = "connection_error"

    else:
        html = response.text
    # logger.debug(f"{html=}")

    seconds = None
    error = ""

    try:
        seconds0 = int(html)
        if str(html) == str(seconds0):
            seconds = seconds0
        else:
            error = f"html not int ({html=})"
    except Exception as er:
        error = f"exception with {html=}"
        if html == "connection_error":
            error = "connection_error"

    if seconds == -1:
        logger.error(f"pstk not logined (seconds=-1)")

    logger.debug(f"   +{fun} {seconds=} {error=}")
    if error:
        logger.error(f"{error=}")
        return api_error(error)
    else:
        return api_success(seconds=seconds)


def set_last_action_time(
    pstk="", info={}, login="", domain="com", session=None
):
    """устанавливаю время последнего действися (чтобы не разлогинило)
    """
    # pstk = ""
    fun = "set_last_action_time"
    url = get_bet365url_in_domain(
        f"https://www.bet365.com/sessionactivityapi/activityalert?action=continue",
        domain=domain,
    )
    headers_txt = get_useragent_in_domain(
        f"""
Host: www.bet365.com
User-Agent: [user_agent]
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Connection: keep-alive
Cookie: pstk=[pstk]
Upgrade-Insecure-Requests: 1
Cache-Control: max-age=0
""",
        domain=domain,
    )

    headers_txt = headers_txt.replace("[pstk]", pstk)

    if not session:
        if info:
            logger.debug(f"get prepared session")
            session = info.get("session")

        else:
            logger.debug(f"creating new session")
            session = get_bet365_session(proxy="", login=login)

    headers = parse_headers_from_text(headers_txt)

    kwargs = {
        "url": url,
        "headers": headers,
        "allow_redirects": False,
    }
    t_start_request = time.time()
    step = 0
    while True:
        step += 1
        duration = time.time() - t_start_request
        if duration > 60 * 20:
            m = "check, may be bad proxy"
            logger.critical(m)
            inform_critical(m)

        r = request_with_requests_html(session, **kwargs)
        logger.debug(
            f"""  + {step=} ({duration:0f} seconds from start), durations {r["duration_details"]}"""
        )
        # show_dict(r)
        break

    response = r["response"]
    try:
        html = response.text
    except Exception as er:
        html = ""
    # logger.debug(f"{html=}")

    seconds = None
    error = ""

    try:
        seconds0 = int(html)
        if str(html) == str(seconds0):
            seconds = seconds0
        else:
            error = f"html not int ({html=})"
    except Exception as er:
        error = f"exception with {html=}"

    logger.debug(f"   +{fun} {seconds=} {error=}")
    if error:
        logger.error(f"{error=}")
        return api_error(error)
    else:
        return api_success(seconds=seconds)


def check_refreshslip(
    login="",
    domain="com",
    cookie="",
    session=None,
    nst="",
    # want_linux=True,
    want_linux=False,
    want_get_before_post: bool = False,
    headers_txt: str = None,
):
    """проверяем куку
    todo:
    что значит:
        <Error><Message>An error has occurred.</Message></Error>
    """
    fun = "check_refreshslip"
    logger.debug(f"[{fun}: with {cookie=}")
    url = get_bet365url_in_domain(
        f"https://www.bet365.com/BetsWebAPI/refreshslip", domain,
    )
    if not session:
        session = get_bet365_session(proxy="", login=login, domain=domain)

    if not cookie:
        # cookie = "__cf_bm=t2ldRiN47NWas3X4BxUWWK_EcT5DogBUrdDdynwNrQg-1643378185-0-ASv4NpAZZmINQSRBysa2fjLPeQE3WJaZCp3EdKHhgRVdsqq58H9R81yhFj9MMFbCn4JKFEEyv4KnyAtzMJCvvus=; aaat=di=b10a4fe2-8bf8-4d3b-abfb-3a4d75f3ce0d&am=0&at=e978ff35-d0bf-40b1-9990-a1070bd2e1ff&un=AwolPole&ts=28-01-2022 13:56:26&v=2; pstk=26289B00FB94450C8B07A99A926E7AB1000004; qBvrxRyB=AxgY-aB-AQAABk9f_qMNEIcpwGrteypGxGuFeVR8Uk9WGXBZasiFkNY9HblNAV7CsneucqIfwH8AAEB3AAAAAA|1|1|c4f81dc34e82628aa6498101da2a9eb28a3b4d28; aps03=lng=1&tzi=1&ct=197&cst=0&cg=2; session=processform=0; usdi=uqid=1DE38F44-7A46-4888-9BB0-4E1710B025BA"
        # сменяю куку клаудфлара
        # cookie = "__cf_bm=; aaat=di=b10a4fe2-8bf8-4d3b-abfb-3a4d75f3ce0d&am=0&at=e978ff35-d0bf-40b1-9990-a1070bd2e1ff&un=AwolPole&ts=28-01-2022 13:56:26&v=2; pstk=26289B00FB94450C8B07A99A926E7AB1000004; qBvrxRyB=AxgY-aB-AQAABk9f_qMNEIcpwGrteypGxGuFeVR8Uk9WGXBZasiFkNY9HblNAV7CsneucqIfwH8AAEB3AAAAAA|1|1|c4f81dc34e82628aa6498101da2a9eb28a3b4d28; aps03=lng=1&tzi=1&ct=197&cst=0&cg=2; session=processform=0; usdi=uqid=1DE38F44-7A46-4888-9BB0-4E1710B025BA"
        pass

    if not nst:
        nst = get_saved_token()
        logger.warning(f"{nst=}")

    if headers_txt is None:
        logger.debug(f"get default headers_txt")
        headers_txt = """
        Host: www.bet365.com
    User-Agent: [user_agent]
    Accept: */*
    Accept-Language: en-US,en;q=0.5
    Accept-Encoding: gzip, deflate, br
    Referer: https://www.bet365.com/
    Content-type: application/x-www-form-urlencoded
    X-Net-Sync-Term: [nst]
    Content-Length: 377
    Origin: https://www.bet365.com
    Connection: keep-alive
    # Cookie: __cf_bm=LSRAQtjlTClQ6AhBrGDixGBYIsXkrtztRgRE8RQdFcM-1643375806-0-AQsGNTqZsw7eTwaFpPOO187OvWNsY3UugF6RSHS9P3vPhxqSwTxkDvu+qXZ18uw4J6JBOLSKkjDbOfyCDaOJWFY=; cf_chl_prog=b; pstk=C6517C2E5D1FFB54B4B4D444746AACB5000004; rmbs=3; aaat=di=68f3b0ed-c0ea-45ad-9162-305ad3622ad7&am=0&at=7e464e6c-8b9e-4841-935a-1a1a82093871&un=Waldasa90&ts=28-01-2022 13:06:49&v=2; qBvrxRyB=A0Wty6B-AQAA8xLRQLpzmno1xX4Mugk1FKQM6-ppEAthGNVJOCBq3Ep4CPVWAbmnTU-cuL5iwH8AAEB3AAAAAA|1|1|5f92e81e6857a164afcf4bd4c133161e3711f22a; aps03=ao=0&cf=E&cg=2&cst=0&ct=197&hd=Y&lng=1&oty=1&tt=2&tzi=1; usdi=uqid=9D9A7B93-2378-44CF-8F08-D20E23EAFB63; session=lgs=1&ntfr=
    Cookie: [cookie]

    """
    if want_linux:
        headers_txt = """
            Host: www.bet365.es
        User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0
        Accept: */*
        Accept-Language: en-US,en;q=0.5
        Accept-Encoding: gzip, deflate, br
        Referer: https://www.bet365.es/
        Content-type: application/x-www-form-urlencoded
        X-Net-Sync-Term: UV8BYg==.C3zzOv0hurqKI3YpI3lINlvgDJ7sXQBf2iNhhZAcZL4=
        Content-Length: 376
        Origin: https://www.bet365.es
        Connection: keep-alive
        Cookie: rmbs=3; aaat=di=8c75bf77-618c-4a85-9441-a070495e31b9&am=0&at=f5744cb4-6595-4057-8fba-123dc67a6787&ts=06-02-2022 18:04:58&v=2; __cf_bm=R1wMZXjtL6.YY7P2G4M9czKkc1OYsU3TAKgqIUaWSE0-1644170645-0-AeLfVT88zZdgWmKl/Lwdsfec08XPrjtKJFJiKhUqzw09fZVNPiA9TCRb1qoQ+3luIDWW6Mpz0nehFfpejqjVOzc/pY9PoKbki+GpnzSxMMDdL9jA+qe1nmUgrlNC/sNAogiNiwrD/ww0UiD0N7AV3i/P1ydUiapJKoHilbZ8O2jx; pstk=74199594DC75FA3DBAC1497185C49FB8000004; session=lgs=1; aps03=ao=1&cf=E&cg=4&cst=0&ct=171&hd=Y&lng=1&oty=2&tt=2&tzi=4; usdi=uqid=C2E8B8FA-C874-41CD-A1DD-118B7CB364C1; gstk=74199594DC75FA3DBAC1497185C49FB8000004
        Sec-Fetch-Dest: empty
        Sec-Fetch-Mode: cors
        Sec-Fetch-Site: same-origin
        """

    if 1:
        headers_txt = """
        Host: www.bet365.es
User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0
Accept: */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Referer: https://www.bet365.es/
Content-type: application/x-www-form-urlencoded
X-Net-Sync-Term: [nst]
Content-Length: 466
Origin: https://www.bet365.es
Connection: keep-alive
Cookie: [cookie]
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin
        """

    headers_txt = (
        get_useragent_in_domain(headers_txt, domain)
        .replace("[cookie]", cookie)
        .replace("[nst]", nst)
        .replace("Cookie: \n", "\n")
    )

    # logger.debug(f"{headers_txt=}")
    # wait_for_ok(f"good headers?")
    url = get_bet365url_in_domain(url, domain)
    headers_txt = get_bet365url_in_domain(headers_txt, domain)
    headers = parse_headers_from_text(headers_txt)

    if want_get_before_post:  # оказалось фигня - там бет просто не работает!
        t = 1
        if t:
            logger.warning(f"want_get_before_post, so get {url=}:")
            kwargs = {
                "url": url,
                "headers": headers,
                "allow_redirects": False,
            }
            r_refreshslip = request_with_requests(session, **kwargs)
        else:
            r_refreshslip = check_session_on_refreshslip(
                session, domain=domain
            )
        logger.debug(f"finished GET: {r_refreshslip=}")

    kwargs = {
        "url": url,
        "headers": headers,
        "allow_redirects": False,
        # "data": "&ns=pt%3DN%23o%3D31%2F20%23f%3D114093723%23fp%3D537090574%23so%3D%23c%3D1%23mt%3D16%23id%3D114093723-537090574Y%23%7CTP%3DBS114093723-537090574%23%7C%7Cpt%3DN%23o%3D7%2F10%23f%3D114093718%23fp%3D537090165%23so%3D%23c%3D1%23mt%3D16%23id%3D114093718-537090165Y%23%7CTP%3DBS114093718-537090165%23%7C%7C&betsource=FlashInPLay&bs=1&cr=1",
        "data": r"&ns=pt%3DN%23o%3D11%2F1%23f%3D113872927%23fp%3D516681335%23so%3D%23c%3D1%23sa%3D6204f9c6-C55FB3EC%23mt%3D16%23%7CTP%3DBS113872927-516681335%23%7C%7Cpt%3DN%23o%3D5%2F4%23f%3D113872923%23fp%3D516681149%23so%3D%23c%3D1%23sa%3D6204f9cb-62D18229%23mt%3D16%23%7CTP%3DBS113872923-516681149%23%7C%7Cpt%3DN%23o%3D6%2F1%23f%3D114001077%23fp%3D528192730%23so%3D%23c%3D1%23sa%3D6204f9e1-7376A4E7%23mt%3D16%23%7CTP%3DBS114001077-528192730%23%7C%7C&betsource=FlashInPLay&bs=1&cr=1",
    }
    t_start_request = time.time()
    step = 0
    while True:
        step += 1
        duration = time.time() - t_start_request
        if duration > 60 * 20:
            m = "check, may be bad proxy"
            logger.critical(m)
            inform_critical(m)

        r_response = request_with_requests(session, **kwargs)
        logger.debug(
            f"""  + {step=} ({duration:0f} seconds from start), durations {r_response["duration_details"]}"""
        )
        # show_dict(r_response)
        break

    response = r_response["response"]
    post_error = r_response["error"]
    answer = r_response["json"]

    tip = parse_answer_tip(
        answer=answer, post_error=post_error, response=response
    )

    logger.debug(f"{tip=} {post_error=}")

    html = response.text
    bg = find_from_to_one('"bg":"', '"', html)

    if tip == "addbet_success":
        logger.debug(f"{tip=} {bg=}")
        result = api_success(tip=tip, bg=bg)
    else:
        logger.debug(f"{html=}")
        error = post_error
        logger.error(f"{error=}")
        result = api_error(error, tip=tip, html=html)

    logger.debug(f" +{fun} {result=}]")

    return result


if __name__ == "__main__":
    from bet365_one_api.bet365_login import get_proxy_login_password_for_bet365

    name = ""

    name = "77 (pirxts for login)"
    pstk = "24F9195366942DDB96DDC00A3B6224B0000004"
    domain = "com"

    t = 1
    if t:
        pstk = "57CE34625CC5DE199A6D79788D5DAC10000004"  # 118 spanish auto
        domain = "es"
        name = "spain"

    special = "check_max_logins_with_pstk"
    special = "set_last_action_time"
    special = "get_balance_with_pstk"
    special = "check_refreshslip"
    special = "keep_pstk_alive"
    special = "get_last_action_time"

    if special == "get_last_action_time":
        result = get_last_action_time(pstk=pstk)
        logger.info(f"{result=}")

    elif special == "check_refreshslip":
        session = None
        t = 1
        if t:
            login_id = "112"  # порезка
            login_id = "77"  #
            domain = "com"

            t = 1
            if t:
                domain = "es"
                login_id = "118"  # spain
                name = "spain"

            proxy, login, password = get_proxy_login_password_for_bet365(
                special=login_id
            )
            # wait_for_ok(f"{login=}")

            d_data = r"s:\!kyxa\!code\!documentation\py4seo\advanced\08\dor_minimum\universal_bookmaker\api_bet365\temp"
            nst = get_saved_token()
            cookie = get_saved_cookie()
            ##############

            kwargs = {
                "proxy": proxy,
                "session_from": "cloudscraper",
                "login": login,
                "domain": domain,
                # "want_check_bet365_access": False,
                # "want_cache": False,
            }
            session = get_bet365_session(**kwargs)

            logger.debug(f"{session=}")
            wait_for_ok()

        step = 0
        t_start = time.time()
        while True:
            step += 1
            duration = time.time() - t_start
            result = check_refreshslip(
                cookie=cookie, domain=domain, session=session, nst=nst
            )
            logger.info(
                f"{step=} time={get_human_time()} duration from start {get_human_duration(duration)}, {result=}"
            )
            if is_api_error(result):
                m = f"error: {result=}"
                logger.critical(m)
                inform_critical(m)

            sleep_(60)

    elif special == "keep_pstk_alive":
        result = keep_pstk_alive(pstk=pstk, domain=domain, name=name)
        logger.info(f"{result=}")

    elif special == "set_last_action_time":
        result = set_last_action_time(pstk=pstk)
        logger.info(f"{result=}")

    elif special == "check_max_logins_with_pstk":
        result = check_max_logins_with_pstk(pstk=pstk)
        logger.info(f"{result=}")

    elif special == "get_balance_with_pstk":
        result = get_balance_with_pstk(pstk=pstk)
        logger.info(f"{result=}")

    else:
        logger.critical(f"unknown {special=}")
