#!/usr/bin/python
# -*- coding: utf-8 -*-

from browsermobproxy import Server
from modules import *

# from modules_mega import *
from modules_mega.start_service_with_cmd import *


class BrowserMobProxyService(ServiceStarter):
    def __init__(
        self,
        f_exe=r"s:\!installs\!proxies\browsermob-proxy-2.1.4\lib\browsermob-dist-2.1.4.jar",
        port=9000,
        host="localhost",
    ):
        name = "MobProxyServer_%s" % port

        self.host = host
        self.port = port
        self.f_exe = self.get_f_exe(f_exe)

        cmd = 'java -jar "[f_exe]" --port [port] --'

        repl = {
            "[port]": self.port,
            "[f_exe]": self.f_exe,
        }

        # title_tpl = '--marionette-port [marionette_port] --port [geckodriver_port] '
        title_tpl = "--port [port] --"

        super(BrowserMobProxyService, self).__init__(
            name=name,
            cmd=cmd,
            repl=repl,
            title_tpl=title_tpl,
            host=self.host,
            port=self.port,
        )


class BrowserMobStarter:
    def __init__(
        self,
        path=r"s:\!installs\!proxies\browsermob-proxy-2.1.4\bin\browsermob-proxy",
        f_exe=r"s:\!installs\!proxies\browsermob-proxy-2.1.4\lib\browsermob-dist-2.1.4.jar",
        port=9000,
        name="",
        external_proxy="",
    ):
        """
        external_proxy == http/https proxy
        """
        if name == "":
            name = "BrowserMob_%s" % port
        self.name = name

        self.path = path
        self.f_exe = f_exe
        t = 0
        if t:
            self.port = port
            self.port_for_proxy = self.port + 500
        else:
            self.port_for_proxy = (
                port  # это реальный прокси, который в браузере прописывается
            )
            self.port = port + 500
        self.server = None
        self.proxy = None
        self.external_proxy = ""

    def start_proxy(self, port=None, seconds_sleep=0):
        fun = "start_proxy"
        if port is None:
            port = self.port
        print("[%s %s port=%s " % (self.name, fun, port))
        mps = BrowserMobProxyService(f_exe=self.f_exe, port=port)
        # mps.run()
        mps.run_if_not_active()

    def start_server(self, port=None, seconds_sleep=0, mode_start="cmd"):
        """
        Запускается из browsermobproxy невидимым - меня не устраивает. Поэтому использую start_proxy - сам открываю если надо
        :param port: 
        :param seconds_sleep: 
        :return: 
        """
        fun = "start_server"
        if port is None:
            port = self.port
        print("[%s %s port=%s " % (self.name, fun, port))
        options = {"port": port}
        print("server...")
        server = Server(path=self.path, options=options)

        print("start...")
        if mode_start == "cmd":
            self.start_proxy()
        else:
            server.start()

        self.server = server
        sleep_(seconds_sleep)
        print("+]")
        # wait_for_ok('%s done' % fun)
        return server

    def create_proxy(self, params=None):
        if self.proxy is not None:
            return self.proxy

        server = self.server
        if 1 and server is None:
            server = self.start_server()

        options = {
            # 'existing_proxy_port_to_use': 8081,
        }
        # options = {}
        params = params if params is not None else {}
        _ = {
            "port": self.port_for_proxy,
            "trustAllServers": True,
        }
        params.update(_)
        """
        # еще можно localhost поменять
            or if running BrowserMob Proxy in a multi-homed environment, specify a desired bind address (default is 0.0.0.0):

            [~]$ curl -X POST -d 'bindAddress=192.168.1.222' http://localhost:8080/proxy
            {"port":8086}
        """
        if self.external_proxy:
            _ = {
                "httpProxy": self.external_proxy,
                "httpsProxy": self.external_proxy,
            }
            params.update(_)

        t = 0
        if t:
            # Start proxy instance with trustAllServers set to true, store returned port number
            r = requests.post("http://localhost:8080/proxy", data=params)
            port = json.loads(r.text)["port"]
        else:
            proxy = server.create_proxy(params=params, options=options)

        self.proxy = proxy
        return proxy

    def __repr__(self):
        return "%s" % self.name


def scan_har(har):
    for e in har["log"]["entries"]:
        _request = e["request"]
        _url = _request[
            "url"
        ]  # "method", "url", "cookies", "queryString"... are keys of the request object
        _response = e["response"]
        _content = _response.get("content", "")
        if 1 or "explore_tabs" in _url:
            print(" Status: {}".format(_response["status"])),
            print(" Request URL: {}".format(_url))


def save_har(data, f="temp/captured_har.json"):
    with open(f, "w") as har_file:
        json.dump(data, har_file)


def save_har_2(data="", f="temp/captured_har.har"):
    # result_har = json.dumps(data, ensure_ascii=False)
    result_har = json.dumps(data)
    with open(f, "w") as harfile:
        harfile.write(result_har)


if __name__ == "__main__":

    path = r"s:\!installs\!proxies\browsermob-proxy-2.1.4\bin\browsermob-proxy"
    f_exe = r"s:\!installs\!proxies\browsermob-proxy-2.1.4\lib\browsermob-dist-2.1.4.jar"
    port = 10000
    port = 9001
    port = 9000

    special = "BrowserMobProxyService"
    special = "BrowserMobStarter"

    if special == "BrowserMobProxyService":
        mps = BrowserMobProxyService(f_exe=f_exe, port=port)
        # mps.run()
        print("is_active", mps.is_active())
        r = mps._is_listening()
        # mps.run_if_not_active()
        print("r=%s" % r)

    elif special == "BrowserMobStarter":
        args = {
            "path": path,
            "f_exe": f_exe,
            "port": port,
        }
        bm = BrowserMobStarter(**args)
        print(bm)
        # bm.start_server()

        params = {}
        proxy = bm.create_proxy(params=params)
        print("proxy=%s" % proxy, proxy.selenium_proxy())
        # wait_for_ok('good proxy?')

        t = 1
        if t:
            from selenium import webdriver

            profile = webdriver.FirefoxProfile()
            profile.set_proxy(proxy.selenium_proxy())
            driver = webdriver.Firefox(firefox_profile=profile)

            # proxy.new_har("google")
            proxy.new_har(
                "req", options={"captureHeaders": True, "captureContent": True}
            )

            url = "https://bet365.es"
            url = "https://www.google.com"
            driver.get(url)

            # proxy.har  # returns a HAR JSON blob

            har = proxy.har
            scan_har(har)
            save_har(har)

    else:
        wait_for_ok("ERROR - unknown special=%s" % special)

"""
Прокси прописывается в профиле автоматически?
    https://octopus.com/blog/selenium/11-adding-the-browsermob-proxy/adding-the-browsermob-proxy
"""
