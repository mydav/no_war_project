#!/usr/bin/python
# -*- coding: utf-8 -*-

from browsermobproxy import Server
from modules import *

# from modules_mega import *


class ServiceStarter(object):
    def __init__(
        self,
        name="",
        cmd="",
        repl={},
        title_tpl="",
        host="localhost",
        port=9091,
    ):
        if not name:
            name = "ServiceStarter"
        self.title_tpl = title_tpl
        self.name = name
        self.cmd = cmd
        self.repl = repl
        self.host = host
        self.port = port

    def run_if_not_active(self):
        fun = "run_if_not_active"
        logger.debug("[%s" % fun)
        r = self.is_active()
        if r:
            logger.debug("already active")
        else:
            self.run()
        logger.debug("+%s]" % fun)

    def run(self, want_kill_old=0):
        r"""
            "C:\Windows\geckodriver.exe" --connect-existing --marionette-port 57800 --port 49999 --log trace
            """
        fun = "run"
        logger.debug("[%s" % fun)

        if want_kill_old:
            self.kill()

        f_bat = self.get_f_bat()
        cmd = 'START cmd /K "%s"' % self.cmd
        repl = self.repl
        cmd = no_probely(cmd, repl)
        # wait_for_ok(cmd)
        text_to_file(cmd, f_bat)
        logger.debug(" run_bat `%s` with cmd `%s`" % (f_bat, cmd))
        os_system_f(f_bat)

        self.wait_for_service_to_be_active()

        logger.debug("+]")

    def kill(self):
        fun = "kill"
        print("[%s title=`%s`" % (fun, title)),

        title = self.get_title()
        r = kill_werfault(programs=[title])
        logger.debug("+]")
        return r

    def wait_for_service_to_be_active(self, retry_sleep=0.2, retry_count=10):
        fun = "wait_for_service_to_be_active"
        logger.debug("[%s" % fun)
        t_start = time.time()
        count = 0
        while not self._is_listening():
            sleep_(retry_sleep)
            count += 1
            logger.debug(count)
            if count == retry_count:
                self.stop()
                raise ProxyServerError("Can't connect to Browsermob-Proxy")
        seconds = time.time() - t_start

        logger.debug("+%s in %.3f seconds]" % (fun, seconds))

    def _is_listening(self):
        fun = "_is_listening"
        port = self.port
        logger.debug("[%s :%s..." % (fun, port))
        try:
            socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_.settimeout(1)
            socket_.connect((self.host, port))
            socket_.close()
            status = True
        except socket.error:
            status = False
        logger.debug("+%s]" % status)
        return status

    def is_active(self, *args, **kwargs):
        return self._is_listening()

        fun = "is_active"
        title = self.get_title()
        print("[%s title=`%s`" % (fun, title)),

        q = 'select * from Win32_Process where CommandLine like "%[program]%"'.replace(
            "[program]", title
        )
        programs = search_programs([], q=q, special="all")
        logger.debug(" %s programs: %s" % (len(programs), programs))
        r = len(programs) > 0
        logger.debug("+ %s=%s]" % (fun, r))
        return r

    def get_title(self):
        return no_probely(self.title_tpl, self.repl)

    def get_f_exe(self, f_exe=None, files=None):
        if files is None:
            files = [
                "s:\\!data_main\\chromedrivers\\geckodriver-v0.28.0.exe",
                # real actual version,
                r"data/geckodriver.exe",
            ]

        if f_exe is None:
            for f in files:
                if file_exists(f):
                    f_exe = f
                    break

            if f_exe is None or not file_exists(f_exe):
                wait_for_ok("no f_exe in %s" % files)

        return f_exe

    def get_f_bat(self):
        return os.path.abspath("run_%s.bat" % (self.name))

    def __repr__(self):
        return self.name


class ProxyServerError(Exception):
    pass
