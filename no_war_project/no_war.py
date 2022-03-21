from no_war_project.settings import *

# from modules import *
from no_war_project.no_war_browser import *
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
        }
        # wait_for_ok(kwargs)
        klas = NoWarBrowser

        browser = klas(**kwargs)
        logger.debug(f"{browser=}")
        self.browser = browser

    def work_in_browser(self):
        browser = self.browser
        r = browser.browser_start_or_reconnect()

        logger.debug0(f"+browser_start_or_reconnect {r=}")

        kwargs = {
            # 'max_step': 1,
            # 'max_duration': 60,
            # 'tasks_za_raz': 1,
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

    parser = optparse.OptionParser("usage: %prog [options] target")
    d_dev = d_root + r"\data\development"
    d_profile = (
        d_root + r"\data\development\GoogleChromePortable64\Data\profile"
    )

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
            "pwd": "no_war",
            "lang": settings["lang"],
            "work_with": settings["work_with"],
        }
        ideal = NoWar(**kwargs)
        ideal.work_in_browser()

    else:
        logger.critical(f"no {special=}")
