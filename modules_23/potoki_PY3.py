# -*- coding: utf-8 -*-


from time import time, sleep

# from threading import Thread
from concurrent.futures import ThreadPoolExecutor
from random import randint


class MagicThreader:
    """Наконец многопоточно могу спокойно делать все"""

    def __init__(
        self, max_workers=100, func=None, tasks=None, name="MagicThreader"
    ):
        self.func = func
        self.tasks = tasks
        self.max_workers = max_workers

        self.results = None
        self.duration = None
        self.name = name

    def get_results(
        self, func=None, tasks=None, max_workers=None, debug=False
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
            func = test_threading_func

        """
        fun = "get_results"
        if func is None:
            func = self.func
        if tasks is None:
            tasks = self.tasks

        if max_workers is None:
            max_workers = self.max_workers
        if max_workers == "cnt_tasks":
            max_workers = len(tasks)

        m = f"[{self.name} {fun} {max_workers} workers run {len(tasks)} tasks:"
        print(m)

        t_start = time()

        results = []
        if max_workers == 1:
            for num, args_kwargs in enumerate(tasks, 1):
                if isinstance(args_kwargs, dict):
                    args = ()
                    kwargs = args_kwargs
                else:
                    args, kwargs = args_kwargs
                result = func(*args, **kwargs)
                results.append(result)
                if debug:
                    print(num, result)

        elif max_workers > 1:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                all_futures = []
                for num, args_kwargs in enumerate(tasks, 1):
                    if isinstance(args_kwargs, dict):
                        args = ()
                        kwargs = args_kwargs
                    else:
                        args, kwargs = args_kwargs
                    # print(num, args, *args)
                    my_future = executor.submit(func, *args, **kwargs)
                    t = 0
                    if t:
                        print(
                            num, my_future
                        )  # 5 <Future at 0x14e283e1280 state=pending>
                        # print(dir(my_future))
                    # break
                    all_futures.append(my_future)

            for num, future in enumerate(all_futures, 1):
                result = future.result()
                results.append(result)
                if debug:
                    print(num, future, result)

        seconds = time() - t_start
        self.duration = seconds

        print(f"{max_workers=}, {len(tasks)=} done in {seconds:.2f} seconds]")

        self.results = results[:]
        return results


def test_threading_func_args_kwargs(
    url,
    name="",
    *args,
    kwarg1="kwarg1",
    kwarg2="kwarg2",
    kwarg3="kwarg3",
    **kwargs,
):
    """Ф-я для теста многопоточноcти"""
    seconds_sleep = randint(1, 1000) / 1000.0
    print(
        f"{name=} run test_threading_func for {url} ({kwarg1=} {kwarg2=} {kwarg3=} {args} {kwargs}) with {seconds_sleep:.2f}s...",
        end=" ",
    )
    sleep(seconds_sleep)
    print(f"+{url} {seconds_sleep:.2f}s]", end="")
    return seconds_sleep


def test_threading_func_2(url, name=""):
    """Ф-я для теста многопоточноcти"""
    seconds_sleep = randint(1, 1000) / 1000.0
    print(
        f"{name=} run test_threading_func for {url} with {seconds_sleep:.2f}s...",
        end=" ",
    )
    sleep(seconds_sleep)
    print(f"+{url} {seconds_sleep:.2f}s]", end="")
    return seconds_sleep


def test_threading_func(url):
    """Ф-я для теста многопоточноcти"""
    seconds_sleep = randint(1, 1000) / 1000.0
    print(
        f"run test_threading_func for {url} with {seconds_sleep:.2f}s...",
        end=" ",
    )
    sleep(seconds_sleep)
    print(f"+{url} {seconds_sleep:.2f}s]", end="")
    return seconds_sleep


if __name__ == "__main__":
    from modules import show_list, wait_for_ok

    special = "v1_executor_submit"
    special = "MagicThreader"

    if special == "MagicThreader":
        max_workers = 5
        max_workers = 1
        max_workers = "cnt_tasks"

        test_size = 100
        test_size = 10
        test_size = 1
        test_size = 3

        mode = "multiple_arguments"
        mode = "one_argument"
        mode = "multiple_args_kwargs"

        if mode == "one_argument":
            tasks = [((f"task_{num}",), {}) for num in range(1, test_size + 1)]
            func = test_threading_func

        elif mode == "multiple_arguments":
            tasks = [
                ((f"task_{num}", f"name_{num}"), {})
                for num in range(1, test_size + 1)
            ]
            func = test_threading_func_2

        elif mode == "multiple_args_kwargs":
            func = test_threading_func_args_kwargs
            tasks = []
            for num in range(1, test_size + 1):
                args = (f"task_{num}", f"name_{num}", "arg_secret")
                kwargs = {
                    "kwarg1": "111",
                    "kwarg2": "222",
                    "kwarg_secret": "secret",
                }
                # print(**kwargs)

                t = 1
                t = 0
                if t:
                    r = func(*args, **kwargs)
                    wait_for_ok(f"{r=}")

                task = (
                    args,
                    kwargs,
                )
                tasks.append(task)
            print(f"{tasks=}")

        args = {
            "max_workers": max_workers,
            "func": func,
            "tasks": tasks,
            "name": "testMagicThreader",
        }
        magic = MagicThreader(**args)
        results = magic.get_results()
        print("results:")
        show_list(results)
        print(f"done in {magic.duration:.2f} seconds")

    elif special == "v1_executor_submit":
        pages = [
            "https://google.com",
            "https://yandex.ru",
        ]
        max_workers = 100
        max_workers = 10
        max_workers = 1
        max_workers = 5

        t0 = time()
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            all_futures = []
            for num, link in enumerate(pages, 1):
                my_future = executor.submit(test_threading_func, link)
                t = 0
                if t:
                    print(
                        num, my_future
                    )  # 5 <Future at 0x14e283e1280 state=pending>
                    # print(dir(my_future))
                # break
                all_futures.append(my_future)

        # for i in range(1000):
        #    print (i, result.done())

        seconds = time() - t0

        print(f"{max_workers=}, {len(pages)=} done in {seconds:.2f} seconds")

        for num, ft in enumerate(all_futures, 1):
            print(num, ft, ft.result())
