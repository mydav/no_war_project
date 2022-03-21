from functools import wraps
import time
from random import randint
from modules.logging_functions import get_logger

logger = get_logger(__name__)


def my_timer(func):
    @wraps(func)
    def wrapper_my_timer(*args, **kwargs):
        print_h1(f"{func.__name__}")
        t_start = time.time()
        res = func(*args, **kwargs)
        seconds = time.time() - t_start
        print(f"timer: in {seconds:.2f} seconds for {func.__name__}")
        print("-" * 50 + "\n")
        return res

    return wrapper_my_timer


def print_h1(message: str = ""):
    print("\n" + "<" * 40)
    print("=" * 10 + message)
    print(">" * 40 + "\n")


def sleep_(seconds, want_print=True, otl=None, fun="sleep_"):
    if otl is not None:
        want_print = otl

    if isinstance(seconds, str) and str(seconds).find("-") != -1:
        ot, do = str(seconds).split("-")
        seconds_sleep = randint(int(ot), int(do))
        mess = "%s-%s=%s" % (ot, do, seconds_sleep)
    else:
        seconds = float(seconds)
        seconds_sleep = seconds
        mess = seconds_sleep

    if seconds_sleep not in [0.0, 0]:
        if want_print:
            logger.debug(f"           [{fun} {mess}")
            # print("            [%s %s" % (fun, mess), end="")

        time.sleep(seconds_sleep)

        # if 1 and want_print:
        #     print("+]")


def sleep0_(seconds, want_print=True, otl=None):

    if not otl:
        want_print = otl

    if want_print:
        print(f"sleep_{seconds:.2f}...", end="", flush=1)

    time.sleep(seconds)

    if want_print:
        print(f"+")


if __name__ == "__main__":
    # sleep_(1)
    sleep_("2-25")
    print_h1("hello")
