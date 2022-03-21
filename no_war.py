# -*- coding: utf-8 -*-

from no_war_project.settings import *

# from no_war_project import *

# print("no_war")
from no_war_project.no_war_browser import *

# print("no_war2")

import optparse

logger = get_logger(__name__)

t = 1
if t:
    zsuv = 2
    frmt = "print"
    want_format = True

    setup_all_loggers(zsuv=zsuv, want_format=want_format, frmt=frmt)


class NoWar:
    """
    нет войне - автожалоба
    """

    def __init__(
        self,
        d=None,
        d_dev=None,
        d_profile=None,
        pwd=None,
        lang=None,
        work_with=None,
        delays_between_reports=None,
    ):
        if not d:
            d = get_f_here_main()
        kwargs = {
            "d": d,
            "d_dev": d_dev,
            "d_profile": d_profile,
            "pwd": pwd,
            "want_start_browser": False,
            "lang": lang,
            "work_with": work_with,
            "delays_between_reports": delays_between_reports,
        }
        # wait_for_ok(kwargs)
        klas = NoWarBrowser

        browser = klas(**kwargs)
        logger.debug(f"{browser=}")
        self.browser = browser

    def work_in_browser(self):
        browser = self.browser

        browser.start_browser_if_need()

        kwargs = {
            # "max_step": 1,
            # "tasks_za_raz": 1,
            # 'max_duration': 60,
        }
        result = browser.no_war_mozg(**kwargs)
        logger.info(f"no_war_mozg {result=}")

        # logger.info("start debug")
        # browser.explore_function()


def parse_args(args=None):
    if getattr(sys, "frozen", False):
        # cx_freeze windows:
        d_root = os.path.dirname(sys.executable)
        # multiprocessing.freeze_support()
    else:
        # everything else:
        d_root = os.path.dirname(os.path.realpath(__file__))

    d_dev = d_root + r"\data\development"
    d_profile = d_root + r"\data\development\GoogleChromePortable64\Data\profile"

    t = 0
    if t:
        d_root = r"s:\!kyxa\!code\no_war"
        d_dev = r"s:\!data\!no_war\installs\development"
        d_profile = "s:\!data\!no_war\profiles\profile"

    parser = optparse.OptionParser("usage: %prog [options] target")
    parser.add_option(
        "-d",
        "--dir",
        dest="d_root",
        default=d_root,
        type="string",
        help="directory with tasks and settings (default=directory of .EXE)",
    )
    parser.add_option(
        "-v",
        "--dir_dev",
        dest="d_dev",
        default=d_dev,
        type="string",
        help="directory with development tools (default=directory of .EXE)",
    )
    parser.add_option(
        "-p",
        "--profile",
        dest="d_profile",
        default=d_profile,
        type="string",
        help="chrome profile directory",
    )

    (options, args) = parser.parse_args(args)
    # logger.debug(f"{options=} {type(args)=} {args=}")

    for k, v in options.__dict__.items():
        k = k.strip()
        v = v.strip()
        options.__dict__[k] = v

    # if len(args) < 1 and options.filter == "" and options.targets == "":
    #     parser.error("You must provie a target. Use -h for help.")

    return options


def get_f_here_main(name=""):
    if getattr(sys, "frozen", False):
        # cx_freeze windows:
        d_root = os.path.dirname(sys.executable)
        # multiprocessing.freeze_support()
    else:
        # everything else:
        d_root = os.path.dirname(os.path.realpath(__file__))
    return os.path.abspath(f"{d_root}/{name}")


if __name__ == "__main__":
    special = "parse_args"
    special = "NoWar"

    args = parse_args()
    logger.debug(f"{args=}")

    if special == "parse_args":
        args = ["--dir", "nah", "--profile", "/profile", "--dir_dev", "f:/dev"]
        args = parse_args(args)
        logger.info(f"{args=}")

    elif special == "NoWar":

        f = get_f_here_main("налаштування.txt")
        logger.debug(f"settings from {f=}")
        settings = get_default_settings(f=f)
        kwargs = {
            "d": args.d_root,
            "d_dev": args.d_dev,
            "d_profile": args.d_profile,
            "pwd": "{eq  dfv f yt Erhf]ye",
            "lang": settings["lang"],
            "work_with": settings["work_with"],
            "delays_between_reports": settings["delays_between_reports"],
        }
        ideal = NoWar(**kwargs)
        ideal.work_in_browser()

    else:
        logger.critical(f"no {special=}")
