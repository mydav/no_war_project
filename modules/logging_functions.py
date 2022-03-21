# pyarmor options: no-spp-mode
# -*- coding: utf-8 -*-

import os, sys
import logging
from logging import Formatter
import datetime
from copy import copy

from modules.print_colored import *

# tpl = '%(message)s [%(levelname)s] [%(filename)s:%(lineno)d %(funcName)20s]'
# dct = {'relativeCreated': 886.0001564025879, 'process': 6520, 'args': (), 'module': 'logging_functions', 'funcName': 'lprint', 'exc_text': None, 'message': 'print 1', 'name': '\x1b[36mPRINT\x1b[0m', 'thread': 8896, 'created': 1626444119.871, 'threadName': 'MainThread', 'msecs': 871.0000514984131, 'filename': '\x1b[36mlogging_functions.py\x1b[0m', 'levelno': 20, 'processName': 'MainProcess', 'pathname': 'S:/python2.7/Lib/site-packages/modules/logging_functions.py', 'lineno': 15, 'msg': 'print 1', 'exc_info': None, 'levelname': '\x1b[36mINFO\x1b[0m'}
# print(tpl % dct)
# os._exit(0)

"""
adding custom loggers:
    https://stackoverflow.com/questions/2183233/how-to-add-a-custom-loglevel-to-pythons-logging-facility/13638084#13638084
"""

# 0
DEBUG_LEVEL0_NUM = logging.DEBUG + 1
logging.addLevelName(DEBUG_LEVEL0_NUM, "DEBUG0")


def debug0(self, message, *args, **kws):
    if self.isEnabledFor(DEBUG_LEVEL0_NUM):
        # Yes, logger takes its '*args' as 'args'.
        self._log(DEBUG_LEVEL0_NUM, message, args, **kws)


logging.Logger.debug0 = debug0


# 1
DEBUG_LEVEL1_NUM = logging.DEBUG + 2
logging.addLevelName(DEBUG_LEVEL1_NUM, "DEBUG1")


def debug1(self, message, *args, **kws):
    if self.isEnabledFor(DEBUG_LEVEL1_NUM):
        # Yes, logger takes its '*args' as 'args'.
        self._log(DEBUG_LEVEL1_NUM, message, args, **kws)


logging.Logger.debug1 = debug1

# 2
DEBUG_LEVEL2_NUM = logging.DEBUG + 3
logging.addLevelName(DEBUG_LEVEL2_NUM, "DEBUG2")


def debug2(self, message, *args, **kws):
    if self.isEnabledFor(DEBUG_LEVEL2_NUM):
        # Yes, logger takes its '*args' as 'args'.
        self._log(DEBUG_LEVEL2_NUM, message, args, **kws)


logging.Logger.debug2 = debug2

# 3
DEBUG_LEVEL3_NUM = logging.DEBUG + 4
logging.addLevelName(DEBUG_LEVEL3_NUM, "DEBUG3")


def debug3(self, message, *args, **kws):
    if self.isEnabledFor(DEBUG_LEVEL3_NUM):
        # Yes, logger takes its '*args' as 'args'.
        self._log(DEBUG_LEVEL3_NUM, message, args, **kws)


logging.Logger.debug3 = debug3


def lprint(x):
    """logger print - печать через логгер"""
    print_logger.info(x)


def setup_logging(name=None, level="debug"):
    # setup_global_logging_level(level=level)
    disable_unimportant_logging()
    if name:
        logger = get_logger(name=name, level=level)
        return logger


def check_logger(logger, methods="all"):
    try:
        print(
            "-" * 20,
            "check:",
            logger.name,
            logger.level,
            logger,
            logger.handlers,
        )
    except Exception as er:
        print("-" * 20, "check:", logger)
        pass

    if methods == "min":
        methods = ["debug", "critical"]
    else:
        methods = [
            "debug",
            "debug0",
            "debug1",
            "debug1",
            "debug1",
            "debug2",
            "debug3",
            "info",
            "warning",
            "error",
            "critical",
        ]
    for method in methods:
        getattr(logger, method)("проверка метода %s" % method)


def setup_global_logging_level(level="", want_check=0):
    fun = "setup_global_logging_level"
    debug_level = get_debug_level(level)

    # повторно установить уровень, по другому не устанавливается
    root_logger = get_root_logger()
    if root_logger.handlers:
        print("%s already setuped, so edit_logger" % (fun))
        edit_logger(root_logger, debug_level)
        return root_logger
    # else:
    #     edit_logger(root_logger, debug_level)
    #     return root_logger

    sys_stdout = sys.stdout
    formatter = get_colored_formatter()

    mode = "old"
    mode = "simplest"
    mode = "old_v2"
    mode = "new"

    consoleHandler = get_LoggerHandler_for_console()

    if mode == "simplest":
        setup_logging_basic_config(debug_level)

    elif mode == "old":

        logging.basicConfig(
            # stream=sys_stdout,
            format=get_logging_format(),
            level=debug_level,
        )

    elif mode == "old_v2":

        logging.basicConfig(
            # stream=sys_stdout,
            level=debug_level,
            # format=get_logging_format(),
            # format=Formatter(get_logging_format()),
            # format=formatter,
            handlers=[
                # logging.FileHandler("debug.log"),
                # logging.StreamHandler()
                consoleHandler,
            ],
        )
    elif mode == "new":
        logging.basicConfig(level=debug_level,)
        root_logger = get_root_logger()
        print(root_logger.handlers)

        # root_logger.addHandler(consoleHandler) - не работает!!!
        root_logger.handlers = [consoleHandler]  # а так работает

    else:
        print("ERROR %s unknown mode %s" % (fun, mode))
        os._exit(0)

    # want_check = True
    if want_check:
        check_logger(logging)
        check_logger(root_logger)

    root_logger = get_root_logger()
    print(
        "%s finished, handlers: %s, level: %s"
        % (fun, root_logger.handlers, root_logger.handlers[0].level)
    )


def setup_logging_basic_config(level=""):
    debug_level = get_debug_level(level)
    logging.basicConfig(
        # stream=sys_stdout,
        # format=get_logging_format(),
        level=debug_level,
    )


def edit_logger(name=None, level=None, logger=None):
    debug_level = get_debug_level(level)
    if logger is None:
        if isinstance(logger, basestring):
            logger = get_logger(name=name)
        else:
            logger = name

    print(
        " edit_logger name `%s` %s , level `%s` debug_level %s `%s`"
        % (name, logger, level, type(debug_level), debug_level)
    )

    if debug_level is not None:
        logger.setLevel(debug_level)

    # отдельно по потокам:
    t = 0
    if t:
        for handler in logger.handlers:
            for handler in logger.handlers:
                handler.setLevel(level)
                # if isinstance(handler, type(logging.StreamHandler())):
                #     handler.setLevel(logging.DEBUG)


def disable_unimportant_logging(
    unimportant_logger_names="default", level="info"
):
    """отключаем логи неважных модулей
    """
    # посмотреть все модули
    # show_dict(logging.Logger.manager.loggerDict)
    # wait_for_ok()

    if unimportant_logger_names == "default":
        unimportant_logger_names = [
            "urllib3",  # connectionpool.py
            "selenium",  # remote_connection.py
        ]
    for name in unimportant_logger_names:
        logging.getLogger(name).setLevel(get_debug_level(level))
        logging.getLogger(name).propagate = False


def get_root_logger():
    return logging.getLogger("")


# def get_logger(name, *args, **kwargs):
#     logger = logging.getLogger(name)
#     return logger


def get_logger(name, level="debug", tpl="min"):
    # level = 1
    debug_level = get_debug_level(level)
    t = 0
    if t:
        print(
            "       get_logger `%s`, level `%s` debug_level %s `%s`"
            % (name, level, type(debug_level), debug_level)
        )

    logger = logging.getLogger(name)
    logger.setLevel(debug_level)

    if logger.handlers:
        print("     ALREADY EXISTS %s" % name)
        return logger

    if logger.handlers:
        # print(logger.handlers)
        print("     CLEAR previous handlers")
        logger.handlers = []

    if not logger.handlers:
        t = 0
        t = 1
        if t:
            # create console handler with a higher log level
            cf = get_colored_formatter(tpl=tpl)

            ch = logging.StreamHandler(sys.stdout)
            ch.setLevel(debug_level)
            ch.setFormatter(cf)

            logger.addHandler(ch)

    logger.propagate = False

    return logger


def get_LoggerHandler(
    mode="console", level="debug", stream=sys.stdout, formatter_tpl=""
):
    if mode == "console":
        return get_LoggerHandler_for_console(
            level=level, stream=stream, formatter_tpl=formatter_tpl
        )
    elif mode == "file":
        return get_LoggerHandler_for_file(
            level=level, stream=stream, formatter_tpl=formatter_tpl
        )


def get_LoggerHandler_for_console(
    level="", stream=sys.stdout, formatter_tpl=""
):
    debug_level = get_debug_level(level)
    formatter = get_colored_formatter(tpl=formatter_tpl)
    consoleHandler = logging.StreamHandler(stream=stream)
    consoleHandler.setLevel(debug_level)
    consoleHandler.setFormatter(formatter)
    return consoleHandler


def get_LoggerHandler_for_file(level="debug", f="temp/log_from_logger.log"):
    fh = logging.FileHandler(f)
    fh.setLevel(logging.DEBUG)
    formatter = get_logger_tpl(tpl=tpl)
    fh.setFormatter(formatter)
    return fh


def get_colored_formatter(tpl=""):
    tpl = get_logger_tpl(tpl=tpl)
    return ColoredFormatter(tpl)


def get_logger_tpl(tpl=""):
    if tpl == "min":
        # tpl = "%(filename)s[:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s"
        # tpl = "[%(name)-20s %(levelname)20s] [%(filename)s:%(lineno)d %(funcName)20s]  %(message)s"
        tpl = "[%(levelname)10s][%(filename)s:%(lineno)d:%(funcName)s]  %(message)s"
        # tpl = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
        # [l][DEBUG]  debug1 (logging_functions.py:384)

    elif tpl == "print":
        tpl = "%(message)s"

    elif tpl == "like_print":
        tpl = "PRINT----> %(message)s [%(levelname)s] [%(filename)s:%(lineno)d:%(funcName)s]"
        # [l][DEBUG]  debug1 (logging_functions.py:384)

    elif tpl in ["", "default"]:
        tpl = get_logging_format()

    # else:
    #     logging.error("error get_logger_tpl: unknown tpl=%s" % tpl)
    #     os._exit(0)

    return tpl


def get_logging_format():
    return "[%(name)s] %(filename)s[:%(lineno)d %(funcName)20s]# %(levelname)-8s [%(asctime)s]  %(message)s"


def get_debug_level(level="debug"):
    dct = {
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "debug": logging.DEBUG,
        "debug0": DEBUG_LEVEL0_NUM,
        "debug1": DEBUG_LEVEL1_NUM,
        "debug2": DEBUG_LEVEL2_NUM,
        "debug3": DEBUG_LEVEL3_NUM,
        "": logging.DEBUG,
    }
    debug_level = dct.get(level, level)
    return debug_level


class ColoredFormatter(Formatter):
    PREFIX = "\033["
    SUFFIX = "\033[0m"
    # default_color = 41
    default_color = 37  # white
    default_color = 34  # blue
    default_color = "white"  # blue
    MAPPING = {
        "DEBUG": default_color,  # white
        "DEBUG0": default_color,  # white
        "DEBUG1": default_color,  # white
        "DEBUG2": default_color,  # white
        "DEBUG3": default_color,  # white
        "INFO": "cyan",  #
        "WARNING": "yellow",  #
        "ERROR": "LIGHTRED_EX",  # red
        "CRITICAL": "red",  # white on red bg
    }
    MAPPING_fg_bk = {
        "DEBUG": ("black", "white"),
        "DEBUG0": ("black", "LIGHTMAGENTA_EX"),
        "DEBUG1": ("black", "LIGHTMAGENTA_EX"),
        "DEBUG2": ("black", "blue"),
        "DEBUG3": ("black", "cyan"),
        "INFO": ("black", "green"),
        "WARNING": ("black", "yellow"),
        "ERROR": ("black", "LIGHTRED_EX"),
        "CRITICAL": ("black", "red"),
    }

    def __init__(self, patern, want_zsuv_message: bool = True):
        Formatter.__init__(self, patern)
        self.want_zsuv_message = want_zsuv_message

    def format(self, record):
        debug = False
        colored_record = copy(record)
        # print('colored_record=%s' % colored_record)
        self.color_record(colored_record)
        # print(colored_record)

        want_zsuv_message = self.want_zsuv_message

        if want_zsuv_message:
            format_orig = self._style._fmt
            t = 1
            if t:
                # Save the original format configured by the user
                # when the logger formatter was instantiated

                level_now = record.levelno
                key = f"fixed_otstup_{level_now}"
                if 1 or not getattr(self, key, None):
                    max_otstup = 5
                    start_level = logging.DEBUG
                    otstup_size = level_now - start_level
                    # otstup_size = min(0, otstup_size)
                    otstup_real = max_otstup - otstup_size

                    otstup = "   " * otstup_real
                    if debug:
                        print(
                            f"{record.levelno=} {otstup_real=}  {otstup_size=} {start_level=} _frmt={self._style._fmt}"
                        )
                    frmt = self._style._fmt
                    frmt = frmt.replace("%(message)s", otstup + "%(message)s")
                    self._style._fmt = frmt
                    setattr(self, key, True)

        result = Formatter.format(self, colored_record)
        if want_zsuv_message:
            self._style._fmt = format_orig

        return result

    def color_record(self, colored_record):
        levelname = colored_record.levelname
        color = self.MAPPING.get(levelname, self.default_color)
        fg_color, bg_color = self.MAPPING_fg_bk.get(
            levelname, self.default_color
        )

        keys = [
            "name",
            "levelname",
            "filename",
            "funcName",
            # 'lineno',
            "msg",
        ]
        # print(colored_record.__dict__) # тут рассмотрел атрибуты
        # os._exit(0)
        for key in keys:
            value = getattr(colored_record, key)
            # colored_value = ("{0}{1}m{2}{3}").format(
            #     self.PREFIX, color, value, self.SUFFIX
            # )

            if key == "lineno":
                value = str(value)

            if 1 and key in ["msg"]:
                # print(f"{type(value)} {color=}")
                colored_value = color_text(value, fg=color)
            else:
                colored_value = color_text(value, fg_color, bg_color)
            # print('key=%s, value=%s, color=%s: %s' % (key, value, color, colored_value ))
            setattr(colored_record, key, colored_value)


def setup_all_loggers(
    zsuv: int = 2, want_format: bool = False, frmt="print", debug=False
):
    """настройки всех логеров"""
    loggers = [
        logging.getLogger(name) for name in logging.root.manager.loggerDict
    ]
    for logger in loggers:
        logger.setLevel(logging.DEBUG + zsuv)

        if want_format:
            for handler in logger.handlers:
                cf = get_colored_formatter(frmt)
                # cf = logging.Formatter(frmt)
                if debug:
                    logger.info(f"new colored_formatter {cf} for {handler=}")
                handler.setFormatter(cf)
                # os._exit(0)


# Настройки принта через лог
# print_logger = get_logger("PRINT", "info", tpl="like_print")

# print("+logging_functions")
if __name__ == "__main__":
    pass
    t = 0
    t = 1
    if t:
        level = "debug"
        setup_global_logging_level(level=level)

    t = 1
    if t:
        logger = get_logger(__name__)
        want_format = True
        zsuv = 0
        frmt = "print"
        frmt = ""
        setup_all_loggers(
            zsuv=zsuv, want_format=want_format, frmt=frmt, debug=True
        )
        check_logger(logger)
        os._exit(0)

    t = 1
    t = 0
    if t:
        # check_logger(logging)

        level = "debug"
        next_level = "info"

        t = 1
        if t:
            print("before level %s" % level)
            setup_global_logging_level(level=level)
            check_logger(logging)

            print("after level %s" % level)
            t = 1
            t = 0
            if t:
                root_logger = get_root_logger()
                edit_logger(root_logger, next_level)
                # check_logger(root_logger)
            else:
                setup_global_logging_level(level=next_level)

            check_logger(logging)

        os._exit(0)

    # logger = setup_logging('l', 'debug')

    lprint("start logging")
    logging.info("text logging with info")

    logger = get_logger("l", "debug")
    logger.critical("ЖОПА!")
    os._exit(0)

    # logger = get_logger('l', 'debug')
    # logger = get_logger('l', 'debug')
    # print = logger.info

    logger.debug("debug1")
    logger.debug("debug2")
    method = "info"
    getattr(logger, method)("check method %s" % method)
    check_logger(logger)
    # os._exit(0)

    # check_logger(m)
    # os._exit(0)

    logger_2 = get_logger("l2", "debug")

    logger_3 = get_logger("l3", "debug")
    # logger_3 = logging.getLogger('l3')

    t = 1
    if t:
        logger_3.setLevel(1)
        cf = get_colored_formatter("min")
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(cf)
        logger_3.addHandler(ch)
        os._exit(0)

    # logging.debug('debug logging')
    # print(1)
    # my_print('my_print')
    # logging.info('info logging')

    loggers = [
        logger,
        logger_2,
        logger_3,
        # logging,
    ]
    for logger_ in loggers:
        check_logger(logger_)

    print("print 1")
    lprint("print 1")
    logger_3.debug("logger 3")
    logger.debug("logger 1")

    logging.debug("logging.info 1")

    # проверяем смену уровня логгера на лету
    print("-" * 10)
    lprint("-" * 10)
    print(logger)
    lprint(logger)
    logger.debug("before debug")
    logger.debug1("DEBUG 1 GOOD?")
    logger.debug2("DEBUG 2 GOOD?")
    logger.debug3("DEBUG 3 GOOD?")
    os._exit(0)

    edit_logger(logger=logger, level="debug")
    logger.debug("edit_logger to debug")

    edit_logger(logger=logger, level="info")
    logger.debug("edit_logger to info - no debug")
    logger.info("edit_logger to info - exists only info")

    edit_logger(logger=logger, level="debug")
    logger.debug("edit_logger to debug")

    edit_logger(logger=logger, level="debug2")
    logger.debug2("edit_logger to debug2")

    # check_logger(logging)
    # logging.info('logging info')
