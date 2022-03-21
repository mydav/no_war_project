#!/usr/bin/python
# -*- coding: utf-8 -*-

from modules_23.minimum_important_functions import *
from my_requests.url_helpers import *
import requests

import time
from random import shuffle
from random import choice as random_choice
from six.moves.urllib.parse import quote
from my_requests.parsers.headers_helpers import *

logger = get_logger(__name__)


def pycus_u(t, debug=False):
    fun = "pycus_u"
    # debug = True

    if debug:
        logger.debug("[%s %s" % (fun, t))
    sys.stdout.flush()

    t_start = time.time()

    t = hitro_dict(t, "u")
    # show_dict(t)
    # wait_for_ok()

    u_download = t.get("u", False)
    if u_download == False:
        u_download = t.get("url", False)
    if u_download == False:
        if debug:
            logger.debug("pycus_u: no url")
        return {}
    post = t.get("post", False)

    d = {
        #        'u'
        "timeout": 15,
        "connect_timeout": 15,
        "post": False,
        "limit": 2,
        "headers": {"User-Agent": get_useragent(),},
        "headers_only": -1,  # send only! this headers!
        "otl": True,
        # tor
        "want_tor": 1,
        "tor": -1,
        "tor_change_polube": False,
        "sleep_bad_code": 0,  # если плохой код - сколько ждать? Например свои сайты досить нехорошо
        # 'sposob':'pycus',    #хочу ли я реквестами работать?    requests
        "sposob": "requests",
        "session": None,
        "requests_keep_alive": False,
        "proxies": None,
        "proxy": "",
        "proxy_type": "",
        "f": "",  # сохранять в файл?
        "verbose": 0,  # выводить инфу?
        "special": "",  # get_session == возврат сессии
    }
    t = add_defaults(t, d)
    T = Bunch(t)

    if isinstance(T.headers, str):
        T.headers = parse_headers_from_text(T.headers)

    if T.otl:
        logger.debug("[pycus_u %s %s" % (T.sposob, u_download))

    if 0 and u_download.find("api.pinnaclesports.com") != -1:
        show_dict(t)

    # edit cyrrilic domain
    domen = get_domen_from_url(u_download)
    domen_idn = domen_to_idna(domen)
    # logger.debug('domen %s, domen_idn %s' % (domen, domen_idn))
    if domen != domen_idn:
        u_download = u_download.replace(domen, domen_idn)
        logger.debug("cyrrilic domain, change url to %s" % u_download)

    if type(T.post) == type({"x": 1}):
        for k in T.post:
            v = T.post[k]
            v = str(v)
            T.post[k] = v

    rez = {}
    error = ""
    i = 0
    while True:
        i += 1
        default_answer = {
            "kod": "",
            "html": "",
            "location": "",
            "url": "",
            "headers": {},
            "g": "",
            "error": error,
            "raw_request": None,
        }

        if i > T.limit:
            rez = add_defaults(rez, default_answer)
            logger.debug("limit (max cnt_tries %s) reached, exit" % T.limit)
            break

        if T.sposob == "requests":
            # инофрмация о requests            http://www.pythonforbeginners.com/requests/using-requests-in-python
            # http://docs.python-requests.org/en/latest/user/advanced/
            # http://stackoverflow.com/questions/13137817/how-to-download-image-using-requests - тут как именно картинку сохранить
            # logger.debug('session=%s' % T.session)
            if T.session:
                ses = T.session

            else:
                ses = requests.session()

                if not T.requests_keep_alive:
                    ses.keep_alive = False

                # ses.stream = True
                ses.timeout = (T.connect_timeout, T.timeout)
                # ses.timeout = 0.00000001
                # logger.debug('ses.timeout=%s' % str(ses.timeout))

                proxies = None
                if T.proxies is not None:
                    proxies = T.proxies

                elif T.proxy != "":
                    if T.proxy_type.find("socks") != -1 or 1:
                        proxy = "%s://%s" % (T.proxy_type, T.proxy)
                        proxies = {
                            "http": proxy,
                            "https": proxy,
                            # "http"  : self.http_proxy,
                            # "https" : self.https_proxy,
                            # "ftp"   : self.ftp_proxy
                        }

                if proxies:
                    if 0 and T.otl:
                        logger.debug("setup proxies: %s", proxies)
                    ses.proxies = proxies

                try:
                    if T.headers_only != -1:
                        ses.headers = T.headers
                    else:
                        ses.headers.update(T.headers)
                except Exception as er:
                    logger.error("error %s" % er)

            if T.special == "get_session":
                # print 'special %s, so return %s' % (T.special, ses)
                return ses

            # print 'u_download=%s' % u_download
            want_try = 0
            want_try = 1
            if want_try:
                try:
                    if T.post != False:
                        r = ses.post(
                            u_download, data=T.post, timeout=ses.timeout
                        )
                    else:
                        r = ses.get(u_download, timeout=ses.timeout)
                except Exception as er:
                    logger.error("error %s: %s" % (fun, er))
                    error = str(er)
                    continue
            else:
                if T.post != False:
                    r = ses.post(u_download, data=T.post)
                else:
                    r = ses.get(u_download)

            kod = r.status_code
            url = r.url

            headers = r.headers
            enc = headers.get("Content-Encoding", "")

            t = 1
            t = 0
            if t:
                page = r.text

                page = page
                if type(page) == type("unicode"):
                    page = page.encode("utf8", "ignore")
            else:
                page = r.content
                # if enc=='gzip':#сам делает?
                #    page = ungzip(page)
                # logger.debug('type: %s' % type(page))

            page = bytes_to_str(page)
            m = "%s %s" % (type(page), page)
            logger.debug(m)
            # wait_for_ok(m)

            # if type(page) == type("unicode"):
            #     page = page.encode("utf8", "ignore")

            location = headers.get("Location", False)
            if location != False:
                location = url_abs(u_download, location)

            raw_request = get_prepared_request(r, t_start=t_start)

            rez = {
                "kod": kod,
                "html": page,
                "location": location,
                "url": url,
                "headers": headers,
                "g": ses,
                "raw_request": raw_request,
            }

        elif T.sposob == "pycus":

            g = t.get("g", 0)
            if g == 0:
                g = Pycus()

            if T.verbose:
                # g.setup(pycurl.VERBOSE,1)
                g.curl.setopt(pycurl.VERBOSE, 1)
            # try:
            #    g = T.g
            #    logger.debug('already_have_g')
            # except Exception, er:
            #    g = Pycus()
            # do_tor(g, user)

            # if T.otl:
            #    logger.debug('g=%s' % g)

            if T.tor != -1 and T.want_tor:
                logger.debug("tor%s" % T.tor)
                do_tor(g, t)
                tor_change_ip_potok(t, polube=T.tor_change_polube)
            else:
                pass
            #            wait_for_ok('no tor?')

            if T.headers_only != -1:
                g.setup(headers_only=T.headers_only)
            else:
                g.setup(headers=T.headers)

            if T.proxy != "":
                g.setup(proxy=T.proxy, proxy_type=T.proxy_type)

            g.setup(connect_timeout=T.connect_timeout, timeout=T.timeout)
            if T.post != False:
                # looger.debug('post query "%s"' % T.post)
                # wait_for_ok()
                # logger.debug('u=%s' % u_download)

                g.setup(url=u_download, post=T.post)
            else:
                g.setup(url=u_download)

            g.request()

            headers = g.res.headers

            url = g.res.url

            location = headers.get("Location", False)
            if location != False:
                location = url_abs(u_download, location)

            enc = headers.get("Content-Encoding", "")

            if enc == "gzip":
                page = g.body
                page = ungzip(page)
            else:
                page = g.body

            # logger.debug('page: %s' % page)

            kod = g.res.code

            rez = {
                "kod": kod,
                "html": page,
                "location": location,
                "url": url,
                "headers": headers,
                "g": g,
            }

        rez = add_defaults(rez, default_answer)
        if kod == 200:
            break
        else:
            sleep = T.sleep_bad_code
            logger.debug("-bad_code_sleep%s" % sleep)
            time.sleep(sleep)

    error_short = ""
    if error:
        if "Failed to establish a new connection" in error:
            error_short = "connection_error"  # SOCKSHTTPSConnectionPool(host='api.pinnacle.com', port=443): Max retries exceeded with url: /v2/bets/straight (Caused by NewConnectionError('<urllib3.contrib.socks.SOCKSHTTPSConnection object at 0x00000000048F8F08>: Failed to establish a new connection: [Errno 10065] A socket operation was attempted to an unreachable host',))
    rez["error_short"] = error_short

    rez["code"] = rez["kod"]

    duration = round(time.time() - t_start, 3)
    rez["duration"] = duration

    if T.otl:
        logger.debug("  +code `%s` in %s seconds]" % (rez["code"], duration))
    if T.f != "":
        text_to_file(rez["html"], T.f)

    # wait_for_ok('final rez: %s' % rez)

    return rez


def print_response_info(r):
    print("response info:")
    print(
        r.url,
        len(r.content),
        r.elapsed,
        r.elapsed.total_seconds(),
        "history=",
        r.history,
        "\n",
        [(l.status_code, l.url) for l in r.history],
        # str(r.headers.items()), str(r.cookies.items()),
    )


def get_useragent():
    """возвращаем случайный юзерагент"""
    user_agents = """
Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 2.0.50727; .NET CLR 3.0.04506.30)
Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; ru) Opera 8.50
Opera/9.21 (Windows NT 5.1; U; ru)
Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.1)
Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; MRA 4.8 (build 01709); .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.04506.30; InfoPath.1)
Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; .NET CLR 1.1.4322)
Mozilla/5.0 (Windows; U; Windows NT 5.1; ru; rv:1.8.0.7) Gecko/20060909 Firefox/1.5.0.7
Mozilla/5.0 (Macintosh; U; PPC Mac OS X; ru-ru) AppleWebKit/419.3 (KHTML, like Gecko) Safari/419.3
Mozilla/5.0 (Windows; U; Windows NT 5.1; ru; rv:1.8.1.2) Gecko/20070219 Firefox/2.0.0.2
Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; MRA 4.10 (build 01952); MRSPUTNIK 1, 8, 0, 17 SW)
Mozilla/5.0 (Windows; U; Win98; ru; rv:1.8.1.7) Gecko/20070914 Firefox/2.0.0.7
Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506; InfoPath.2)
Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; MRA 4.9 (build 01863); .NET CLR 2.0.50727; .NET CLR 3.0.04506.30)
Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; Maxthon; InfoPath.2)
Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; PKVS; .NET CLR 1.1.4322; InfoPath.2)
Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser; InfoPath.1)
Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 2.0.50727)
Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; .NET CLR 1.1.4322)
Mozilla/4.0 (compatible; MSIE 5.00; Windows 98)
Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; MRA 4.9 (build 01863); InfoPath.1; .NET CLR 2.0.50727; .NET CLR 3.0.04506.30)
Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; .NET CLR 1.0.3705; InfoPath.1; .NET CLR 2.0.50727; .NET CLR 3.0.04506.30)
Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.04506.30; InfoPath.2)
Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 2.0.50727; InfoPath.2)
Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)
Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; MyIE2; .NET CLR 1.1.4322; .NET CLR 2.0.50727)
Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; MyIE2; .NET CLR 2.0.50727)
Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)
Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)
Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)
Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.8.1) Gecko/20061010 Firefox/2.0
Mozilla/4.0 (compatible; MSIE 5.01; Windows NT 5.0)
Mozilla/5.0 (Windows; U; Windows NT 5.1; ru; rv:1.8.1.7) Gecko/20070914 Firefox/2.0.0.7
Mozilla/5.0 (Windows; U; Windows NT 5.1; rv:1.7.3) Gecko/20041001 Firefox/0.10.1
Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)
Opera/9.23 (Windows NT 5.1; U; ru)
Mozilla/4.0 (compatible; MSIE 6.0b; Windows NT 5.0; .NET CLR 1.0.2914);"""

    return random_choice(clear_list(user_agents))


def get_prepared_request(res, t_start=None, request_error=None):
    """
    At this point it is completely built and ready
    to be fired; it is "prepared".

    However pay attention at the formatting used in
    this function because it is programmed to be pretty
    printed and may differ from the actual request.

    https://stackoverflow.com/questions/20658572/python-requests-print-entire-http-request-raw
    """
    header = "___________REQUEST___________"
    delimiter = "___________RESPONSE___________"
    delimiter_content = "___________response_content___________"

    prepared = get_prepared_request_from_response(res)

    if 1 and res in [None, {}]:
        res_status_code = ""
        res_reason = ""
        res_url = ""
        res_headers = "wrong_response"
        res_text = ""
    else:
        res_status_code = res.status_code
        res_headers = format_headers(res.headers)
        res_reason = res.reason
        res_url = res.url
        res_text = res.text

    error_info = ""
    if request_error:
        error_info = f"\nERROR={request_error}"

    duration = ""
    if t_start:
        duration = "%.3f" % round(time.time() - t_start, 3)
    if duration:
        duration = "in %s seconds: " % duration

    got = f"{duration} {res_status_code} {res_reason} {res_url}\n{res_headers}{error_info}\n\n{delimiter_content}\n{res_text}"
    # got = got.encode("utf8")  # был unicode - нужно только для питон2

    t = 1
    t = 0
    if t:
        logger.debug("got: %s %s" % (type(got), got))  # unicode
        lst = [header, prepared, delimiter, got]
        for num, _ in enumerate(lst, 1):
            logger.debug("%s %s %s" % (num, type(_), _))

    prepared = "%s\n%s\n\n%s\n%s" % (header, prepared, delimiter, got)
    return prepared


def get_prepared_request_from_response(res):
    if 1 and res in [None, {}]:
        prepared = "wrong_request"
    else:
        req = res.request

        headers = format_headers(req.headers)

        post = ""
        if req.body is not None:
            post = req.body
        # print 'post %s' % post
        prepared = f"{req.method} {req.url}\n{headers}\n\n{post}"
        prepared = prepared.strip()
    return prepared


def get_urls_to_check_ip():
    ## vvazhlyv0
    urls = []
    return urls


def quote_plus(txt):
    try:
        r = urllib.parse.quote_plus(txt)
    except Exception as er:
        r = urllib.quote_plus(txt)
    return r


def quote_plus(text="", safe=""):
    r = urllib.parse.quote_plus(text, safe=safe)
    return r


def urldecode(url):
    rex = re.compile("%([0-9a-hA-H][0-9a-hA-H])", re.M)
    return rex.sub(htc, url)


def htc(m):
    return chr(int(m.group(1), 16))


def url_fix(url, safe="%/:=&?~#+!$,;'@()*[]"):
    """url in 1251        урл перед скачкой экранировать"""
    return quote(text_to_charset(url, "utf8", "cp1251"), safe=safe)


if __name__ == "__main__":
    # from modules import *
    # from modules import *

    special = "get_useragent"
    special = "get_prepared_request"
    special = "pycus_u"
    special = "small"
    special = "parse_headers_from_and_make_request"
    special = "func_format_headers"

    if special == "small":
        logger.info(url_fix("dsfladsjfрвадво"))

    elif special == "pycus_u":
        _ = {"u": "http://zhurnal.net/tools/test_proxy_min.php?spec=NoProx"}
        r = pycus_u(_)
        html = r["html"]
        logger.info("r=%s" % r)
        logger.debug("hello" in html)

    elif special == "get_useragent":
        for i in range(10):
            print(get_useragent())

    elif special == "parse_headers_from_and_make_request":
        text = """
    User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64; rv:56.0) Gecko/20100101 Firefox/56.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
    Accept-Language: en-US,en;q=0.5
    Accept-Encoding: gzip, deflate
    Cookie: sesid=dncs0t-odxdk*y_rgkfp-u0mcnbq0vbw-t^vaxemivhucnbn_t*vfqbn_t*vfqbn; _ym_visorc_27984774=w
    Connection: keep-alive
    Upgrade-Insecure-Requests: 1
    Cache-Control: max-age=0
            """

        headers = parse_headers_from_text(text)
        show_dict(headers)

        u_edit = "https://www.blogger.com/blog/post/edit/2889894091199548735/6390454267405903445?hl=ru"
        u_edit = "https://google.com"
        u_edit = "https://www.bukvarix.com/keywords/?q=%D0%BA%D0%B0%D0%BA%20%D0%B1%D0%B5%D0%BD%D0%B4"
        u_edit = "https://www.google.com/search?q=beauty&ie=utf-8&oe=utf-8&client=firefox-b-ab"
        f = "temp/last_pycus_u.html"
        _ = {
            "u": u_edit,
            "headers": headers,
            "f": f,
        }

        want_proxy = random_choice([True, False])
        want_proxy = False
        want_proxy = True

        print("want_proxy=%s" % want_proxy)

        if want_proxy:
            proxies = clear_list(
                """
    178.162.202.44:2242
    117.69.231.253:30002
    125.123.70.53:42888
    62.122.213.164:8080
    115.213.63.43:1080
    125.123.66.144:40015
    125.123.66.3:32989
    117.92.116.98:3000
    """.replace(
                    "\t", ":"
                )
            )

            f_proxies = r"s:\!kyxa\!code\!documentation\py4seo\advanced\08\dor_minimum\data\!proxies\fineproxy.org.txt"
            proxies = clear_list(text_from_file(f_proxies))
            shuffle(proxies)

            proxies = [_ for _ in proxies if not _.startswith("#")]

            proxy_type = "socks5"
            proxy_type = "http"

            want_fixed_proxy = True
            want_fixed_proxy = False
            fixed_proxy = "167.71.149.119:3128"

            if want_fixed_proxy:
                proxy = fixed_proxy
                print("fixed_proxy=%s" % fixed_proxy)
            else:
                random_proxy = random_choice(proxies)
                proxy = random_proxy
                print("random_proxy=%s" % random_proxy)

            proxy_with_type = "%s://%s" % (proxy_type, proxy)
            _proxy = {
                #   proxies=dict(http='socks5://user:pass@host:port',
                "proxies": dict(http=proxy_with_type, https=proxy_with_type),
                # 'proxy_type': 'http',
                # 'proxy': proxy,
                # 'proxy': random_proxy,
                # 'proxy': 'Geonathe:qTCnVFNw@79.174.13.233:24011',
            }
            print(_proxy)
        else:
            _proxy = {
                "proxy": "",
                "proxies": {},
            }
        _ = add_defaults(_proxy, _)

        r = pycus_u(_)
        # print(r)
        show_dict(r)

        html = r["html"]
        # print(html)
        text_to_file(html, "temp/test_downloader.html")

    elif special == "get_prepared_request":
        f_to = os.path.abspath("temp/get_prepared_request.txt")
        logger.debug("start")
        t_start = time.time()
        response = requests.get("https://google.com")
        answer = get_prepared_request(response, t_start=t_start)
        text_to_file(answer, f_to)
        logger.debug("check in %s" % f_to)

    else:
        logger.error("unknown special=%s" % special)
