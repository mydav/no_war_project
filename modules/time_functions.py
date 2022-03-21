import time
import os
from modules.text_functions import find_from_to_one
import datetime
from random import choice

from modules.logging_functions import get_logger

logger = get_logger(__name__)


def get_human_time(seconds="", frmt="%Y-%m-%d %H:%M:%S"):
    if seconds == "":
        seconds = time.time()
    return time.strftime(frmt, time.localtime(seconds))


def convert_humantime_in_str_to_seconds(date_from, frmt="%Y-%m-%d %H:%M:%S"):
    """last_24h or """
    debug = True
    debug = False
    if debug:
        print(f"convert {date_from=} with {frmt=}")
    last_hours = find_from_to_one("last_", "h", date_from)
    if last_hours:
        last_hours = float(last_hours.replace(",", "."))
        seconds = time.time() - 60 * 60 * last_hours
    else:
        seconds = convert_time_in_str_to_seconds(date_from, frmt=frmt)
    return seconds


def convert_time_in_str_to_seconds(time_str, frmt="%Y-%m-%d %H:%M:%S"):
    """
        получи время в строчном виде, и конвертнул его в секунды
            #>>> x = datetime.strptime('Jul 1 12:00:00 2015 GMT', '%b %d %H:%M:%S %Y %Z')
            #>>> x.timestamp()
            #1435744800.0

    """
    seconds = time.mktime(time.strptime(time_str, frmt))
    return seconds


def mlsec(tpl="%Y-%m-%d %H:%M:%S.{}", created_at=None):
    if created_at == None:
        created_at = time.time()

    # https://stackoverflow.com/a/41679167
    mlsec = repr(created_at).split(".")[1][:3]
    created_at_human = time.strftime(
        tpl.format(mlsec), time.localtime(created_at),
    )
    return created_at_human


def get_date_in_range_from_now(
    day_start="now", day_in_last=-10, day_in_future=0, return_format="human"
):
    """получаем случайную дату - говорим сколько дней назад и сколько дней вперед можно 2009-01-01"""
    if day_start == "now":
        day_start = str(datetime.date.today())
        # print(day_start)

    day_in_last = int(day_in_last)
    day_in_future = int(day_in_future)

    parts1 = list(map(int, day_start.split("-")))
    # print(parts1)
    year_ot = parts1[0]
    month_ot = parts1[1]
    day_ot = parts1[2]

    now = datetime.date(year_ot, month_ot, day_ot)
    difference1 = datetime.timedelta(
        days=choice(range(day_in_last, day_in_future + 1))
    )
    #    print day_start, difference1

    new_date = now + difference1

    human_date = "%s %02d:%02d:%02d" % (
        new_date,
        choice(range(1, 24)),
        choice(range(1, 60)),
        choice(range(1, 60)),
    )
    if return_format == "human":
        return human_date
    elif return_format == "seconds":
        frmt = "%Y-%m-%d %H:%M:%S"
        return convert_time_in_str_to_seconds(human_date, frmt)
    else:
        logger.error(f"unknown {return_format=}")


def get_human_duration(
    seconds=None, round_to=0, want_remove_zeros: bool = False
):
    """
    человеческая продолжительность - все 33837 секунд пишет дни и т.д.
    """
    seconds = round(seconds, round_to)
    r = "{:0>8}".format(str(datetime.timedelta(seconds=seconds)))

    # удаляю пустые часи-минуты-секунды
    if want_remove_zeros:
        bad_starts = ["00:"]
        while True:
            found = False
            for bad in bad_starts:
                if r.startswith(bad):
                    found = True
                    r = r[len(bad) :]
            if not found:
                break
    return r


if __name__ == "__main__":
    special = "convert_time_in_str_to_seconds"
    special = "get_date_in_range_from_now"
    special = "get_human_duration"
    if special == "get_human_duration":
        durations = [
            1.2342342,
            0.2342342,
            78,
            366,
            2342,
            29992,
            29734927,
        ]
        for seconds in durations:
            h = get_human_duration(seconds)
            logger.debug(f"{seconds=} {h=}")

    if special == "get_date_in_range_from_now":
        return_format = "human"
        return_format = "seconds"
        for i in range(100):
            d = get_date_in_range_from_now(
                "now", -30, return_format=return_format
            )
            print(d)

    elif special == "convert_time_in_str_to_seconds":
        time_str = "05/Mar/2020:19:43:43"
        frmt = "%d/%b/%Y:%H:%M:%S"

        # time_str = '05/Mar/2020:19'
        # frmt = '%d/%b/%Y:%'

        t = 1
        if t:
            frmt = "%Y-%m-%d %H:%M:%S"
            time_str = "2021-07-14 01:27:38"

        seconds = convert_time_in_str_to_seconds(time_str, frmt)

        new_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(seconds))

        print(time_str, new_time)
        os._exit(0)
