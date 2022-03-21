from modules import *

logger = get_logger(__name__)

try:
    import undetected_chromedriver.v2 as uc
except Exception as er:
    logger.debug(f"can not import undetected_chromedriver")


def get_driver_undetectable(
    d_profile=None, f_driver=None, f_exe=None, port=None, **kwargs
):
    logger.debug("[get_driver_undetectable")

    headless = kwargs.get("headless", False)

    options = uc.ChromeOptions()

    # setting profile
    if d_profile:
        options.user_data_dir = d_profile
        # another way to set profile is the below (which takes precedence if both variants are used
        options.add_argument(f"--user-data-dir={d_profile}")

    # just some options passing in to skip annoying popups
    options.add_argument(
        "--no-first-run --no-service-autorun --password-store=basic"
    )

    t = 0
    if t:
        options.service_log_path = "temp/driver_log.log"
        options.debug = True
        options.log_level = 1

    if headless:
        options.headless = True

    kwargs = {
        "options": options,
        "version_main": 98,
    }
    if f_driver:
        kwargs["executable_path"] = f_driver

    if f_exe:
        kwargs["browser_executable_path"] = f_exe

    if port:
        kwargs["debug_port"] = port

    if headless:
        # options.add_argument("--headless")
        # options.headless = True
        kwargs["headless"] = True

    driver = uc.Chrome(**kwargs)

    t = 0
    if t:
        driver.get(
            "https://nowsecure.nl"
        )  # known url using cloudflare's "under attack mode"

    return driver


def reconnect_to_existing_undetectable_chrome(port=6814, f_driver=None):
    fun = "reconnect_to_existing_undetectable_chrome"
    logger.debug(f"[{fun} {port=} {f_driver=}")
    # chrome_options = chromeOptions()
    chrome_options = uc.ChromeOptions()

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

    logger.debug(f"   +{driver=}")
    # print(driver.title)
    # driver.get(f"https://google.com/#{get_human_time()}")
    return driver
