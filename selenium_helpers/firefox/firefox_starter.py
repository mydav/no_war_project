#!/usr/bin/python
# -*- coding: utf-8 -*-

from modules import *

from windows_functions.windows_funcs import *
from subprocess import Popen, STDOUT
from selenium_helpers.firefox.firefox_profile import DirectoryFirefoxProfile
from selenium_helpers.firefox.geckodriver_starter import (
    run_geckodriver_with_special_port,
    run_geckodriver_with_special_port_if_not_active,
    kill_geckodriver_with_special_port,
)


def get_abs_profile_path(profile_path=""):
    repl = {"[d_profiles]": "s:\\!data_main\\!firefox_profiles"}
    r = no_probely(profile_path, repl)
    return r


def run_firefox_with_special_profile(
    f_firefox="",
    profile_path="[d_profiles]\\rust_mozprofile.fQ6mvxDgBPDy",
    geckodriver_port="6813",
    marionette_port=57800,
    firefox_command_line_arguments0=["-height 1920", "-width 1080"],
    firefox_command_line_arguments=[],
    want_geckodriver=1,
    starting_mode="popen",
    log_file=None,
    f_geckodriver=None,
    want_kill_old=False,
    want_hide_selenium=True,
):
    """
        \xd0\xb7\xd0\xb0\xd0\xbf\xd1\x83\xd1\x81\xd0\xba \xd1\x84\xd0\xb0\xd0\xb5\xd1\x80\xd1\x84\xd0\xbe\xd0\xba\xd1\x81\xd0\xb0 \xd1\x81 \xd0\xbd\xd1\x83\xd0\xb6\xd0\xbd\xd1\x8b\xd0\xbc \xd0\xbf\xd1\x80\xd0\xbe\xd1\x84\xd0\xb0\xd0\xb9\xd0\xbb\xd0\xbe\xd0\xbc:
                "C:\\Program Files\\Firefox Developer Edition\x0cirefox.exe" -marionette -foreground -no-remote -profile c:\\chromedrivers\x0cirefox_profiles
ust_mozprofile.5mKMfVUE3b1H

                \xd0\xb2 \xd0\xbf\xd1\x80\xd0\xbe\xd1\x84\xd0\xb0\xd0\xb9\xd0\xbb\xd0\xb5 \xd0\xbf\xd1\x80\xd0\xbe\xd0\xbf\xd0\xb8\xd1\x81\xd0\xb0\xd0\xbd \xd0\xbf\xd0\xbe\xd1\x80\xd1\x82 marionette
                        user_pref("marionette.port", 57800);

        #window_size='1921,1080' - \xd0\xbd\xd0\xb5\xd1\x82 \xd1\x82\xd0\xb0\xd0\xba\xd0\xbe\xd0\xb3\xd0\xbe
        """
    fun = "run_firefox_with_special_profile"

    if f_firefox == "":
        f_firefox = "c:\\Program Files\\Firefox Developer Edition\\firefox.exe"

    d_firefox = os.path.dirname(f_firefox)
    f_firefox_default = "%s/firefox.exe" % d_firefox

    bin_error = ""
    if not file_exists(f_firefox_default):
        bin_error = "no default firefox %s" % f_firefox_default
    else:
        size_default = get_file_size(f_firefox_default)
        size_my = get_file_size(f_firefox)
        if size_my != size_default:
            bin_error = "size of %s = %s != %s of %s" % (
                f_firefox,
                size_my,
                size_default,
                f_firefox_default,
            )
            print(bin_error)

            logger.debug("copy default firefox")
            r = copy_file(f_firefox_default, f_firefox)
            logger.debug("+%s" % r)
            if r:
                bin_error = ""
            else:
                bin_error = "can not copy default firefox"

    if bin_error:
        inform_me("ERROR %s - bin error %s" % (fun, bin_error))

    _log_file = log_file or open(os.devnull, "wb")

    # # сначала пробую влоб войти - авось получится?
    # if want_kill_old == False:
    #     logger.debug('not want_kill_old, so just try to reconnect...')
    #     try:
    #         run_geckodriver_with_special_port(
    #             geckodriver_port=geckodriver_port,
    #             marionette_port=marionette_port, f_geckodriver=f_geckodriver, want_kill_old_geckodriver=0)
    #         logger.debug('+]')
    #         wait_for_ok()
    #         return

    # except Exception as er:
    #     logger.error('error %s' % er)
    #     wait_for_ok()

    if profile_path is None:
        profile_path = "temp/firefox_profiles/%s" % geckodriver_port

    profile_path = get_abs_profile_path(profile_path)
    if not os.path.isdir(profile_path):
        wait_for_ok(
            "%s ERROR - NO dir for profile_path=%s" % (fun, profile_path)
        )

    profile = DirectoryFirefoxProfile(profile_path)

    want_marionette = True
    if marionette_port in [None, "disabled"]:
        want_marionette = False

    logger.debug(
        "marionette_port %s, want_marionette %s"
        % (marionette_port, want_marionette)
    )

    """
       !!! идеально прячет селениум! - отсюда
       
       Еще разные варианты можно донастраивать, типа https://www.coursehero.com/file/pjjhub9/securityfeaturePolicywebidlenabled-true-userprefdomstorageenabled-false/
        user_pref("dom.webdriver.enabled", false);
        user_pref("geo.enabled", false);
        user_pref("javascript.enabled", false)
    """
    if want_hide_selenium:
        profile.set_preference("dom.webdriver.enabled", False)
        profile.set_preference("useAutomationExtension", False)
        # profile.set_preference('general.useragent.override', ' Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0')

        """
            firefox88 детектит?
        """
        # profile.set_preference('navigator.webdriver', False)

    profile.delete_preference("general.useragent.override")
    profile.delete_preference(
        "navigator.webdriver"
    )  # случайно установил когда в 88 версии разбирался с паливом селениума - в 87 этого просто не надо

    # Настраиваю удобняшки юзерам
    profile.set_preference(
        "browser.newtabpage.enabled", True
    )  # тогда пропишу любые нужные сайты
    profile.set_preference("signon.rememberSignons", True)  # помнить пароли
    profile.set_preference("signon.autofillForms", True)  # помнить пароли

    if want_marionette:
        profile.set_preference("marionette.port", marionette_port)
        profile.set_preference("marionette.enabled", True)
    else:
        profile.set_preference("marionette.enabled", False)

    # else:
    #     profile.set_preference('marionette.port', '')

    firefox_command_line_arguments_txt = (" ").join(
        firefox_command_line_arguments
    )
    repl_command = {
        "[f_firefox]": f_firefox,
        "[profile_path]": profile_path,
        "[firefox_command_line_arguments]": firefox_command_line_arguments_txt,
    }

    active = False

    starting_mode = "bat"
    starting_mode = "popen"

    if starting_mode == "bat":
        start_firefox_bat(repl_command)

    else:
        commands_start = [
            "[f_firefox]",
        ]

        commands_marionette = []
        if want_marionette:
            commands_marionette = [
                "-marionette",
                # для идентификации в поиске по порту (при запуске в файл - невозможно порт отследить)
                "marionette_port",
                marionette_port,
            ]

        commands_finish = [
            "-foreground",
            "-no-remote",
            "-profile",
            "[profile_path]",
        ]

        commands_tpl = [
            commands_start,
            firefox_command_line_arguments,
            commands_marionette,
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
            logger.info("\npopen commands to start:")
            show_list(commands)

            t = 1
            t = 0
            if t:
                active = check_popen_process_active(commands)
                wait_for_ok("firefox active?")

        if want_kill_old:
            logger.debug("killing old firefox...")
            active = check_popen_process_active(commands, want_kill=True)
            active = False
            logger.debug("+")
        else:
            active = check_popen_process_active(commands)

        logger.debug("firefox active=%s" % active)
        if active:
            print(" firefox already active")
        else:
            # увидел через s:\!installs\ProcessMonitor\Procmon.exe
            # "c:\Program Files\Firefox Developer Edition\firefox_scrapping_google_ua.exe" -marionette -foreground -no-remote -profile s:\!data_main\!firefox_profiles\google_for_scrapping_googleUA

            logger.debug("start Popen with commands %s" % (commands))
            process = Popen(commands, stdout=_log_file, stderr=STDOUT)
            # start_firefox_bat(repl_command)
            # wait_for_ok('started popen?')
            logger.debug("  +")

    # если браузер пришлось запускать - нужно удалить геко
    if not active:
        r = kill_geckodriver_with_special_port(
            geckodriver_port=geckodriver_port, marionette_port=marionette_port
        )

    if want_geckodriver:
        run_geckodriver_with_special_port_if_not_active(
            geckodriver_port=geckodriver_port,
            marionette_port=marionette_port,
            f_geckodriver=f_geckodriver,
        )

    return


def start_firefox_bat(repl_command):
    fun = "start_firefox_bat"
    f_bat = os.path.abspath("%s.bat" % fun)
    cmd = '"[f_firefox]" -marionette [firefox_command_line_arguments] -foreground -no-remote -profile "[profile_path]"'
    cmd = 'START cmd /K "%s"' % cmd
    cmd = no_probely(cmd, repl_command)
    text_to_file(cmd, f_bat)
    logger.debug("[%s run_bat %s" % (fun, f_bat))
    r = os_system_f(f_bat)
    logger.debug("+%s]" % fun)
    return r


def run_firefox(
    geckodriver_port=6813,
    f_firefox_exe="firefox.exe",
    f_firefox_defaultBinary="c:\\Program Files (x86)\\Google\\firefox\\Application\\firefox.exe",
):
    f_firefox = "%s/%s" % (
        os.path.dirname(f_firefox_defaultBinary),
        f_firefox_exe,
    )
    if not file_exists(f_firefox):
        wait_for_ok("ERROR - no file %s" % f_firefox)
    r = run_firefox_with_special_profile(
        f_firefox=f_firefox, geckodriver_port=geckodriver_port
    )


if __name__ == "__main__":
    pass
    # firefox_starter_usage
