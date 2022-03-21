from modules import *

# from modules.downloaders import requests_u
# import time

logger = get_logger(__name__)


def fun_polube(
    fun,
    cnt_tries=10,
    on_error="wait_for_ok",
    debug_fun_polube=False,
    seconds_sleep_on_error=0,
    *args,
    **kwargs,
):
    """
    Полюбе исполняю ф-ю
    """
    fn = "fun_polube"
    done = False

    if debug_fun_polube:
        print(
            "[%s: fun %s, cnt_tries=%s, args=%s, kwargs=%s"
            % (fn, fun, cnt_tries, args, kwargs)
        )

    want_try = False
    want_try = True
    for num_try in range(1, cnt_tries + 1):
        if want_try:
            try:
                r = fun(*args, **kwargs)
                done = True
                break

            except Exception as er:
                logger.error(
                    f"     ERROR {fn} {num_try}/{cnt_tries}: {fun } - {er }"
                )
                sleep_(seconds_sleep_on_error)
        else:
            r = fun(*args, **kwargs)
            done = True
            break

    if done is False:
        m = "ERROR %s - can not run function %s with args %s, kwargs %s" % (
            fn,
            fun,
            args,
            kwargs,
        )
        if on_error == "wait_for_ok":
            wait_for_ok(m)
        elif on_error in ["continue", "ERROR_FUN_NOT_CALCULATED"]:
            r = "ERROR_FUN_NOT_CALCULATED"
        elif on_error == "inform_me":
            inform_me(m)
        else:
            wait_for_ok("ERROR %s - unknown on_error=%s" % (fn, on_error))
    return r


def fun_wrong():
    """Неправильная ф-я для теста"""
    # return 1 / 0
    return requests_u("http://localhost:8081/save_info/", data="nah")


def execute_func_while_not_found(
    func,
    func_kwargs={},
    func_filter=None,
    seconds_sleep_if_no_tasks: int = None,
    max_step: int = 0,
    max_searching_duration: int = 0,
    **kwargs,
):
    if seconds_sleep_if_no_tasks is None:
        seconds_sleep_if_no_tasks = 5
    step = 0
    t_start = time.time()
    tasks = []
    while True:
        step += 1
        duration = time.time() - t_start
        # logger.debug(f'{func=} {max_step=} {step=}')

        if max_step and step > max_step:
            logger.debug(f"reached {max_step=}, so break")
            break

        elif max_searching_duration and duration > max_searching_duration:
            logger.debug(
                f"reached maximum {max_searching_duration=}, so break"
            )
            break

        elif step > 1:
            logger.debug(f"no tasks, so sleep {seconds_sleep_if_no_tasks}")
            sleep_(seconds_sleep_if_no_tasks, 0)

        want_try = False
        if want_try:
            try:
                tasks = func(**func_kwargs)
            except Exception as er:
                logger.warning(f"{er=}")
        else:
            # logger.debug(f'{func=}')
            tasks = func(**func_kwargs)
        duration = time.time() - t_start

        if func_filter:
            filtered_tasks = func_filter(tasks)
            logger.debug(
                f"  {step=}, found {len(filtered_tasks)}/{len(tasks)} filtered tasks, searching tasks {get_human_duration(duration)}"
            )
            tasks = filtered_tasks[:]

        logger.debug(f"{tasks=}")
        if tasks:
            shuffle(tasks)
            break

    return tasks


def fun_random_list():
    size = choice([0, 5])
    return list(range(size))


if __name__ == "__main__":
    special = "fun_polube"
    special = "execute_func_while_not_found"

    if special == "fun_polube":
        kwargs = {
            "fun": fun_wrong,
        }
        r = fun_polube(**kwargs)
        print(r)

    elif special == "execute_func_while_not_found":
        kwargs = {
            "func": fun_random_list,
        }
        r = execute_func_while_not_found(**kwargs)
        logger.debug(f"execute_func_while_not_found {r=}")

    else:
        logger.critical(f"unknown {special}")
