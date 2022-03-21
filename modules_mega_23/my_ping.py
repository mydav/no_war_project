#!/usr/bin/python
# -*- coding: utf-8 -*-

import socket
import requests
import time

# from modules.my_forms import pycus_u
# from modules.file_save_open import obj_from_json
from modules import *
from modules.logging_functions import *

logger = get_logger(__name__)


def change_proxy_ip(
    url=None,
    proxy=None,
    max_steps=30,
    minimum_speed=0.5,
    mode_check=None,
    want_dinamic_minimum_speed=True,
):
    """
    сменить ип прокси!
    причем так, чтобы скорость была не менее minimum_speed
    
    проверить, и сменить только если скорость медленная
    mode_check='change_only_if_low_speed'):
    want_dinamic_minimum_speed - динамическая скорость, после каждой проверки повышаем на 5%
        очень часто скорость крутится близко минимальной, но не совсем
    """
    fun = "change_proxy_ip"
    if mode_check is None:
        mode_check = "all"
    logger.debug(f"[{fun} {mode_check=} {minimum_speed=}")

    min_proxy = proxy.replace("https://", "")
    if min_proxy in ["no"]:
        logger.debug("no proxy, so do not change nothing")
        return {
            "status": "no_proxy",
            "details": "no proxy, so do not change nothing",
        }

    if not url:
        url = min_proxy + "/api/changeIP?apiToken=40d137c72d0b8a4e"
        logger.debug(f"url from proxy = {url}")

    if not url:
        m = "no url to change proxy"
        logger.critical(m)
        inform_critical(m)

    if not url.startswith("http"):
        url = f"http://{url}"

    logger.debug(f"url to change ip={url}")

    _ = {
        "url": url,
    }
    history = []
    step = 0
    cnt_bad_codes = 0
    status = ""
    ip = ""
    t_start = time.time()
    while True:
        step += 1
        if (step - cnt_bad_codes) > max_steps:
            m = f"can not change proxy ip (step {step})"
            logger.critical(m)
            inform_critical(m)

        duration = time.time() - t_start

        if want_dinamic_minimum_speed:
            # minimum_speed_dinamic = minimum_speed * (1.05)**(step-1)
            minimum_speed_dinamic = min(
                minimum_speed * 1.5, minimum_speed + (0.1) * (step - 1)
            )
        else:
            minimum_speed_dinamic = minimum_speed
        logger.debug2(
            f"{step=} {minimum_speed=} from start {duration} seconds ({cnt_bad_codes=}, {history })"
        )

        if step == 1 and mode_check == "change_only_if_low_speed":
            logger.debug("check speed before changing")
            r_speed = is_proxy_quick(
                proxy, minimum_speed=minimum_speed_dinamic
            )

            if not is_api_error(r_speed):
                status = "already_quick"
                logger.debug("proxy is quick, so good")
                break

        # по настоящему запрос на смену прокси
        r = pycus_u(_)
        code = r["code"]
        html = r["html"]
        answer = obj_from_json(html)

        logger.debug("     step %s, answer=%s from r=%s" % (step, answer, r))

        if code != 200:
            logger.error("code=%s, so retry" % code)
            cnt_bad_codes += 1
            sleep_(10)
            history.append("bad_code")
            continue

        ip = answer.get("IP")
        logger.debug("new proxy ip=%s" % ip)
        if not ip:
            logger.error("ip not changed, retry")
            history.append("ip_not_changed")
            continue

        r_speed = is_proxy_quick(proxy, minimum_speed=minimum_speed_dinamic)
        if is_api_error(r_speed):
            logger.debug(
                "step %s - proxy changed but the speed is LOW, so will change ip again"
                % step
            )
            sleep_(31)
            history.append("low_speed")
            continue

        status = "changed_proxy_to_quick"
        break

    duration = time.time() - t_start
    # logger.debug('r_speed=%s' % r_speed)
    speed = r_speed["details"]
    proxy_speed = speed["maximum"]
    details = {
        "duration": int(duration),
        "step": step,
        "speed": speed,
    }
    return {
        "status": status,
        "ip": ip,
        "proxy_speed": proxy_speed,
        "details": details,
    }


def is_proxy_quick(proxy, minimum_speed=0.5):
    """проверка что прокси - быстрый"""
    r_ping = ping_proxy_for_bet365(proxy=proxy)
    maximum = r_ping["maximum"]
    error = ""
    if maximum > minimum_speed:
        logger.warning(
            "proxy speed too low=%s>%s=minimum_speed    /%s"
            % (maximum, minimum_speed, r_ping)
        )
        error = "low_speed"
    return {"error": error, "details": r_ping}


def ping_proxy_for_bet365(*args, **kwargs):
    """тест именно бетки"""
    kwargs["url"] = "http://bet365.com"
    return ping_proxy(*args, **kwargs)


def ping_proxy(
    url="http://bet365.com", proxy="", cnt_checks=3, calc_stats_from=1, bad_duration = 10000
):
    """
    stats_from - откуда считать (например первый пропускаю)
    :param url: 
    :param proxy: 
    :param cnt_checks: 
    :param stats_from: 
    :return: 
    """
    fun = "ping_proxy"
    proxy0 = proxy

    domain = url.split("/")[-1]

    if proxy and "/" in proxy:
        proxy = proxy.split("/")[-1]  # если ввел https://proxy:port
        logger.debug("new proxy %s from %s" % (proxy, proxy0))

    proxy_user = ""
    proxy_password = ""
    proxy_without_login_password = proxy
    if proxy and "@" in proxy:
        proxy_user_password, proxy_without_login_password = proxy.split("@")
        proxy_user, proxy_password = proxy_user_password.split(":")

    logger.debug2(
        "proxy=%s, cnt_checks=%s for url=%s" % (proxy, cnt_checks, url)
    )

    commands = []
    t = 1
    if t:
        """
        --proxy-user x           имя пользователя для прокси
                                 аутентификации
        --proxy-password x       пароль для прокси аутентифик�

         *** HTTP аутентификация ***
            -A   / --basic-auth      активировать ("basic") аутентифи�
                                     �ацию
            -U x / --username        имя пользователя для аутенти�
                                     �икации
            -P x / --password        пароль для аутентификации

        -f - флуд, без задержек
        -l - ssl (для https урлов)
        """
        tpl = "httping -f -c [cnt_checks] --proxy-user [proxy_user]  --proxy-password [proxy_password] -x [proxy_without_login_password] -g [url]"
        commands.append(tpl)

    t = 1
    if t:
        tpl = """'ping -c [cnt_checks] [domain]    # can't resolve, no proxy set

    export http_proxy=[proxy]
    ping -c [cnt_checks] [domain]"""
        commands.append(tpl)

        tpl = """env http_proxy=[proxy] ping -c [cnt_checks] [domain]"""
        commands.append(tpl)

    command = "\n\n".join(commands)
    command = (
        command.replace("[cnt_checks]", str(cnt_checks))
        .replace("[proxy]", str(proxy))
        .replace("[url]", url)
        .replace("[domain]", domain)
        .replace("[proxy_user]", proxy_user)
        .replace("[proxy_password]", proxy_password)
        .replace(
            "[proxy_without_login_password]", str(proxy_without_login_password)
        )
    )

    t = 0
    if t:
        logger.debug(
            "\n".join(
                [
                    "TERMINAL COMMANDS: " + "<" * 10,
                    "\n",
                    command,
                    "\n",
                    "-" * 10,
                    "\n" * 2,
                ]
            )
        )

    durations = []

    for num_check in range(1, cnt_checks + 1):
        t_start = time.time()
        proxies = {
            "http": "http://%s" % proxy,
            "https": "http://%s" % proxy,
        }
        _kwargs = {
            "timeout": (10, 10),
        }

        if proxy:
            _kwargs["proxies"] = proxies

        error = ""
        try:
            response = requests.head(url, verify=True, **_kwargs)
        except Exception as er:
            error = str(er)
            logger.error(error)

        duration = time.time() - t_start


        if error:
            duration = bad_duration
        else:
            seconds_send_received = response.elapsed.total_seconds()
            seconds_diff = duration - seconds_send_received
            response_headers = response.headers

            #  headers={'Connection': 'keep-alive', 'Content-Length': '0', 'Location': 'http://websafe.virginmedia.com/childsafe-blocked.html', 'Date': 'Sat, 19 Feb 2022 18:12:40 GMT'} - плохие
            if 'Location' in response_headers:
                logger.warning(f"Location in headers, so proxy is bad")
                duration = bad_duration

            logger.debug(
                f"check {num_check}/{cnt_checks} ({seconds_send_received:.3f}, diff={seconds_diff:.3f}) seconds, headers={response_headers}"
            )
        durations.append(duration)

    # for duration in durations:
    #     print('%.3f seconds' % duration)
    logger.debug("durations=%s" % durations)

    # floats_full = [round(_, 3) for _ in durations if isinstance(_, float)]
    floats_full = [round(_, 3) for _ in durations]
    floats = floats_full[calc_stats_from:]
    average = None
    minimum = None
    maximum = None
    if floats:
        logger.debug("  floats=%s, calc stats" % floats)
        average = round(sum(floats) / len(floats), 3)
        minimum = min(floats)
        maximum = max(floats)

    r = {
        "durations": floats,
        "durations_full": floats_full,
        # 'floats': floats,
        "average": average,
        "minimum": minimum,
        "maximum": maximum,
    }
    cnt_errors = len(durations) - len(floats)
    if cnt_errors:
        r["error"] = "%s errors" % cnt_errors
    logger.debug2("   +%s %s]" % (fun, r))

    return r


def internet(host="8.8.8.8", port=443, timeout=1):
    """
    проверка интернета
        host_ip = socket.gethostbyname('www.google.com')
        port = 80
    """
    t_start = time.time()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)  # correction from s.timeout(timeout)
        s.connect((host, port))
        s.shutdown(socket.SHUT_RDWR)
        s.close()
        duration = round(time.time() - t_start, 4)
        logger.debug("+internet in %.3f seconds" % duration)
        return duration

    except OSError:
        s.close()
        return False


if __name__ == "__main__":
    url = "http://bet365.com"

    t = 1
    t = 0
    if t:
        url = "https://bet365.com"
        url = "http://bet365.es"
        url = "https://www.bet365.es/"
        url = "https://www.bet365.com/"  # прокси хуана только так умеет
        url = "http://8.8.8.8:443"  # google dns

    proxy = (
        "node-ru-110.astroproxy.com:10573"  # astroproxy 050 Sky Broadband 0.5
    )
    proxy = "node-ru-131.astroproxy.com:10811"  # astroproxy 073 vodafone 0.5
    proxy = "2.tcp.eu.ngrok.io:11258"  # juan 0.2
    proxy = (
        "http://node-uk-4.astroproxy.com:10381"  # 078 - 0.2??? 176.26.233.238
    )
    proxy = "juai4w:o37xhd@77.232.40.27:53596"  # proxym.net 0.4
    proxy = "http://78.157.219.234:10363"
    proxy = None  # 0.1
    proxy = "http://ihorilnitskiy4937:6ae58f@node-ru-227.astroproxy.com:10129"
    proxy = "http://109.248.7.187:10573"
    proxy = "https://node-uk-4.astroproxy.com:10365"  #  105
    proxy = "http://78.157.219.234:10381"  #  84
    proxy = "http://51.89.191.226:10061"  #  108
    proxy = "https://node-uk-4.astroproxy.com:10381"
    proxy = "https://node-uk-3.astroproxy.com:10283"  # 77_2
    proxy = "http://juai4w:o37xhd@185.244.181.187:41765"  #  proxym koni_live
    proxy = "http://78.157.219.235:10367"  #  104
    proxy = "http://193.23.50.210:10751"  #  110
    proxy = "http://78.157.219.235:10373"  #  103
    proxy = "node-gb-2.astroproxy.com:10163"  # 98
    proxy = "http://78.157.219.231:10381"  #  107
    proxy = "node-ru-256.astroproxy.com:10615"  # astroproxy 109
    proxy = "77.232.38.120:8353"  # proxyM zapas 2 - вообще не быстрый???
    proxy = ""
    proxy = "EURO250678:t91YK1ex@185.217.198.50:6250"
    proxy = "https://node-uk-3.astroproxy.com:10009"  #  106
    proxy = "node-gb-3.astroproxy.com:10555"  # 116
    proxy = "node-ru-131.astroproxy.com:10811"  #  111
    proxy = "node-uk-3.astroproxy.com:10381"  # 78
    proxy = "node-uk-2.astroproxy.com:10381"  # 100
    proxy = "node-uk-3.astroproxy.com:10009"

    special = "internet"
    special = "ping_proxy"
    special = "change_proxy_ip"
    special = "is_proxy_quick"

    logger.info(f"{special=}")

    if special == "is_proxy_quick":
        r = is_proxy_quick(proxy)
        logger.info("r=%s" % r)

    elif special == "ping_proxy":
        _kwargs = {
            "url": url,
            "proxy": proxy,
        }
        r = ping_proxy(**_kwargs)
        print(r)

    elif special == "internet":
        durations = []
        for i in range(10):
            duration = internet()
            durations.append(duration)
        print(durations)

    elif special == "change_proxy_ip":
        url = None
        # url = 'node-ru-258.astroproxy.com:10607/api/changeIP?apiToken=40d137c72d0b8a4e'
        # proxy = 'node-ru-258.astroproxy.com:10607'
        # r = change_proxy_ip(url=url, proxy=proxy)
        kwargs = {
            "proxy": proxy,
            # 'mode_check': 'change_only_if_low_speed',
        }
        r = change_proxy_ip(**kwargs)
        logger.info("r=%s" % r)
        inform_me_one("found")
        # wait_for_ok()

    else:
        logger.error("unknown special=%s" % special)
