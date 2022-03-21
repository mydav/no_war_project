#!/usr/bin/python
# -*- coding: utf-8 -*-

from modules import *
import logging
from modules_23.my_log_functions import log_action

logger = get_logger(__name__)

t = 1
if t:
    debug_level = logging.INFO
    debug_level = logging.WARNING
    debug_level = logging.DEBUG
    logging.basicConfig(
        format="%(filename)s[:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s",
        level=debug_level,
    )

# наследование - как прописать некоторые аргументы?


def make_release_calcCacher(d_to=""):
    _ = {
        "d_to": d_to,
        "want_cache": False,
        "want_save_all": True,
        # 'delete_data_on_setup': True,
        "delete_data_on_setup": False,
        "name": "RELEASE_calc_cacher",
    }
    calc_cacher = CalculateCacher(**_)
    return calc_cacher


def make_debug_calcCacher(d_to=""):
    _ = {
        "d_to": d_to,
        "want_cache": True,
        "want_save_all": False,
        "delete_data_on_setup": False,
        "name": "DEBUG_calc_cacher",
    }
    calc_cacher = CalculateCacher(**_)
    return calc_cacher


class CalculateCacher:
    def __init__(
        self,
        want_cache=False,
        want_save_all=True,
        d_to=None,
        name="CalculateCacher",
        MT=None,
        delete_data_on_setup=False,
    ):
        """
        в боевой ситуации - я хочу просто все сохранить (для детального анализа), но кеш не использовать
        а когда отладка (проверяю что не так) ставлю want_cache = True и тогда я подтяну всю скачанную инфу. Таким образом получу полный лог.
        delete_data_on_setup - удалять все файлы при инициализации?

        want_cache - берет кешированное?
        want_save_all - сохраняем все просчитанное?
        """
        self.delete_data_on_setup = delete_data_on_setup
        self.set_d_to(d_to)

        self.want_cache = want_cache
        self.want_save_all = want_save_all
        self.f_to_tpl = "[d_to]/[func]__[hash_args]_[hash_kwargs].[extension]"
        self.name = name
        self._stats = {}

        if not MT:
            _ = {
                "print": 0,
                "seq_is_step": 1,
                "want_display": 1,
                "name": self.name,
            }
            MT = log_action(_)

        self.MT = MT

    def calculate(self, *args, **kwargs):
        fun = "calculate"
        debug = True
        debug = False
        if debug:
            logger.debug("%s %s %s" % (fun, args, kwargs))

        MT = self.MT
        want_cache, cache_logic = self.check_want_cache(*args, **kwargs)

        kwargs["want_cache"] = want_cache
        kwargs["return_mode"] = "detailed"

        # wait_for_ok(kwargs)
        if self.want_cache or self.want_save_all or "f_to" in kwargs:
            f_to = kwargs.get("f_to", "")
            f_to = self.get_f(f_to)
            # wait_for_ok(f_to)
            kwargs["f_to"] = f_to

        res = calculate_with_cacher(*args, **kwargs)

        result_from = res["result_from"]
        m = "+%s %s in %.2f" % (res["func_name"], result_from, res["duration"])
        MT.seq(m)
        self._stats[result_from] = self._stats.get(result_from, 0) + 1

        result = res["result"]
        return result

    def check_want_cache(self, *args, **kwargs):
        """
        проверка - нужно кешировать или нет?
        """
        fun = "check_want_cache"
        debug = True
        debug = False
        func, _args, _kwargs = parse_func_args_kwargs(
            self.get_to_calculate(*args, **kwargs)
        )
        func_name = get_func_name(func)
        if debug:
            logger.debug(
                "%s %s func_name=%s" % (fun, type(func_name), func_name)
            )
        checking = [
            (
                kwargs.get("want_cache"),
                "in_kwargs",
            ),  # возможно жестко в аргументах
            (
                get_class_attribute(self, kwargs.get("cache_name")),
                "cache_name",
            ),  # возможно есть cache_name и для него прописали
            (
                get_class_attribute(self, func_name),
                "func_name",
            ),  # возможно есть как имя ф-ии и для него прописали
            (self.want_cache, "main want_cache"),  # дефолтно
        ]
        if debug:
            logger.debug("%s" % checking)
            m = "%s %s func_name=%s" % (
                fun,
                get_class_attribute(self, "demo_return_num"),
                func_name,
            )
            logger.debug(m)
            wait_for_ok(m)

        for want_cache, logic in checking:
            if want_cache in [True, False]:
                logger.debug(
                    "  %s want_cache=%s (logic %s)" % (fun, want_cache, logic)
                )
                return want_cache, logic

    def set_d_to(self, d_to=None):
        if not d_to:
            d_to = "temp/!cache_calculate_with_cacher"

        self.d_to = os.path.abspath(d_to)
        if self.delete_data_on_setup:
            rmdir(self.d_to)

    def resave_file(self, f=""):
        """
        пересохраним файл себе в главную папку
        """
        f_to = self.get_f_in_data(f)
        # copy_file(f, f_to)
        copy_file_with_attributes(f, f_to)
        logger.debug("resave_file (copy) to %s from %s" % (f_to, f))
        return f_to

    def obj_from_file(self, f=None):
        f_to = self.get_f_in_data(f)
        obj = obj_from_file(f_to)
        logger.debug("obj_from_file %s" % (f_to))
        return obj

    def resave_obj_to_file(self, obj={}, f=""):
        f_to = self.get_f_in_data(f)
        obj_to_file(obj, f_to)
        logger.debug("resave_obj_to_file %s from %s" % (f_to, f))

    def resave_text_to_file(self, html="", f=""):
        f_to = self.get_f_in_data(f)
        text_to_file(html, f_to)
        logger.debug("resave_text_to_file to %s" % f_to)
        return f_to

    def get_to_calculate(self, *args, **kwargs):
        if "to_calculate" in kwargs:
            return kwargs["to_calculate"]
        elif len(args) > 0:
            return args[0]
        else:
            return {"func": None}

    def get_stats(self):
        return self._stats

    def get_f_in_data(self, f="", name=""):
        if f:
            name = os.path.basename(f)
        return "%s/%s" % (self.d_to, name)

    def get_f(self, f_to="", must_be_in_data_directory=True):
        """
        must_be_in_data_directory
            мы полюбому будем ложить именно в папку кешера
        """
        d_to = self.d_to
        if not f_to:
            f_to = self.f_to_tpl
        repl = {
            "[d_to]": d_to,
        }
        f_to = no_probely_one(f_to, repl)
        if must_be_in_data_directory and not d_to in f_to:
            f_to = "%s/%s" % (d_to, f_to)
        return f_to

    def print_log(self):
        self.MT.flush_all_messages(min_procent=0)

    def __repr__(self):
        return "%s: want_cache=%s, want_save_all=%s, stats=%s, d_to=%s" % (
            self.name,
            self.want_cache,
            self.want_save_all,
            self.get_stats(),
            self.d_to,
        )


def calculate_with_cacher(
    to_calculate={},
    to_load={},
    to_mockup={},
    f_to=None,
    f_to_tpl="temp/!cache_calculate_with_cacher/[func]__[hash_args]_[hash_kwargs].[extension]",
    want_cache=True,
    save_mode="obj_to_file",
    return_mode="only_result",
    **kwargs
):
    """
    если я хочу кеш, но файла нет - значит файл точно нужен, создадим файл по хешу ф-ии + параметров
    """
    fun = "calculate_with_cacher"

    t_start = time.time()
    default_save_mode = "obj_to_file"

    if save_mode not in ["obj_to_file", "json"]:
        logger.error(
            "error %s - bad save_mode %s, use default"
            % (fun, save_mode, default_save_mode)
        )
        save_mode = default_save_mode

    save_mode_to_extension = {
        "obj_to_file": "obj",
        "json": "json",
    }

    if want_cache and f_to is None:
        f_to = f_to_tpl
    f_to = f_to.replace("[extension]", save_mode_to_extension[save_mode])

    func, args, kwargs = parse_func_args_kwargs(to_calculate)
    func_name = get_func_name(func)
    logger.debug(
        "%s %s want_cache=%s save_mode=%s f_to=%s"
        % (fun, func_name, want_cache, save_mode, f_to)
    )

    f_to = get_file_name_for_cache(f_to, func, args, kwargs)

    res = None
    result_from = None

    # wait_for_ok('%s to_mockup=%s' % (fun, to_mockup))
    if to_mockup.get("mockup"):
        if to_mockup != True:  # я могу вместо тру-фолс прописать нужное
            res = to_mockup["mockup"]
            result_from = "mockup_in_mockup"
        else:
            res = to_mockup["mockuped"]
            result_from = "mockup_in_mockuped"
        logger.debug("%s cache from mockup" % (fun))

    elif want_cache:
        no_option_for_cache = True
        if f_to:
            no_option_for_cache = False
            if file_exists(f_to):
                if save_mode == "obj_to_file":
                    res = obj_from_file(f_to)
                elif save_mode == "json":
                    res = json_from_file(f_to)
                result_from = "cache_file"
                logger.debug("%s cache from file %s" % (fun, f_to))
            else:
                logger.debug("%s no cache_file %s" % (fun, f_to))

        if res is None and to_load:
            no_option_for_cache = False
            func_load, args_load, kwargs_load = parse_func_args_kwargs(to_load)
            res = func_load(*args_load, **kwargs_load)
            logger.debug("%s cache_loaded with %s" % (fun, func_load.__name__))
            # result_from = 'cache_loaded with %s' % (func_load.__name__)
            result_from = "cache_loaded"

        if no_option_for_cache:
            logger.error("%s no option to load cache" % fun)

        if res is None and not no_option_for_cache:
            logger.debug("%s no cache" % fun)

    if res is not None or result_from == "mockup":
        try:
            to_print = str(res)[:200]
        except Exception as er:
            to_print = res
        logger.debug(
            "%s successfull cache %s %s..." % (fun, type(res), to_print)
        )
    else:
        result_from = "calculated"
        logger.debug(
            "bad res=%s, so %s calculating %s..." % (res, fun, func_name)
        )
        res = func(*args, **kwargs)
        logger.debug("%s calculated %s %s" % (fun, type(res), res))
        # logger.debug('res=%s' % res)

        if res is not None:
            if f_to:
                logger.info("%s save to %s" % (fun, f_to))
                if save_mode == "obj_to_file":
                    obj_to_file(res, f_to)
                elif save_mode == "json":
                    f_to = json_to_file(res, f_to)

    duration = time.time() - t_start
    duration = round(duration, 3)

    logger.debug(
        "    +func %s calculated in %.2f seconds, result_from=%s"
        % (func_name, duration, result_from)
    )

    if return_mode == "only_result":
        return res
    else:
        _ = {
            "duration": duration,
            "result": res,
            "result_from": result_from,
            "func_name": func_name,
        }
        return _


def get_file_name_for_cache(f_to, func, args, kwargs):

    f_to_real = f_to
    if f_to:
        func_name = get_func_name(func)
        repl = {
            "[func]": func_name,
            "[hash_args]": to_hash(args),
            "[hash_kwargs]": to_hash(kwargs),
        }
        f_to_real = no_probely_one(f_to, repl)
    f_to = f_to_real
    if f_to == "nah":
        f_to = None

    if f_to:
        f_to = os.path.abspath(f_to)
    return f_to


if __name__ == "__main__":
    from test_calculation_cacher import *

    # assert 1 == 1
    special = "calculate_with_cacher"
    special = "test"
    if special == "test":
        test_cacher_calculated()
        test_cacher_return_saved_in_file()
        test_cacher_return_saved_with_func()

    elif special == "calculate_with_cacher":
        to_calculate = get_demo_return_args()
        to_load = {}

        want_cache = True
        want_cache = False
        calculated = calculate_with_cacher(
            to_calculate, to_load, want_cache=want_cache
        )
        logger.debug("calculated %s" % calculated)

    else:
        wait_for_ok("unknown special %s" % special)
