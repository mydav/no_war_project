#!/usr/bin/python
# -*- coding: utf-8 -*-

r"""
!!!СИНХРОНИЗИРУЙ PY2-PY3 sync_py2_py3
"""

from modules import *
from bet365_one_api.bet365_session import *
from universal_repo.repository import RedisRepository
from bet365_one_api.pstk_functions import *

logger = get_logger(__name__)


def bet365_login(
    login="",
    domain="com",
    repo=None,
    want_cache: bool = False,
    want_save_cache: bool = False,
    want_check_cached_pstk: bool = False,
    main_key=f"login:[login]",
    **kwargs,
):
    """
    буду логиниться используя предыдущую информацияю, c repo
    """
    if not repo:
        main_key = main_key.replace("[login]", login)
        repo = RedisRepository(main_key)

    t = 0
    if t:
        repo.delete()
        logger.debug("deleted repo")
        wait_for_ok()

    logger.debug(f"login with {repo=} {domain=}")

    logined_from = "cache"
    balance = None

    login_reason = ""  # причина перелогина
    if want_cache:
        r_logined = repo.get()
        logger.debug(f"{r_logined=}")

        if not r_logined:
            login_reason = "cache not exists"

        else:  # проверяем - норм результат?
            if want_check_cached_pstk:
                logger.debug(f"want_check_cached_pstk, so check pstk")
                step_check = 0
                while True:
                    step_check += 1
                    if step_check > 5:
                        m = f"{step_check=} - what to do?"
                        logger.critical(m)
                        inform_critical(m)

                    pstk = r_logined["pstk"]
                    r_balance = get_balance_with_pstk(
                        pstk, login=login, domain=domain
                    )
                    error = get_api_error(r_balance)
                    logger.info(f"{step_check=} {r_balance=} {error=}")
                    # if error in ["pirxt_not_logined"]:
                    if error:
                        if error in ["cloudflare_block"]:
                            sleep_(5)
                            continue
                        elif error in ["pirxt_not_logined", "bot_ip"]:
                            login_reason = "have cached pirxt, but pirxt_not_logined, so retry"
                            repo.delete()
                        else:
                            m = f"unknown {error=}"
                            logger.critical(m)
                            inform_critical(m)
                    else:
                        balance = r_balance["balance"]
                        logger.debug(f"+pstk check success with {balance=}")

                    break

    else:
        login_reason = "do not want use cached pirxt"

    if login_reason:
        logger.debug(f"{login_reason=}, so relogin")
        # wait_for_ok()
        logined_from = "live"

        r_logined = bet365_login_live(login=login, domain=domain, **kwargs)

        error = get_api_error(r_logined)
        if error:
            logger.error(f"got {error=}")
        else:
            more_data = {
                # "kwargs": kwargs,
                "t_add": datetime.datetime.utcnow(),
            }
            r_logined.update(more_data)
            if want_save_cache:
                logger.debug(f"saving to repo {r_logined=}")
                repo.add(r_logined)

    reached_maximum_logins = r_logined.get("reached_maximum_logins")
    session = r_logined.get("session")

    if 0 and session:
        cookie = r_logined["cookie"]
        # cookie_line = f"Cookie: {cookie}"
        # session.cookie = cookie
        logger.warning(f"adding {cookie=} to session")
        # wait_for_ok()

    t = 0
    if t:
        """пока не проверяе - похоже после этого сессия сгорает"""
        check_session_on_bet365_cloudflare_access(session, domain=domain)

    life = 0
    if r_logined.get("t_add"):
        life = round(
            (datetime.datetime.utcnow() - r_logined["t_add"]).total_seconds(),
            2,
        )
    r_logined["life"] = life
    r_logined["logined_from"] = logined_from
    if balance is not None:
        r_logined["balance"] = balance
    pstk = r_logined.get("pstk")
    logger.debug1(
        f" +{pstk=} {logined_from=}, life={get_human_duration(life)} {reached_maximum_logins=}"
    )
    return r_logined


def bet365_login_live(
    login="",
    domain: str = "com",
    password="",
    proxy="",
    pstk=None,
    screen_size="1705 x 960",  # ihor
    user_agent: str = None,
    pirxt_headers: str = "",
    func_get_pirxt_headers=None,
    device: str = "RANDOM",  # с какого девайса типа логинимся. Ihor - как у игоря было
    want_check_max_logins: bool = True,  # хочу проверить макс. логинов?
    want_check_logined_cookie: bool = True,  # хочу проверить финальный куки?
    want_check_bet365_access: bool = True,  # проверить доступ сессии к бетке
    want_check_refreshslip_before_login: bool = False,  # хочу перед логином дернуть рефрешслип?
    session=None,
    seconds_sleep_before_request: str = "1-1",  # сколько ждать перед каждым запросом. Часто вылазит not_logined
    mode_login: str = "login_with_pstk_from_members",
    **kwargs,
):
    """логин живой - пробую залогиниться"""
    explore = False
    explore = True
    if explore:
        logger.warning(f"explore == changing default parameters")
        # want_check_refreshslip_before_login = True
        # seconds_sleep_before_request = "5-5"  # сколько ждать перед каждым запросом. Часто вылазит not_logined

    user_agent = get_nonempty_useragent(user_agent)
    cloudflare_cookie = ""

    if domain == "es":
        func_com_to_es = com_to_es_polube
    else:
        func_com_to_es = com_to_es_no

    def get_f(name=""):
        d_temp = f"temp/login_with_api/{login}"
        d_temp = os.path.join(
            os.path.dirname(__file__), "temp", "login_with_api", login
        )
        return f"{d_temp}/{name}"

    fun = "bet365_login_live"

    t = 0
    device = choice(["ihor", "laptop_with_touch"])
    if t:
        func_get_pirxt_headers = None
        logger.warning("do not use func_get_pirxt_headers")

    if device == "RANDOM":
        device = choice(["ihor"])
        device = choice(["ihor", "laptop_with_touch"])
        logger.debug(f"random {device=}")

    if device not in ["ihor", "laptop_with_touch"]:
        logger.critical(f"unknown {device=}, use device=ihor")
        device = "ihor"

    seconds_sleep_before_request = get_random_value_in_range(
        seconds_sleep_before_request
    )

    if pstk is None:
        pstk = "E65EBDC9370530B7A1469F8015C648EF200003"  # возможно готовый пстк отлично будет работать всю жизнь :)
        pstk = "DA1104FD51322F2D82FDA70804515E7A000003"  # 2021-12-07 13:00
        pstk = "7954637B250D9639926B0B1D2BCF3C2E000003"  # 2021-12-07 17:00
        pstk = ""  # bot_ip == пстк сгорел? просто ухожу от фиксированного пстк

    t = 0
    if t:
        pstk = ""
        # screen_size="1280 x 950"
        # user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
        # pstk = "DA1104FD51322F2D82FDA70804515E7A000003"

    user_agents = clear_list(user_agent.split("|"))
    if user_agents:
        user_agent = choice(user_agents)
    else:
        user_agent = ""

    f_logined = get_f("01.html")
    f_raw_request = get_f("raw_request.txt")

    logger.debug(
        f"[{fun} {login}:{password} {proxy=} {domain=} {device=} {seconds_sleep_before_request=} {user_agent=}"
    )
    # wait_for_ok()

    mode = "debug"
    mode = "real"

    if session is None:
        if mode == "debug":
            logger.warning(f"{mode=}, so get demo session")
            kwargs = {
                "proxy": proxy,
                "domain": domain,
                "want_check_bet365_access": True,
                "want_check_bet365_access": False,
                # "session_from": "requests",
                "session_from": "cloudscraper",
            }
            session = get_bet365_session(**kwargs)

        else:
            session = get_bet365_session(
                login=login,
                proxy=proxy,
                domain=domain,
                want_check_bet365_access=want_check_bet365_access,
            )

    want_emulate_browser = True
    want_emulate_browser = False
    if want_emulate_browser:
        logger.warning(f"want_emulate browser")
        r = emulate_browser_for_bet365_session(session, domain=domain)
        logger.debug(f"emulated browser, {r=}")
        # session = r["session"]
        wait_for_ok("emulated browser, continue?")

    # реальный логин если надо протестить

    # 2022-01-21 00:10 from login
    # 2022-01-21 13:15 from login
    # 2022-01-22 09:40 from login
    # 2022-01-22 21:40 from login - 12 часов!!!
    # 2022-01-23 09:50 from login
    # 2022-01-23 21:20 from login - на запас. И реально через 12 часов (21:50) вырубало!
    # 2022-01-24 10:40 from login - на запас - опять 12 часов!
    # 2022-01-24 23:25 from login - на запас - опять 12 часов!
    # 2022-01-25 19:35
    # 2022-01-26 10:05 from login
    # 2022-01-26 22:27 from login
    # 2022-01-27 13:03 from login
    # 2022-01-28 10:07 from login
    # 2022-01-28 23:40 from login
    # 2022-01-29 17:27 from login
    # 2022-01-29 22:37 from login 118
    # 2022-01-31 13:25 from login 77
    # 2022-02-01 08:25 from login 77
    text_headers_login = """
"""
    pirxts_saved = get_saved_pirxts()
    if pirxts_saved is None:
        logger.error(f"no saved pirxts?")
        os._exit(0)
    else:
        text_headers_login = pirxts_saved

    pirxt_headers_from_func = ""
    if func_get_pirxt_headers:
        if "<nah_pirxt_headers_from_func>" in pirxts_saved:
            logger.debug(
                f"skip func_get_pirxt_headers (found <nah_pirxt_headers_from_func>)"
            )
        else:
            logger.debug(f"get pirxt_headers with {func_get_pirxt_headers=}")
            pirxt_headers_from_func = func_get_pirxt_headers()

    if 1:  # pirxt_headers or pirxt_headers_from_func:
        text_headers_login = f"{text_headers_login}\n#pirxt_header\n{pirxt_headers}\n#pirxt_headers_from_func\n{pirxt_headers_from_func}"
        logger.debug(f"new {text_headers_login=}")
    # logger.debug(f"{pirxts_saved=}")
    # wait_for_ok()

    text_headers_like_browser = get_text_headers_like_in_browser(
        user_agent=user_agent
    )
    repl = {
        "[user_agent]": user_agent,
    }
    text_headers_login = func_com_to_es(
        no_probely_one(text_headers_login, repl)
    )

    # get pstk
    if pstk:
        logger.warning(f"use fixed {pstk=}")

    else:

        logger.debug("start getting pstk:")
        urls = clear_list(
            """
            # https://bet365.com/
            https://www.bet365.com/
            # https://www.bet365.com/en/
            # https://www.bet365.com/
            https://www.bet365.com/defaultapi/sports-configuration
            """,
            bad_starts="#",
        )
        for num, url in enumerate(urls, 1):
            url = func_com_to_es(url)
            # wait_for_ok(url)
            f_temp = get_f(f"0_{num}.html")
            f_raw = get_f(f"0_{num}_raw_request.txt")

            logger.debug2(f"download url {num}/{len(urls)} {url=}")

            if num == 1:  # step_1
                new_headers = f"""{text_headers_like_browser}
                Sec-Fetch-User: ?1
                """

                headers = prepare_headers_for_bet365_placebet(
                    min_browser_headers="",
                    fixed_headers=new_headers,
                    final_process_func=func_com_to_es,
                )
                want_fix_first_cookie = False
                want_fix_first_cookie = True
                if want_fix_first_cookie:
                    t = 0
                    if t:
                        cookie = "pstk=E6DBF2551024D98C89499A79001BC532000003; rmbs=3; aaat=di=26bd48d8-61a2-4f83-a6aa-bef167d80f13&am=0&at=449ed0d5-247e-45bb-8838-7203429a90e7&ts=02-02-2022 15:16:24&v=2; aps03=ao=1&cf=E&cg=4&cst=0&ct=171&hd=Y&lng=1&oty=2&tt=2&tzi=4"
                        logger.warning(
                            f"fix cookie for spain account {cookie=}"
                        )
                        headers["Cookie"] = cookie

                    t = 0
                    if t:
                        session.cookies.clear()
                        # del session.cookies["__cf_bm"]
                        # session.cookie = cookie
                    # wait_for_ok()

                    t = 0
                    if t:
                        cookie = r"rmbs=3; aaat=di=8c75bf77-618c-4a85-9441-a070495e31b9&am=0&at=f5744cb4-6595-4057-8fba-123dc67a6787&ts=06-02-2022 18:04:58&v=2; pstk=2FB9DF45C42B453CA38D230422B76749000003; aps03=ao=1&cf=E&cg=4&cst=0&ct=171&hd=Y&lng=1&oty=2&tt=2&tzi=4; __cf_bm=rpmuYqPkF3ScjnaubZdPP1QaTXfB1p27lJkPujxcRSo-1644187432-0-AYodR5TQmKMTRRv8Pr7ZJBqGC0m2Xp0Ans7zfrmZ5gM0Db0+e9hFnaXfgJAtM1BC5XhwUTigTWXmzPE5ptHHmUZfYRHwU1S9DeTh0tcqd+Q9Xd9q6wzH+LSSdVhzYq+WjmOFxnCAgjYyv7f13km/yqJVbBcZMIUbDYP64vKFlsoG"
                        cookie_dict = parse_cookieString_to_dict(cookie)
                        logger.warning(
                            f"add cookies: {pretty_dict(cookie_dict)}"
                        )
                        session.cookies.clear()
                        session.cookies.update(cookie_dict)
            else:
                new_headers = f"""{text_headers_like_browser}
                Accept: */*
                Sec-Fetch-Dest: empty
                Sec-Fetch-Mode: cors
                Sec-Fetch-Site: same-origin
                """

                headers = prepare_headers_for_bet365_placebet(
                    min_browser_headers="",
                    fixed_headers=new_headers,
                    final_process_func=func_com_to_es,
                )
                # show_dict(headers)
                # wait_for_ok()

                show_dict(headers)

            url_real = url
            if "sports-configuration" in url:
                url_real = url + sports_config_finish
            kwargs = {
                "url": url_real,
                "headers": headers,
                "allow_redirects": False,
            }
            t_start_request = time.time()
            step = 0
            while True:
                step += 1
                if step > 1:
                    sleep_(1)

                duration = time.time() - t_start_request
                if duration > 60 * 20:
                    m = "check, may be bad proxy"
                    logger.critical(m)
                    inform_critical(m)

                sleep_(seconds_sleep_before_request)
                r = request_with_requests_html(session, **kwargs)
                logger.debug(
                    f"""  + {step=} ({duration:0f} seconds from start), durations {r["duration_details"]}"""
                )

                response = r["response"]

                t = 1
                if t:
                    logger.debug(f"{response=}")
                    show_dict(r)
                    # wait_for_ok()

                if not response or response is None:
                    continue

                # проверка на клаудфлар
                if response.status_code == 403:
                    status = check_bet365_cloudflare(response.text)
                    if status in ["cloudflare_block", "cloudflare_captcha"]:
                        logger.critical(f"cloudflare detected: {status=}")
                        os._exit(0)

                break

            html = response.text
            logger.debug(f"  {html[:200]=}...")
            text_to_file(html, f_temp)

            raw_request = r["raw_request"]
            join_text_to_file(raw_request, f_raw_request)
            text_to_file(raw_request, f_raw)

            logger.debug(f"response cookies={response.cookies}")
            explore_cookies(response.cookies)

            if num == 1:
                cloudflare_cookie = response.cookies.get("__cf_bm")
                if not cloudflare_cookie:
                    logger.debug(f"session cookies:")
                    explore_cookies(session.cookies)
                    __cf_bm = session.cookies.get(
                        "__cf_bm",
                        domain=get_bet365url_in_domain(".bet365.com", domain),
                    )
                    if not __cf_bm:
                        __cf_bm = session.cookies.get("__cf_bm")
                    cf_clearance = session.cookies.get(
                        "cf_clearance",
                        domain=get_bet365url_in_domain(".bet365.com", domain),
                    )
                    logger.debug(f"{__cf_bm=}\n{cf_clearance=}")
                    cloudflare_cookie = [f"{__cf_bm}"]
                    if 0 and cf_clearance:
                        cloudflare_cookie.append(
                            f"cf_clearance={cf_clearance}"
                        )
                    cloudflare_cookie = "; ".join(cloudflare_cookie)
                    logger.warning(
                        f"no cloudflare_cookie in response, so get cloudflare_cookie from session {cloudflare_cookie=}"
                    )
                logger.debug(f"{cloudflare_cookie=}")
                t = 0
                if t:
                    logger.warning(
                        f"change __cf_bm in cookies to {cloudflare_cookie}"
                    )
                    del session.cookies["__cf_bm"]
                    session.cookies["__cf_bm"] = cloudflare_cookie
                # wait_for_ok()

                if not cloudflare_cookie:
                    logger.critical(
                        f"no cloudflare cookies in {response.cookies}"
                    )
                    os._exit(0)
            # wait_for_ok()

            if "Location: http://localhost" in raw_request:
                error = "bot_ip"
                logger.critical(error)
                return api_error(error)

            if num == 1:
                sports_config_finish = find_from_to_one(
                    '"SITE_CONFIG_LOCATION":"/defaultapi/sports-configuration',
                    '"',
                    html,
                )
                logger.debug(f"{sports_config_finish=}")
            else:
                sports_config_finish = ""

        pstk = response.cookies.get("pstk", None)
        if pstk is None:
            error = "no_pstk"
            logger.error(error)
            return api_error(error)

    if want_check_refreshslip_before_login:
        logger.warning(f"want_check_refreshslip_before_login")
        wait_for_ok("start check?")
        r_refreshslip = check_refreshslip(
            domain=domain, session=session, headers_txt=""
        )
        logger.debug(f"refreshslip result {r_refreshslip=}")
        # wait_for_ok()

    logger.debug(f"loginning with {pstk=}...")
    url = "https://members.bet365.com/members/lp/default.aspx"
    url = func_com_to_es(url)
    login = quote_plus(login)
    password = quote_plus(password)

    if device == "ihor":
        post_device = {
            "{platform}": 1,
            "{IS}": 11,
            "{AuthenticationMethod}": 0,
        }
    elif device == "laptop_with_touch":
        post_device = {
            "{platform}": 2,
            "{IS}": 21,
            "{AuthenticationMethod}": 3,  # помнить логин
            "{screen_size}": "1280 x 950",
        }
    else:
        logger.critical(f"unknown {device=}")
        os._exit(0)

    post_data = "txtType={txtType}&txtTKN={pstk}&txtLCNOVR=GB&platform={platform}&IS={IS}&txtUsername={login}&txtPassword={password}&AuthenticationMethod={AuthenticationMethod}&txtScreenSize={screen_size}"
    repl = {
        "{txtType}": 85,
        "{pstk}": pstk,
        "{screen_size}": screen_size,
        "{login}": login,
        "{password}": password,
    }
    repl.update(post_device)

    repl["{screen_size}"] = quote_plus(repl["{screen_size}"])
    post_data = no_probely_one(post_data, repl)

    # logger.debug(f"{repl=} created {post_data=}")
    # my_post_data = "txtType=85&txtTKN=C1E6FB8BA7FF464E889C917D4C5054C6000003&txtLCNOVR=GB&platform=2&IS=21&txtUsername=Waldasa90&txtPassword=Trim9850%2524&AuthenticationMethod=0&txtScreenSize=1280%20x%20950"

    headers = prepare_headers_for_bet365_placebet(
        fixed_headers=text_headers_login, final_process_func=func_com_to_es,
    )
    t = 0
    if t:
        logger.debug("headers:")
        show_dict(headers)

    kwargs = {
        "url": url,
        "headers": headers,
        "data": post_data,
    }
    sleep_(seconds_sleep_before_request)
    # pstk = ""
    if mode_login == "login_with_pstk_from_members":
        r = login_with_pstk_from_members(
            pstk=pstk,
            login=login,
            password=password,
            session=session,
            domain=domain,
        )
    else:
        r = request_with_requests_html(session, **kwargs)

    logger.debug(f"""+{r["duration_details"]}""")
    response = r["response"]
    request_error = r["error"]

    if response:
        html = get_response_text(response)
        # logger.debug(f"  {type(html)=} {html=}")

        # wait_for_ok()

        t = 0
        if t:  # что за запиненная инфа - расшифровать
            f_pickled = os.path.abspath(r"temp/response.pickled")
            obj_to_file(html, f_pickled)

            html_content = response.content
            logger.debug(f"  {type(html_content)=} {html_content=}")
            f_pickled_content = os.path.abspath(
                r"temp/response_content.pickled"
            )
            obj_to_file(html_content, f_pickled_content)

            m = f"saved pickled html to {f_pickled}"
            logger.warning(m)
            wait_for_ok(m)

        text_to_file(html, f_logined)

        raw_request = r["raw_request"]
        join_text_to_file(raw_request, f_raw_request)
        text_to_file(raw_request, f_logined)

        explore_cookies(response.cookies, "respones cookies:")

        if "txtPSTK=" in html:
            logger.debug(f"     pstk from html")
            pstk = find_from_to_one("txtPSTK=", ",", html)
        else:
            logger.debug(f"     pstk from cookies")
            pstk = session.cookies.get("pstk")
        # txtPSTK=DCCBF83EBFB949548F458A189E27EB70000004,notificationsActive=True,notificationsRequired=False

        error = ""
        if not pstk:
            error = "no_pstk"

            # угадываю - почему его нет
            want_guess_reason = True
            if want_guess_reason:
                if len(response.cookies) == 1:
                    cookie_value = response.cookies.values()[
                        0
                    ]  # cookie qBvrxRyA: A9oZjwV-AQAAcw6AJIH1t4aRyYWgJO0Wh7RFBzir5rqC1Qhy7a6f1f9gBPCQAVrApjCcuL5iwH8AAEB3AAAAAA|1|0|0b0c5f9c05fa59c37871d7041dea97db5972b69d
                    parts = cookie_value.split("|")
                    show_list(parts)
                    if (
                        len(parts) == 4 and parts[1] == "1" and parts[2] == "0"
                    ):  # Но не обязательно пирхт плохой :)
                        possible_reason = "wrong_pirxt"
                        logger.warning(f"may be {possible_reason=}")
                        inform_me_one(possible_reason)

        elif not pstk.endswith("00004"):
            error = "not_logined"

    elif "Max retries exceeded with url: http://localhost" in request_error:
        error = "bot_ip"

    else:
        error = "connection_error"

    result = {}
    if error:
        logger.error(error)
        result = api_error(error)
    else:
        result = None
        while True:  # break at result
            cookies = response.cookies
            want_fix_cookie = False
            if want_fix_cookie:
                repl = {
                    "session": "lgs=1",
                    "aps03": "ao=1&cf=E&cg=4&cst=0&ct=171&hd=Y&lng=1&oty=2&tt=2&tzi=4",
                    "rmbs": "3",
                }
                for key, value in repl.items():
                    cookies.set(key, None)
                    cookies.set(key, value, domain=".bet365.es")

                logger.warning(f"fixed cookies with {repl}:")
                explore_cookies(cookies)

            cookie = convert_cookies_to_str(cookies)
            if cloudflare_cookie and cloudflare_cookie not in cookie:
                logger.debug(f"add to cookies {cloudflare_cookie=}")
                cookie = f"__cf_bm={cloudflare_cookie}; {cookie}"

            logger.info(f"final response Cookie: {cookie}")

            reached_maximum_logins = None
            if want_check_max_logins:
                # wait_for_ok("now refreshslip?")
                logger.debug2("want_check_max_logins...")
                r_check = check_max_logins_with_pstk(
                    # cookie=cookie,
                    domain=domain,
                    session=session,
                    # nst=nst,
                )
                logger.debug1(f"    +check_max_logins_with_pstk {r_check=}")
                login_warning = get_api_error(
                    r_check
                )  # 'error': 'reached_maximum_logins'
                if login_warning:
                    logger.warning(f"{login_warning=}")
                if login_warning == "reached_maximum_logins":
                    reached_maximum_logins = True
                else:
                    reached_maximum_logins = False
            session.reached_maximum_logins = reached_maximum_logins

            if want_check_logined_cookie:
                # wait_for_ok("sleep before check (addbet will relogin)")
                d_data = r"s:\!kyxa\!code\!documentation\py4seo\advanced\08\dor_minimum\universal_bookmaker\api_bet365\temp"
                f_nst_headers = [
                    pathlib.Path(__file__).parent / "data" / "nst_headers.txt",
                    f"{d_data}\\nst_headers.txt",
                    r"c:\nst_headers.txt",
                ]
                nst = text_from_file(f_nst_headers)
                if nst is None:
                    m = f"no files {f_nst_headers} to check"
                    logger.critical(m)
                    inform_critical(m)

                nst = nst.replace("X-Net-Sync-Term: ", "").strip()

                # если надо - проверяю будут ли куки постить
                cnt_checks = 1
                for num_check in range(1, cnt_checks + 1):
                    if 0 and num_check == 1:
                        logger.debug("sleep a little")
                        sleep_(5)

                    t = 0
                    if t:
                        r_balance = get_balance_with_pstk(
                            pstk, login=login, domain=domain, session=session
                        )
                        error = get_api_error(r_balance)
                        logger.info(f"{r_balance=} {error=}")

                    t = 0
                    if t:
                        r_check = keep_pstk_alive(
                            pstk=pstk,
                            domain=domain,
                            max_steps=1,
                            session=session,
                        )
                        logger.debug(
                            f"   {num_check=}/{cnt_checks} {r_check=}"
                        )

                    t = 0
                    if t:
                        # wait_for_ok("now refreshslip?")
                        r_check = check_refreshslip(
                            cookie=cookie,
                            domain=domain,
                            session=session,
                            nst=nst,
                        )
                        logger.debug(
                            f"   {num_check=}/{cnt_checks} {r_check=}"
                        )
                        logined_error = get_api_error(r_check)
                        if logined_error:
                            logger.error(f"{logined_error=}")
                            result = api_error(
                                "cookie_not_logined", logined_error
                            )
                            break

                    if cnt_checks == num_check:
                        break

                    sleep_(10)

            if result is None:  # значит не ошибка а проверку прошло
                # session.cloudflare_cookie = cloudflare_cookie
                # test_without_fixed_cookie
                # session.cookie = cookie

                logger.debug1(f"logined, {pstk=}, Cookie: {cookie}")
                # wait_for_ok("")
                data = dict(
                    cookie=cookie,
                    pstk=pstk,
                    response=response,
                    session=session,
                    reached_maximum_logins=reached_maximum_logins,
                )
                result = api_success(**data)
            else:
                logger.error(f"error login: {result=}")
            break

    logger.debug1(f"    +{fun}: for {device=} {result=}")
    return result


def get_proxy_login_password_for_bet365(special="77"):

    text_login_password_proxy = ""

    if not special:
        logger.critical(f"empty special")
        os._exit(0)

    elif special == "ihor":
        proxy = "juai4w:o37xhd@77.232.38.120:8353"
        login_password = """jameswaby8\twikseav"""
        login, password = login_password.split("	")

    elif special == "77":
        proxy = "https://node-gb-3.astroproxy.com:10463"
        login_password = """Waldasa90	Trim9850$"""
        login, password = login_password.split("	")

    elif special in ["078", "78"]:
        proxy = "juai4w:o37xhd@77.232.38.120:8353"
        proxy = "node-uk-3.astroproxy.com:10381"
        login_password = """Philipp49Hgd	Pretty&8543FFg"""
        login, password = login_password.split("	")

    elif special == "100":
        text_login_password_proxy = (
            "Kwashiorkor	9L4j8neG3A		node-uk-2.astroproxy.com:10381"
        )

    elif special == "103":
        login = "Ligyrophobia"
        password = "sa6yN5G2S"

    elif special == "105":
        text_login_password_proxy = (
            "SsStep01	ddGB3R55q1		https://node-uk-4.astroproxy.com:10365"
        )
    elif special == "106":
        text_login_password_proxy = (
            "CailiRickshaw	Ggjh996		https://node-uk-3.astroproxy.com:10009"
        )
    elif special == "107":
        proxy = "node-uk-2.astroproxy.com:10381"
        login_password = """J22Rau02	15Kf43SSax"""
        login, password = login_password.split("	")

    elif special == "108":
        text_login_password_proxy = (
            "JamesQuondam	Fellps59GO		https://node-gb-3.astroproxy.com:10061"
        )

    elif special == "109":
        proxy = "node-ru-256.astroproxy.com:10615"
        login_password = """GlitzlectGlyph	36dLk97eRB"""
        login, password = login_password.split("	")

    elif special == "111":
        proxy = "node-ru-131.astroproxy.com:10811"  # 111
        login_password = """Bjt23Yokel	2RkSjD5b5"""  # 111
        login, password = login_password.split("	")

    elif special == "112":
        proxy = "https://node-uk-4.astroproxy.com:10373"
        login_password = """AwolPole	f8jh4E7KB"""
        login, password = login_password.split("	")

    elif special == "113":
        text_login_password_proxy = (
            "Crepitus	z2dYV3Kj7		node-uk-4.astroproxy.com:10367"
        )

    elif special == "117":
        text_login_password_proxy = (
            "SaltcelMeep	Kc6Br94Cc2		node-ru-131.astroproxy.com:10811"
        )

    elif special == "118":
        text_login_password_proxy = "Diagraphics	55hBajAG4	no"

    elif special == "ihor_01":
        text_login_password_proxy = "maricasapo\tSapo1010\tno"

    else:
        logger.critical(f"unknown {special=}")
        os._exit(0)

    if text_login_password_proxy:
        parts = clear_list(text_login_password_proxy.split("\t"))
        logger.debug(f"{text_login_password_proxy=}, {parts=}")
        login, password, proxy = parts

    if proxy == "no":
        proxy = ""

    return proxy, login, password


def emulate_browser_for_bet365_session(
    session,
    cookie="",
    domain="com",
    want_get_before_post: bool = True,
    want_fix_session_useragent=False,
):
    fun = "emulate_browser_for_session"
    logger.debug(f"[{fun} {domain=}:")
    url = "https://www.bet365.es/#/HO/"
    post_data = ""
    text_headers = """
Host: www.bet365.es
User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Connection: keep-alive
Cookie: [cookie]
Upgrade-Insecure-Requests: 1
Sec-Fetch-Dest: document
Sec-Fetch-Mode: navigate
Sec-Fetch-Site: same-origin
Cache-Control: max-age=0, no-cache
Pragma: no-cache
    """

    url = "https://www.bet365.es/"
    post_data = ""
    text_headers_browser = """
    Host: www.bet365.es
User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Connection: keep-alive
Cookie: pstk=E6DBF2551024D98C89499A79001BC532000003; rmbs=3; aaat=di=26bd48d8-61a2-4f83-a6aa-bef167d80f13&am=0&at=449ed0d5-247e-45bb-8838-7203429a90e7&ts=02-02-2022 15:16:24&v=2; aps03=ao=1&cf=E&cg=4&cst=0&ct=171&hd=Y&lng=1&oty=2&tt=2&tzi=4
Upgrade-Insecure-Requests: 1
Sec-Fetch-Dest: document
Sec-Fetch-Mode: navigate
Sec-Fetch-Site: none
Sec-Fetch-User: ?1
        """
    text_headers_browser_er = """
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
    text_headers = text_headers_browser
    text_headers = text_headers_browser_er

    t = 1
    if t:
        url = "https://members.bet365.com/members/lp/default.aspx"
        text_headers = """
        Host: members.bet365.es
User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0
Accept: */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Referer: https://www.bet365.es/
Content-type: application/x-www-form-urlencoded
PIRXTcSdwp-f: A1Yj7b9-AQAARiQSqlKQfuQ-9w6TKd147UCRGzyqx6OPEUMpjnr4iDUyHgjCAVR8mu2cuNP0wH8AADQwAAAAAA==
PIRXTcSdwp-b: -qroz8
PIRXTcSdwp-c: AACD4r9-AQAAGVtBqoceHMprjbqNPSmaV-pOx8EBVQeM5FICHo4PCSuH9X0Q
PIRXTcSdwp-d: ABaChIjBDKGNgUGAQZIQhISi0eIApJmBDgCODwkrh_V9EP_____56fBkAK_ByvXxaPg7HzJXC5aRwmE
PIRXTcSdwp-z: q
PIRXTcSdwp-a: ssQ_A=Tpmve6Z770iUOSzON9lr_-74qPmw2gjNmmjx0WPK0TpkZnsQptGroK2fqD5-uIBfsk=-2_gRBrxHhIoiJNiAGtketehcTD79owZ8sMAn=Ee81cPrWg0yCWwNMeCkuw4U3IrEAW6IwZDI0ZfMv4TfmkbGMySrBTt7qByjMIJGigp36DMvf4nIJpVuRlhNOP-v=N5iPlgOSh-mXoIiCwWhBk0eZs94rHKMvfWaSADaOvUI3XVRLH37Mn4uRn_=Vu2jNVdRU4ioysUjWJL1iXy=_AVCmom2J5Gpr3dQScTddnliq5xw5cp4Tb98Vy60MarYVEDPsVNWm5TndjbOgpMVMfbd-S7pqRlqLz_JSpecun3WqhnL3Gt7j-ctEkRG8gLGfTMUdwHg3MNutLdmCGVizuwAMBlm-L97HDk3=ZMSGel9QWHw4D6U5x182EEJhgHnrhoGkVwuiIRzLkpkoCbcUnktrstRbt-up1ao32e6L1eEUHomf-yr-Vc08nz60uUmERRpfmcLpvhgGAin4cB8CitRCvsYGpwyfbNUHTH3GOOUwqY7H=_pI_d8EaxospdEnUVnJbmmbZBy4iDOe5QsOylYzPuVQ3Ovl35CEhLNEW5xd92dC35Of_e=ayVQLaEdnRzypRQGE5kL_XUXPjlrnAxRJsRY5RpOEqs2_RUJOIBy-6KIyuD2peDnwtXdZJ6jlMVUb=ru9piyvlfbMCanwEqE4tcsJRDhO8sEAfUOySGvUMRaOmiHXfwB65XIeedIUO_aZi60n8xJNkmttTk1pPRX-3=2SgxATXCRqLmihwNnNsVHi2IRNKl3RCk4ftUkAgAu2W4wJNyUGn7szxdisDJQSntr0L0CV0s7BXs8ZCn5zmPZ1rmRBDfop_Q9Imwvn58cvfsPSH_obvVEWO_SAuaLrsuwJchZkxBd4XhQRfSHJUERwGRcBQMuQ7fwtdmpKJtuaMYXlnwbEwshGMt8Q_saiwXLyRq0d6=ySYBIgQziYEO-4veXqpkT_p7R8riD8JbPM7PExnSl1vNmMmiR0SSZIsdHPUf-gdTmk009x_WCxwN9VnPO5yQBgyK4gpfpxTW7-VuBQCysmlj5_DgJXk25yjuEM59NssV9_eblPz_inSt5n2vi7TMmfLzQbYdr-k3AKKSVI2Jv7i7xPBjzjMwDjZZrJT8mthLrXQYzOepW2Bur_HLKuHRQeTwn4hpGBk8AutlexwzQw8zlu4Ed0ihwbhTNQB2Ill5ySKN_208KlVKZUpSVKps5HTp6CdKRbhcE1==jpXukoVxkMXM_koVAOyCBv8olcuwKR89Yv3xs3pS1rYwp-6GGKbEsjm78xS2NJM6VxnWaKGpnSN=CqjkesAGBlqZ3KYEEAwJhG-cTnYDNTY5KPci5eKaEbAE8jIMEBvN8DdjtByEhqTSRWGpPh-2EVuvHLuVgljM_7qvy1r8AG5SSQ5G=d0UCBUoTUxbofCVOauhSB=J59GyZHnvU4tR-tLnStnjGyC6yvPMiye4N=MEjCGRKRkwZ23Iz-uGfB-lJyd_O8I92ubjdOmR=tGhaEZPyXNC22m7KPsoI7s3T_uXt0_wPItcOJoB40RX=qyW8M4LWIdu-ETIB2srqx=7bOPch9l8PS5f6DA6q7jS0bsDgXznPJsKf70ZO6qmSEKTQ_4cCoZwbGMMWUq_E=sZnctHNRQ1LuANMvmpDo43wDiVXXI1N70s3313MvyAUJpHGzH1sNmvMG76hCEAtEium7bEU5RI_u3NqJ_m5OAAuqHgZDYtxtWhNM7Um6xuslaeV-C9MsWftcl8Tcxo1KECp-8TWlWeQMVwYfW4U4TOThC--6KsC=CA9tRnOYfqsMbtMelTtM98gTlvu=KVYWqLq=Md2v8PSOnoTZJWrr5g5IkJICvXu3s558Au6Ec7yWWeB4PwmiHv455RsSD465kZiXDSlZWbTJSEy4=KPEqcCO_1iIsGWYNHqMHgqcTYjkx49HoWBz16WBo3WpHgP5SZR7u_lUKibo1yx4ZtXaj2GYNff2th8cHDLPvX3SDgB-xvi2V6jen_EwDubU3pEMfaCHEfHJcar2V_ad4sL5bzCAxBbn1TmlZIJI0UHf9Y9=4GJR-qJOWzfGcxsA4gYIsWSryVowZGlqP0ERAEvdWvJJhTh4ZXeQHsR41yUulAErVjAIGJDeeHbO3-SDVVDBQf0W8GoIgrilx20w=rZ66lpr2b6Zmxpks03oCQ03pp9OT_es8nXrprcC-W-YnphR_Zkau_6CJBP323_2xfWi5hbH5I2RYcMGu_pYcZPZ9jwa36hLYow1a5-i8dbS8gQB4gcRivnKVn58v2VOGkzb2U8DHPr=D-i6_1=kxIHY2ckJESHKy=e0-Muua8lXKmY81x1V6N9w8B5sRzWGmdJXdEZM4-qOApt7os-Qp=aAIZ_6WEs58l4k6EmPYBC_6QkdoBnZmMopOv_W0ccwyBqLSZZuGHIDWp3f8-Y_kx7Gvt5X0egKH=UhZ85rqhMtRunf_uhdV1CSdcrzXDQpohc=AODsvMG7ybe0ln_a5YLcyKmB2gYCdPTthjfmt54YlYM-kEqz0jSPu9XVhy7Q579mDtyjNhc_TN6xM0_m-NyhW20GiNBXg-AQdTNLzBKtwVv_gyVq=hG8CyePrAtfYhwQAywK2qNiN3SAr7BO=oLHB9iISOYaBIjlIVKNgPPjGxHbVLZSIsIk_RVN89AN8-32oG2gM9LkVNr9IupefEKMD7Ia6Ib7q-H1=4RYtHy806Xci5ZjNPyvG0Qow5eVuwx3ZVKT8cLHDPG7MBQHAkLoz-UtgIj5TPbJEyACjlJhrEcTlqpCsIRnIT7rwUoNggvy54Ps7f=YI=2NN5ejpsx__yYRnTs1zrPPfHRDCyEjgQ5y3vsbQBSxIEz8dxqs2_cqLXY8PZ1Lic9zvlr_=gyhpX37-wHLNhukJq-KPuPmESg8K7WHU6DU4ul73t6pPNNZIUBksA1MSldbOTioGrGBSjVW=pELY80t95lAIbJ0ZgAbUbXrOvOzaEWs=d9XQU2Wm9iU=TAQ6cl5bH_3MHRVrfnkIAN-8dMwU==rM0rWHfeK6vwgX3hfhEY6fIcdwSvjocmJjg=iAecJEx1oW5=WlLLOv7wgbVHQ_Ad_8bvWaozgZjQ6O9I1uWmDmzdvRs803S-LOkxYilKK2yG04Y-7WvDeuzlhmRrQpxwIhbcbONZ4avRB542N3E2G7x_yWev88R84BzVr4KkUOmCL46Qta3xq8NZ2igUOyU0s8yjO6bKOGJpPfHqv21yzZMRAcYRKKXWev=JLUcQDKCYhEx3Q=RLTgNObx1XQ4M9gdoM7VGy90vPI0Tj6wXzfwpV2JK9m1tQEk2Hgua1MTDN16Xd1jh8aX0uy-OvhI5n37UbJxh2ZGIEaAzTIJ5aHt4hQLCKuHReefwdAhH=7krVeJb_GAgCUJn5QdSRx-9glVZyfXiA8Ej_PcnGaY3k0hdO=TohMv2nE_t2hyinkQl7CvG0ep5B8Ka5ThOmQ0Xa09jGS31xA8QkO0hPMOAsWVt7IcCupluVmXqTu11AaiY3OciLB_XipbbuvE8X5A_-fNvz7-ZOkKg1kec=lxBTnkp7pA7fDSDygEMJOyGP0W00fts5CogA9-7f4eglYvbVtyvzhnkSEtdG_1b1DZXnk9p9vBINLx-f8jonLzu0p_818HlVNKCLozzj-M_Ypq-pwXeSfcsRbHjY6mNBM86gu6C0y7_9pTzl33pDj8HN=qztaacg9vu275DCkdHp59reWBaDDIRImR_xCuQ=0-eDmG3n49zA3oIPmg9qN6SfIoK0aBtbhR8OqtwCpf5W_f9bn0jvCJi8l83h4pa9PSVm6zP0K5Lgpc6jNSgb_MMPoKp=Dty2KChSDQWHM-9_taSMvugZBuVvTRO7LEr=I70uca6Qo927gxyoXiqAN8_hG6=lg4b5oeiNSZ-Lhk-0n85auwT4=AbBSmmXQX_5pBe2tm-rfnPPtdavrSL-0uvZ5ND_jPHl=pxn6AqbhV2oZT7I3ZA4rk=wmOBx9JHd33AL8qeyYZ0_vbX0i=qGpG2wtsAK_Zpk6=z4-6PMM9Y9BXDum5CqST-uiEjd8yD=RaI-ZMhB9SLNud1Tyl-rqqzMQBqqxmgoMwyBbL1BRrNc_H_SI7IgsodxjdeTOS-nt-PqK3Bi6gp_AphErdjCJhVlMt4GAL8I=qUNHCfDKgcdawTK7CTprxazmY6hLv5OJfyAhUArf7zEEW0U=0zfk5TrgzfP-KnP4LOMT9P_L8K7lRbbWH2YGlil93YKKaP0ESM0KoTHkfa7wQvN7Lw4x0Qq5Ncplupr-3S_Z3muydxlj1Z9-eaolkmCHdBsv
Content-Length: 185
Origin: https://www.bet365.es
Connection: keep-alive
Cookie: [cookie]
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-site
        """
        text_headers = """
        Host: members.bet365.es
User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0
Accept: */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Referer: https://www.bet365.es/
Content-type: application/x-www-form-urlencoded
PIRXTcSdwp-f: A0GE18V-AQAAyy0aVb3Fw4BfWMASZMqdBSmFaFKEXti4kHUSvEtuskmJ9wL1AVR8mu2cuC2nwH8AADQwAAAAAA==
PIRXTcSdwp-b: -wzzzvi
PIRXTcSdwp-c: AMAhycV-AQAABq2UCoc4S-7OZHRxrjdV02pwe1-yNzAXwViSSp5MeLuDae0X
PIRXTcSdwp-d: ABaChIjBDKGNgUGAQZIQhISi0eIApJmBDgCeTHi7g2ntF______56fBkAIxxgzPDYWk2CXaLBNT-h1w
PIRXTcSdwp-z: q
PIRXTcSdwp-a: h3sbxPaaaUwX7TQmq4VXFJyZiUmqPfZkKhr_lzjB6nuyW=-saxugR5eg1iTk49cd0WJXp=F3ozBu4MC5aPAXD41V8i4h8U6HGN6Z0uCv_jhVFgugM6pwjgAwzjAZFRI=seGlOR=3UpcRf=h6DBjS5_XI5k5Aj9UstihJfp9A5ZXV96D0G0FNtQPT1SAjlnFk58Pqa13A1Kx1k0_Tf9Jj9o9o3=OFoPS2ll2bjj5FT9Owta6QcTkV2CUgvRaxuJ1SX6JHpzTsJoIyaEuz4d4Z18hTPOkUDNHFb=Ix0iGjjVLusEcR-86KihrT3963nIPNN4dBUNiUvVvDb5AXhWXecq33JjpUjQ4zLsJlH4z4bSRArU81G94woCNOPzczQ6igJ8kUREdXqARQrlmnGywVkC3yDpdeLDme7OrCHDZ5CULQordT=5EUh-IdKE=v7ddo5hWLT=ogDz3-pawml5a3WlrN0MP0QzIPJxNGbnuvfqsjfMAG12G-1l6dnV61PUVc08IO3FqZh-ixx-xbxCOhTUq-wzizZS91zgRl8t_sjhHtT7nSPfPd9-2W0auHSseMM8K9_NfK9f2=abMZsg=yEwQbDI0xfkWc-ZfvGy6xKv670aShkZt4lHWxVj9u4swMJvl8lcFmzML=ue4Pv75HZV3luVD8JN3F0R3obDFWpljMLmBNG60d4iJkXzkM7J_grcJkFojgu=xOZaVzxIKDMaTKsRTTvnhaLSMMphWEJup162OJxfg6XoHBtSuzIoT8cPg6yMCEEKGjRr51DJFOMVOeRsLO4PTHdcmec7TIAf9pDNjeU4gUJ2e33iczs2MbmNj7TlEcmzwluPbwHlT-I4DvHUzszQqC3m4L97vDeBRGw1rq3T4jF_WWaLWKTwgI=bIaOOJ=EFZRx85fHHru91DTOq6-ZW67lBBZ_Wb-vVpzdbHLdCuowxOvo2SzfMk9rvlIAEgxiUiIkqIsFNAyD0hGx1=rRmBe8vXuoExuGZkAwt8vi1bfJjqJ2TdtHKkkRrTTraO0t_AfN6korHee_sSFWFSQfq01R1tLeKBNkpfaSf-MGn224_VBRZs2aUZA1rEImZREjrRrP0Xe6=UkO14s0IchaRf7wbGtXEsbB_9vuxBgCEI9ipJowQfkHi3_C_QuXHVbCsicjzkXzIwUw6MLpKjV8mIfl6kh-Khmf-_ZWJE7q-=yeH7mvqVLIb-b0HxrMMOwxV3G_fZEluxwQHPo2dZ=gjOkwyB3Z68To5HB4D9ba-qMSrdshPl5fjQ7S_a_2u1E1oIXLIal4wnkg8wrhGRHZFgBNL_z56K6IM_3oFlBfg_Jyjw0CVGV3HdHeS5l0i7JS4Xr3zPasFIpbh3hwB5Xl7r2tT5Ghi1VQ9sa9eB-GMqiAcbb3UgNWrq6MVj_VngtRO0J7G2jhJZni290BoH9p_A4IkFHkl7N0PEsyzVtOjkrvfQPPif7GeyLxVdMz-Zy9GWmye45tP65UUrkBuawkx112maOzAT5tovxX2lEOvoemq68r5m=wT=e=TzwDhR-aOoG=wVFfFwrlOqec5o6GgdTCOOoVX_-LlvnQ02eugUq-mRAtbnd4l4ge3hT690qLlieu_bJFRX1l5PeMpd-vx2VXA1bbRDqtDgb5E8eR9Ztk_TdEdRIX=lGsSUxzV7_J8jfblSfy0PcxK2ah-UVX0MeR_1Z_2KAK707g4-DEVVPSVOr=cXtLVgq=0v97qSRKiiCmMciBy-TgRL0O_vgoX0lsGXf-yChFoFSAklQIJedFdVJcF=k1g9pC2_qzAc8H9K15r88Nc0W8sxN2qDiQTC9x9_nDKKE7GJGTy_F9AoZd2uLmK8ooe2_6apSQXhd63_4oUOmIiUpupONRLWS0twSyxyErkc--QnFerZEp=G5v7TQLFeXhwPdW6vf3Gx-OrKuorPV8CwZ3Su2pbEVTt56JfxH0rSP2KjG-DIlkra0zm7bJdAQ3py_o6VXHEb8vjwzLGkr20D-B9mSdMv3ieTgJzuhzewVR47pLKnKtKraNGw2laEbeqq1EV7U9xycijng6JKVWJCAC9r3d_RmNniv4nDKSdwHHAFr6qInErDyZdh723Hb8FCQhX95OoZ023kZcKxIMZuKvKBTU25U_FSmJ4uieK140Cpo2BbXu1CNL04IkDFzr-vG7kpsFZANfJgqhPW29fUj1raFIDOjqdSEX-D6U_==Lq3aDmKAeB2a7k_ubz1THsdh0-w8osxToBMXCoTZICdCtIytf2ZUn6An9mkSe55lDFQIukM5vR5TCa9XFGefXFyO26leGAAw363=80__IaJMUvO6CNHiNNzw1HaNa51oEUCeOgt=SXhPwL90pryxrvGct8FQm9MVebLpdVKn1PwwX1Xg3ote0AZOONUQQ=eaHLIMh0cCq6q5NnQmuBBcByESjQhegJHZHn6bNW8rwC9=MOOJTjLlbW1djIZVPuZFs7X2k0eEqgj2rgqHB0O3potnbBGwvLVKn8DbiBgCOyaZR1l-vkWascwfoq_vB8QGeXM3iLrgwE8mBszyUDEU4VP_biRasaqH0IxaVmH7kfu_pHFfOEIWFZnRUwdinAB0lZkuQmkyFPV9VIe2pC_gTC1fNxSmCfQkgXrxNJwGdRXPg9mwibWPrdlU52raKGwlxl=5PwNScFe4fEMs=0nhXZ-3rRvLkt61wBB1qDwf9ucSz8p2=qcuHJQQ9hEO3DFvJbHuH31l-z35pxWZ2C0aI89MG7ozPRPxcHm31OQSfa054xh1O49Jo287qpQ=XPyjcxqUwJZJR5PabddM5B6afNjOkCV3kqRRxQUe_fm5uZNTqcjl8oWqhqCXu5_--vcGBFouQgRBNiX-25IsSiZdImGs2OcUeSdzNit=Dq6V1ye9JMerASy3dePwDjC_cqdf0D6daZbaDnHzpz81kuvH1urS7I0irZNhApBaUhA1VLXTKuwccCErv3DwqJVNX3O=jTgWap=4io_X0_X9eG3TAn3iU1wOE5ke3IVK6UTbMjI5MjgPttLua_0n5KHkZbR2O4OwggtRXBDe_6-T4uZnp=TUuzGq8nRLTiWTdOv_kpm_K9CSznPDcQMKLjTJV2VSrQS3w1Im==kFlSPx7zT=LfAtV_=otxEIZlNZC6GpvcKKi1kRUD_MaEcTnD7vFi1Mlx9CL5=Eqoj7yzsl7XHAre72_xI3Sq6B50jEN8TMh=l-Gd0Dj=ASqRauqpuwA-4JfDAmA=P1HZM7p2vqkU=Mqhr3-UKwuA_Gi6uR88LrgJHg1mLDbd_HKUe_ba040senzmm_qlH6fanfXS=uSGVnWIKaTShx4SNAJ-FK-pn_FEGH0lt6uleGaJHofGuj3p7TNyUoErp0P=zKlcO4kUksPazoLz30HxOS1OGNNwQf8hBkJpXuIM5kWoyUeTEWTdEU4UtSWw-ysf_6RrTk58sC9otdrEdwv9GCKCH9eIKhrPI8uLvEQXWC0ycOzqqbLwZkolMt15QcpVc-ojZjNqot1E-S2Mxkly7UXTQ3rost-TSxku8vZCHqNf6u2RlMtBEyE849y22cbk6_4h6Zi5CgcMqTP79bK=pHQbG2Jr1ky7xOtCyj6sqJLlqHBdVVWMCriiug3A9UF6EHVcyq_zBdE5g2iq2GGw8dBKZx-LoFFQjAAnoEAlCfSB9gQ4ksv1Jo3-CDxZPuuqy-AVXLvr0RvpDUeBARzD2KwWVf2S9Mrs=6RfWH1VOCr0ckiDPEG-lZmGt7hMnhIsTl1I_JnxuOyV1OkV1TWiCSJVPwTZITrPy1Gac1UHDS44jVNclSGq7X1A_7gw_ht-63bBPxB0iFfrQktBMk4FcWeWOZ92nD3tSNchq6_zz1K730p7W0IauhzKg
Content-Length: 185
Origin: https://www.bet365.es
Connection: keep-alive
Cookie: pstk=3F53814876B24C2B87BC3F9B48B66524000003; aps03=lng=1&tzi=4&ct=171&cst=0&cg=4; aaat=di=ae360759-83d8-427f-9f8d-94320753c76e&am=0&at=1658787a-adf7-424a-b4cf-7dcca313b238&ts=03-02-2022 14:20:40&v=2; usdi=uqid=D4DC5BDB-FF56-4DB9-B783-2F1319841BE1; __cf_bm=uSbm1CM.S222k_oytnTuf4xWkKLRG7lNA_LfPZoIFaI-1643996737-0-AY7KErIhQl7XAU8QxM/3J2hIynQ6HUnpAYeAURSPXkA4fy1jUe5m2UCSpt+283Y91kQlPRkjwhkvPhntFbt4aMHpmw43D4PJkxP22xJtMYmGvzAOx1pgwsw5BCHgFnmtD9qfZmmTsBpxQxbo7uO8wORd8+x9G/ta69xjbZgKjJSo
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-site
        """
        post_data = "txtType=85&txtTKN=82F7AD393B36409A82FFB4C43A327618000003&txtLCNOVR=ES&platform=1&IS=11&txtUsername=Diagraphics&txtPassword=55hBajAG4&AuthenticationMethod=0&txtScreenSize=1525%20x%20752"

    t = 1
    if t:
        url = "https://www.bet365.es/BetsWebAPI/addbet"
        text_headers = """
Host: www.bet365.es
User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0
Accept: */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Referer: https://www.bet365.es/
Content-type: application/x-www-form-urlencoded
X-Net-Sync-Term: ljwCYg==.K/iV1DaSXN7h3dIh4Pfgfob6eEwY5jfb9BGF6rN1ZK8=
PIRXTcSdwp-f: A9xcltN-AQAAdX-NlN1xHd0dBeQcZMHS9wgn6_4tOC-LmKEY1bgcAWr-DjGcAVR8mu2cuC2nwH8AADQwAAAAAA==
PIRXTcSdwp-b: -xgx1q
PIRXTcSdwp-c: AMDBhNN-AQAArANy1831ctkIbMXoQVFx4EBLnrqHYPL2aMZ8r60ehB6yNRgw
PIRXTcSdwp-d: ABaChIjBDKGNgUGAQZIQhISi0eIApJmBDgCtHoQesjUYMP_____56fBkAOTYMNHAxTbMwIB21cDNRm8
PIRXTcSdwp-z: q
PIRXTcSdwp-a: OEVNCFNJyAKv9TBe_9ghw=S8G6Fd53TffkGc5wpAtP-bRYoHPJSwwOaxuA=N82cBBlz8FyswwNHSzXBxnQByEVP0pNYJCWf020YtVPVPstjuVi2pGuUAFEjMCxYYj5Q=gyOB-fO2VuD0N8mdalVktpi0a8y-liDJPLbDjLgkzVBh_REQhXZPp=V9hpQhOZWUZBnVTVPOT89eHiLsnLJ5bGLuYgQYDm8wDqqeuM7eFgzqfvJheL6SnD=MKG3bwJk7wf2lsa6NzqP2hj-76x3V5mlfY5R8Mrjrx5YEVCCIDVUBulNXuI5ID9eOdte5gl5CQ4=OlVzslFK4-UN6NuzEZpXCsdHd6Yy4D5KFWXz8cwrrBxc0_bkzxr5tEZ_zwFWZ34i7eW_l8BDkUwLiJu6VDkvtjYzTMx6Td2dtvGnORfphGoM7Onp8jG9GhumdBsPijcqR29wZ8yAQzrWXsxwMR8guWFHoxA9=WYuznFgtlIYRf0vWJF-Ldek94OdCKZzWhTGsh_n25Woso=o5gL7GI4m45vmKp_egzaaGkAxxfRZQ8JlzeFoqBWTh436n69Rrv5ZYAp=pTf_ZZBQFUioFn6IecO05V=m-ncL0WoxVld2n9a-JaSUNBI4fexDhqkX8TEUJivWDB3KB6Jid834QAKoyNY8f-lOagNHbTbvJJGbEi5UsuwAHWkH38v4Fr7suQQqrhLUiVntYV_Tr=XnSKmY4TM=qasMOM=-ExOG6Pyf6k3X6qfWOhiR8Y=CFHkoLNUv2zN6d7dSD6jNmx7_7p5_PkiYuhAy_7eJ3FOlCZH6XY-DKTm96EISukyUs9Hl0O63dBt-Dji0Uj3oXOKY=DNksK7I92s=hwkMspZTMUfiGTft_JoCCmMTTn=XJkmjdkAJHhbSysC6f4JI6T78QIrSF_6JVXNlKJx5VdhCDW0NtbHTRO-oBah78nChaZRhxjYabJFhwSqKIQ-AsupRstfj0f-OuqOrpRp7sck9-r9DbwBFd7RLbKUNEz2wC26UP47QV4dNs-x4Tl_9eByFl7fhRMqcSyZkrnvu6wfLosAuoLjMxpkOz8nt6FtcoYwJK2OZ0qXfan-bldxyWjbtdM84T=deNlDRZflY-Ls_iD6Npi2tXrRnqvpFYFnjaPJ6yq8I5Z6RbM-OYpWDshFWCMWGQuYg3lLhNjPqTAyPl-qVHvrlKwXoCsUlag8C=8bHU3qGGwo-QvnczTUNc4QwCXU0M8=M_itUKjQBReBxBo9Cq2hxzks9Vp0HKljvYgiCc46fyFjIT2IFc4KU-e4skutNIzEhvlfaZiHsYkUWLYs5zxlJgX8JXrPx-rhrEt3UPx=s=ioU99=offOqGX6S7VX=f99J_ihE7K0le6Lu7HaWOomDmY96LgMcsvDAXh-ZiY8zlgvBsFO=xtkWxxsVyUh6o_ywZxGMoJquw8__yJkPzJiVpe9LdGs8jVl9Yc0ElVPaD8Y7LnukCQ92-uXJ==hooCE3pXNztK4V5CsT7_6xlN32=CYuZs2l0GZJ6J-lzXuI8LSY0s3lhv6PuOnoZ0OHBprmmGiX3CqdvSVrc5O4h-TkUcuK9RUkoBVCcdKzJYlOoFzVtxHjVZlkegON-g9MiMkcL-WU7g9JvWy6nCpNNV6BKPxCdZ3IcrHMr9Z2TR=vafXYYkzPUILF66jkuZtBc=BZTQgv7xEVfhieeU4nQjiPcY9pm8v7AktRwxNJ097NYsyM4fAOV699zkxp-=9bFlDc0lg2pXe3mopj9=5lStdioaFrNJVLRFbI8h5W0qoMQLTWzgQeGI-=J0cRaVzC2dA9IoFJ=r5o5r9cspJ4dbIIqWw97_JPmPmTx5DrO8_kUqmePvSB6963kAUg5UZWafB4Wty4NKKmZM6hNM6zE20iO_2TIRsJetNwP22_7oqcZWiR=waS-Ik5x6LHt9qCYzyK6nd0-KAdnaT4=XCG-=dcvDxPqv9giGXLQ0mr_WiHEyj8Tl7IQF8Yr67L_0oycq5aCtLJ-eW2HqGXSaXqfgXtbXt=g7mH6Gnj-tqzTFVGgZwIzjhbBZFDEf7bsC_QF8o7MwBEFjX3jWQh0SR8We6sDlvwryEYWuuyJpmlV4rjWTT4FB0sa5Mf-F0QgJGXm7g8S7h8I=v=Gjl8F5ZG4Hf7n8e5=y0=IdDnKpUVZ-SxO9UGI5=jmH3rFc-AljsjEISVvDjy6s3ZBHqMp7skKKgDX7R-2j7fFrYSIvEexflIQl0VqAeAhnX3Y3bN06MhA53PyYJ6TTftVnSwJrMcyIu0aBinzHu6Xlhv5wFTkCPA6SB-x-JV_bnWIGI8q78sHnCa9W7HXiz0vlXM2R2jvIF7UiPtlfKHVcsjiChwLTp368qcJvQMQFytZu7Om58pRiqR6hkvfEetuPaS9rnRs8eqaEHaPHTKOeQjlboYpcpT7=X=0Jm48PD_bVlp=0sHpY4xSOCg2=hH0ynM-SMcNxb3eshUEnZv9V7WyGtK7dT9B=7TRSpXHRbWqkgFVgDof7UfGE-CosN95CHgrIjqcQTk2MpVGR8bhk8yitjLzemoNpkJBBsqkNNXPyeoTAI4ERSt7nxhwndE9ufl2XDXe_eqwD_5KucyF48KSIgzEhLpgE5-oA9Ss34yTyGNkTkjswIio75mMl8QGBEnQrQe6hy06RE4VZlw0DrZ_q6EH9LI8oVbdyYTgOh2u3DC9SkfzoZuFDHmyyjIh4_nDPUeehsWHEoSD9avBycfL7H24EATSM8vcPt97hUXka8vQOGFEANEnCzILSL08Y4nFEvpCqIk6E0EkCedyLfpi9P0nAY_knBy63oiHHW8RjfNClvs4YTsoB5eC5upPMjQoHdhwbOhPqJJmfr0wlUejcfhuJ3yu_3oQYC-SErAQLvFKYeLtWiA5LGQ2AlstWP-ezso6deY-dDmH-wVdYGr0K=OR6m9MnKQ4933cRGuwbaa=E5Mtro7TWinohxZzf=ZfpHu_9l_u9UMXV3yAzg-Leyy5lkqhxZz3PWMkv-vs2UWqOid-9Nd0D4WDrTbsJalviqxjt0jf0H4BcQw_FFcL7sxuYa93xENviFaOTMf3mLLD94J0E=Pem2tQowFYRl-M4fLewhmYosAfc2nQb7yfX=H-74zy5A8o3rQJRU-oIPd5GPUkcQuHRlY-j2bbNndFwG5jTXmEAVvGacC6InwO9ccY0GlT_ZpDS2alvL0is2AG4FwNm39hLdHjH8wi7cgPlnrXNmElbtCAtGcEH3crcYm5sZZxar2XYxPWEVsV2khjVXsEoVAi_7n=kaWM39jINHgIqTr-Fps77Ou5ADtoeQyOFrgaK_SFW3V2X58Mh4LjW7tIROUZKeqqFX=sIpBsm2CzCtss4u2hfHuBHySQacC02-=ItoSvHxlc8RV9Hb9vk=ze=EAy2kbEB3gEDgb3dct2GcOuw-SXOZMBHFeTI2PqMUKr7F-dEmjrvIW80ICj8aeFWS8N2ea-SrU4UMcOrrtPjO=Z6i2rR9I9MZ6bUa4ARbkA3MaQdCqHUDHRmBsnNbHWKUq2=xY37ZKr895wGVmM3CxlIKm8iwLB2d0XIm2bwW_aZsvX8-nnvOhoDs7MgAJuH7E_v_Qw0auxqkilJhK4v=6aXXlfxt5Oqh8S0_pZLnRF5=c5O7GWaJFJpXNap4l9C5QaWo46Z93z6VRsUf-KXxxCFgfRZ=OgkqhIj5n4I2UiusArWDbAB0ZUn4e0D3syM2plZkJFJsiU9mqiL=eBbFJjbrXUEQ=NrWfbzDN
Content-Length: 187
Origin: https://www.bet365.es
Connection: keep-alive
Cookie: rmbs=3; aaat=di=8c75bf77-618c-4a85-9441-a070495e31b9&am=0&at=f5744cb4-6595-4057-8fba-123dc67a6787&ts=06-02-2022 18:04:58&v=2; pstk=394DB265EB2F4AD8BB050044A0636CB0000003; aps03=ao=1&cf=E&cg=4&cst=0&ct=171&hd=Y&lng=1&oty=2&tt=2&tzi=4; __cf_bm=mFMOgM6VW.ChAspUpkG1Ft1Ot1qi779jgS2cOa6lFb0-1644226920-0-AR2BXEQy4DfTZq3Xf7K6Kth8Zphjp52YmcAw1EYMATXHblYEcf4Eb1wbQCSy/vqJzAD7XEitYa0Zs8fomo+4RgBKXLsDTNfmpXny/dzhnOxentp2krPs8OmwcFmcN9BCkFxET2UcF4BjULlmDvUO9XYSYCAFVNRhf0cGv3+MBLfy
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin
                                    """
        post_data = """&ns=pt%3DN%23o%3D5%2F1%23f%3D113826266%23fp%3D512463236%23so%3D%23c%3D1%23mt%3D16%23id%3D113826266-512463236Y%23%7CTP%3DBS113826266-512463236%23%7C%7C&betsource=FlashInPLay&bs=1&qb=1&cr=1"""

    if not cookie:
        cookie = "pstk=CE51140EC5F4DDF6B0AB69FCFCB59866000003; aps03=lng=1&tzi=4&ct=171&cst=0&cg=4; aaat=di=45b0d8bb-f457-4316-9299-6796404712d6&am=0&at=2259874e-74db-4b40-bb93-20c4b9daf391&ts=03-02-2022 11:53:39&v=2; usdi=uqid=D4DC5BDB-FF56-4DB9-B783-2F1319841BE1; session=processform=0; __cf_bm=caKPqPfoSfKmx3lStwg1_pJPbPE11OsxZaFwZuleT0c-1643897487-0-AZ2qszjbAkt2w3o3EvU7HC+F0XPx/dq/eiYds5VPJgWTLF8oGn9cZC9s9EPTeo5wrsZKW6Gir7zV5MUHnrH5Tn+0WX3B5Ph7RD25RJhrBr+jFUSGWauhD58kYOUvxBnVMs8oEl1jmFkwW2MPzVvv/r0fX0Lk8/oNy9FLQ/38QBTL"
        logger.warning(f"empty cookie, so use {cookie=}")
        # wait_for_ok()

    text_headers = text_headers.replace("bet365.es", "bet365.com")
    url = url.replace("bet365.es", "bet365.com")
    url = url.replace("bet365.es", "bet365.com")

    text_headers = text_headers.replace("[cookie]", cookie)
    text_headers = get_bet365url_in_domain(text_headers, domain)
    url = get_bet365url_in_domain(url, domain)
    url_main = get_bet365url_in_domain("https://www.bet365.com/", domain)

    headers = parse_headers_from_text(text_headers)
    logger.debug(f"headers: {pretty_dict(headers)}")

    if want_fix_session_useragent:
        logger.warning(f"fix session headers to {headers['User-Agent']}")
        session.headers["User-Agent"] = headers["User-Agent"]

    if want_get_before_post:
        logger.warning(f"want_get_before_post:")
        r_response = request_with_requests(
            session=session,
            debug=True,
            url=url_main,
            headers={"Cookie": headers["Cookie"]},
        )
        logger.debug(f"get finished, {r_response=}")
        wait_for_ok()

    kwargs = {
        "url": url,
        "headers": headers,
    }

    # wait_for_ok(session)
    if post_data:
        kwargs["data"] = post_data
    r_response = request_with_requests(session=session, debug=True, **kwargs)
    response = r_response["response"]
    explore_cookies(response.cookies, "response cookies")

    want_add_cookies_to_session = False
    want_add_cookies_to_session = True
    if want_add_cookies_to_session:
        cookie = headers["Cookie"]
        cookie_dict = parse_cookieString_to_dict(cookie)
        logger.warning(f"add cookies: {pretty_dict(cookie_dict)}")
        session.cookies.clear()
        session.cookies.update(cookie_dict)
        explore_cookies(response.cookies)

    logger.debug(f"+{fun}]")
    return r_response


if __name__ == "__main__":
    special = "login_and_get_balance"

    if not special:
        logger.critical(f"empty {special=}")
        os._exit(0)

    elif special == "login_and_get_balance":
        func = bet365_login
        func = bet365_login_live

        login = "login"
        password = "password"
        proxy = "juai4w:o37xhd@77.232.40.27:53596"
        proxy = ""

        login_id = "107"
        login_id = "111"
        login_id = "103"
        login_id = "109"
        login_id = "ihor"
        login_id = "78"
        login_id = "113"
        login_id = "100"
        login_id = "77"  # для логина, порезанный
        login_id = "112"  # порезка

        domain = "com"

        t = 1
        if t:
            domain = "es"
            login_id = "118"  # spain

        proxy, login, password = get_proxy_login_password_for_bet365(
            special=login_id
        )
        logger.info(f"will login {login}:{password} {proxy=}")

        kwargs = {
            "login": login,
            "password": password,
            "proxy": proxy,
            "want_cache": False,
            "domain": domain,
        }
        t = 1
        if t:
            _ = {
                "want_cache": True,
                "want_save_cache": True,
                "want_check_cached_pstk": True,
            }
            kwargs.update(_)

        r_login = func(**kwargs)

        error = None
        if not r_login:
            logger.error(f"empty {r_login=}")

        elif not is_api_error(r_login):
            f_cookie = r"s:\!kyxa\!code\!documentation\py4seo\advanced\08\dor_minimum\universal_bookmaker\api_bet365\temp\cookie_headers.txt"

            cookie = r_login["cookie"]
            cookie_line = f"{cookie=}"
            text_to_file(cookie_line, f_cookie)
        else:
            error = get_api_error(r_login)
            logger.error(f"{error=}")

        logger.info(f"tried to login {login_id=} {login=} {r_login=}")

        if not error:
            pstk = r_login.get("pstk")
            t = 0
            if t:
                pstk = "8343E964F5EDCCAEB340C0ECE227107F000004"  # 100
                pstk = "CE74C113521D437A81211E123D3EA46B000004"  # 77

            action = "get_balance_with_pstk"
            action = "check_max_logins_with_pstk"
            action = "get_last_action_time"
            action = "keep_pstk_alive"
            action = "nah"

            if action == "get_balance_with_pstk":
                balance = get_balance_with_pstk(
                    pstk, info=r_login, domain=domain
                )
                logger.info(f"{balance=}")

            elif action == "keep_pstk_alive":
                keep_pstk_alive(pstk=pstk)

            elif action == "set_last_action_time":
                r_login = None
                result = set_last_action_time(pstk, info=r_login)
                logger.info(f"set_last_action_time {result=}")

    else:
        logger.critical(f"unknown {special=}")
