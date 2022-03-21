#!/usr/bin/python
# -*- coding: utf-8 -*-

r"""
!!!СИНХРОНИЗИРУЙ PY2-PY3 sync_py2_py3
s:\!kyxa\!code\!documentation\py4seo\advanced\08\dor_minimum\modules\redis_funcs.py
s:\python2.7\Lib\site-packages\modules\redis_funcs.py
"""

from modules.my_audio import inform_critical
from modules.logging_functions import get_logger

# для питон2-питон3
try:
    from modules.test_helpers import sleep_
except Exception as er:
    from modules.my_translit_ import sleep_

from modules.inspection_functions import *
import time

logger = get_logger(__name__)


def try_execute_function(
    task={},
    max_cnt_tries=0,
    max_duration=60 * 10,
    message="redis not working",
    seconds_sleep_on_error=1,
    critical_errors=[],
    errors_to_break=[],
):
    """
    пробую выполнить ф-ю пока хватает сил :)
    -> {"break_error": ... если ошибка в errors_to_break}
    """
    func, args, kwargs = parse_func_args_kwargs(task)
    func_name = func.__name__
    t_start = time.time()
    step = 0
    result = None

    while True:
        step += 1
        duration = time.time() - t_start
        er = ""
        if max_duration and duration > max_duration:
            er = "duration %d > %s max_duration" % (duration, max_duration,)

        elif max_cnt_tries and step > max_cnt_tries:
            er = "step %d > %s max_cnt_tries" % (step, max_cnt_tries)

        if er:
            er = "ERROR: %s %s" % (message, er)
            logger.critical(er)
            inform_critical(er)

        try:
            result = func(*args, **kwargs)
            break
        except Exception as er:
            logger.error(
                f"ERROR {func_name} - {step=} (from start {duration}), {er=}"
            )
            error = str(er)
            for critical_error in critical_errors:
                if critical_error in error:
                    m = f"critical_error: {error}"
                    logger.critical(m)
                    inform_critical(m)

            for error_to_return in errors_to_break:
                if error_to_return in error:
                    m = f"break_error: {error}"
                    logger.warning(m)
                    return {"break_error": error}

            sleep_(seconds_sleep_on_error)
    return result


def func_to_test(*args, **kwargs):
    return {"args": args, "kwargs": kwargs}


if __name__ == "__main__":
    task = {"func": func_to_test, "args": (1, 2,), "kwargs": {"x": "y",}}
    r = try_execute_function(task)
    logger.debug("r=%s" % r)
