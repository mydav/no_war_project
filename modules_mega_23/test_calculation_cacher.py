#!/usr/bin/python
# -*- coding: utf-8 -*-

from modules import *
from modules_mega_23.calculation_cacher import *


def test_cacher_calculate_mockup():
    calc_cacher = make_calculateCacher()
    to_mockup = {
        "mockup": True,
        "mockuped": 123,
    }
    result = calc_cacher.calculate(to_mockup=to_mockup)
    assert result == 123


def test_cacher_save_mode_json():
    calc_cacher = make_calculateCacher()

    start_from = 25
    to_calculate = {
        "func": demo_return_num,
        "kwargs": dict(num=start_from),
    }

    # цель - сохранить вместо pickle json
    f_saved = "in_json"
    f_real = calc_cacher.get_f(f_saved)
    rmfile(f_real)

    assert file_exists(f_real) == False

    _kwargs = {
        "to_calculate": to_calculate,
        "save_mode": "json",
        "f_to": f_saved,
    }
    result = calc_cacher.calculate(**_kwargs)
    assert result == start_from
    assert file_exists(f_real) == True


def test_resave_file():
    calc_cacher = make_calculateCacher()
    f = r"s:\python2.7\Lib\site-packages\modules_projects\data\parse_elements.js"
    f_saved = calc_cacher.resave_file(f)
    assert file_exists(f_saved) == True


def test_resave_to_file():
    calc_cacher = make_calculateCacher()
    html = "привет! Сохрани меня пожалуйста"
    f = "asdfadfadf/some_special_name_of_file.json"

    f_saved = calc_cacher.resave_text_to_file(html, f)
    assert file_exists(f_saved) == True


def test_scenario_calcCacher_releaseVersion_and_debug():
    start_from = 25
    to_calculate = {
        "func": demo_return_num,
        "kwargs": dict(num=start_from),
    }

    # на сервере - все сохраняем, ничего не кешируем
    d_to = r"s:\python2.7\Lib\site-packages\modules_projects\temp\!cache_calculate_with_cacher\!typical_bet"
    _kwargs = {
        "want_cache": False,
        "want_save_all": True,
        "d_to": d_to,
    }
    calc_cacher = make_calculateCacher(**_kwargs)

    result = calc_cacher.calculate(to_calculate)
    logger.debug("result=%s" % result)
    assert result == start_from
    assert calc_cacher._stats == {"calculated": 1}

    # а теперь типа дебаг - я хочу подтянуть инфу
    _kwargs = {
        "want_cache": True,
        "want_save_all": False,
        "d_to": d_to,
    }
    calc_cacher = make_calculateCacher(**_kwargs)

    result = calc_cacher.calculate(to_calculate)
    logger.debug("result=%s" % result)
    assert result == start_from
    assert calc_cacher._stats == {"cache_file": 1}


def test_demo_multifunc(calc_cacher=None):
    calc_cacher = make_calculateCacher(calc_cacher=calc_cacher)

    start_from = 25
    adding = 10
    res1, res2 = demo_multifunc(
        calc_cacher=calc_cacher, start_from=start_from, adding=adding
    )

    assert res1 == start_from
    assert res2 == start_from + adding


def test_check_want_cache(calc_cacher=None):
    """
    правильно определяем хотим кеш или нет?
    """
    fun = "test_check_want_cache"
    calc_cacher = make_calculateCacher(calc_cacher=calc_cacher)

    num = 25
    func, args, kwargs = demo_return_num, (num,), {}
    to_calculate = func_args_kwargs_to_dict(func, args, kwargs)

    _kwargs = {
        "to_calculate": to_calculate,
        "cache_name": "to_calculate_step_2",
    }

    t = 0
    t = 1
    if t:
        want_cache, cache_logic = calc_cacher.check_want_cache(**_kwargs)
        logger.debug(
            "want_cache %s, cache_login %s" % (want_cache, cache_logic)
        )
        assert want_cache == True
        assert cache_logic == "main want_cache"

    # test 2
    t = 1
    if t:
        calc_cacher.demo_return_num = True
        want_cache, cache_logic = calc_cacher.check_want_cache(**_kwargs)
        logger.debug(
            "want_cache %s, cache_login %s" % (want_cache, cache_logic)
        )
        assert want_cache == True
        assert cache_logic == "func_name"

    # test 3
    t = 1
    if t:
        calc_cacher.to_calculate_step_2 = True
        want_cache, cache_logic = calc_cacher.check_want_cache(**_kwargs)
        logger.debug(
            "want_cache %s, cache_login %s" % (want_cache, cache_logic)
        )
        assert want_cache == True
        assert cache_logic == "cache_name"

    # test 4
    t = 1
    if t:
        _kwargs["want_cache"] = False
        calc_cacher.to_calculate_step_2 = True
        want_cache, cache_logic = calc_cacher.check_want_cache(**_kwargs)
        logger.debug(
            "want_cache %s, cache_login %s" % (want_cache, cache_logic)
        )
        assert want_cache == False
        assert cache_logic == "in_kwargs"


def test_cacher_return_saved_with_func():
    num = 25
    func, args, kwargs = demo_return_num, (num,), {}
    to_calculate = func_args_kwargs_to_dict(func, args, kwargs)

    func, args, kwargs = demo_return_num_25, (), {}
    to_load = func_args_kwargs_to_dict(func, args, kwargs)

    calculated = calculate_with_cacher(
        to_calculate, to_load=to_load, f_to="nah"
    )

    assert calculated == num


def test_cacher_return_saved_in_file():
    num = 26
    func, args, kwargs = demo_return_num, (num,), {}
    to_calculate = func_args_kwargs_to_dict(func, args, kwargs)

    calculated = calculate_with_cacher(to_calculate, want_cache=True)

    assert calculated == num
    assert calculated != 1.11


def test_cacher_calculated():
    to_calculate = get_demo_return_args()
    func, args, kwargs = parse_func_args_kwargs(to_calculate)

    calculated = calculate_with_cacher(to_calculate, want_cache=False)

    # logger.debug('calculated %s' % calculated)
    assert calculated == (args, kwargs)
    assert calculated != "some error"


def get_demo_return_num(num):
    func = demo_return_num
    args = ((num),)
    kwargs = {}
    r = func_args_kwargs_to_dict(func, args, kwargs)
    logger.debug("%s" % r)
    return r


def get_demo_return_args():
    func = demo_return_args
    args = (1, 2)
    kwargs = {"x": 1, "y": 2}
    return func_args_kwargs_to_dict(func, args, kwargs)


def demo_return_args(*args, **kwargs):
    return args, kwargs


def demo_return_num(num=1):
    return num


def demo_return_num_25():
    return 25


def demo_add(num, num_2=2):
    return num + num_2


def demo_multifunc(calc_cacher=None, start_from=25, adding=10):
    """
    ф-я из 2-х шагов:
    """
    if calc_cacher is None:
        calc_cacher = make_calculateCacher()
    func_calculate = calc_cacher.calculate

    # func1
    to_calculate = {
        "func": demo_return_num,
        "kwargs": dict(num=start_from),
    }
    res1 = func_calculate(to_calculate)
    # logger.debug('%s %s' % (res, expected))

    # func2
    to_calculate = {
        "func": demo_add,
        # 'args': (res1, adding,),
        "kwargs": dict(num=res1, num_2=adding),
    }
    want_cache = False
    res2 = func_calculate(to_calculate, want_cache=want_cache)
    # 25 + 10 == 35

    return (res1, res2)


def make_calculateCacher(calc_cacher=None, *args, **kwargs):
    if calc_cacher:
        return calc_cacher

    d_to = kwargs.get("d_to")
    if not d_to:
        d_to = r"s:\python2.7\Lib\site-packages\modules_projects\temp\!cache_calculate_with_cacher\!from_tester"

    d = {
        "want_cache": True,
        "d_to": d_to,
    }
    kwargs = add_defaults(kwargs, d)

    calc_cacher = CalculateCacher(*args, **kwargs)
    return calc_cacher


if __name__ == "__main__":
    special = "test_check_want_cache"
    special = "demo_multifunc"
    special = "test_scenario_calcCacher_releaseVersion_and_debug"
    special = "test_resave_to_file"
    special = "test_cacher_save_mode_json"
    special = "test_cacher_calculate_mockup"

    _ = {
        "want_cache": False,
        "want_cache": True,
    }
    calc_cacher = make_calculateCacher(**_)
    logger.debug("calc_cacher=%s" % calc_cacher)

    if special == "demo_multifunc":
        r = demo_multifunc(calc_cacher)
        logger.debug("%s" % r)

    elif special == "test_cacher_save_mode_json":
        test_cacher_save_mode_json()

    elif special == "test_resave_to_file":
        r = test_resave_to_file()
        r = test_resave_file()
        logger.debug("%s" % r)

    elif special == "test_scenario_calcCacher_releaseVersion_and_debug":
        test_scenario_calcCacher_releaseVersion_and_debug()

    elif special == "test_check_want_cache":
        r = test_check_want_cache()

    elif special == "test_cacher_calculate_mockup":
        special = test_cacher_calculate_mockup()

    else:
        wait_for_ok("unknown special=%s" % special)

    logger.debug("final: %s" % calc_cacher)
    # сколько времени ушло на все про все?
    calc_cacher.print_log()
