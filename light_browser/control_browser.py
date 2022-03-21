# -*- coding: utf-8 -*-

from modules_23.random_functions import get_random_value_in_range

from selenium_helpers.chrome.chrome_starter import (
    run_chrome_with_special_profile,
    is_chrome_with_special_port_active,
)
from selenium.webdriver.chrome.options import Options as chromeOptions

from selenium_functions.selenium_funcs import *
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from modules_mega_23.xpath_functions import Xpather
from translator.my_translator import Translator

# from multiprocessing.pool import ThreadPool as Pool
# from light_browser.undetected_browser import *

logger = get_logger(__name__)


class LightBrowser(Xpather):
    def __init__(
        self,
        d=None,
        d_dev=None,
        d_profile="",
        name="",
        d_temp=None,
        want_start_browser=False,
        seconds_random_sleep="1-2",
        kwargs_search_element=None,
        lang="en",
        # mode_driver="undetectable",
        mode_driver="normal",
        **kwargs,
    ):
        if not name:
            name = "NoWarBrowser"

        self.mode_driver = mode_driver

        self.name = name

        if not d:
            d = get_f_here()
        self.d = d
        # d_temp
        if d_temp is None:
            d_temp = "temp"

        dir_name = self.name
        if not d_temp.endswith(dir_name):
            d_temp = f"{d}/{d_temp}/user_{dir_name}"
        d_temp = os.path.abspath(d_temp)

        self.d_temp = d_temp

        # profile
        if not d_dev:
            d_dev = self.d
        self.d_dev = d_dev
        self.f_driver = self.get_f_dev("chromedriver_98.exe")
        self.f_exe = self.get_f_dev(
            r"GoogleChromePortable64\App\Chrome-bin\chrome.exe"
        )
        logger.debug(f"f_driver={self.f_driver}, f_exe={self.f_exe}")

        if not d_profile:
            d_profile = self.get_f_dev(r"GoogleChromePortable64\Data\profile")

        self.d_profile = d_profile

        self.S = None
        self.driver = None

        self.lang = lang
        self.translator = self.get_translator()

        # self.xpather = Xpather(dct=xpaths)
        xpaths = self.get_important_xpaths()
        Xpather.__init__(self, dct=xpaths, special=[])
        self.update_xpaths_for_browser(xpaths)

        self.seconds_random_sleep = seconds_random_sleep
        if not kwargs_search_element:
            kwargs_search_element = {
                "timeout": 20,
                "timeout": 5,
                "checking": "clickable",
            }
        self.kwargs_search_element = kwargs_search_element

        if want_start_browser:
            self.browser_start_or_reconnect()

    def explore_function(self):
        special = "check_browser_is_controlled"
        if special == "check_browser_is_controlled":
            r = self.S.check_browser_is_controlled()
            logger.debug(f"{special} {r=}")
        else:
            logger.critical(f"unknown {special=}")

    def action(
        self,
        xpath="insta_skarga1",
        message=f"click skarga",
        warning_not_exists="element to click not found",
        error_not_exists="no_3_dots",
        click_method="click_js",
        want_highlight=False,
        kwargs_search_element=None,
        select_random=False,
    ):
        if not kwargs_search_element:
            kwargs_search_element = self.kwargs_search_element
        S = self.S
        error = None
        xpath = self.xpath(xpath)
        logger.debug2(message)
        element = S.wait_for_presence(xpath, **kwargs_search_element)
        if not element:
            logger.warning(warning_not_exists)
            error = error_not_exists
        else:
            if select_random:  # выбрать рандомный элемент
                elements = S.search_elements_xpath(xpath)
                element = choice(elements)

            if want_highlight:
                r = S.hover_xpath(element=element, seconds_highlight=-1,)

            sending = [
                [element, click_method],
            ]
            r_clicked = S.ssend_values_quick(sending)
            logger.debug(f"{r_clicked=}")
            self.random_sleep()
        return error

    def random_sleep(self):
        ot_do = self.seconds_random_sleep
        seconds = get_random_value_in_range(ot_do)
        logger.debug(f"random sleep {seconds} from {ot_do}")
        sleep_(seconds, 0)

    def save_page_to_debug_situation(
        self, name="last_error", page=None, want_screenshot=False
    ):
        fun = "save_page_to_debug_situation"
        S = self.S
        if not page:
            page = S.sgp()

        if want_screenshot:
            f_screenshot = self.get_f(name=f"!debug/{name}", rash=".png")
            mode = "new"
            mode = "selenium"

            if mode == "selenium":
                _ = {
                    "f_to": f_screenshot,
                    "mode_maximum_height": "body",
                }
                try:
                    r = S.screenshot_element(_)
                    logger.debug(f"+screenshot_element {r=}")
                except Exception as er:
                    logger.debug(f"screenshot impossible, {er=}")
            else:
                driver = S.driver
                elem = driver.find_element_by_tag_name("body")
                total_height = elem.size["height"] + 1000
                driver.set_window_size(1920, total_height)
                time.sleep(2)
                driver.save_screenshot(f_screenshot)

        if page:
            f_to = self.get_f(name=f"!debug/{name}")

            logger.debug(f" +{fun}: saved page {name} to debug, {f_to=}")
            page = f'<head><meta charset="UTF-8"></head>\n{page}'
            text_to_file(page, f_to)
        else:
            logger.error(
                f"{fun}: unable to save error {name} (page not available)"
            )

    def browser_start_or_reconnect(self, more_extensions=[]):
        f_cache = self.get_f(f"driver.dat")
        reason = "no_cache"
        if 1 or (not file_exists(f_cache)):
            reason = "no cache"
        else:
            try:
                driver = obj_from_file(f_cache)
            except Exception as er:
                reason = f"damaged {f_cache=}"
                logger.warning(reason)
                rmfile(f_cache)

        step_start = 0
        while True:
            step_start += 1
            if reason:
                logger.info(f"start browser {step_start}")
                driver = self.start_browser(more_extensions=more_extensions)

            if driver:  # проверяем - работает?
                _ = {
                    "s_driver": driver,
                }
                S = wrap_selenium_class(_)
                url = S.url()
                logger.debug(f"url in browser={url=}")

                t = 0
                if t:
                    logger.debug(f"successful connection, saving to {f_cache}")
                    obj_to_file(driver, f_cache)
                break

        self.driver = driver
        self.S = S
        return self.driver

    def start_browser(self, *args, **kwargs):
        want_try = False
        if not want_try:
            r = self.start_browser_one(*args, **kwargs)
        else:
            try:
                r = self.start_browser_one(*args, **kwargs)
            except Exception as e:
                error = str(e)
                if "user data directory is already in use" in error:
                    m = "You've already opened the browser. Please close it and restart the program.\nУЖЕ ЕСТЬ ОТКРЫТЫЙ БРАУЗЕР - ЗАКРОЙТЕ ЕГО СНАЧАЛА"
                    logger.critical(m)

                m = "Impossible to start the browser\nНевозможно открыть браузер"
                logger.critical(m)
                inform_critical(m)
        return r

    def start_browser_one(self, more_extensions=[]):
        u_start = "https://nowsecure.nl"  # known url using cloudflare's "under attack mode"
        u_start = (
            "https://www.youtube.com/channel/UCjWy2g76QZf7QLEwx4cB46g/about"
        )
        logger.debug("start chrome")

        want_reconnect = True
        want_reconnect = False

        command_executor = "http://localhost:64699"
        if want_reconnect:
            logger.debug("reconnect")
            # reconnect
            driver = webdriver.Remote(command_executor=command_executor)
            u_start = f"{u_start}###reconnect"

        elif 1 == 1:
            _ = {
                "d_profile": self.d_profile,
                "f_driver": self.f_driver,
                "f_exe": self.f_exe,
                "more_extensions": more_extensions,
            }
            # _ = {
            #     "d_profile": self.d_profile,
            # }
            logger.debug(f"{_}")
            if self.mode_driver == "undetectable":
                func = get_driver_undetectable
            else:
                func = get_driver
            driver = func(**_)

        else:
            # another way to set profile is the below (which takes precedence if both variants are used

            # options.add_argument(f'--no_war_browser--')
            # options.add_argument(f'--remote-debugging-port=9222')
            # options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

            options.add_argument(f"--user-data-dir={self.d_profile}")

            # just some options passing in to skip annoying popups
            options.add_argument(
                "--no-first-run --no-service-autorun --password-store=basic"
            )

            logger.debug(f"    init chrome with {options=}...")
            wait_for_ok()

            _ = {
                # 'options': options,
                # 'executable_path': f_driver,
            }
            driver = uc.Chrome(**_)
            wait_for_ok(f"{driver=}")

        command_executor = driver.command_executor._url
        session_id = driver.session_id

        logger.debug(
            f"driver.command_executor._url: {command_executor}"
        )  # http://localhost:63925/
        logger.debug(f"driver.session_id: {session_id}")

        return driver

        logger.debug(f"open url {u_start}")
        driver.get(u_start)
        wait_for_ok("opened?")

        t = 1
        if t:
            driver2 = webdriver.Remote(
                command_executor=command_executor, desired_capabilities={}
            )
            driver2.command_executor._url
            driver2.session_id = session_id
            logger.debug(f"url in new browser={driver2.current_url}")
            driver2.get("https://google.com")
            wait_for_ok("opened google?")

    def get_translator(self, lang=None, translations=None):
        if not lang:
            lang = self.lang
        return Translator(lang=lang, translations=translations)

    def get_f(self, name="", rash=".html", d_to=""):
        if not d_to:
            d_to = self.d_temp
        return self.get_f_here(f"{name}{rash}", d_to)

    def update_xpaths_for_browser(self, xpaths=None):
        if not xpaths:
            xpaths = self.get_important_xpaths()
        self.xpath_dict = xpaths

    def get_important_xpaths(self):
        return {}

    def get_f_dev(self, name):
        return f"{self.d_dev}\{name}"

    def get_f_here(self, name="", d=None):
        """получаем файл относительно этой папки"""
        if d is None:
            d = self.d
        return f"{d}\{name}"

    def __repr__(self):
        return f"<LightBrowser:{self.name}, d={self.d}, d_profile={self.d_profile}, d_dev={self.d_dev} >"


def get_driver(
    d_profile=None,
    f_driver=None,
    port=0,
    f_exe=None,
    want_test_driver: bool = True,
    mode_driver="normal",
    more_extensions=[],
):
    _ = {
        "d_profile": d_profile,
        "f_driver": f_driver,
        "port": port,
        "f_exe": f_exe,
    }
    I = get_browserConnect_info(**_)
    # logger.debug(f"{_=}")
    # logger.debug(f"{I=}")

    chrome_command_line_arguments = [
        "--no-first-run --no-service-autorun --password-store=basic"
    ]
    if more_extensions:
        more_extensions = [os.path.realpath(_) for _ in more_extensions]
        extensions_line = ",".join(more_extensions)
        chrome_command_line_arguments.append(
            # f'--load-extension="{extensions_line}"'
            f"--load-extension={extensions_line}"
        )
    logger.debug(f"start browser with {I}, {chrome_command_line_arguments=}")
    # os._exit(0)
    r = run_chrome_with_special_profile(
        f_chrome=I.f_exe,
        profile_path=I.d_profile,
        debugger_port=I.port,
        chrome_command_line_arguments=chrome_command_line_arguments,
    )
    logger.debug(f"browser started: {r=}")
    error = get_api_error(r)
    if error:
        return r

    if mode_driver == "undetectable":
        func = reconnect_to_existing_undetectable_chrome
    else:
        func = reconnect_to_existing_chrome
    driver = func(port=I.port, f_driver=I.f_driver)
    logger.debug(f"{driver=}")
    if want_test_driver:
        browser_is_controlled = check_browser_is_controlled(driver)
        logger.debug(f"{browser_is_controlled=}")
    return driver


def get_driver_old(
    mode="existing_browser", d_profile=None, f_driver=None, port=0, f_exe=None,
):
    logger.debug(f"[get_driver {mode=}, {d_profile=}")

    if mode == "webdriver":
        options = webdriver.ChromeOptions()
    else:
        options = uc.ChromeOptions()
        # options = uc.Chrome()

    options.binary_location = f_exe

    # setting profile
    # options.user_data_dir = "c:\\temp\\profile"
    # options.add_argument(f'--remote-debugging-port={port}')

    # another way to set profile is the below (which takes precedence if both variants are used
    options.add_argument(f"--user-data-dir={d_profile}")

    # just some options passing in to skip annoying popups
    # options.add_argument('--no-first-run --no-service-autorun --password-store=basic')

    if mode == "webdriver":
        service = Service(f_driver, port=port)

        _ = {
            "service": service,
            "options": options,
            # 'version_main': 98,
            # 'executable_path': f_exe,
            "port": port,
        }
        # _ = {}

        driver = webdriver.Chrome(**_)

    elif mode == "existing_browser":
        driver = reconnect_to_existing_chrome(port, f_driver=None)

    else:
        _ = {}
        driver = uc.Chrome(**_)

    t = 0
    if t:
        test_driver(driver)

    return driver


def reconnect_to_existing_chrome(port=6814, f_driver=None):
    logger.debug(f"[reconnect_to_existing_chrome {port=} {f_driver=}")
    chrome_options = chromeOptions()
    # chrome_options = uc.ChromeOptions()

    chrome_options.add_experimental_option(
        "debuggerAddress", f"127.0.0.1:{port}"
    )
    # Change chrome driver path accordingly
    if not f_driver:
        f_driver = (
            "s:\!chaos\!no_war\dist\data\development\chromedriver_98.exe"
        )
    driver = webdriver.Chrome(f_driver, chrome_options=chrome_options)
    # driver = uc.Chrome(f_driver, options=chrome_options)

    driver.browser_pid = is_chrome_with_special_port_active(port)

    logger.debug(f"   +{driver=}")
    # print(driver.title)
    # driver.get(f"https://google.com/#{get_human_time()}")
    return driver


def get_free_port() -> int:
    """
    Determines a free port using sockets.
    """
    free_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    free_socket.bind(("127.0.0.1", 0))
    free_socket.listen(5)
    port: int = free_socket.getsockname()[1]
    free_socket.close()
    return port


def get_browserConnect_info(
    d_profile=None,
    f_driver=None,
    port=0,
    f_exe=None,
    want_check_cached_port=True,
):
    """
    проверяю - возможно есть браузер с открытым предыдущим портом - тогда порт верну тот же
    """
    if not d_profile:
        error = "empty d_profile"
        logger.critical(error)
        raise ValueError(error)

    if port in [0, None, "random"]:
        if not want_check_cached_port:
            port = get_free_port()
        else:
            h = to_hash(
                d_profile[0].lower() + d_profile[1:]
            )  # странно - запускаю одну прогу получаю D:/ , запускаю в командной строке получаю d:
            f_cache = get_f_here(f"temp/profile_to_ip/{h}")
            logger.debug(f"check cached port from {f_cache=} ({d_profile=})")

            reason = ""
            if not file_exists(f_cache):
                reason = "no f_cache with port"
            else:
                try:
                    port = int(text_from_file(f_cache))
                    browser_exists = is_chrome_with_special_port_active(port)
                    if not browser_exists:
                        reason = f"no browser on saved {port=}"
                        rmfile(f_cache)
                    else:
                        logger.debug(f"already exists chrome with {port=}")
                except Exception as er:
                    reason = "wrong port in file"
                    rmfile(f_cache)

            if reason:
                logger.debug(f"get random free port, {reason=}")
                port = get_free_port()
                text_to_file(str(port), f_cache)
                logger.debug(f"saved new {port } to cache")

    logger.debug(f"found random {port=}")

    if not f_driver:
        f_driver = (
            r"s:\!kyxa\!code\no_war\data\development\chromedriver_99.exe"
        )
        f_driver = r"s:\!kyxa\!code\no_war\data\development\chromedriver.exe"
        f_driver = (
            r"s:\!kyxa\!code\no_war\data\development\chromedriver_98.exe"
        )

    if not f_exe:
        f_exe = r"s:\!kyxa\!code\no_war\data\development\GoogleChromePortable64\App\Chrome-bin\chrome.exe"
        # f_exe = r"s:\!kyxa\!code\no_war\data\development\chrome.exe"

    info = {
        "port": port,
        "d_profile": d_profile,
        "f_driver": f_driver,
        "f_exe": f_exe,
    }
    return Bunch(info)


def get_f_here(name=""):
    if getattr(sys, "frozen", False):
        # cx_freeze windows:
        d_root = os.path.dirname(sys.executable)
        # multiprocessing.freeze_support()
    else:
        # everything else:
        d_root = os.path.dirname(os.path.realpath(__file__))
    return os.path.abspath(f"{d_root}/{name}")


def test_driver(driver):
    u_test = f"https://youtube.com#{get_human_time()}"
    u_test = f"https://nowsecure.nl#{get_human_time()}"
    driver.get(u_test)  # known url using cloudflare's "under attack mode"
    # wait_for_ok('loaded url?')


if __name__ == "__main__":
    f_driver = (
        r"s:\!data\!no_war\installs\development\chromedriver_undetected.exe"
    )

    browser_executable_path = (
        r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    )
    browser_executable_path = None
    browser_executable_path = r"e:\INSTALLS\development\GoogleChromePortable64\App\Chrome-bin\chrome.exe"
    browser_executable_path = r"s:\!data\!no_war\installs\development\GoogleChromePortable64\App\Chrome-bin\chrome.exe"  # thinkpad

    port = 9999

    d_profile = r"e:\\INSTALLS\\development\\profiles\\profile"
    d_profile = r"s:\!data\!no_war\profiles\profile"

    special = "get_driver_undetectable"
    special = "reconnect_to_existing_undetectable_chrome"
    special = "open_browser"

    if special == "reconnect_to_existing_undetectable_chrome":
        driver = reconnect_to_existing_undetectable_chrome(
            port=port, f_driver=f_driver
        )
        logger.info(f"reconnected, {driver=}")
        test_driver(driver)

    elif special == "get_driver_undetectable":
        driver = get_driver_undetectable(
            d_profile=d_profile,
            f_driver=f_driver,
            f_exe=browser_executable_path,
            port=port,
        )
        logger.info(f"undetectable {driver=}")

    elif special == "open_browser":
        kwargs = {
            "d": r"s:\!kyxa\!code\no_war",
            "want_start_browser": False,
        }
        klas = LightBrowser
        # klas = NoWarBrowser

        browser = klas(**kwargs)
        logger.debug(f"{browser=}")
        # logger.debug(f"{browser.get_f('nah')}")

        # logger.debug(f"demo xpath={browser.xpath('flazhok')}")
        # wait_for_ok()

        # wait_for_ok()

        r = browser.browser_start_or_reconnect()
        logger.debug1(f"+browser_start_or_reconnect {r=}")

        logger.info("start debug")

        # wait_for_ok()

    else:
        logger.critical(f"unknown {special=}")

    seconds_sleep = 1000000
    logger.debug(f"sleep {seconds_sleep} not to close")
    sleep_(seconds_sleep)
    os._exit(0)
