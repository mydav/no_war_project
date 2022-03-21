#!/usr/bin/python
# -*- coding: utf-8 -*-

from modules import *
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver

from selenium_functions.selenium_funcs import *

# from [bulkadu]_helpers import *

from selenium_helpers.firefox.firefox_starter import *

from selenium_helpers.chrome.chrome_starter import *

# from selenium_helpers.selenium_recaptcha import *

# from gmail_register.youtuber import *
# from modules_google_search.download_google_with_searchuss import *
# from modules_google_search.google_search import *
# from modules_rozetka.rozetka_helpers import *

logger = get_logger("explore_selenium")

U_SEARCHUSS = "http://localhost:8081/searchuss/"
U_SEARCHUSS = ""


class FirefoxBinaryTimeouted(FirefoxBinary):
    def __init__(self, firefox_path=None, log_file=None, timeout=45):
        super(FirefoxBinaryTimeouted, self).__init__(
            firefox_path=firefox_path, log_file=log_file
        )
        self.set_timeout(timeout)
        # wait_for_ok('done with FirefoxBinaryTimeouted, timeout=%s' % self.timeout)

    def set_timeout(self, timeout=30):
        self.timeout = timeout

    def launch_browser(self, profile, timeout=None):
        """Launches the browser for the given profile name.
        It is assumed the profile already exists.
        """
        if timeout is None:
            timeout = self.timeout

        self.profile = profile

        self._start_from_profile_path(self.profile.path)
        # wait_for_ok('timeout %s' % timeout)
        self._wait_until_connectable(timeout=timeout)


def test_driver(driver):
    u_start = "http://localhost"
    driver.get(u_start)

    t = 1
    t = 0
    if t:
        logger.debug("driver_capabilities:")
        driver_capabilities = driver.capabilities
        show_dict(driver_capabilities)

    t = 1
    t = 0
    if t:
        for entry in driver.get_log("browser"):
            logger.debug(entry)

    logger.debug("driver.service.service_url: %s" % driver.service.service_url)
    logger.debug(
        "driver.command_executor._url: %s" % driver.command_executor._url
    )
    logger.debug("driver.session_id: %s" % driver.session_id)

    save_connectionInfo(driver)

    t = 1
    if t:
        wait_for_ok("quit?")
        driver.quit()


def create_driver_session(session_id, executor_url):
    # Save the original function, so we can revert our patch
    org_command_execute = RemoteWebDriver.execute

    def new_command_execute(self, command, params=None):
        if command == "newSession":
            # Mock the response
            return {"success": 0, "value": None, "sessionId": session_id}
        else:
            return org_command_execute(self, command, params)

    # Patch the function before creating the driver object
    RemoteWebDriver.execute = new_command_execute

    new_driver = webdriver.Remote(
        command_executor=executor_url, desired_capabilities={}
    )
    new_driver.session_id = session_id

    # Replace the patched function with original function
    RemoteWebDriver.execute = org_command_execute

    return new_driver


def get_firefoxProcessId_from_marionette(port=2828):
    """
        зная порт марионетте, получаем ип фаерфокса
    """
    # u'moz:processID': 11340
    from marionette_driver.marionette import Marionette

    client = Marionette(host="localhost", port=port)
    r = client.start_session()
    session_capabilities = client.session_capabilities
    processID = session_capabilities["moz:processID"]
    return processID


def test_marionette(port=2828):

    firefor_process_id = get_firefoxProcessId_from_marionette(port)
    logger.debug("firefor_process_id: %s" % firefor_process_id)
    # wait_for_ok()

    from marionette_driver.marionette import Marionette
    from marionette_driver import By

    client = Marionette(host="localhost", port=port)
    logger.debug("client: %s" % client)

    session = client.start_session()
    logger.debug("start_session: %s" % session)

    # wait_for_ok()
    # logger.debug("client.session_capabilities %s' % client.session_capabilities)
    # wait_for_ok()

    handles = client.window_handles
    logger.debug("handles: %s" % handles)

    logger.debug("window_rect: %s" % client.window_rect)

    t = 1
    if t:
        f_js = "simple.js"

        js = """
        function double(x){
            return x * 2;
        }

        window.wrappedJSObject.test1 = "foo";
        window.wrappedJSObject.test2 = "bar";
        return double(5);
        return window.wrappedJSObject.test1 + window.wrappedJSObject.test2;

        """
        js0 = "return double(5);"
        js0 = """
        let battery = window.navigator.battery;
        return battery;
        """

        # client.import_script(f_js)
        js_result = client.execute_script(js)
        logger.debug("js_result: %s" % js_result)
        # wait_for_ok()

    t = 1
    t = 0
    if t:
        # Switch to the chrome context for a minute (content is default)
        with client.using_context(client.CONTEXT_CHROME):
            urlbar = client.find_element(By.ID, "urlbar")
            logger.debug("urlbar: %s" % urlbar)
            urlbar.send_keys("about:robots")
            # try this one out yourself!
        wait_for_ok()

    # client.navigate("http://www.mozilla.org")
    client.navigate(get_random_url())

    # sleep_(5)
    url = client.get_url()
    logger.debug("url: %s" % url)

    # first_link = client.find_element(By.TAG_NAME, "a")
    first_link = client.find_element(By.XPATH, "//a//h3")
    logger.debug("first_link: %s" % first_link)

    first_link.click()


def get_random_url():
    u_random = "https://www.google.com/search?source=hp&q=[query]&oq=[query]"
    repl = {
        "[query]": random.randint(1, 1000),
    }
    u_random = no_probely(u_random, repl)
    return u_random


def click_on_random_element(S, xpath="//a//h3"):
    mode = "random"
    mode = "click_like_human"
    S.click_xpath(xpath, mode=mode)
    # elements = S.driver.find_elements_by_xpath(xpath)
    # element = shuffle(elements)
    # S.click(element)


def run_browser_crawler_for_monitoring_indexed(
    S,
    f_tasks="",
    d_to="temp",
    cnt_checks=1,
    sleep_after=60 * 30,
    max_tasks=100000000,
):
    """
    есть файл, вида
    site:https://rozetka.com.ua/gtgate/g91/
    мы хотим просто периодически эти запросы дергать
    есть много урлов. Мы хотим проверить по ним индексацию. Но мы делаем это не для всех ссылок, а например делаем 10 проверок по 20 случайных ссылок, и приблизительно понимаем процент индексации
    """
    fun = "run_browser_crawler_for_monitoring_indexed"
    if f_tasks == "":
        f_tasks = r"s:\!data\!!![bulkadu]\!queries_to_monitore_in_google.txt"

    otl = 0
    if otl:
        max_tasks = 1
        cnt_checks = 1

    seconds_sleep = 0
    seconds_sleep = 2

    gs = GoogleSearch()

    history = []

    step = 0
    stats = {}

    while True:
        analizy = []

        step += 1

        links = get_links_from_file(f_tasks)
        links = links[:max_tasks]
        # show_list(links)
        # wait_for_ok()

        cnt_tasks = len(links)
        for num_link in range(cnt_tasks):
            # взяли задачу
            tasks = []
            cnts = []

            max_cnt = 3000
            query = links[num_link]

            Show_step(
                "%s step %s %s/%s, query `%s`"
                % (fun, step, num_link, cnt_tasks, query)
            )

            # 2 вида записей:
            # site:https://rozetka.com.ua/gtgate/g91/
            # 86    3000 - это значит что раздел розетки
            parts = query.split("\t")
            logger.debug("%s parts" % len(parts))
            if len(parts) == 2:
                max_cnt = parts[1]
                query = parts[0]
                try:
                    query = int(parts[0])
                    query = "site:https://rozetka.com.ua/gtgate/g%s/" % query
                except Exception as er:
                    logger.error("ERROR: %s" % er)

            # wait_for_ok('query `%s`, max_cnt %s' % (query, max_cnt))

            query_start = query

            max_cnt = int(max_cnt)

            # query_short_name = to_hash(query)
            query_short_name = (
                filename(query, False)
                .replace("site-https-//", "")
                .replace("site-http-//", "")
            )
            d_time = time.strftime("%Y-%m-%d", time.localtime(time.time()))

            #           создали нужное количество проверок
            for num_check in range(cnt_checks):
                query_hashed = gs.add_random_hash_to_query(query)
                time_detailed = time.strftime(
                    "%H-%M-%S", time.localtime(time.time())
                )

                f_abs = "%s/!monitoring_indexed/%s/%s/%s_%s.html" % (
                    d_to,
                    query_short_name,
                    d_time,
                    time_detailed,
                    num_check,
                )
                # wait_for_ok(f_abs)
                if not file_exists(f_abs):
                    _ = {
                        "query": query_hashed,
                        "f_to": f_abs,
                        "max_cnt": max_cnt,
                    }
                    tasks.append(_)

            #           проверили
            logger.debug(
                "will check %s queries (from %s links)"
                % (len(tasks), len(links))
            )
            show_list(tasks)
            # wait_for_ok()

            num_task = 0
            for task in tasks:
                num_task += 1
                logger.debug(
                    "\n" * 2 + "%s/%s %s" % (num_task, len(tasks), task)
                )
                query = task["query"]

                if query.find("rozetka") != -1:
                    custom_search_id = "rozetka"
                    url = gs.generate_custom_search_url_from_query(
                        query, custom_search_id=custom_search_id
                    )
                else:
                    custom_search_id = "like_real_google"
                    # url = gs.generate_custom_search_url_from_query(query, custom_search_id=custom_search_id)
                    url = gs.generate_normal_search_url_from_query(
                        query, num=max_cnt
                    )
                    # wait_for_ok(url)

                if not stats.has_key(custom_search_id):
                    stats[custom_search_id] = 0
                stats[custom_search_id] += 1

                t = 1
                t = 0
                if t:
                    logger.debug("%s %s" % (custom_search_id, url))
                    wait_for_ok()

                # custom_search_id = 'like_real_google'
                # url = gs.generate_custom_search_url_from_query(query, custom_search_id=custom_search_id)

                f_to = task["f_to"]

                page = S.sgp(url, seconds_sleep=seconds_sleep)
                sleep_(0)  #     еще ждем, подольше
                page = "<base_url>%s</base_url>%s" % (url, page)
                text_to_file(page, f_to)

                cnt = gs.parse_cnt_results(page)
                cnts.append(cnt)

                t = 1
                if t:
                    logger.debug(
                        "%s %s, cnts %s" % (custom_search_id, url, cnts)
                    )
                    # wait_for_ok()

            #           проанализировали проверки
            t = 1
            if t:
                logger.debug("cnts: %s" % cnts)

                analiz = gs.analyze_cnts(
                    cnts, max_cnt=task["max_cnt"], analizy=["max"]
                )
                logger.debug("analiz=%s" % analiz)
                logger.debug("file %s finished" % f_to)

                analiz_name = query_start.replace(
                    "site:https://rozetka.com.ua/gtgate", ""
                )
                analizy.append("\t".join([analiz_name, analiz]))

            show_list(analizy)

            logger.debug("stats:")
            show_dict(stats)

        history.append(analizy)

        Show_step("history")
        show_list(history)

        Show_step("analizy")
        show_list(analizy)

        logger.info("stats:")
        show_dict(stats)

        sleep_(sleep_after)


def run_browser_crawler_for_counting_indexed_approximately(
    S,
    f_tasks="",  # файл с урлами для проверки индексации
    cnt_checks=10,
    # max_cnt=20,
    max_cnt=30,  # в запросе гугл разрешает 32 слова максимум
    d_to="temp",
    links=[],  # можно просто список ссылок дать
    special="",
    # special='just_scrap_google_queries',
    tpl_one_query="inurl",
    f_abs_tpl="[d_to]/!counting_indexed/[file_name]/[time_human_day]/[time_human_hour_minute]/[links_hash].html",
    # f_abs_tpl='[d_to]/!counting_indexed/[file_name]/[time_human_month]/[links_hash].html',
):
    """
    есть много урлов. Мы хотим проверить по ним индексацию. Но мы делаем это не для всех ссылок, а например делаем 10 проверок по 20 случайных ссылок, и приблизительно понимаем процент индексации
    """
    fun = "run_browser_crawler_for_counting_indexed_approximately"

    if special == "just_scrap_google_queries":
        max_cnt = 1
        cnt_checks = len(links)

    if cnt_checks == "all":
        cnt_checks = 100000000000000000000

    seconds_sleep = 2
    seconds_sleep = 0

    gs = GoogleSearch()
    f_name = os.path.basename(f_tasks)

    tasks = []
    if links == []:
        links = get_links_from_file(f_tasks)

    # оптимизирую количество проверок - если ссылок 5 то не нужно делать 20 проверок по 20 страниц
    pa4ki_links = split_list(links, max_cnt)

    pa4ki_links = pa4ki_links[:cnt_checks]

    time_human_month = time.strftime("%Y-%m", time.localtime(time.time()))
    time_human_day = time.strftime("%Y-%m-%d", time.localtime(time.time()))
    time_human_hour_minute = time.strftime(
        "%H-%M", time.localtime(time.time())
    )
    f_repl = {
        "[d_to]": d_to,
        "[time_human_month]": time_human_month,
        "[time_human_day]": time_human_day,
        "[time_human_hour_minute]": time_human_hour_minute,
        "[file_name]": f_name,
    }

    for links_checking in pa4ki_links:
        # query = gs.generate_searchsite_query(links_checking, max_cnt=len(links_checking))
        # show_list(links_checking)
        # wait_for_ok()
        query = gs.generate_searchsite_query(
            links_checking,
            max_cnt=len(links_checking),
            tpl_one_query=tpl_one_query,
        )
        section = ""

        # f_abs = '%s/!counting_indexed/%s/%s/%s.html' % (d_to, f_name, time_human_day, to_hash(query))
        f_repl2 = {
            "[query_hash]": to_hash(query),
            "[links_hash]": to_hash(links_checking),
        }
        f_repl = add_defaults(f_repl2, f_repl)
        f_abs = no_probely(f_abs_tpl, f_repl)
        # wait_for_ok(f_abs)

        if 0 and special == "just_scrap_google_queries":
            line = links_checking[0]
            query = find_from_to_one(",", "nahposhuk", line)
            section = find_from_to_one("nahposhuk", ",", line)
            hash = to_hash(query)
            f_abs = "%s/%s/%s.html" % (d_to, f_name, hash)
            # logger.debug('query `%s`, hash `%s`, file %s' % (query, hash, f_abs))
            # wait_for_ok()

        # wait_for_ok(f_abs)
        if not file_exists(f_abs):
            t = 0
            if t:
                logger.debug("links_checking %s" % links_checking)
                logger.debug(query)
                logger.debug(f_abs)
                wait_for_ok()

            _ = {
                "query": query,
                "section": section,
                "f_to": f_abs,
                "cnt_must_be": len(links_checking),
            }
            tasks.append(_)
        else:
            logger.debug("a")
            stats_collector_one.plus_1("already_downloaded")

    url_reload = "https://google.com"

    logger.debug(
        "will do %s queries in google (from %s links)"
        % (len(tasks), len(links))
    )

    # stats collector
    short_names = {
        "already_downloaded": "a",
        "downloaded": ".",
        "captcha": "C",
    }
    stats_collector_one = StatsCollector(
        "crawler_stats_one", short_names=short_names
    )
    stats_collector_one.total_size = len(tasks)

    cnts = []
    num_task = 0

    t0 = time.time()

    for task in tasks:
        num_task += 1
        seconds_from_start = time.time() - t0
        minutes_from_start = int(seconds_from_start / 60)
        seconds_srednee = "%.1f" % (seconds_from_start / num_task)

        logger.info(
            "\n" * 2
            + "%s/%s seconds_from_start %d, seconds_srednee %s, %s"
            % (num_task, len(tasks), seconds_from_start, seconds_srednee, task)
        )
        captcha_solver.print_stat()
        # stats_collector.print_stat()
        stats_collector_one.print_stat()

        # wait_for_ok()

        query = task["query"]
        section = task["section"]

        # url = gs.generate_custom_search_url_from_query(query, custom_search_id='random')

        if query.find("rozetka") != -1:
            custom_search_id = "rozetka"
            url = gs.generate_custom_search_url_from_query(
                query, custom_search_id=custom_search_id
            )
        else:
            custom_search_id = "like_real_google"
            # url = gs.generate_custom_search_url_from_query(query, custom_search_id=custom_search_id)
            url = gs.generate_normal_search_url_from_query(query, num=max_cnt)

        logger.debug("query=`%s`" % query)
        # logger.debug('url=`%s`' % url)
        # wait_for_ok()

        f_to = task["f_to"]

        step = 0

        _ = {
            "S": S,
        }
        captcha_solver.update_settings(_)

        t = 1
        t = 0
        if t:
            recaptcha_container = guess_recaptcha_containerPath(S.driver)
            wait_for_ok(recaptcha_container)

        while True:
            step += 1
            if S == "my_searchuss":
                limit_popitok = 1000
                mess = ""
                bot_sleep = 3

                r_page = download_googleSearchResultsPage_from_searchuss(
                    u_search=U_SEARCHUSS,
                    phrase=query,
                    language="ru",
                    num=max_cnt,
                    limit_popitok=limit_popitok,
                    mess=mess,
                    bot_sleep=bot_sleep,
                )

                if r_page["status"]:
                    page = r_page["page"]
                else:
                    wait_for_ok("todo %s" % S)
            else:
                page = S.sgp(url, seconds_sleep=seconds_sleep)
            # if page.find('Our systems have detected unusual traffic from your computer network') !=-1:
            if captcha_solver.is_page_with_captcha(page):
                stats_collector.plus_1("captcha")
                stats_collector_one.plus_1("captcha")

                logger.debug("     captcha, step %s" % (step))

                if step > 1:
                    logger.debug("captcha was bad!")
                    r = captcha_solver.mark_captcha_bad_guessed()
                    logger.debug("mark_captcha_bad_guessed: %s" % r)
                    # wait_for_ok()

                mode_guess = "debug"
                mode_guess = "real"
                if mode_guess == "real":
                    r = captcha_solver.guess_captcha_on_any_page(url, page)
                else:
                    r = True, "debug_guessed"
                logger.debug("r=%s" % r)

                # wait_for_ok(r)
                status, hacked = r

                if status == False:  # значит капчу не разгадали
                    logger.error("problem")
                    sleep_(5)

                for i in range(1):
                    r = captcha_solver.insert_guessed_recaptcha(
                        hacked, mode="old"
                    )
                    logger.debug("insert_guessed_recaptcha: %s" % r)
                    status, mess = r
                    sleep_(2)

                # sleep_(5)
                # wait_for_ok('recaptcha!')
                continue

            break

        page = "<base_url>%s</base_url><section>%s</section>%s" % (
            url,
            section,
            page,
        )
        logger.debug(f_to)
        text_to_file(page, f_to)

        if special == "just_scrap_google_queries":
            cnt = 0
        else:
            cnt = gs.parse_cnt_results(page)
        logger.debug("cnt_pages: %s" % cnt)
        stats_collector.plus_1("downloaded")
        stats_collector_one.plus_1("downloaded")

        cnts.append([cnt, task["cnt_must_be"]])

        if 0 and num_task % 10 == 0:
            S.sgp(url_reload)

    t = 1
    if t:
        logger.debug("cnts: %s" % cnts)
        analiz = gs.analyze_cnts(cnts, max_cnt, analizy=["general"])
        logger.debug("analiz %s" % analiz)
        logger.debug("file %s finished" % f_name)
    return analiz


def run_browser_crawler(S, f_tasks="", d_to="temp"):
    """
        полазим по браузеру с заданиями
    """
    items = text_from_file(f_tasks).split("\n")
    tasks = []
    for item in items:
        f, url = item.split("\t")
        f_abs = "%s/%s" % (d_to, f)
        if not file_exists(f_abs):
            _ = {
                "url": url,
                "f_to": f_abs,
            }
            tasks.append(_)

    url_reload = "https://google.com"

    logger.debug("todo %s/%s queries" % (len(tasks), len(items)))

    gs = GoogleSearch()

    num_task = 0
    for task in tasks:
        num_task += 1
        logger.debug("%s/%s %s" % (num_task, len(tasks), task))
        query = task["url"]

        t = 1
        if t:
            if query.find("rozetka") != -1:
                custom_search_id = "rozetka"
                url = gs.generate_custom_search_url_from_query(
                    query, custom_search_id=custom_search_id
                )
            else:
                custom_search_id = "like_real_google"
                # url = gs.generate_custom_search_url_from_query(query, custom_search_id=custom_search_id)
                url = gs.generate_normal_search_url_from_query(query)

        f_to = task["f_to"]

        seconds_sleep = 0
        seconds_sleep = 2
        S.sgp(url, f_to, seconds_sleep)

        if num_task % 10 == 0:
            S.sgp(url_reload)


def test_selenium_class(
    driver,
    S="",
    mode_fixed="",
    want_scrap_indexed_unindexed=0,
    want_crawl_google_fixed=None,
    cnt_checks=5,
    max_cnt=4,
    tpl_one_query="inurl",
    good_phrases_fixed=None,
):

    if S == "":
        _ = {
            "s_driver": driver,
        }
        S = wrap_selenium_class(_)

    t = 0
    t = 1
    if t:
        mode = "run_browser_crawler"
        mode = "run_browser_crawler_for_monitoring_indexed"
        mode = "run_browser_crawler_for_counting_indexed_approximately"

        f_abs_tpl = "[d_to]/!counting_indexed/[file_name]/[time_human_day]/[time_human_hour_minute]/[links_hash].html"
        # f_abs_tpl='[d_to]/!counting_indexed/[file_name]/[time_human_month]/[links_hash].html'

        # как часто проверяем?
        recheck_after = 0  # одна проверка
        recheck_after = 60 * 60 * 1  # периодически, все время

        want_shuffle_links = 1

        want_crawl_google = 0
        want_crawl_google = 1

        if want_crawl_google_fixed is not None:
            want_crawl_google = want_crawl_google_fixed

        # cnt_checks = 5
        # cnt_checks = 10
        # cnt_checks = 20
        #
        # max_cnt = 30
        # max_cnt = 3 # good
        # max_cnt = 6 # bad
        # max_cnt = 5 # bad
        # max_cnt = 4 # good
        # max_cnt = 10

        d_to_base = "s:\!data\!google.com"
        d_to = d_to_base

        special = "just_scrap_google_queries"
        special = ""

        # нужны какие-то спецдомены?
        domains_to_check_for_indexation = "new_domain_2020-04-27"
        domains_to_check_for_indexation = "new_domain_2020-04-27_online"
        domains_to_check_for_indexation = []

        want_clear_pureSpam = 1

        if domains_to_check_for_indexation == []:
            pass

        elif domains_to_check_for_indexation == "new_domain_2020-04-27":
            domains_to_check_for_indexation = clear_list(
                """
                    ancesit.ru
                    ithatted.ru
                    piciener.ru
                    exieforou.ru
                    swittled.online
                    suppoksar.online
                    shepheread.online
                    ponced.ru
                    """
            )

        elif domains_to_check_for_indexation == "new_domain_2020-04-27_online":
            domains_to_check_for_indexation = clear_list(
                """
                    swittled.online
                    suppoksar.online
                    shepheread.online
                    """
            )

        else:
            wait_for_ok(
                "ERROR: unknown domains_to_check_for_indexation %s"
                % domains_to_check_for_indexation
            )

        if special == "just_scrap_google_queries":
            d_to = (
                "%s\!downloaded_google_queries\!scraped_google_queries"
                % d_to_base
            )

        if mode == "run_browser_crawler":
            f = r"x:\modules_google_search\temp\rozetka_tasks_89.txt"
            f = r"x:\modules_google_search\temp\rozetka_tasks_89.txt"
            f = r"x:\modules_google_search\temp\rozetka_tasks_89.txt"
            f = r"x:\modules_google_search\temp\rozetka_tasks_2020-02-22 1-brands_5000 and more.txt.txt"
            run_browser_crawler(S, f_tasks=f, d_to=d_to)

        ##############смотрим на количество проиндексенных
        elif mode == "run_browser_crawler_for_counting_indexed_approximately":
            f = r"s:\!data\!!![bulkadu]\!links\[bulkadu]_tasks\060_3-301-g90 (copy ru057-301-g87-jino1).txt"
            f = r"s:\!data\!!![bulkadu]\!links\[bulkadu]_tasks\060_3-301-g90 (copy ru057-301-g86 ).txt"
            f = r"s:\!data\!!![bulkadu]\!links\[bulkadu]_tasks\060_3-301-g90 (copy ru057-301-g86 ).txt"
            f = r"s:\!data\!!![bulkadu]\!links\[bulkadu]_tasks\060_3-301-g91 (copy ru057-301-g87-jino2).txt"
            f = r"s:\!data\!!![bulkadu]\!links\[bulkadu]_tasks\060_3-301-g91 compare_hostings_with_new_domains.txt"
            f = r"s:\!data\!!![bulkadu]\!links\[bulkadu]_tasks\060-301-g89 (copy ru057-301-g87-server ).txt"
            f = r"s:\!data\!!![bulkadu]\!links\gootheme_urls90+.txt"
            f = r"s:\!data\!!![bulkadu]\!links\gootheme_urls90+.txt"
            f = r"s:\!data\!!![bulkadu]\!links\gootheme_urls91+.txt"
            f = r"s:\!data\!!![bulkadu]\!links\gootheme_urls92+.txt"
            f = r"s:\!data\!!![bulkadu]\!links\gootheme_urls89+.txt"
            f = r"s:\!data\!!![bulkadu]\!links\2020-02-21 type=alternative_producer_restrict=2_section_created_date_from=01-2-2020_section_created_date_to=21-2-2020.txt"
            f = r"s:\!data\!!![bulkadu]\!links\2020-02-22 1-brands_1-5000+.txt"
            f = r"s:\!data\!!![bulkadu]\!links\2020-02-22 1-brands_5000 and more.txt"
            f = r"s:\!data\!!!rozetka\!pereindex\2020-02-22 - g64 g65 g66 g68 g72 g73 g74 g75 g76 g77 - from12001 to14000.txt"
            f = r"s:\!data\!!![bulkadu]\!links\2020-02-23 smug.txt"
            f = r"s:\!data\!!!rozetka\!pereindex\2020-03-01 - g120 g121 g122 g123 g124 g125 g126 g127 g128 g129 g130 - from2001 to2200.txt"
            f = r"s:\!data\!!!rozetka\!pereindex\2020-03-01 - g64 g65 g66 g68 g72 g73 g74 g75 g76 g77 - from18001 to18200.txt"
            f = r"s:\!data\!!!rozetka\!pereindex\2020-02-29 - g120 g121 g122 g123 g124 g125 g126 g127 g128 g129 g130 - from1001 to2000.txt"
            f = r"s:\!data\!!!rozetka\!pereindex\2020-03-04 - g64 g65 g66 g68 g72 g73 g74 g75 g76 g77 - from18201 to18400.txt"
            f = r"s:\!data\!!!rozetka\!tempory_check_indexation\03-20.txt"
            f = r"s:\!data\!!!rozetka\!tempory_check_indexation\03-21.txt"
            f = r"s:\!data\!!!rozetka\!tempory_check_indexation\03-22.txt"

            files_txt = r"""
            #s:\!data\!!!rozetka\!tempory_check_indexation\03-20.txt
            #s:\!data\!!!rozetka\!tempory_check_indexation\03-21.txt
            #s:\!data\!!!rozetka\!tempory_check_indexation\03-22.txt
            #s:\!data\!!!rozetka\!tempory_check_indexation\03-23.txt
            #s:\!data\!!!rozetka\!tempory_check_indexation\03-25.txt
            #s:\!data\!!!rozetka\!tempory_check_indexation\03-25 22-20.txt
            #s:\!data\!!!rozetka\!tempory_check_indexation\03-26.txt
            #s:\!data\!!!rozetka\!tempory_check_indexation\site_topcasinos.online.txt


            #s:\!data\!!!rozetka\!tempory_check_indexation\04-01_full__.txt
            #s:\!data\!!!rozetka\!tempory_check_indexation\04-01_full__old_domains_with_13k_pages.txt

            #s:\!data\!!!rozetka\!tempory_check_indexation\2020-04-25.txt
            #s:\!data\!!!rozetka\!tempory_check_indexation\2020-04-25 - 2.txt

            #s:\!data\!!!rozetka\!tempory_check_indexation\2020-04-27.txt
            #s:\!data\!!!rozetka\!tempory_check_indexation\2020-04-28.txt

            #s:\!data\!!!rozetka\!tempory_check_indexation\2020-04-29__my_test_100.txt
            #s:\!data\!!!rozetka\!tempory_check_indexation\2020-04-29__my_test_100_100-200.txt
            #s:\!data\!!!rozetka\!tempory_check_indexation\2020-04-29__my_test_100_500-800.txt

            #s:\!data\!!!rozetka\!tempory_check_indexation\2020-04-29.txt

            #s:\!data\!!!rozetka\!tempory_check_indexation\2020-04-30 12-06-41__ot_100-do_800.txt

            #s:\!data\!!!rozetka\!tempory_check_indexation\2020-05-01.txt
            #s:\!data\!!!rozetka\!tempory_check_indexation\2020-05-01 add-url.info_50_old_subdomain.txt

            #s:\!data\!!!rozetka\!tempory_check_indexation\2020-05-02_rozetka.txt
            #s:\!data\!!!rozetka\!tempory_check_indexation\2020-05-02-2_rozetka.txt

            #s:\!data\!!!rozetka\!tempory_check_indexation\2020-05-02_andr_comp(check ip).txt
            #s:\!data\!!!rozetka\!tempory_check_indexation\2020-05-02_andr_comp(check fixed user).txt
            #s:\!data\!!!rozetka\!tempory_check_indexation\2020-05-05_andr_comp(check fixed user).txt
            #s:\!data\!!!rozetka\!tempory_check_indexation\2020-05-05_andr_comp(check fixed user2).txt

            #s:\!data\!!!rozetka\!tempory_check_indexation\2020-05-06_andr_comp(check fixed user_UNIVERSAL).txt

            s:\!data\!!!rozetka\!tempory_check_indexation\2020-05-06_andr_comp(check buyaccs).txt
            s:\!kyxa\!code\!google_addurl_selenium\temp\indexed_redirect.txt

            """

            d = r"s:\!kyxa\!code\!google_addurl_selenium\temp\!indexed_redirect"
            d = r"s:\!data\!!!rozetka\!tempory_check_indexation"
            files = get_all_file_names(d)

            # test_concurent_indexators
            files_txt = r"""
#s:\!data\!!!rozetka\!tempory_check_indexation\2020-05-01 add-my-url.com_50_old_subdomain.txt
#s:\!data\!!!rozetka\!tempory_check_indexation\2020-05-01 add-my-url.com_50_new_subdomain.txt
#s:\!data\!!!rozetka\!tempory_check_indexation\2020-05-01 add-url.info_50_new_subdomain.txt
#s:\!data\!!!rozetka\!tempory_check_indexation\2020-05-01 add-url.info_50_old_subdomain.txt

s:\!data\!!!rozetka\!tempory_check_indexation\2020-05-08 add-my-url.com_50_new_subdomain.txt
s:\!data\!!!rozetka\!tempory_check_indexation\2020-05-08 webMasterBot_50.txt
s:\!data\!!!rozetka\!tempory_check_indexation\2020-05-08 linkbox.pro_50.txt

"""
            files0 = clear_list(files_txt)

            if special == "just_scrap_google_queries":
                d_with_scrap_tasks = (
                    r"s:\!data\!!!rozetka\!!!scrap_google_results"
                )
                files = get_all_file_names(d_with_scrap_tasks)
                files = clear_list(
                    r"""
                    #s:\!data\!!!rozetka\!!!scrap_google_results\rozetka_odezhda_2020-03-26.txt
                    s:\!data\!!!rozetka\!!!scrap_google_results\2020-04-02_prodvizhenie_youtube.txt
                    #s:\!data\!!!rozetka\!!!scrap_google_results\2020-04-03-rozetka_sections.txt
                    """
                )

            # filter files?
            t = 0
            t = 1
            if t:
                special_files = None

                good_phrase = "2020-05-08"
                good_phrase = "2020-05-09"

                any_phrase_is_good = []
                good_phrases = []
                good_phrases2 = ["nah"]
                bad_phrases = []

                mode = "multilinks_v0_test_competitor"  # самый первый был тест, всех конкурентов сравнивал
                mode = "recheck 2020-05-13 exp1"  # что проверить и когда
                mode = "multilinks_rozetka"
                mode = "exact_file"
                mode = "pageCreation_do_2020.05.15"
                mode = "get_mega_accs"
                mode = (
                    "tatet__subdomains_of_created_pages&fromTask=1528853.txt"
                )

                mode = "2020_05_15__vmb_VS_aui"
                mode = "ivan_doindex"

                mode = "recheck_doindex_vmb_working"
                mode = "recheck_doindex_vmb_working__AllOther"
                mode = "ivan_2020_05_18"
                mode = "recheck 2020-05-14 add-url.info"

                mode = "ivan_2020_05_17"  # иван за 05-17
                mode = "ivan_2020_05_21"

                mode = "ivan_2020_05_23"

                mode = "ivan_all_latest"
                mode = "ivan_2020_05_22"

                mode = "test_concurrent_0516"

                mode = "2020-10-14 20 door pages"

                if mode_fixed:
                    mode = mode_fixed

                d_with_files = (
                    r"s:\!data\!!!rozetka\!tempory_check_indexation\%s" % mode
                )

                if dir_exists(d_with_files):
                    good_phrases = [mode]
                    # good_phrases = [mode, '__bot=']
                    # good_phrases = [mode, '-2.txt']

                    # want_scrap_indexed_unindexed = 1
                    # want_scrap_indexed_unindexed = 0

                    if want_scrap_indexed_unindexed:
                        want_crawl_google = 0
                        special = "parse_indexed_unindexed"

                elif mode == "exact_file":
                    # 2020-05-14__check_some_addurl_end_exit.txt
                    good_phrases = clear_list(
                        """
                            rooth223--2020-05-14--22-48-01__tatet_variant{au}.txt

                            """
                    )

                    bad_phrases = clear_list(
                        """
                            """
                    )

                elif mode == "ivan_2020_05_17":
                    good_phrases = clear_list(
                        """
                            rooth
                            2020-05-17
                            """
                    )

                elif mode == "ivan_2020_05_18":
                    good_phrases = clear_list(
                        """
                            rooth
                            2020-05-18
                            """
                    )

                elif mode == "ivan_2020_05_21":
                    good_phrases = clear_list(
                        """
                            rooth
                            2020-05-21
                            """
                    )

                elif mode == "ivan_2020_05_22":
                    good_phrases = clear_list(
                        """
                            rooth
                            2020-05-22
                            """
                    )

                elif mode == "ivan_2020_05_23":
                    good_phrases = clear_list(
                        """
                            rooth
                            2020-05-23
                            """
                    )

                elif mode == "test_concurrent_0516":
                    good_phrases = clear_list(
                        """
                            test_concurrents_2020.05.16
                            """
                    )

                elif mode == "ivan_doindex":
                    good_phrases = clear_list(
                        """
                            ivan_doindex
                            """
                    )

                elif mode == "ivan_all_latest":
                    good_phrases = clear_list(
                        """
                            rooth
                            """
                    )

                    dates = clear_list(
                        """
                            #2020-05-17
                            #2020-05-18
                            #2020-05-19
                            #2020-05-20
                            #2020-05-21

                                2020-05-22

                                #2020-05-23
                                #2020-05-25
                                #2020-05-26

                            #2020-05-27
                            #2020-05-28
                            #2020-05-29
                            #2020-05-30
                            #2020-05-31
                            """
                    )

                    special_files = [
                        f
                        for f in files
                        if (
                            1
                            # and (good_phrases != [] and found_all_phrases_in_text(good_phrases, f))
                            and found_phrase_in_text(dates, f)
                        )
                    ]
                    special_files = [
                        f
                        for f in special_files
                        if not found_phrase_in_text(bad_phrases, f)
                    ]
                    # show_list(special_files)
                    # wait_for_ok()

                elif mode == "recheck_doindex_vmb_working":
                    any_phrase_is_good = clear_list(
                        """
                            +joined__for_doindex_2020-05-15
                            """
                    )
                    """
                    """

                elif mode == "recheck_doindex_vmb_working__AllOther":
                    any_phrase_is_good = clear_list(
                        """
                            joined__for_doindex_2020-05-15__variant{wmb}&cnt=AllOther.txt
                            """
                    )
                    """
                            joined__for_doindex_2020-05-15__variant{wmb}&cnt=AllOther__ABVariants
                    """

                elif mode == "2020_05_15__vmb_VS_aui":
                    any_phrase_is_good = clear_list(
                        """
                            rooth223--2020-05-15--20-59-01__variant{addurl.info}&cnt=5852.txt
                            rooth223--2020-05-15--20-59-01__variant{wmb1}&cnt=2500.txt
                            rooth223--2020-05-15--20-59-01__variant{wmb2}&cnt=2500.txt
                            """
                    )
                    """
                    """

                elif (
                    mode
                    == "tatet__subdomains_of_created_pages&fromTask=1528853.txt"
                ):
                    any_phrase_is_good = clear_list(
                        """
                            tatet__subdomains_of_created_pages&fromTask=1528853.txt
                            """
                    )

                    cnt_checks = "all"
                    want_shuffle_links = 0
                    want_clear_pureSpam = 1

                    want_scrap_indexed_unindexed = 0
                    want_scrap_indexed_unindexed = 1
                    if want_scrap_indexed_unindexed:
                        want_crawl_google = 0
                        special = "parse_indexed_unindexed"

                elif mode == "get_mega_accs":
                    any_phrase_is_good = clear_list(
                        """
                                2020-05-15__check_indexedByAndrcomp.txt
                            """
                    )

                    cnt_checks = "all"
                    want_shuffle_links = 0

                    want_scrap_indexed_unindexed = 0
                    want_scrap_indexed_unindexed = 1
                    if want_scrap_indexed_unindexed:
                        want_crawl_google = 0
                        special = "parse_indexed_unindexed"

                elif mode == "pageCreation_do_2020.05.15":
                    any_phrase_is_good = clear_list(
                        """
                                2020-05-15__check_indexedByAndrcomp.txt
                            """
                    )
                    any_phrase_is_good0 = clear_list(
                        """
                                rooth223--2020-05-14--10-14-01 (1).txt
                                rooth223--2020-05-13--11-02-01.txt
                                rooth223--2020-05-13--09-35-02.txt
                            """
                    )
                    """
                    """

                    bad_phrases = clear_list(
                        """
                            __tatet
                            """
                    )

                    cnt_checks = "all"
                    want_shuffle_links = 0

                    want_scrap_indexed_unindexed = 1
                    want_scrap_indexed_unindexed = 0
                    if want_scrap_indexed_unindexed:
                        want_crawl_google = 0
                        special = "parse_indexed_unindexed"

                elif mode == "recheck 2020-05-14 add-url.info":
                    # http://wonary.ru/loguss?f_log=stat_full/stats/wonary.ru_full.txt&max_lines=1000&search=ff057d4c7f1
                    good_phrases = clear_list(
                        """
                            rooth223--2020-05-14--10-14-01 (1)__variant{au}&cnt=50.txt
                            """
                    )

                    bad_phrases = clear_list(
                        """
                            """
                    )

                elif mode == "recheck 2020-05-13 exp1":
                    good_phrases = clear_list(
                        """
                            2020-05-10-myMulitlinks_50_news.txt
                            """
                    )

                    bad_phrases = clear_list(
                        """
                            """
                    )

                elif mode == "multilinks_v0_test_competitor":
                    good_phrases = clear_list(
                        """
                            -myMulitlinks_
                            """
                    )

                elif mode == "multilinks_rozetka":
                    # мой тест мультилинков
                    good_phrases = clear_list(
                        """
                            multilinks_rozetka
                            """
                    )

                    bad_phrases = clear_list(
                        """
                            rooth223--2020-05-13--09-35-02.txt
                            rooth223--2020-05-13--11-02-01.txt
                            __variant{blk
                            """
                    )

                else:
                    wait_for_ok("unknown mode %s" % mode)

                if good_phrases_fixed is not None:
                    good_phrases = good_phrases_fixed

                logger.info("good_phrases: %s" % good_phrases)
                # show_list(good_phrases)
                logger.info("good_phrases_fixed: %s" % good_phrases_fixed)

                want_scrap_indexed_unindexed = 1
                want_scrap_indexed_unindexed = 0
                if want_scrap_indexed_unindexed:
                    want_crawl_google = 0
                    special = "parse_indexed_unindexed"

                if special_files is not None:
                    files = special_files[:]

                else:
                    files = [
                        f
                        for f in files
                        if (
                            (
                                any_phrase_is_good != []
                                and found_phrase_in_text(any_phrase_is_good, f)
                            )
                            or (
                                good_phrases != []
                                and found_all_phrases_in_text(good_phrases, f)
                            )
                            or (
                                good_phrases2 != []
                                and found_all_phrases_in_text(good_phrases2, f)
                            )
                        )
                    ]

                    files = [
                        f
                        for f in files
                        if not found_phrase_in_text(bad_phrases, f)
                    ]

            t = 0
            t = 1
            if t:
                logger.debug("%s files:" % len(files))
                show_list(files)
                # wait_for_ok()

            tasks_for_checking = []

            links = []

            t = 1
            if t:
                for f in files:
                    if not file_exists(f):
                        logger.debug("ERROR - NO FILE %s" % f)
                        # wait_for_ok()
                        continue

                    links = get_links_from_file(f)
                    links2 = set(links)

                    # уникализируем только если точно надо
                    if len(links2) != len(links):
                        links = unique_with_order(links)

                    if want_clear_pureSpam:
                        logger.debug("clear_pureSpam")
                        f_pure_spam = r"s:\!kyxa\!code\!google_addurl_selenium\data\!domains_pure_spam_full.txt"
                        pure_spam = set(
                            text_from_file(f_pure_spam).split("\n")
                        )
                        logger.debug("have %s in pure_spam" % len(pure_spam))
                        # wait_for_ok()

                        links_nospam = []
                        for i, _ in enumerate(links):
                            if i % 5000 == 0:
                                logger.debug(len(links) - i)

                            link_domain = find_from_to_one(".", "/", _)
                            # logger.debug(link_domain)
                            if link_domain in pure_spam:
                                continue
                            links_nospam.append(_)
                        logger.debug(
                            "have %s/%s nospam"
                            % (len(links_nospam), len(links))
                        )

                        if len(links_nospam) != len(links):
                            links = links_nospam[:]
                            sleep_(2)
                            wait_for_ok()

                    if want_shuffle_links:
                        shuffle(links)

                    if len(links) == 0:
                        logger.warning("WARNING: NO LINKS IN %s" % f)
                        continue

                    # оставляем из списков только норм. линки
                    if domains_to_check_for_indexation != []:
                        links_filtered = filter_urls_in_domains(
                            links, domains_to_check_for_indexation
                        )
                        logger.debug(
                            "filtered %s/%s links in %s"
                            % (len(links_filtered), len(links), f)
                        )
                        links = links_filtered[:]
                        # wait_for_ok()

                    # links = links[:1]
                    name_detailed = os.path.basename(f)
                    _ = {
                        "f": f,
                        "links": links,
                        "name_detailed": name_detailed,
                    }
                    tasks_for_checking.append(_)

            t = 1
            t = 0
            if t:
                roz = Rozetka()

                t = 1
                t = 0
                if t:
                    theme = "124"

                    ot = 1
                    do = 2000

                    # network
                    ot = 2000
                    do = 3000

                t = 1
                t = 0
                if t:
                    theme = "125"

                    ot = 1
                    do = 3000

                    # network
                    ot = 3000
                    do = 4000

                t = 1
                t = 0
                if t:
                    theme = "g126"

                    # network
                    ot = 1
                    do = 1000

                    ot = 1000
                    do = 5500

                t = 1
                t = 0
                if t:
                    theme = """
                                111
                                116
                                """

                    ot = 3001
                    do = 4000

                    # network
                    ot = 1001
                    do = 2000

                t = 1
                t = 0
                if t:
                    theme = """
                                g66
                                #g68
                                """

                    ot = 3001
                    do = 4000

                    # network
                    ot = 9001
                    do = 10000

                    # network2
                    ot = 8001
                    do = 9000

                t = 1
                t = 0
                if t:
                    theme = """
                            g130

                                """

                    # network
                    ot = 5501
                    do = 5745

                    ot = 1
                    do = 5500

                t = 1
                t = 0
                if t:
                    theme = """
                            g120
                            g121
                            g122
                            g123
                            g124
                            g125
                            g126
                            g127
                            g128
                            g129
                            g130
                            """

                    # network 2020.02.29
                    ot = 1001
                    do = 2000

                t = 1
                t = 0
                if t:
                    theme = """
                        g132
                            """

                    # g132-blogNetwork
                    ot = 3700
                    do = 3987

                    # normal
                    ot = 1
                    do = 3700

                t = 1
                t = 0
                if t:
                    theme = """
                        g135
                            """

                    # g135-blogNetwork
                    ot = 3800
                    do = 4000

                t = 1
                t = 0
                if t:
                    theme = """
                        g140
                            """

                    # new domains
                    # 52% == 104/200        [11, 10, 15, 11, 10, 8, 10, 9, 8, 12]
                    ot = 1
                    do = 5000

                    # old domains
                    ot = 5000
                    do = 7000

                t = 1
                t = 0
                if t:
                    theme = """
                        g141
                            """

                    # new domains
                    # 52% == 104/200        [11, 10, 15, 11, 10, 8, 10, 9, 8, 12]
                    ot = 1
                    do = 3000

                    # old domains
                    # 52% == 104/200        [11, 10, 15, 11, 10, 8, 10, 9, 8, 12]
                    ot = 3001
                    do = 3700

                t = 1
                t = 0
                if t:
                    theme = "142"

                    # 2001    3000    g142 domains_all_3.txt
                    # 03.03 16:30    3% == 6/200        [1, 0, 1, 0, 0, 1, 1, 0, 1, 1]
                    # 24% == 49/200        [3, 6, 4, 7, 5, 4, 4, 7, 5, 4]
                    ot = 2001
                    do = 3000

                    # 1    2000    g142 domains_jino_2020.03.02.txt
                    # 03.03 16:30    21% == 42/200        [4, 3, 9, 5, 3, 5, 2, 4, 4, 3]
                    # 03.03 23:17    62% == 125/200        [12, 12, 11, 9, 14, 17, 13, 11, 12, 14]
                    ot = 1
                    do = 2000

                    # 3001    4342    g142 domains_2020.03.03-1-2.txt
                    # 03.03 16:30    7% == 14/200        [3, 0, 2, 2, 1, 2, 3, 0, 1, 0]
                    # 03.03 23:17    18% == 37/200        [3, 5, 1, 4, 3, 3, 5, 6, 5, 2]
                    # 22% == 45/200        [2, 4, 6, 5, 7, 2, 3, 6, 5, 5]
                    ot = 3001
                    do = 4340

                t = 1
                t = 0
                if t:
                    theme = """
                            g64
                            g65
                            g66
                            g68
                            g72
                            g73
                            g74
                            g75
                            g76
                            g77
                        """
                    ot = 14001
                    do = 17000

                    # network 2020.02.29
                    ot = 17001
                    do = 18000

                    # network 2020.02.29
                    ot = 18201
                    do = 18400

                t = 0
                t = 1
                if t:
                    txt_with_task = """
                        1    1000    g143 domains_all_3.txt
                        1001    2000    g143 domains_jino_2020.03.02.txt
                        2001    3000    g143 domains_2020.03.03-1-2.txt
                        3001    4000    g143 domains_2020.03.03-2-5.txt
                        4000    5103    g143 domains_2020.03.03-3-20.txt
                    """

                    txt_with_task = """
                        1    2000    g142 domains_jino_2020.03.02.txt
                        2001    3000    g142 domains_all_3.txt
                        3001    4342    g142 domains_2020.03.03-1-2.txt
                        """

                    txt_with_task = """
                            1    3000    g141 domains_jino_2020.03.02.txt
                            3001    3757    g141 domains_all_3.txt
                        """

                    txt_with_task = """
                        1    5000    g140 domains_jino_2020.03.02.txt
                        5001    6091    g140 domains_all_3.txt
                        """

                    txt_with_task = """
                            #1    1000    g145 domains_2020.03.03-3-20.txt
                            #1001    2000    g145 domains_all_3.txt
                            #2001    3000    g145 domains_jino_2020.03.02.txt
                            #3001    4000    g145 domains_2020.03.03-2-5.txt
                            #4001    5000    g145 domains_2020.03.04-1-5.txt
                            5001    5687    g145 blogNetwork domains_2020.03.04-3-ru-10.txt
                            #5688    5898    g145 addurlinfo

                        """

                    tasks_theme_ot_do = get_task_for_generating_rozetka_urls(
                        txt_with_task
                    )
                    # theme, ot, do = tasks[0]

                for T in tasks_theme_ot_do:
                    theme = T["theme"]
                    name = T["name"]
                    ot = T["ot"]
                    do = T["do"]
                    theme = clear_list(theme)
                    theme = [_ for _ in theme if _[0] not in ["#"]]

                    theme.sort()
                    theme_name = " ".join(theme)

                    links = roz.get_links_in_themes(theme, ot, do)

                    shuffle(links)

                    # wait_for_ok('have %s links' % len(links))
                    f = (
                        r"s:\!data\!!![bulkadu]\!links\gootheme_urls%s+.txt"
                        % theme_name
                    )

                    _ = {
                        "f": f,
                        "links": links,
                    }
                    T = add_defaults(_, T)
                    tasks_for_checking.append(T)

            # show_list(tasks_for_checking)
            # wait_for_ok()

            t = 1
            t = 0
            if t:

                # а теперь оставляем только обработанные логом!
                links0 = links[:]

                # urls_addurled = get_addurled_from_log_grubo()
                # urls_addurled = parse_addurl_log_files()

                f = r"s:\!kyxa\!code\!google_addurl_selenium\full_log_FOREVER_LOCAL.txt"
                mode = ""

                max_hours = 24
                min_hours = 6

                min_hours = 3
                min_hours = 0

                max_hours = 6

                min_hours = 6

                filters = [
                    # {'max_age': 60*60*max_hours},
                    {"min_age": 60 * 60 * min_hours},
                ]
                logs = parse_addurl_log_files(
                    files=[f], mode=mode, filters=filters
                )
                logs = filter_addurlLogs(logs, "no_hashes")
                urls_addurled = [_["url"] for _ in logs]

                # wait_for_ok()

                # wait_for_ok()
                links = [_ for _ in links if _ in urls_addurled]
                logs = filter_addurlLogs(logs, urls=links)
                logger.debug("addurled:")
                print_addurl_log_pretty(logs)

                want_no_addurled = 0
                want_no_addurled = 1
                if want_no_addurled:
                    # а если непроиндексенные взять?
                    links = list_minus_list(links0, links)
                    wait_for_ok("want_no_addurled")

                logger.debug(
                    "%s/%s addurled, check only them"
                    % (len(links), len(links0))
                )

                # хочу создать файл Ивану?
                t = 1
                t = 0
                if t:
                    log_lines = prettify_addurl_log(logs, first=100000)

                    f_to = "[d_to]/[theme_name] min_hours=[min_hours] max_hours=[max_hours] links=[cnt].txt"
                    f_to = "[d_to]/[theme_name] min_hours=[min_hours] links=[cnt].txt"
                    repl = {
                        "[d_to]": r"s:\!data\!!!rozetka\[blog_network]",
                        "[min_hours]": min_hours,
                        "[max_hours]": max_hours,
                        "[cnt]": len(log_lines),
                        "[theme_name]": theme_name,
                    }
                    f_to = no_probely(f_to, repl)
                    txt = "\n".join(log_lines)
                    text_to_file(txt, f_to)
                    webbrowser_open(f_to)
                    wait_for_ok("copy file %s" % f_to)

                sleep_(1)

            # analized = run_browser_crawler_for_counting_indexed_approximately(S, f, cnt_checks=cnt_checks, d_to=d_to, links=links)
            # cnt_checks = 1

            # wait_for_ok(special)
            m = "special %s, have %s tasks" % (
                special,
                len(tasks_for_checking),
            )
            Show_step(m)
            # wait_for_ok(special)

            #       начинаем проверки
            step_main_check = 0
            while True:
                step_main_check += 1
                Show_step("STEP: %s" % step_main_check)

                name_to_analiz = {}
                num = 0
                for task in tasks_for_checking:
                    num += 1
                    name = task["name_detailed"]
                    Show_step(
                        "%s/%s %s" % (num, len(tasks_for_checking), name)
                    )
                    if want_crawl_google:
                        # stats_collector.total_size = int( len(task['links']) / max_cnt )
                        if len(task["links"]) == 0:
                            wait_for_ok("no links")

                        analiz = run_browser_crawler_for_counting_indexed_approximately(
                            S,
                            task["f"],
                            cnt_checks=cnt_checks,
                            d_to=d_to,
                            links=task["links"],
                            special=special,
                            max_cnt=max_cnt,
                            tpl_one_query=tpl_one_query,
                            f_abs_tpl=f_abs_tpl,
                        )
                        name_to_analiz[name] = analiz

                    if special == "parse_indexed_unindexed":
                        Show_step(special)
                        f_name = os.path.basename(task["f"])
                        # d_downloaded = '%s/%s' % (d_to, f_name)
                        d_downloaded = (
                            r"s:\!data\!google.com\!counting_indexed\%s"
                            % f_name
                        )
                        d_result = (
                            r"s:\!data\!google.com\!indexed_unindexed\%s"
                            % f_name
                        )
                        logger.debug(
                            "f_name %s, d_downloaded %s"
                            % (f_name, d_downloaded)
                        )

                        gs = GoogleSearch()

                        parse_indexed_unindexed_from_directory(
                            d=d_downloaded, d_result=d_result, want_open=0,
                        )
                        # wait_for_ok()

                    if special == "just_scrap_google_queries":
                        Show_step(special)
                        f_name = os.path.basename(task["f"])

                        # d_downloaded = r's:\!data\!!!rozetka\!!!downloaded_google_results\%s' % f_name
                        d_downloaded = "%s/%s" % (d_to, f_name)

                        d_result = (
                            r"s:\!data\!!!rozetka\!!!scrap_google_results_done\%s"
                            % f_name
                        )

                        f_rez_xls = "%s/podskazki.xls" % (d_result)
                        f_rez_txt = "%s/podskazki.txt" % (d_result)
                        f_rez_xls = None

                        #       сохранили полную задачу
                        f_full_task = "%s/zaprosy.txt" % (d_result)
                        text_to_file("\n".join(task["links"]), f_full_task)

                        t = 1
                        t = 0
                        if t:
                            parse_bottom_podskazki_for_rozetka_directory(
                                d=d_downloaded,
                                f_rez_xls=f_rez_xls,
                                f_rez_txt=f_rez_txt,
                                want_open=0,
                            )

                        # и позиции определяю
                        t = 1
                        if t:
                            gs = GoogleSearch()

                            f_positions = "%s/pozitions.xls" % (d_result)
                            gs.calculate_positions_in_directory(
                                d_from=d_downloaded,
                                site="rozetka.com.ua",
                                f_rez_xls=f_positions,
                                special_task="for_rozetka_1_otdelno",
                                d_special_task=d_result,
                                max_position=5,
                                want_open=0,
                            )

                    # wait_for_ok('%s done' % name)

                logger.debug("name_to_analiz %s" % name_to_analiz)
                show_dict(name_to_analiz)

                if recheck_after == 0:
                    wait_for_ok("analyze now")
                else:
                    logger.debug(
                        "step_main_check %s done, recheck_after  %s"
                        % (step_main_check, recheck_after)
                    )
                    sleep_(recheck_after)
            os._exit(0)

        elif mode == "run_browser_crawler_for_monitoring_indexed":
            f = r"s:\!data\!!![bulkadu]\!queries_to_monitore_in_google.txt"
            run_browser_crawler_for_monitoring_indexed(S, f, d_to=d_to)

        else:
            wait_for_ok("unknown mode %s" % mode)

        os._exit(0)

    t = 1
    t = 0
    if t:
        click_on_random_element(S)
        wait_for_ok()

    # S.driver.get('https://google.com')
    # wait_for_ok('and now even more - with wrap_selenium_class')


def test_youtuber(S):
    yt = Youtuber(S=S)

    # r = yt.test_server_with_youtube()
    # r = yt.test_one_function()
    # r = yt.random_scroll()
    # r = yt.hover_random_video()
    xpath = '//*[@id="content"]'
    xpath = '//img[@id="img"]'
    xpath = '//a[@id="thumbnail"]'
    r = yt.S.hover_xpath(xpath)
    # r = yt.scroll_down()
    logger.debug("r=%s" % r)
    wait_for_ok("test finished?")


class Selenium_starter:
    def __init__(
        self,
        geckodriver_port=7890,
        marionette_port=57890,
        marionette_port_fixed=None,
        profile_path=r"",
        special="",
        special_potok=0,
        # special='avtomatize_actions',
        f_firefox="",
        f_geckodriver=None,
        browser="",
        f_chrome=None,
        chrome_profile_path="",
        f_chrome_driver=None,
        minimum_debug_level="info",
    ):
        fun = "Selenium_starter/__init__"
        # wait_for_ok(marionette_port_fixed)

        self.minimum_debug_level = minimum_debug_level
        want_number_in_profile = True

        if special == "":
            pass

        elif special == "avtomatize_actions":
            geckodriver_port = 7890
            marionette_port = 57890
            profile_path = r"[d_profiles]\avtomatize_actions"

        elif special == "avtomatize_actions_1":
            geckodriver_port = 7891
            marionette_port = 57891
            profile_path = r"[d_profiles]\avtomatize_actions_01"

        elif special == "avtomatize_actions_clean":
            geckodriver_port = 10000
            marionette_port = 60000
            profile_path = r"[d_profiles]\avtomatize_actions_clean"

        elif special == "avtomatize_actions_surebets":
            geckodriver_port = 15000
            marionette_port = 65000
            profile_path = r"[d_profiles]\avtomatize_actions_surebets"

        elif special == "bet365_avstria_old_firefox":
            geckodriver_port = 6000
            marionette_port = 56000
            profile_path = r"[d_profiles]\bet365_avstria_old_firefox"
            want_number_in_profile = False

            f_firefox = r"c:\Program Files\Firefox Developer Edition\firefox_avstria.exe"

        elif special == "bet365":
            geckodriver_port = self.get_first_geckodriver_port(special)
            marionette_port = 56000
            want_number_in_profile = False

        elif special == "bet365_avstria":
            geckodriver_port = 6000
            marionette_port = 56000
            # marionette_port = None
            profile_path = r"[d_profiles]\bet365_avstria"
            want_number_in_profile = False

            f_firefox = r"c:\Program Files\Firefox Developer Edition\firefox_avstria.exe"
            f_firefox = r"s:\Program Files (x86)\Mozilla Firefox 81 avstria\firefox_avstria.exe"

            f_firefox = r"s:\!installs\!portable_browsers\bet365_spain\FirefoxPortableDeveloper\FirefoxPortable.exe"

            #   portable
            profile_path = r"s:\!installs\!portable_browsers\bet365_avstria\FirefoxPortableDeveloper\Data\profile"
            f_firefox = r"s:\!installs\!portable_browsers\bet365_avstria\FirefoxPortableDeveloper\App\Firefox\firefox_avstria.exe"

        elif special == "indigo_kuha_1":
            geckodriver_port = 6001
            marionette_port = 56001
            # marionette_port = None
            want_number_in_profile = False

            f_firefox = r"c:\Program Files\Firefox Developer Edition\firefox_avstria.exe"
            f_firefox = r"s:\Program Files (x86)\Mozilla Firefox 81 avstria\firefox_avstria.exe"
            f_firefox = r"s:\!installs\!portable_browsers\bet365_spain\FirefoxPortableDeveloper\FirefoxPortable.exe"

            #   portable
            # profile_path=r'[d_profiles]\bet365_avstria'
            profile_path = r"s:\!installs\!portable_browsers\indigo_kuha1\MLA.5139895597454467208"
            f_firefox = r"s:\!installs\!portable_browsers\bet365_avstria\FirefoxPortableDeveloper\App\Firefox\firefox_avstria.exe"
            f_firefox = r"C:\Users\kyxa\.indigobrowser\data\deps\com\multiloginapp\browser-stealthfox\79.2\browser-stealthfox-79.2-win64.tar.gz\firefox.exe"

        elif special == "bet365_spain":
            geckodriver_port = 6000
            marionette_port = 56000
            # marionette_port = None
            want_number_in_profile = False

            profile_path = r"s:\!installs\!portable_browsers\bet365_spain\FirefoxPortableDeveloper\Data\profile"
            f_firefox = r"s:\!installs\!portable_browsers\bet365_spain\FirefoxPortableDeveloper\App\Firefox\firefox.exe"

        elif special == "bukvarix":
            geckodriver_port = 6011
            marionette_port = 56011
            # marionette_port = None
            want_number_in_profile = False
            # f_firefox = r's:\Program Files (x86)\Mozilla Firefox 81 avstria\firefox_avstria.exe'
            # f_firefox = r's:\Program Files (x86)\Firefox Developer Edition 82 german\firefox_avstria.exe'

            profile_path = r"s:\!installs\!portable_browsers\bukvarix.com_2019-2020__Copy\Data\profile"
            f_firefox = r"s:\!installs\!portable_browsers\bukvarix.com_2019-2020__Copy\FirefoxPortable.exe"
            f_geckodriver = (
                r"s:\!data_main\chromedrivers\geckodriver_0.18.0__32.exe"
            )

            f_firefox = r"s:\!installs\!portable_browsers\bukvarix.com_2019-2020__Copy\App\Firefox\firefox.exe"  # real exe not needed?

        elif special.startswith("gmail_"):  # gmail._login@.gmail.com
            geckodriver_port = 5000
            marionette_port = 55000
            profile_path = r"[d_profiles]\%s" % special
            want_number_in_profile = False

        elif special == "google_for_debugging_[bulkadu]":

            geckodriver_port = 6888
            marionette_port = 57888
            profile_path = "[d_profiles]\\google_for_debugging_[bulkadu]"

        elif special == "google_for_scrapping_googleEN":
            want_number_in_profile = False
            geckodriver_port = 6889  # scrapping google
            marionette_port = 57889
            profile_path = "[d_profiles]\\%s" % special

        elif (
            special == "google_for_scrapping_googleUA"
        ):  # для скрапинга поиска в гугле
            want_number_in_profile = False
            geckodriver_port = 6900
            marionette_port = 56900
            profile_path = "[d_profiles]\\%s" % special

        else:
            wait_for_ok("unknown special %s" % special)

        if marionette_port_fixed is not None:
            marionette_port = marionette_port_fixed

        # logger.debug('marionette_port=%s (marionette_port_fixed=%s)' % (marionette_port, marionette_port_fixed))
        # wait_for_ok()

        if 1:  # special_potok>0:
            geckodriver_port = geckodriver_port + special_potok

            if isinstance(marionette_port, int):
                marionette_port = marionette_port + special_potok

            if want_number_in_profile:
                profile_path = "%s__%05d" % (profile_path, special_potok)

            logger.debug("profile_path=%s" % profile_path)

            t = 1
            t = 0
            if t:
                logger.debug("check locals for %s" % fun)
                show_dict(locals())
                wait_for_ok("")

        # if not dir_exists(profile_path)

        self.f_firefox = f_firefox
        self.f_geckodriver = f_geckodriver
        self.geckodriver_port = geckodriver_port
        self.marionette_port = marionette_port
        self.profile_path = profile_path
        self.driver = None

        self.browser = browser
        self.f_chrome = f_chrome
        self.f_chrome_driver = f_chrome_driver
        self.debugger_port = geckodriver_port
        self.chrome_profile_path = chrome_profile_path

    def get_first_geckodriver_port(self, special="bet365", default_port=6000):
        special_to_port = {
            "bet365": 6000,
        }
        return special_to_port.get(special, default_port)

    def run_chrome_with_special_profile(self, want_kill_old=False):
        return run_chrome_with_special_profile(
            f_chrome=self.f_chrome,
            profile_path=self.chrome_profile_path,
            debugger_port=self.debugger_port,
            want_kill_old=want_kill_old,
        )
        # sleep_(5) # после запуска браузер чуть ждем

    def run_firefox_with_special_profile(
        self, want_geckodriver=1, want_kill_old=False
    ):
        # wait_for_ok(self.f_geckodriver)
        run_firefox_with_special_profile(
            f_firefox=self.f_firefox,
            profile_path=self.profile_path,
            geckodriver_port=self.geckodriver_port,
            marionette_port=self.marionette_port,
            # firefox_command_line_arguments=firefox_command_line_arguments,
            want_geckodriver=want_geckodriver,
            f_geckodriver=self.f_geckodriver,
            want_kill_old=want_kill_old,
        )

        # sleep_(5)
        # wait_for_ok('started selenium?')

    def save_driver(self, driver=None):
        if driver == None:
            driver = self.driver

        f_driver = self.get_f_driver()
        save_selenium_driver(driver, f_driver)
        # obj_to_file_p(driver, self.get_f_driver())
        self.driver = driver
        return f_driver

    def load_driver(self):
        f_driver = self.get_f_driver()
        driver = obj_from_file_p(f_driver)
        self.driver = driver
        return driver

    def get_marionette_status(self):
        u_marionette = "http://127.0.0.1:%s" % self.marionette_port
        marionette_status = quick_check_service_status(u_marionette)
        # wait_for_ok()
        return marionette_status

    def create_driver_session_with_marionette(
        self, want_try=1, want_check_marionette=False,
    ):
        fun = "create_driver_session_with_marionette"
        logger.info("[%s: " % fun)
        connection_info = self.load_connection_info()
        session_id, executor_url = connection_info.split("|")
        # want_try = 0

        logger.debug("executor_url=%s" % executor_url)

        """
            проверяю - возможно даже не запущен марионете, тогда и не рыпаемся
        	html
			"{"value":{"error":"unknown command","message":"GET / did not match a known command","stacktrace":""}}"
            kod
                    404

        """
        if want_check_marionette:
            marionette_status = self.get_marionette_status()
            logger.debug("marionette_status=%s" % marionette_status)

            # if marionette_status in ['connection_refused']:
            if marionette_status not in ["success"]:
                logger.info("ERROR: no marionette")
                return False

        geckodriver_status = quick_check_service_status(executor_url)
        logger.info("geckodriver_status=%s" % geckodriver_status)
        # wait_for_ok()

        if geckodriver_status not in ["success"]:
            logger.info("geckodriver_status, reason: %s" % geckodriver_status)
            # show_dict(r)
            logger.info("ERROR: no geckodriver")
            return False
            # wait_for_ok()

        logger.info(
            "geckodriver exists, starting session to connect to marionette"
        )
        if want_try:
            try:
                # если сессия не начата, мы ее создадим
                new_driver = webdriver.Remote(
                    command_executor=executor_url, desired_capabilities={}
                )
            except Exception as er:
                try:
                    er = str(er)
                except Exception as er2:
                    logger.error("error printing error %s, err=%s" % (er, er2))

                if "Session is already started" in er:
                    logger.error(" Session is already started")
                    # к сожалению вытягивать не получается - теперь geckodriver спрятал это
                    # https://tarunlalwani.com/post/enumerating-running-firefox-browser-selenium/
                    new_driver = create_driver_session(
                        session_id, executor_url
                    )
                    # wait_for_ok('todo - how to find existing session?')
                else:
                    logger.info("ERROR %s: %s" % (fun, er))

                    # висит драйвер, но браузер умер
                    if (
                        "No connection could be made because the target machine actively refused it"
                        in er
                    ):
                        logger.error(
                            " known error: geckodriver can not connect to marionette"
                        )
                        logger.error(
                            "browser is without marionette or no browser, so total restart"
                        )
                        return False

                    else:
                        logger.error(" ERROR %s: %s" % (fun, er))
                        wait_for_ok("unknown error")

        else:
            new_driver = webdriver.Remote(
                command_executor=executor_url, desired_capabilities={}
            )

        new_driver.command_executor._url = executor_url
        self.save_connectionInfo(new_driver)
        self.driver = new_driver
        return new_driver

    def setup_executor_url_to_driver(driver):
        connection_info = self.load_connection_info()
        session_id, executor_url = connection_info.split("|")
        driver.command_executor._url = executor_url
        return driver

    def save_connectionInfo(self, driver):
        fun = "save_connectionInfo"
        f_connection = self.get_f_connectionInfo()
        message = "%s|%s" % (driver.session_id, driver.command_executor._url)
        f_connection_info = self.get_f_connectionInfo()
        text_to_file(message, f_connection_info)
        logger.info("[%s %s]" % (fun, message))

    def load_connection_info(self):
        connection_info = (
            "5011f174-a308-425c-903a-51239235d754|http://127.0.0.1:%s"
            % self.geckodriver_port
        )
        f_connection_info = self.get_f_connectionInfo()
        if 1 and file_exists(f_connection_info):
            connection_info = text_from_file(f_connection_info)
            m = "got connection_info `%s` from file f_connection_info `%s`" % (
                connection_info,
                f_connection_info,
            )
            logger.debug(m)
            # wait_for_ok(m)
        return connection_info

    def get_S(self, driver=None):
        if driver is None:
            driver = self.driver
        if driver is None:
            logger.error("ERROR: no driver")

        driver = self.driver
        _ = {
            "s_driver": driver,
            "s_autostart": 0,
            "minimum_debug_level": self.minimum_debug_level,
        }
        S = wrap_selenium_class(_)
        return S

    def reconnect_and_get_S(
        self, want_kill_old_geckodriver=False, want_kill_old=False
    ):
        fun = "reconnect_and_get_S"
        logger.info("[%s:" % fun)

        if want_kill_old_geckodriver:
            logger.debug("want_kill_old_geckodriver")
            killed = kill_geckodriver_with_special_port(
                geckodriver_port=self.geckodriver_port,
                marionette_port=self.marionette_port,
            )
            logger.debug("killed=%s" % killed)
            # wait_for_ok(m)

            t = 0
            if t:
                # полюбому запускаем гекодрайвер
                r_new_geckodriver = run_geckodriver_with_special_port_if_not_active(
                    geckodriver_port=self.geckodriver_port,
                    marionette_port=self.marionette_port,
                    f_geckodriver=self.f_geckodriver,
                )
                logger.debug("r_new_geckodriver=%s" % (r_new_geckodriver))
                # wait_for_ok()

        # полюбому запускаем фаерфокс и все к нему (если не запущено)

        # сначал пробую просто запуститься - выйдет значит все уже запущено и супер
        logger.warning("-" * 10 + "CHECK IF BROWSER ALREADY STARTED")

        # self.run_firefox_with_special_profile(want_geckodriver=1,
        #                                       want_kill_old=want_kill_old)

        if self.browser == "chrome":
            self.run_browser_with_profile(want_kill_old=want_kill_old)

        S = self.reconnect()

        logger.debug(" found S=%s" % S)

        # урл проверить быстрее чем страницу качать на пару метров
        # page_url = S.sgp()
        page_url = S.url(1)
        # logger.debug(type(page_url))
        logger.debug("S url=%s" % page_url)
        # wait_for_ok()

        if page_url in [False, ""]:
            logger.warning("-" * 10 + "NEED RESTART FIREFOX")
            # wait_for_ok('want_kill_old=%s' % want_kill_old)
            self.run_browser_with_profile(want_kill_old=want_kill_old)
            S = self.reconnect()
        # wait_for_ok('run_firefox_with_special_profile done')

        S.marionette_port = self.marionette_port
        S.geckodriver_port = self.geckodriver_port

        if self.browser == "chrome":
            S.debugger_port = self.debugger_port
        return S

    def run_browser_with_profile(self, want_kill_old=False):
        if self.browser == "chrome":
            self.run_chrome_with_special_profile(want_kill_old=want_kill_old)
        else:
            self.run_firefox_with_special_profile(
                want_geckodriver=1, want_kill_old=want_kill_old
            )

    def reconnect(self):
        if self.browser == "chrome":
            r = self.reconnect_to_chrome()
        else:
            r = self.reconnect_to_firefox()
        return r

    def reconnect_to_chrome(self):
        fun = "reconnect_to_chrome"

        chrome_options = webdriver.ChromeOptions()

        chrome_options.add_experimental_option(
            "debuggerAddress", f"127.0.0.1:{self.debugger_port}"
        )

        logger.debug(f"{chrome_options=}")

        # desired_capabilities = {
        #     'goog:chromeOptions': {'debuggerAddress': '127.0.0.1:6814',
        #                            'args': [], 'extensions': []},
        #     'platform': 'ANY', 'browserName': 'chrome', 'version': ''}

        args = {
            "executable_path": self.f_chrome_driver,
            # "executable_path": r"c:\GeckoDriver\chromedriver_96.exe",
            "chrome_options": chrome_options,
            # "desired_capabilities": desired_capabilities,
        }
        logger.debug(f"{args=}")
        driver = webdriver.Chrome(**args)

        t = 0
        if t:
            t = 1
            if t:
                logger.debug("driver=%s" % driver)
                simple_pickle(driver)
                wait_for_ok("pickled?")

        self.driver = driver
        logger.debug("+%s driver=%s]" % (fun, driver))
        return self.get_S(driver)

    def reconnect_to_firefox(self):
        fun = "reconnect_to_firefox"
        logger.info("[%s " % fun)

        f_driver = self.get_f_driver()
        f_connection_info = self.get_f_connectionInfo()

        connection_info = self.load_connection_info()

        session_id, command_executor = connection_info.split("|")

        t = 0
        if t:
            session_id = "44fe0ca2-e225-4fa4-bc6a-5c7e046507db"
            command_executor = "http://127.0.0.1:58630"

        logger.info("reconect with %s" % connection_info)

        mode_reconnect = "reconnect_remote"
        mode_reconnect = "tupo"
        mode_reconnect = "create_driver_session"
        mode_reconnect = "obj"
        mode_reconnect = "create_driver_session_with_marionette"

        logger.debug("f_driver=%s" % f_driver)
        # wait_for_ok()

        if mode_reconnect == "obj" and file_exists(f_driver):
            driver = self.load_driver()
            logger.debug("driver: %s" % driver)

        elif mode_reconnect == "reconnect_remote":
            logger.debug("remote...")
            capabilities = DesiredCapabilities.FIREFOX.copy()

            driver = webdriver.Remote(
                desired_capabilities=capabilities,
                command_executor=selenium_grid_url,
            )
            if (
                driver.session_id != session_id
            ):  # this is pretty much guaranteed to be the case
                logger.debug("removing old session %s" % driver.session_id)
                # driver.close()   # this closes the session's window - it is currently the only one, thus the session itself will be auto-killed, yet:
                driver.quit()  # for remote connections (like ours), this deletes the session, but does not stop the SE server

        elif mode_reconnect == "create_driver_session":
            driver = create_driver_session(session_id, command_executor)

            logger.debug("session_id")
            driver.session_id = session_id

        elif mode_reconnect == "create_driver_session_with_marionette":
            driver = self.create_driver_session_with_marionette()
            # wait_for_ok()

        else:
            wait_for_ok("unknown mode_reconnect `%s`" % mode_reconnect)

        if driver:
            driver.command_executor._url = command_executor

        self.driver = driver
        logger.info("+%s]" % fun)
        return self.get_S(driver)

    def get_f_driver(self, geckodriver_port=None):
        geckodriver_port = self.get_geckodriver_port(geckodriver_port)
        return self.f_abs(
            "temp/driver__geckodriver_port_%s.obj" % geckodriver_port
        )

    def get_f_connectionInfo(self, geckodriver_port=None):
        geckodriver_port = self.get_geckodriver_port(geckodriver_port)
        return self.f_abs(
            "temp/selenium_connection_info__geckodriver_port_%s.dat"
            % geckodriver_port
        )

    def f_abs(self, f=""):
        return "%s/%s" % (os.path.dirname(os.path.abspath(__file__)), f)

    def get_geckodriver_port(self, geckodriver_port=None):
        if geckodriver_port == None:
            geckodriver_port = self.geckodriver_port
        return geckodriver_port

    def __repr__(self):
        m = (
            """geckodriver_port=%s, marionette_port=%s, profile_path=%s, driver=%s"""
            % (
                self.geckodriver_port,
                self.marionette_port,
                self.profile_path,
                self.driver,
            )
        )
        return m


class StatsCollector:
    def __init__(self, name="", short_names={}):
        self.name = name
        self.stat = {}

        self.short_names = short_names
        self.queue = []
        self.queue_short = []

        self.total_size = 0

    def plus_1(self, key="", value=1):
        """
            апдейтим стату
        """
        if not key in self.stat:
            self.stat[key] = 0
        self.stat[key] += value

        self.queue.append(key)

        short = self.short_names.get(key, key)
        self.queue_short.append(short)

    def print_stat(
        self, with_percent=0, po_100=1, print_only_last=1,
    ):

        print("StatsCollector %s stats: %s" % (self.name, self.stat))

        show_dict(self.stat)

        if with_percent:
            print("\n", "procent")
            keys = self.stat.keys()
            sort_nicely(keys)
            suma = sum(self.stat.values())
            for key in keys:
                value = self.stat[key]
                procent = int(100 * value / suma)
                print(" %s   %s      %s%%" % (key, value, procent))

        if po_100:
            line_size = 100
            pa4ki = split_list(self.queue_short, line_size)

            print("\n", "stata po 100")
            num_pa4ka = 0
            cnt_now = 0
            for pa4ka in pa4ki:
                num_pa4ka += 1
                cnt_now += len(pa4ka)

                if print_only_last and len(pa4ki) != num_pa4ka:
                    continue

                line = "".join(pa4ka)

                procent_info = " "
                if self.total_size != 0:
                    procent = int(100 * cnt_now / self.total_size)
                    procent_info = "=%d%% " % procent

                # print('[%s%s (total_size %s) %s]' % (cnt_now, procent_info, self.total_size, line))
                print(
                    "[%s/%s%s %s]"
                    % (cnt_now, self.total_size, procent_info, line)
                )


def filter_urls_in_domains(urls=[], domains=[]):
    """
    оставляем ссылки только в хороших доменах
    """
    new_urls = []
    for url in urls:
        # http://d.domain.online/
        if is_url_in_domains(url, domains):
            new_urls.append(url)
    return new_urls


def is_url_in_domains(url="", domains=[]):
    """
    проверяем - домен (или субдомен) урла должен быть среди доменов
    """
    # print(domain)
    # wait_for_ok(domain, url)
    domain = get_domain_from_url(url)
    found = 0
    if domain in domains:
        found = "in_domain"
    else:
        root_domain = ".".join(domain.split(".")[-2:])
        # wait_for_ok(root_domain)
        if root_domain in domains:
            found = "in_root_domain"
    return found


def get_domain_from_url(url=""):
    # domain = get_domain_from_url(link)
    # http://0a76c934ffd.soredthe.online/
    parts = url.split("/")
    # logger.debug(parts)
    return parts[2]


def quick_check_service_status(url="http://127.0.0.1:6000"):
    """
    Быстро проверить статус урла
    """
    fun = "quick_check_service_status"
    logger.debug(" [%s %s" % (fun, url))

    t_start = time.time()

    status = False
    step = 0

    while True:
        step += 1
        _ = {
            "u": url,
            "limit": 1,
            "otl": 0,
        }
        r = pycus_u(_)

        if step > 1:
            logger.error("step %s, some error - check:" % step)
            show_dict(r)

        html = r["html"]
        error = r["error"]
        kod = r["kod"]

        # logger.debug("%s html=%s" % (type(html), html))

        if '{"value":{"error":"unknown command","message":"GET /' in html:
            status = "success"

        elif "HTTP method not allowed" == html:
            status = "success"

        elif "marionetteProtocol" in error:
            status = "success"  # 			"('Connection aborted.', BadStatusLine('50:{"applicationType":"gecko","marionetteProtocol":3}',))" - marionette

        elif (
            "No connection could be made because the target machine actively refused"
            in error
            or "Failed to establish a new connection: [WinError 10061]"
            in error
        ):  # когда на порту ничего нет
            status = "connection_refused"

        elif " [Errno 10061]" in error:  # когда на порту ничего нет
            status = "connection_refused"

        elif kod in [200, 404]:
            status = "kod %s" % kod

        if status:
            break

        sleep_(0)

        if step > 10:
            show_dict(r)
            inform_me("%s error" % fun)
            break

    duration = time.time() - t_start
    logger.info(
        "   +[%s status=%s in %.1f seconds for `%s`]"
        % (fun, status, duration, url)
    )
    # wait_for_ok(fun)
    return status


##### init  captcha_solver + stats_collector
_ = {
    "rucaptcha_key": "",
}
# captcha_solver = CaptchaSolver(_)

short_names = {
    "already_downloaded": "a",
    "downloaded": ".",
    "captcha": "C",
}
stats_collector = StatsCollector("crawler_stats", short_names=short_names)


# in explore_selenium.py
if __name__ == "__main__":
    pass
