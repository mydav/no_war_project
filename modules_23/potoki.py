# -*- coding: utf-8 -*-
from time import time as time_time, sleep as time_sleep

# from threading import Thread
from concurrent.futures import ThreadPoolExecutor
from random import randint

from modules.logging_functions import get_logger

logger = get_logger(__name__)


class MagicThreader:
    """Наконец многопоточно могу спокойно делать все"""

    def __init__(
        self, max_workers=100, func=None, tasks=None, name="MagicThreader"
    ):
        self.func = func
        self.tasks = tasks
        self.max_workers = max_workers

        self.results = None
        self.results_detailed = None
        self.duration = None
        self.name = name

    def get_results(
        self,
        func=None,
        tasks=None,
        max_workers=None,
        return_mode="detailed",
        debug=False,
    ):
        """
        tasks это список аргументов (args, kwargs):
            args = (f"task_{num}", f"name_{num}", "arg_secret")
            kwargs = {
                "kwarg1": "111",
                "kwarg2": "222",
                "kwarg_secret": "secret",
            }
            task = (
                args,
                kwargs,
            )
            tasks.append(task)
            func = demo_threading_func

        """
        fun = "get_results"
        if func is None:
            func = self.func
        if tasks is None:
            tasks = self.tasks

        cnt_tasks = len(tasks)
        if max_workers is None:
            max_workers = self.max_workers
        if max_workers == "cnt_tasks":
            max_workers = cnt_tasks

        m = "[{self.name} {fun} {max_workers} workers run {cnt_tasks} tasks:".format(
            **locals()
        )
        logger.debug(m)

        t_start = time_time()

        results_detailed = []
        if max_workers == 1:
            for num, args_kwargs in enumerate(tasks, 1):
                if len(args_kwargs) == 2:
                    func_actual = func
                    args, kwargs = args_kwargs
                elif len(args_kwargs) == 3:  # На 1 месте - ф-я
                    func_actual, args, kwargs = args_kwargs
                else:
                    wait_for_ok(
                        "ERROR %s - unknown args=%s" % (fun, args_kwargs)
                    )
                logger.debug("func_actual=%s" % func_actual)
                timed_func = timed_wrapper_for_future(func_actual)
                duration_future, result = timed_func(*args, **kwargs)
                # results.append(result)
                _ = {
                    "result": result,
                    "duration": duration_future,
                }
                results_detailed.append(_)
                if debug:
                    logger.debug("%s %s" % (num, result))

        elif max_workers > 1:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                all_futures = []
                for num, args_kwargs in enumerate(tasks, 1):
                    # logger.debug('args_kwargs %s' % args_kwargs)
                    # wait_for_ok('good args_kwargs?')
                    func_actual = func
                    if isinstance(args_kwargs, dict):
                        args = ()
                        kwargs = args_kwargs
                    elif len(args_kwargs) == 2:
                        args, kwargs = args_kwargs
                    elif len(args_kwargs) == 3:  # На 1 месте - ф-я
                        func_actual, args, kwargs = args_kwargs
                    else:
                        wait_for_ok(
                            "ERROR %s - unknown args=%s" % (fun, args_kwargs)
                        )
                    # logger.debug('func_actual=%s' % func_actual)
                    my_future = executor.submit(
                        timed_wrapper_for_future(func_actual), *args, **kwargs
                    )
                    t = 0
                    if t:
                        logger.debug(
                            "%s %s" % (num, my_future)
                        )  # <Future at 0x14e283e1280 state=pending>
                        # logger.debug(dir(my_future))
                    # break
                    all_futures.append(my_future)

            # по мере готовности
            """
            for future in concurrent.futures.as_completed(all_futures):
                logger.debug(future.result())
            
            2: если может быть исключение:
            try:
                future.result() - 
            """

            # ждем пока все исполнятся
            for num, future in enumerate(all_futures, 1):
                duration_future, result = future.result()
                if 0 or debug:
                    logger.debug(
                        str[
                            num,
                            future,
                            result,
                            "in %.3f seconds" % duration_future,
                        ]
                    )

                _ = {
                    "result": result,
                    "duration": duration_future,
                }
                results_detailed.append(_)

        seconds = time_time() - t_start
        self.duration = seconds

        logger.debug(
            "max_workers={max_workers}, cnt_tasks={cnt_tasks} done in {seconds:.2f} seconds]".format(
                **locals()
            )
        )

        results = [_["result"] for _ in results_detailed]
        self.results = results[:]
        self.results_detailed = results_detailed[:]
        if return_mode == "detailed":
            return results_detailed
        else:
            return results


def timed_wrapper_for_future(func):
    """
    если я захочу время работы каждого потока:
        https://stackoverflow.com/questions/57560135/track-how-long-a-thread-spent-actually-working-on-a-future
    """

    def _w(*a, **k):
        then = time_time()
        res = func(*a, **k)
        elapsed = time_time() - then
        return elapsed, res

    return _w


def demo_threading_func_args_kwargs(
    url,
    name="",
    kwarg1="kwarg1",
    kwarg2="kwarg2",
    kwarg3="kwarg3",
    *args,
    **kwargs
):
    """Ф-я для теста многопоточноcти"""
    seconds_sleep = randint(1, 1000) / 1000.0
    logger.debug("name=%s" % name)
    logger.debug(
        "name={name} run demo_threading_func for {url} (kwarg1={kwarg1} kwarg2={kwarg2} kwarg3={kwarg3} {args} {kwargs}) with {seconds_sleep:.2f}s...".format(
            **locals()
        )
    )
    time_sleep(seconds_sleep)
    logger.debug("+{url} {seconds_sleep:.2f}s]".format(**locals()))
    return seconds_sleep


def demo_threading_func_2(url, name=""):
    """Ф-я для теста многопоточноcти"""
    seconds_sleep = randint(1, 1000) / 1000.0
    logger.debug(
        "{name=} run demo_threading_func for {url} with {seconds_sleep:.2f}s..."
        % locals()
    )
    time_sleep(seconds_sleep)
    logger.debug("+{url} {seconds_sleep:.2f}s]" % locals())
    return seconds_sleep


def demo_threading_func(url):
    """Ф-я для теста многопоточноcти"""
    seconds_sleep = randint(1, 1000) / 1000.0
    logger.debug(
        "run demo_threading_func for {url} with {seconds_sleep:.2f}s..."
    )
    time_sleep(seconds_sleep)
    logger.debug("+{url} {seconds_sleep:.2f}s]")
    return seconds_sleep


def return_result(result):
    return result


if __name__ == "__main__":

    from modules import show_list, wait_for_ok

    special = "v1_executor_submit"
    special = "MagicThreader"

    if special == "temp":
        fun = return_result
        result = 21
        res = fun(result)
        logger.debug("result=%s" % res)

    elif special == "MagicThreader":
        max_workers = 5
        max_workers = "cnt_tasks"
        max_workers = 1

        test_size = 100
        test_size = 10
        test_size = 1
        test_size = 3

        mode = "multiple_arguments"
        mode = "one_argument"
        mode = "multiple_args_kwargs"

        if mode == "one_argument":
            tasks = [
                (("task_%s" % num,), {}) for num in range(1, test_size + 1)
            ]
            func = demo_threading_func

        elif mode == "multiple_arguments":
            tasks = [
                (("task_{num}" % locals(), "name_{num}" % locals()), {})
                for num in range(1, test_size + 1)
            ]
            func = demo_threading_func_2

        elif mode == "multiple_args_kwargs":
            func = demo_threading_func_args_kwargs
            tasks = []
            for num in range(1, test_size + 1):
                args = ("task_%s" % num, "name_%s" % num)
                kwargs = {
                    "kwarg1": "111",
                    "kwarg2": "222",
                    "kwarg_secret": "secret",
                }
                # logger.debug('%s' % kwargs)

                # test 1-thread?
                want_test_func = True
                want_test_func = False
                if want_test_func:
                    r = func(*args, **kwargs)
                    wait_for_ok("{r=%s}" % r)

                task = (
                    args,
                    kwargs,
                )
                tasks.append(task)
            logger.debug("{tasks}".format(**locals()))
            # wait_for_ok()

        args = {
            "max_workers": max_workers,
            "func": func,
            "tasks": tasks,
            "name": "testMagicThreader",
        }
        magic = MagicThreader(**args)

        for step in range(1, 10):
            logger.debug("-" * 20 + "step %s" % step)
            results = magic.get_results()
            logger.debug("results:")
            show_list(results)
            logger.debug(
                "done in {magic.duration:.2f} seconds".format(**locals())
            )

    elif special == "v1_executor_submit":
        pages = [
            "https://google.com",
            "https://yandex.ru",
        ]
        max_workers = 100
        max_workers = 10
        max_workers = 5
        max_workers = 1

        t0 = time_time()
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            all_futures = []
            for num, link in enumerate(pages, 1):
                my_future = executor.submit(demo_threading_func, link)
                t = 0
                if t:
                    logger.debug(
                        "%s %s" % (num, my_future)
                    )  # 5 <Future at 0x14e283e1280 state=pending>
                    # logger.debug(dir(my_future))
                # break
                all_futures.append(my_future)

        # for i in range(1000):
        #    logger.debug('%s %s' % (i, result.done()))

        seconds = time_time() - t0

        logger.debug(
            "{max_workers=}, {len(pages)=} done in {seconds:.2f} seconds"
            % locals()
        )

        for num, ft in enumerate(all_futures, 1):
            logger.debug(str([num, ft, ft.result()]))
