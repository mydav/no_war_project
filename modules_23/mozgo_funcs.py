#!/usr/bin/python
# -*- coding: utf-8 -*-

from modules.logging_functions import get_logger
from modules.file_functions import file_life, text_to_file
import time

logger = get_logger(__name__)


def timed_func(t):
    # запуск ф-ии в поток
    fun = "timed_func"

    func = t["func"]
    args = t.get("args", ())
    kwargs = t.get("kwargs", {})
    seconds = t.get("seconds", 60)
    mark_on_start = t.get(
        "mark_on_start", True
    )  # отмечаем выполненной ф-ю вначале, иначе вконце

    if seconds is None:
        logger.debug("%s - seconds None, so exit" % (func))
        return

    seconds = int(seconds)

    name = t.get("name", func.__name__)
    f_life = t.get("f", "temp/timed_funcs/%s" % name)

    life = file_life(f_life)
    logger.info(
        "[timed_func %s... name:%s, life: %d, seconds %d - "
        % (name, f_life, life, seconds)
    )

    if seconds is None:
        logger.debug("  seconds==None, so nothing to do")
        return

    # if False:
    if life > seconds or life == -1:
        logger.info("  %s - RUUUUN %s!" % (fun, name))
        if mark_on_start:
            text_to_file("", f_life)

        t0 = time.time()
        res = func(*args, **kwargs)
        # if args=='no_args':
        #     res = func(*args, **kwargs)
        #     res = func()
        # else:
        #     res = func(args)

        if not mark_on_start:
            text_to_file("", f_life)

        logger.info("  +%s]" % name)
        time_next = seconds

    else:
        logger.debug("  too early %s]" % name)
        time_next = seconds - life
        res = {"timed_status": "too_early", "time_next": time_next}

    # wait_for_ok('zapuskatj?')

    # seconds = int( (time.time()-t0)/60 )
    # minu = int(seconds/60)
    # print 'func_v_potok: %s done in %d minutes (%d seconds)]' % (name, minu, seconds)
    #    wait_for_ok('norm v potok?')
    # return time_next
    return res


def demo_func():
    logger.info("EXECUTE demo_func")
    return 1


if __name__ == "__main__":
    _ = {
        "func": demo_func,
    }
    r = timed_func(_)
    logger.debug("r=%s" % r)
