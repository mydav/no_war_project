# from modules import *
from modules.test_helpers import sleep_
import time

try:
    import winsound
except Exception as er:
    pass


def inform_me(message=""):
    print(f"INFORM: {message=}")
    step = 0
    while True:
        step += 1
        beep()
        # print(step)
        # print(f"{step}", end="\r")
        end = "\n\r"
        end = "\r"  # в pycharm не работает
        print(time.ctime(), end=end, flush=True)
        sleep_(1, want_print=False)


def beep(duration=1000):
    # print 'beep',
    # print('\a')

    frequency = 2500  # Set Frequency To 2500 Hertz

    try:
        winsound.Beep(frequency, duration)
    except Exception as er:
        print(f"ERROR beep")
    # winsound.Beep()


if __name__ == "__main__":
    inform_me("hello")
