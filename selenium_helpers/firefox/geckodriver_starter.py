#!/usr/bin/python
# -*- coding: utf-8 -*-

from modules import *
from selenium_helpers.firefox.firefox_profile import DirectoryFirefoxProfile
from windows_functions.windows_funcs import *


def get_f_geckodriver(f_geckodriver=None):
    if f_geckodriver is None:
        # f_geckodriver = 's:\\!data_main\\chromedrivers\\geckodriver_new.exe'
        files = [
            r"data/geckodriver.exe",
            "s:\\!data_main\\chromedrivers\\geckodriver-v0.28.0.exe",  # real actual version,
        ]
        for f in files:
            if file_exists(f):
                f_geckodriver = f
                break

        if f_geckodriver is None:
            wait_for_ok("no geckodriver in %s" % files)

    f_geckodriver = os.path.abspath(f_geckodriver)
    return f_geckodriver


def run_geckodriver_with_special_port_if_not_active(
    geckodriver_port=49999, marionette_port=57800, f_geckodriver=None
):
    f_geckodriver = get_f_geckodriver(f_geckodriver)
    fun = "run_geckodriver_with_special_port_if_not_active"
    logger.debug("[%s" % fun)
    r = is_geckodriver_with_special_port_active(
        geckodriver_port=geckodriver_port, marionette_port=marionette_port
    )
    if r:
        logger.debug("already active")
    else:
        run_geckodriver_with_special_port(
            geckodriver_port=geckodriver_port,
            marionette_port=marionette_port,
            f_geckodriver=f_geckodriver,
        )
    logger.debug("+%s]" % fun)


def run_geckodriver_with_special_port(
    geckodriver_port=49999,
    marionette_port=57800,
    f_geckodriver=None,
    want_kill_old_geckodriver=1,
):
    r"""
        "C:\Windows\geckodriver.exe" --connect-existing --marionette-port 57800 --port 49999 --log trace
        """
    fun = "run_geckodriver_with_special_port"
    f_geckodriver = get_f_geckodriver(f_geckodriver)
    logger.debug("[%s" % fun)

    if want_kill_old_geckodriver:
        kill_geckodriver_with_special_port(
            geckodriver_port=geckodriver_port, marionette_port=marionette_port
        )

    f_bat = os.path.abspath(
        "%s_%s_%s.bat" % (fun, geckodriver_port, marionette_port)
    )
    cmd = '"[f_geckodriver]" --connect-existing --marionette-port [marionette_port] --port [geckodriver_port] --log trace'
    cmd = '''START "[geckodriver_port]" cmd.exe /K "%s"''' % cmd
    repl = {
        "[f_geckodriver]": f_geckodriver,
        "[geckodriver_port]": geckodriver_port,
        "[marionette_port]": marionette_port,
    }
    cmd = no_probely(cmd, repl)
    text_to_file(cmd, f_bat)
    logger.debug("run_bat %s" % f_bat)
    os_system_f(f_bat)


def kill_geckodriver_with_special_port(
    geckodriver_port=49999, marionette_port=57800
):
    fun = "kill_geckodriver_with_special_port"

    title = get_title_of_cmd_for_geckodriver(geckodriver_port, marionette_port)

    t = 1
    if t:
        r = kill_werfault(programs=[title])
        return r
        wait_for_ok()
    logger.debug("[%s %s" % (fun, title))
    _ = {"title": title, "title_re": 1, "kill_after": -1}
    tasks = [_]
    _ = {"tasks": tasks, "close_all": 0, "close_all": 1, "detailed": 1}
    closer = close_bad_windows_class(_)
    closed = closer.close()
    logger.debug("+%s=%s]" % (fun, closed))


def is_geckodriver_with_special_port_active(
    geckodriver_port=49999, marionette_port=57800
):
    fun = "is_geckodriver_with_special_port_active"
    print("[%s" % fun),

    title = get_title_of_cmd_for_geckodriver(geckodriver_port, marionette_port)

    q = 'select * from Win32_Process where CommandLine like "%[program]%"'.replace(
        "[program]", title
    )
    programs = search_programs([], q=q)
    logger.debug(" %s programs: %s" % (len(programs), programs))
    r = len(programs) > 0
    print("+ %s=%s]" % (fun, r))
    return r


def get_title_of_cmd_for_geckodriver(
    geckodriver_port=49999, marionette_port=57800
):
    title_tpl = (
        "--marionette-port [marionette_port] --port [geckodriver_port] "
    )
    repl = {
        "[geckodriver_port]": geckodriver_port,
        "[marionette_port]": marionette_port,
    }
    title = no_probely(title_tpl, repl)
    return title


if __name__ == "__main__":
    special = "kill_geckodriver_with_special_port"
    special = "run_geckodriver_with_special_port"
    special = "is_geckodriver_with_special_port_active"
    special = "run_geckodriver_with_special_port_if_not_active"

    geckodriver_port = 6889
    marionette_port = 57889

    if special == "kill_geckodriver_with_special_port":
        r = kill_geckodriver_with_special_port(
            geckodriver_port=geckodriver_port, marionette_port=marionette_port
        )
        logger.debug("r: %s" % r)

    elif special == "is_geckodriver_with_special_port_active":
        r = is_geckodriver_with_special_port_active(
            geckodriver_port=geckodriver_port, marionette_port=marionette_port
        )

    elif special == "run_geckodriver_with_special_port":
        run_geckodriver_with_special_port(
            geckodriver_port=geckodriver_port, marionette_port=marionette_port
        )

    elif special == "run_geckodriver_with_special_port_if_not_active":
        run_geckodriver_with_special_port_if_not_active(
            geckodriver_port=geckodriver_port, marionette_port=marionette_port
        )

    else:
        os._exit(0)
