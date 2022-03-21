from modules import *

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options


def get_perf_log_on_load(url, headless=True, filter=None):

    # init Chrome driver (Selenium)
    options = Options()
    options.headless = headless
    cap = DesiredCapabilities.CHROME
    # cap['loggingPrefs'] = {'performance': 'ALL'}
    cap["goog:loggingPrefs"] = {"performance": "ALL"}

    executable_path = r"s:\!data_main\chromedrivers\chromedriver_89.exe"
    driver = webdriver.Chrome(
        desired_capabilities=cap,
        options=options,
        executable_path=executable_path,
    )

    # record and parse performance log
    driver.get(url)
    if filter:
        log = [
            item
            for item in driver.get_log("performance")
            if filter in str(item)
        ]
    else:
        log = driver.get_log("performance")
    driver.close()

    return log


kwargs = {
    "url": "https://www.bet365.es/#/HO/",
    "url": "https://whoer.net",
    "headless": False,
}
logs = get_perf_log_on_load(**kwargs)
show_list(logs)

wait_for_ok()
