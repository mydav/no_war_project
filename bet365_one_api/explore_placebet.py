if 1:
    import http.client

    http.client.HTTPConnection.debuglevel = 5

from modules import *
from collections import OrderedDict
from bet365_one_api.bet365_session import *
from my_requests import get_requests_to_replay_from_har
from my_requests.parsers.parse_composer import *
from pirxt_server.model import KyxaPirxtServer, GeorgePirxtServer

logger = get_logger(__name__)

if __name__ == "__main__":
    pirxt_server = KyxaPirxtServer()

    domain = "es"
    special = "copy_har"
    special = "composer_replayer"
    special = "addbet_with_pirxts"

    kwargs = {
        "want_cache": False,
        "session_from": "requests",
        "want_check_bet365_access": False,
        "domain": domain,
    }
    t = 1
    if t:
        _ = {
            "want_cache": True,
            "session_from": "cloudscraper",
            # "want_check_bet365_access": True,
        }
        kwargs.update(_)

    session = get_bet365_session(**kwargs)
    session.headers = OrderedDict(session.headers)
    logger.info(
        f"{session=}, headers {type(session.headers)} {pretty_dict(session.headers, 'session.headers')}"
    )
    # wait_for_ok()

    if special == "copy_har":
        f = r"s:\!kyxa\!code\!documentation\py4seo\advanced\08\dor_minimum\bet365_one_api\data\www.bet365.es_refreshslip.har"

        searching = {
            "url": [
                # "BetsWebAPI/refreshslip",
                "/BetsWebAPI/addbet",
            ],
        }
        all_to_replay = get_requests_to_replay_from_har(f, searching=searching)
        to_replay = all_to_replay[-1]
        logger.debug(f"{to_replay=}")
        logger.debug(f"Cookie: {to_replay['headers']['Cookie']}")

        want_equal_user_agent = True
        if want_equal_user_agent:
            session.my_user_agent = to_replay["headers"]["User-Agent"]
            session.headers["User-Agent"] = session.my_user_agent

            logger.warning(
                f"want_equal_user_agent as in the saved sess {session.my_user_agent}"
            )

        want_delete_bad_headers = True
        want_delete_bad_headers = False
        if want_delete_bad_headers:
            keys_to_delete = ["Host", "Content-Length"]
            logger.warning(f"deleting from headers {keys_to_delete}")
            for k in keys_to_delete:
                del to_replay["headers"][k]

        want_identical_headers = False
        want_identical_headers = True
        if want_identical_headers:
            logger.warning(f"want_identical_headers ")
            replay_headers = to_replay["headers"]
            logger.debug(f"{pretty_dict(replay_headers, 'replay headers')}")
            keys_to_copy = replay_headers.keys()

            t = 0
            if t:
                keys_to_copy = [
                    # "Host",
                    "Connection",
                    # "Content-Length",
                    "sec-ch-ua",
                    "PIRXTcSdwp-b",
                    "PIRXTcSdwp-a",
                    "PIRXTcSdwp-d",
                    "sec-ch-ua-mobile",
                    "X-Net-Sync-Term",
                    "User-Agent",
                    "PIRXTcSdwp-f",
                    "Content-type",
                    "PIRXTcSdwp-z",
                    "PIRXTcSdwp-c",
                    "sec-ch-ua-platform",
                    "Accept",
                    "Origin",
                    "Sec-Fetch-Site",
                    "Sec-Fetch-Mode",
                    "Sec-Fetch-Dest",
                    "Referer",
                    "Accept-Encoding",
                    "Accept-Language",
                    "Cookie",
                ]
            headers = OrderedDict()
            logger.debug(f"keys headers: {keys_to_copy=}")
            for key in keys_to_copy:
                headers[key] = replay_headers[key]

            t = 0
            if t:
                headers = OrderedDict(
                    [
                        ("Host", "bet365.es"),
                        ("Content-Length", "338"),
                        ("Connection", "close"),
                        ("Upgrade-Insecure-Requests", "1"),
                        ("User-Agent", "SomeAgent"),
                        (
                            "Accept",
                            "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,/;q=0.8",
                        ),
                        ("Accept-Encoding", "gzip, deflate"),
                        ("Accept-Language", "Some Language"),
                    ]
                )

            logger.debug(f"{pretty_dict(headers, 'new headers')}")
            # new_headers =
            old_session_headers = session.headers
            session.headers = headers

            to_replay["headers"] = {}

        step = 0
        t_start = time.time()
        while True:
            step += 1
            r = request_with_requests(session, **to_replay)
            duration = time.time() - t_start
            logger.info(
                f"{step }, {get_human_duration(duration)} from start, final {r=}"
            )

            json = r.get("json", {})
            bg = json.get("bg")
            if not bg:
                inform_critical("no bg")

            sleep_(30 * 1)

    elif special == "composer_replayer":
        t_start = time.time()
        replayer = ComposerReplayer()
        logger.info(f"{replayer=}")

        t = 0
        if t:
            f = r"s:\!kyxa\!code\!documentation\py4seo\advanced\08\dor_minimum\bet365_one_api\data\composer_demo_request.txt"
            f = r"s:\!kyxa\!code\!documentation\py4seo\advanced\08\dor_minimum\bet365_one_api\data\spain_login\login_request.txt"
            text = text_from_file(f)
            replaying = replayer.prepare_request(text)
            # replaying.headers["Content-Length"] = "1" # питон обновит

            t = 0  # и с этими логинится?
            if t:
                update_headers(replaying.headers, "empty_pirxt")

            logger.debug(f"will replay: {replaying.details}")

            kwargs = {
                "session": session,
                "replaying": replaying,
            }
            r = request_with_requests_html(**kwargs)
            logger.info(f"final {r=}")

        t = 1
        if t:
            logger.debug(
                f"{explore_cookies(session.cookies, 'response cookies:')}"
            )
            logger.debug(
                f"headers before replay: {pretty_dict(session.headers)}"
            )

        t = 1
        if t:
            seconds_sleep_after_request = 30
            seconds_sleep_after_request = 10
            files_to_replay = [
                r"s:\!kyxa\!code\!documentation\py4seo\advanced\08\dor_minimum\bet365_one_api\data\spain_login\request_step_1.txt",  # в ответ должно быть только header: Set-Cookie: Affiliates=Code=365_084461%2f124294512928&prd=Sports; domain=.bet365.es; expires=Thu, 07-Apr-2022 14:46:06 GMT; path=/; secure ; SameSite=None
                r"s:\!kyxa\!code\!documentation\py4seo\advanced\08\dor_minimum\bet365_one_api\data\spain_login\request_sessionactivity.txt",
                r"s:\!kyxa\!code\!documentation\py4seo\advanced\08\dor_minimum\bet365_one_api\data\spain_login\request_userpreference.txt",
                r"s:\!kyxa\!code\!documentation\py4seo\advanced\08\dor_minimum\bet365_one_api\data\spain_login\request_api#blob.txt",
                r"s:\!kyxa\!code\!documentation\py4seo\advanced\08\dor_minimum\bet365_one_api\data\spain_login\request_api#blob2.txt",
                # r"s:\!kyxa\!code\!documentation\py4seo\advanced\08\dor_minimum\bet365_one_api\data\spain_login\request_addbet.txt",
                r"s:\!kyxa\!code\!documentation\py4seo\advanced\08\dor_minimum\bet365_one_api\data\spain_login\request_addbet#2.txt",
                r"s:\!kyxa\!code\!documentation\py4seo\advanced\08\dor_minimum\bet365_one_api\data\spain_login\request_refreshslip.txt",
            ]
            files_to_replay = [
                # r"s:\!kyxa\!code\!documentation\py4seo\advanced\08\dor_minimum\bet365_one_api\data\spain_login\request_addbet#3.txt",
                r"s:\!kyxa\!code\!documentation\py4seo\advanced\08\dor_minimum\bet365_one_api\data\spain_login\request_refreshslip.txt",
            ] * 1000
            for num_f, f in enumerate(files_to_replay, 1):
                text = text_from_file(f)
                replaying = replayer.prepare_request(text)
                logger.debug2(
                    f"replay {num_f}/{len(files_to_replay)} files, {f=} {replaying=}"
                )

                want_fresh_cookie = True
                if want_fresh_cookie and num_f > 1:
                    cookie = update_cookieString(
                        replaying.headers["Cookie"],
                        session.cookies,
                        skipping=["aps03"],
                    )
                    logger.debug(f'old Cookie: {replaying.headers["Cookie"]}')
                    logger.debug(f"new Cookie: {cookie}")
                    replaying.headers["Cookie"] = cookie

                logger.warning(
                    f"run next step {num_f}/{len(files_to_replay)}?"
                )
                # wait_for_ok()

                kwargs = {
                    "session": session,
                    "replaying": replaying,
                    "debug": True,
                }

                cnt_to_repeat = 10000
                cnt_to_repeat = 1
                t_start_repeat = time.time()
                step_repeat = 0
                while True:
                    step_repeat += 1
                    if step_repeat > cnt_to_repeat:
                        logger.debug(
                            f"  {step_repeat=} reached {cnt_to_repeat=}, so break"
                        )
                        break

                    r = request_with_requests(**kwargs)

                    duration_repeat = time.time() - t_start_repeat
                    duration_total = time.time() - t_start
                    logger.info(
                        f"{num_f}/{len(files_to_replay)} {step_repeat=}/{cnt_to_repeat} {get_human_duration(duration_repeat)}/{get_human_duration(duration_total)} final {r=}"
                    )

                    t = 1
                    if t:
                        answer_json = r["json"]
                        bg = answer_json.get("bg")
                        if not bg:
                            inform_critical("no bg")
                    sleep_(seconds_sleep_after_request)

    elif special == "addbet_with_pirxts":
        t_start = time.time()
        replayer = ComposerReplayer()
        logger.info(f"{replayer=}")

        t = 1
        if t:
            logger.debug(
                f"{explore_cookies(session.cookies, 'response cookies:')}"
            )
            logger.debug(
                f"headers before replay: {pretty_dict(session.headers)}"
            )

        t = 1
        if t:
            seconds_sleep_after_request = 30
            seconds_sleep_after_request = 10
            files_to_replay = [
                r"s:\!kyxa\!code\!documentation\py4seo\advanced\08\dor_minimum\bet365_one_api\data\spain_login\request_addbet#4.txt"
            ] * 1000

            for num_f, f in enumerate(files_to_replay, 1):
                text = text_from_file(f)
                replaying = replayer.prepare_request(text)
                logger.debug2(
                    f"replay {num_f}/{len(files_to_replay)} files, {f=} {replaying=}"
                )

                want_fresh_cookie = True
                if want_fresh_cookie and num_f > 1:
                    cookie = update_cookieString(
                        replaying.headers["Cookie"],
                        session.cookies,
                        skipping=["aps03"],
                    )
                    logger.debug(f'old Cookie: {replaying.headers["Cookie"]}')
                    logger.debug(f"new Cookie: {cookie}")
                    replaying.headers["Cookie"] = cookie

                want_fresh_pirxts = True
                if want_fresh_pirxts:
                    pirxts = pirxt_server.get_pirxt_headers_as_dict()
                    replaying.headers.update(pirxts)
                    logger.debug(f"use fresh {pirxts=}")

                logger.debug(
                    f"{pretty_dict(replaying.headers, 'replaying headers')}"
                )

                logger.warning(
                    f"run next step {num_f}/{len(files_to_replay)}?"
                )

                wait_for_ok()

                kwargs = {
                    "session": session,
                    "replaying": replaying,
                    "debug": True,
                }

                cnt_to_repeat = 10000
                cnt_to_repeat = 1
                t_start_repeat = time.time()
                step_repeat = 0
                while True:
                    step_repeat += 1
                    if step_repeat > cnt_to_repeat:
                        logger.debug(
                            f"  {step_repeat=} reached {cnt_to_repeat=}, so break"
                        )
                        break

                    r = request_with_requests(**kwargs)

                    duration_repeat = time.time() - t_start_repeat
                    duration_total = time.time() - t_start
                    logger.info(
                        f"{num_f}/{len(files_to_replay)} {step_repeat=}/{cnt_to_repeat} {get_human_duration(duration_repeat)}/{get_human_duration(duration_total)} final {r=}"
                    )

                    t = 1
                    if t:
                        answer_json = r["json"]
                        bg = answer_json.get("bg")
                        if not bg:
                            inform_critical("no bg")
                    sleep_(seconds_sleep_after_request)
    else:
        logger.critical(f"unknown {special=}")
