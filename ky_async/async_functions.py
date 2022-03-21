from modules.minimum_important_functions import *
import asyncio
from typing import Coroutine

logger = get_logger(__name__)
# on windows: RuntimeError: Event loop is closed.      On Windows seems to be a problem with EventLoopPolicy, use this snippet to work around it:
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# logger.debug(
#     "asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())"
# )

"""
для работы с прокси:
I did some research. ProactorEventLoop causing the proxy to be ignored.
In python 3.8 changelog:

on Windows, the default asyncio event loop is now ProactorEventLoop

Setting event loop to SelectorEventLoop fixes the issue.

asyncio.set_event_loop(asyncio.SelectorEventLoop())
"""
asyncio.set_event_loop(asyncio.SelectorEventLoop())


async def demo_coro():
    await asyncio.sleep(1)  # <- replace this with your async code
    return "finished"


def run_async(*args, **kwargs):
    return run_async_synchronously(*args, **kwargs)


def run_async_synchronously(
    coro: Coroutine, coro_kwargs: dict = {}, coro_args=(), debug: bool = True
):
    """
    Run async function synchronously
    """
    fun = "run_async_synchronously"
    try:
        name = coro.__name__
    except Exception as er:
        name = coro
    if debug:
        logger.debug(f"[{fun} {name}, {coro_kwargs=}")
    loop = asyncio.get_event_loop()
    coroutine = coro(*coro_args, **coro_kwargs)
    res = loop.run_until_complete(coroutine)
    if debug:
        logger.debug(f" +{res=} {fun}]")
    return res


if __name__ == "__main__":
    special = "run_async_synchronously"
    if special == "run_async_synchronously":
        coro = demo_coro
        res = run_async_synchronously(coro)
        logger.info(f"{res=}")
    else:
        logger.critical(f"unknown {special=}")
