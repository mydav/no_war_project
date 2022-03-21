import logging

# logger = get_logger(__name__)


def func_args_kwargs_to_dict(func, args, kwargs):
    return {"func": func, "args": args, "kwargs": kwargs}


def parse_func_args_kwargs(to_calculate={}):
    fun = "parse_func_args_kwargs"
    if isinstance(to_calculate, dict):
        func = to_calculate.get("func")
        args = to_calculate.get("args", (),)
        kwargs = to_calculate.get("kwargs", {})
    else:
        logging.error("%s ERROR - how to get func, args, kwargs?" % (fun))
    return func, args, kwargs


def get_func_name(func):
    try:
        func_name = func.__name__
    except Exception as er:
        func_name = func

    return func_name

    # if func:
    #     func_name = func.__name__
    # else:
    #     func_name = func
    # return func_name
