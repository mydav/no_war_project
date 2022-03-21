#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
!!!СИНХРОНИЗИРУЙ PY2-PY3 sync_py2_py3
"""

from modules import *
from collections import defaultdict

# from modules.print_colored import *
# from modules.list_functions import clear_list
# from modules.api_functions import *
# from modules.logging_functions import get_logger

logger = get_logger(__name__)


def emulate_pytest(func, names="x,y", parameters=[()]):
    r"""    запуска задачи как pytest
    Например, в pytest было:
        NAMES_test_check_vilka_from_api_lines = "f_name,market,expected_win_procent_100"
        TASKS_test_check_vilka_from_api_lines = [
            (r's:\python2.7\Lib\site-packages\universal_bookmaker\api_betfair\data\match_odds.json',  '1', -2.547),
        ]
        
        @pytest.mark.parametrize(NAMES_test_check_vilka_from_api_lines, TASKS_test_check_vilka_from_api_lines)
        def test_check_vilka_from_api_lines(f_name, market='', expected_win_procent_100=1):
    
    а я запускаю
        emulate_pytest(test_check_vilka_from_api_lines, NAMES_test_check_vilka_from_api_lines, TASKS_test_check_vilka_from_api_lines)
    """
    fun = "emulate_pytest"
    tasks = []
    names_list = clear_list(names.split(","))
    for parameter in parameters:
        task = {}
        for pos in range(len(names_list)):
            key = names_list[pos]
            value = parameter[pos]
            task[key] = value
        tasks.append(task)

    print("%s have %s tasks, demo: %s" % (fun, len(tasks), tasks[0]))

    for num, _kwargs in enumerate(tasks, 1):
        print_h1("\n%s %s/%s" % (fun, num, len(tasks)))
        func(**_kwargs)
        print_success("+%s/%s" % (num, len(tasks)))
    print_success("%s - FULL SUCCESS WITH %s tasks" % (fun, len(tasks)))


def my_tester(tasks, func_to_check, func_compare=None, func_equals=None):
    fun = "my_tester"
    cnt_tasks = len(tasks)
    print(
        f"[{fun}: {cnt_tasks} tasks with func_to_check={func_to_check.__name__}, {func_compare=} {func_equals=}"
    )
    stata = defaultdict(int)
    i = 0
    errors = []
    for args, result_must_be in tasks:
        i += 1
        print(f"    check {i}/{cnt_tasks}", end=" ")

        if isinstance(args, dict):
            calculated = func_to_check(**args)
        elif isinstance(args, tuple):
            calculated = func_to_check(*args)
        else:
            calculated = func_to_check(args)

        if func_compare != None:
            calculated = func_compare(calculated)

        if (calculated == result_must_be) or (
            func_equals and func_equals(calculated, result_must_be)
        ):
            stata["success"] += 1
            print_success("+")

        else:
            stata["error"] += 1
            error = f'  CHECK_ERROR: "{calculated}" != "{result_must_be}" for {args=}"'
            errors.append(error)
            print_error(error)
            logging.error(error)

    print(f"{fun} STATA: {dict(stata)}")

    cnt_errors = stata.get("error", 0)
    if cnt_errors > 0:
        print_error(f"{fun}: {cnt_errors} ERRORS:")
        show_list(errors)
    else:
        print_success(f"{fun}: FULL SUCCESS")


def func_equals_bool(v1, v2):
    """
    True == "1"
    """
    true = ["True", True, "1", 1]
    false = ["False", False, "0", 0]
    if v1 in true and v2 in true:
        return True
    elif v1 in false and v2 in false:
        return True
    else:
        return False


def get_tasks_for_tester_from_txt(txt="", delim="->", mode="", size=None):
    items = clear_list(txt, bad_starts="#")

    tasks_to_check = []
    for item in items:
        if mode == "":
            parts = clear_list(item.split(delim))
            # print(parts)
            task, expecting = parts
        elif mode == "true-false":
            parts = clear_list(item.split(delim))
            if size and len(parts) != size:
                print_error(
                    "bad_size for size={size} parts={parts}".format(**locals())
                )
                continue
            expecting = parts[-1]
            task = tuple(parts[:-1])

        tasks_to_check.append([task, expecting])
    return tasks_to_check


def demo_func(x):
    return x


def compare_result_and_expected(result, expected, default_key="odds", fun=""):
    """
    удобно в тестах использовать expected как словарь, тогда кучу значений еще дополнительно можем проверять
    """
    # logger.debug('%s result %s expected %s' % (fun, result, expected))
    if isinstance(expected, dict):
        for num, k in enumerate(expected, 1):
            logger.debug(
                "%s - key %s/%s %s, result %s, expected %s"
                % (fun, num, len(expected), k, result[k], expected[k])
            )
            assert result[k] == expected[k]
    else:
        api_error = get_api_error(result)
        if api_error:
            result = api_error
        else:
            result = result[default_key]
        logger.debug("%s - result %s, expected %s" % (fun, result, expected))
        assert result == expected


if __name__ == "__main__":
    t = 0
    t = 1
    if t:
        tasks = [
            [[0, 1, 2, 1], [0, 1, 2, 1],],
            [1, 1,],
            [1, 2,],
        ]
        func_to_check = demo_func
        my_tester(tasks, func_to_check)
