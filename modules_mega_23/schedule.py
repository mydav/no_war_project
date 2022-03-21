#!/usr/bin/python
# -*- coding: utf-8 -*-

from modules.logging_functions import *
from modules_23.random_functions import seconds_from_str

# print(seconds_from_str)

# from time import strftime
# from time import gmtime
import datetime
import time

logger = get_logger(__name__)


def is_now_in_good_hours(good_hours=[], seconds=None, zsuv=None):
    """проверяем что попадаем в нужный час"""
    fun = "is_now_in_good_hours"

    if not isinstance(good_hours, list):
        good_hours = get_good_hours(good_hours)

    hour = get_hour(seconds, zsuv=zsuv)

    if hour in good_hours:
        status = True
    else:
        status = False
    logger.debug(
        "[%s=%s for hour=%s (good_hours=%s, zsuv=%s)]"
        % (fun, status, hour, good_hours, zsuv)
    )

    return status


def get_good_hours(line="1-24"):
    working_hours = "9-12,15-19"  # рабочее время
    line_to_replaces = {
        "working_hours": working_hours,  # рабочее время
        "working_hours+evening": "%s,22-23" % working_hours,
    }
    line = line_to_replaces.get(line, line)

    items = [_ for _ in line.split(",")]
    all_hours = []
    for item in items:
        item = item.strip()
        if not item:
            continue
        if "-" in item:
            ot, do = item.split("-")
            ot = ot.strip()
            ot = seconds_from_str(ot)
            do = seconds_from_str(do)
            hours = range(ot, do + 1)
            all_hours += hours
        else:
            all_hours.append(seconds_from_str(item))
    all_hours = list(set(all_hours))
    all_hours.sort()
    return all_hours


def get_seconds_to_the_next_hour():
    """секунд до следующего времени"""

    delta = datetime.timedelta(hours=1)
    now = datetime.datetime.now()
    next_hour = (now + delta).replace(microsecond=0, second=0, minute=0)

    wait_seconds = (
        next_hour - now
    ).seconds + 3  # поправка :)) Реально глючило
    logger.debug(
        "now=%s, next_hour=%s, wait_seconds=%s"
        % (now, next_hour, wait_seconds)
    )
    return wait_seconds


def get_hour(seconds, zsuv=None):
    if zsuv is None:
        zsuv = 0

    if not seconds:
        seconds = time.time()
        seconds = seconds + zsuv * 60 * 60

    seconds_dt = datetime.datetime.fromtimestamp(seconds)
    hour = seconds_dt.hour
    logger.debug(
        "hour=%s for seconds_dt=%s for zsuv %s" % (hour, seconds_dt, zsuv)
    )
    return hour

    # это всякими извратами
    timenow = time.ctime(seconds)  # fetch local time in string format
    timeinhrs = timenow[11:19]
    hours = seconds_from_str(timeinhrs.split(":")[0])

    t = 1
    if t:
        # return int(seconds // 3600 % 24)
        timeinhrs2 = strftime("%H:%M:%S", gmtime(seconds))

        logger.debug(
            "hours=%s, timeinhrs=%s, timeinhrs2=%s  from timenow=%s"
            % (hours, timeinhrs, timeinhrs2, timenow)
        )
    return hours


if __name__ == "__main__":
    from modules import *

    special = "nah"

    if special == "nah":
        pass
    else:
        hours = "1-2, 4 , 8, 16-19, 18 - 20, "
        hours = "working_hours"
        good_hours = get_good_hours(hours)
        logger.info("good_hours=%s" % good_hours)

        zsuv = 0
        zsuv = -2

        is_good_time = is_now_in_good_hours(good_hours, zsuv=zsuv)
        logger.info("is_good_time=%s" % is_good_time)

        seconds_to_the_next_hour = get_seconds_to_the_next_hour()
        logger.info("seconds_to_the_next_hour=%s" % seconds_to_the_next_hour)
