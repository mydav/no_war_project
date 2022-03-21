#!/usr/bin/python
# -*- coding: utf-8 -*-

from subprocess import Popen, STDOUT

# from windows_functions.windows_funcs import search_programs
from windows_functions.search_processes import check_active_by_port

# from chrome_profile import DirectorychromeProfile
from modules import *

# from modules_mega import *


def get_abs_profile_path(profile_path=""):
    repl = {"[d_profiles]": "s:\\!data_main\\!chrome_profiles"}
    r = no_probely(profile_path, repl)
    return r


def run_chrome_with_special_profile(
    f_chrome="",
    profile_path="S:\!installs\!portable_browsers\GoogleChromePortable\Data\profile",
    debugger_port="6814",
    chrome_command_line_arguments=[],
    cache_dir=None,
    # starting_mode="bat",
    starting_mode="popen",
    log_file=None,
    want_kill_old=False,
    want_hide_selenium=True,
):
    """
    """
    fun = "run_chrome_with_special_profile"
    logger.debug("[%s" % fun)

    if f_chrome == "":
        args = locals()
        m = f"no chrome in {args=}"
        logger.critical(m)
        os._exit(0)
        # f_chrome = "S:\!installs\!portable_browsers\GoogleChromePortable\App\Chrome-bin\chrome.exe"

    if cache_dir is None:
        cache_dir = r"C:\temp\chrome_cache\%s" % debugger_port

    if not dir_exists(cache_dir):
        create_dir(cache_dir)

    d_chrome = os.path.dirname(f_chrome)
    f_chrome_default = "%s/chrome.exe" % d_chrome

    bin_error = ""
    t = 0
    if t:
        if not file_exists(f_chrome_default):
            bin_error = "no default chrome %s" % f_chrome_default
        else:
            size_default = get_file_size(f_chrome_default)
            size_my = get_file_size(f_chrome)
            if size_my != size_default:
                bin_error = "size of %s = %s != %s of %s" % (
                    f_chrome,
                    size_my,
                    size_default,
                    f_chrome_default,
                )
                logger.error(bin_error)

                logger.debug("copy default chrome")
                r = copy_file(f_chrome_default, f_chrome)
                logger.debug("+%s" % r)
                if r:
                    bin_error = ""
                else:
                    bin_error = "can not copy default chrome"

    if bin_error:
        m = f"ERROR {fun} - {bin_error}"
        logger.critical(m)
        inform_me(m)

    _log_file = log_file or open(os.devnull, "wb")

    # if profile_path is None:
    #     profile_path = 'temp/chrome_profiles/%s' % debugger_port

    profile_path = get_abs_profile_path(profile_path)
    if not os.path.isdir(profile_path):
        wait_for_ok(
            "%s ERROR - NO dir for profile_path=%s" % (fun, profile_path)
        )

    profile = (
        {}
    )  # todo - возможно в папке профиля нужно будет что-то прописывать

    # прячу селениум?
    if want_hide_selenium:
        pass

    chrome_command_line_arguments_txt = (" ").join(
        chrome_command_line_arguments
    )
    repl_command = {
        "[f_chrome]": f_chrome,
        "[debugger_port]": debugger_port,
        "[profile_path]": profile_path,
        "[chrome_command_line_arguments]": chrome_command_line_arguments_txt,
        "[cache_dir]": cache_dir,
    }

    active = False

    if starting_mode == "bat":
        start_chrome_bat(repl_command, debugger_port)

    else:
        commands_start = [
            "[f_chrome]",
        ]

        commands_finish = [
            get_title_of_cmd_for_chrome(debugger_port),  # по этому ищу
            "--remote-debugging-port=[debugger_port]",
            "--user-data-dir=[profile_path]",
            "--disk-cache-dir=[cache_dir]",
            # '--log-net-log=C:\chrome_log.json',
            # '--net-log-capture-mode=Everything',
            # '--flag-switches-begin',
            # '--flag-switches-end',
        ]

        commands_finish_popen = [
            get_title_of_cmd_for_chrome(debugger_port),  # по этому ищу
            "--remote-debugging-port=[debugger_port]",
            "--user-data-dir=[profile_path]",
            "--disk-cache-dir=[cache_dir]",
        ]

        commands_tpl = [
            # commands_start,
            chrome_command_line_arguments,
            commands_finish,
        ]
        command_tpl = slitj_list_listov(commands_tpl)

        commands = []
        for _ in command_tpl:
            _ = no_probely(_, repl_command)
            commands.append(_)

        commands = list_minus_list(commands, [' "" '])
        t = 1
        if t:
            logger.debug(f"\npopen commands to start: {commands=}")

            t = 1
            t = 0
            if t:
                active = check_popen_process_active(commands)
                wait_for_ok("chrome active?")

        if want_kill_old:
            logger.debug("killing old chrome...")
            kill_chrome_with_special_port(debugger_port)
            active = False
            logger.debug("+")
        else:
            active = is_chrome_with_special_port_active(debugger_port)

        logger.debug(f"chrome {active=}")
        # wait_for_ok()

        status = False
        if active:
            status = "already_active"
            logger.debug(" chrome already active")
        else:
            mode = "popen"
            # увидел через s:\!installs\ProcessMonitor\Procmon.exe
            # "c:\Program Files\chrome Developer Edition\chrome_scrapping_google_ua.exe" -marionette -foreground -no-remote -profile s:\!data_main\!chrome_profiles\google_for_scrapping_googleUA

            if mode == "popen":
                commands.insert(0, f_chrome)
                logger.debug("start Popen with commands %s" % (commands))
                process = Popen(commands, stdout=_log_file, stderr=STDOUT)
                logger.debug(f"{process=}")
            # wait_for_ok(repl_command)
            else:
                start_chrome_bat(commands=commands, repl_command=repl_command)
            # wait_for_ok('started popen?')
            logger.debug("+")

            t_start = time.time()
            while True:
                duration = time.time() - t_start
                if duration > 30:
                    status = False
                    break
                active = is_chrome_with_special_port_active(debugger_port)
                if active:
                    status = "started"
                    break
                sleep_(1, 0)

    if status:
        return api_success(status)
    else:
        return api_error("not_started")


def kill_chrome_with_special_port(debugger_port=49999):
    fun = "kill_chrome_with_special_port"

    title = get_title_of_cmd_for_chrome(debugger_port)

    t = 1
    if t:
        r = kill_werfault(programs=[title])
        return r
        wait_for_ok()


def start_chrome_bat(commands=[], repl_command={}, port=""):
    fun = "start_chrome_bat"
    commands_str = " ".join(commands)
    f_bat = os.path.abspath("%s_%s.bat" % (fun, port))

    cmd = '"[f_chrome]" [commands]'.replace("[commands]", commands_str)
    cmd = 'START cmd /K "%s"' % cmd
    cmd = no_probely(cmd, repl_command)
    text_to_file(cmd, f_bat)

    logger.debug("[%s run_bat %s" % (fun, f_bat))
    r = os_system_f(f_bat)
    logger.debug("+%s]" % fun)
    return r


def is_chrome_with_special_port_active(debugger_port=6814):
    fun = "is_chrome_with_special_port_active"
    logger.debug(f"[{fun} {debugger_port=}")

    t = 0
    if t:
        title = get_title_of_cmd_for_chrome(debugger_port)

        detailed = 0
        detailed = 1
        q = 'select * from Win32_Process where CommandLine like "%[program]%" and Name != "cmd.exe"'
        q = 'select * from Win32_Process where CommandLine like "%[program]%"'
        q = q.replace("[program]", title)
        special = ""
        special = "all"
        programs = search_programs([], q=q, detailed=detailed, special=special)
        logger.debug(" %s programs: %s" % (len(programs), programs))
        r = len(programs) > 0
    else:
        r = check_active_by_port(debugger_port)
    logger.debug("+ %s=%s]" % (fun, r))
    return r


def get_title_of_cmd_for_chrome(debugger_port=6814):
    # title_tpl = ' --remote-debugging-port=[debugger_port] '
    title_tpl = "--chrome_with_port_[debugger_port]_"
    repl = {
        "[debugger_port]": debugger_port,
    }
    title = no_probely(title_tpl, repl)
    return title


def run_chrome(
    debugger_port=6814,
    f_chrome_exe="chrome.exe",
    f_chrome_defaultBinary="c:\\Program Files (x86)\\Google\\chrome\\Application\\chrome.exe",
):
    f_chrome = "%s/%s" % (
        os.path.dirname(f_chrome_defaultBinary),
        f_chrome_exe,
    )
    if not file_exists(f_chrome):
        wait_for_ok("ERROR - no file %s" % f_chrome)
    r = run_chrome_with_special_profile(
        f_chrome=f_chrome, debugger_port=debugger_port
    )


if __name__ == "__main__":
    f_chrome = "s:\!installs\!portable_browsers\GoogleChromePortable\App\Chrome-bin\chrome.exe"
    f_chrome = "s:\!installs\!portable_browsers\GoogleChromePortable\App\Chrome-bin\chrome_6814.exe"
    f_chrome = "s:\!chaos\!no_war\dist\data\development\GoogleChromePortable64\App\Chrome-bin\chrome.exe"

    profile_path = "S:\!installs\!portable_browsers\GoogleChromePortable\Data\profile\Default"
    profile_path = "S:\!installs\!portable_browsers\GoogleChromePortable\Data\profile"  # обязательно так надо!
    profile_path = "s:\!data\!no_war\profiles\profile"
    debugger_port = 6815
    debugger_port = 6814

    chrome_command_line_arguments = []

    special = "kill_chrome_with_special_port"
    special = "is_chrome_with_special_port_active"
    special = "run_chrome_with_special_profile"

    if special == "kill_chrome_with_special_port":
        r = kill_chrome_with_special_port(debugger_port)
        logger.info("r=%s" % r)

    elif special == "is_chrome_with_special_port_active":
        active = is_chrome_with_special_port_active(debugger_port)
        logger.info("chrome active=%s" % active)

    elif special == "run_chrome_with_special_profile":
        account = ""

        Show_step("special: %s, account %s" % (special, account))
        if account == "":
            pass
        elif account == "dev":
            chrome_command_line_arguments = clear_list(
                "\n                    -purgecaches\n                    "
            )
        else:
            wait_for_ok("unknown account `%s`?" % account)

        r = run_chrome_with_special_profile(
            f_chrome=f_chrome,
            profile_path=profile_path,
            debugger_port=debugger_port,
            chrome_command_line_arguments=chrome_command_line_arguments,
        )
        logger.info(f"run result: {r=}")
        os._exit(0)
    else:
        wait_for_ok("ERROR: unknown special=%s" % special)
