"""
Cache result of any function depending on conditions
"""
from modules.file_functions import obj_to_file, obj_from_file, file_life
from modules.text_functions import to_hash
from typing import Callable
import logging

logger = logging.getLogger(__name__)


class FuncCacher:
    """
    хотим кешировать ф-ю
    """

    def __init__(self, func: Callable, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

        self.cacher_id = None
        self.real_kwargs = self.kwargs.copy()
        if "cacher_id" in self.real_kwargs:
            self.cacher_id = self.real_kwargs["cacher_id"]
            del self.real_kwargs["cacher_id"]

        self.d_cache = "temp/cache_FuncCacher"

    def run_function_or_get_cache(self, max_life=60 * 10):
        if self.is_old_cache(max_life=max_life):
            m = f"is_old_cache, so run {self}"
            print(m)
            logger.debug(m)
            r = self.run_function()
            self.save(r)
        else:
            m = f"actual cache, so get cached {self}"
            print(m)
            logger.debug(m)
            r = self.load()

        return r

    def run_function(self):
        return self.func(*self.args, **self.real_kwargs)

    def save(self, r):
        obj_to_file(r, self.get_f())

    def load(self):
        r = obj_from_file(self.get_f())
        return r

    def is_old_cache(self, max_life=60 * 10):
        f_cache = self.get_f()

        life = file_life(f_cache)

        is_old_cache = life == -1 or life > max_life

        return is_old_cache

    def get_f(self):
        hash_args = [self.args, self.kwargs]
        hash_args = to_hash(hash_args)
        f = f"{self.d_cache}/{self.func.__name__}/{hash_args[0]}/{hash_args[1]}/{hash_args}.obj"
        return f

    def __repr__(self):
        return f"FuncCacher: {self.func.__name__}/cacher_id={self.cacher_id} args={self.repr_short(self.args)}, kwargs={self.repr_short(self.real_kwargs)}, f={self.get_f()}"

    def repr_short(self, item="", size=300):
        full = f"{item}"
        short = full[:size]
        if short != full:
            short = f"{short}..."
        return short


def test_args_kwargs(*args, **kwargs):
    args = args + (4,)
    kwargs["edited"] = "edited"
    return args, kwargs


if __name__ == "__main__":
    logging.basicConfig(
        format="%(filename)s[:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s",
        level=logging.DEBUG,
    )

    args = ("a", "b", 1, 2, 3)
    kwargs = {
        "test_kwargs": "some kwargs",
        # "cacher_id": 1,
        "cacher_id": 2,
    }
    r = test_args_kwargs(1, 2, *args, test="true", **kwargs)
    print(f"{r=}")

    r = test_args_kwargs(*args, **kwargs)
    print(f"{r=}")

    f_cache = "temp/cached.obj"
    obj_to_file(r, f_cache)

    r2 = obj_from_file(f_cache)
    print(f"{r2=}")

    cacher = FuncCacher(test_args_kwargs, *args, **kwargs)
    print(cacher)

    r3 = cacher.run_function()
    print(f"{r3=}")

    r4 = cacher.run_function_or_get_cache()
    print(f"{r4=}")
