#!/usr/bin/python
# -*- coding: utf-8 -*-

from modules import *
import time

from modules.mozgo_funcs import fun_polube

# from modules.downloaders import requests_u

# from modules_23.my_forms import pycus_u, print_response_info


class CenterKoordinator:
    def __init__(
        self,
        u_main=None,
        u_save="[u_main]/save_info/",
        u_get="[u_main]/get_info/",
        # save_data
        mode_save_data="pickle",
        cnt_tries_save_data=10,
        on_error_save_data="continue",
        timeout_save_data=0.5,
        headers=None,
        # get_data
        timeout_get_data=0.5,
        cnt_tries_get_data=10,
        seconds_sleep_on_error=1,
        on_error_get_data="ERROR_FUN_NOT_CALCULATED",
        name="CenterKoordinator",
    ):
        if u_main is None:
            u_main = "http://localhost:8081"

        self.name = name
        self.u_main = u_main
        repl = {
            "[u_main]": u_main,
        }
        self.u_save = no_probely(u_save, repl)
        self.u_get = no_probely(u_get, repl)

        self.mode_save_data = mode_save_data
        self.cnt_tries_save_data = cnt_tries_save_data
        self.on_error_save_data = on_error_save_data

        default_headers = {
            "User-Agent": "admin",
        }
        self.headers = headers if headers is not None else default_headers
        self.timeout_save_data = timeout_save_data

        # get data
        self.timeout_get_data = timeout_get_data
        self.cnt_tries_get_data = cnt_tries_get_data
        self.on_error_get_data = on_error_get_data
        self.seconds_sleep_on_error = seconds_sleep_on_error

    def save_data(
        self, data, f=None, timeout=None, cnt_tries=None, on_error=None
    ):
        if cnt_tries is None:
            cnt_tries = self.cnt_tries_save_data

        if on_error is None:
            on_error = self.on_error_save_data

        r = fun_polube(
            fun=self.save_data_one,
            cnt_tries=cnt_tries,
            on_error=on_error,
            data=data,
            f=f,
            timeout=timeout,
        )
        return r

    def save_data_one(self, data, f=None, mode=None, timeout=None):
        debug = True

        if mode is None:
            mode = self.mode_save_data

        if timeout is None:
            timeout = self.timeout_save_data

        posting = None

        if mode == "json":
            json_string = json.dumps(data)
            posting = json_string

        elif mode == "pickle":
            posting = pickle.dumps(data)

        elif mode == "post":
            posting = data

        else:
            wait_for_ok("unknown mode %s" % mode)

        t = 1
        t = 0
        if t:
            print("got data {type(data)} {data}")
            print("send `{json_string}`")

        u_save = self.u_save
        # u_save = 'https://httpbin.org/post'

        t_start = time.time()

        mode = "pycus"
        mode = "learning"
        if mode == "learning":
            response = requests_u(
                u_save, data=posting, headers=self.headers, timeout=timeout
            )
            print("response=%s" % response)

            status_code = response.status_code
            response_text = response.text

        else:
            args = {
                "u": u_save,
                "sposob": "requests",
                "headers": self.headers,
                "post": json_string,
                "connect_timeout": timeout,
                "timeout": timeout,
            }
            r = pycus_u(args)
            print(r)
            response_text = r["html"]
            status_code = r["kod"]

        seconds = time.time() - t_start
        print("sent in %.2f seconds, status code: %s" % (seconds, status_code))

        if debug:
            print(
                "status_code=%s response_text=`%s`"
                % (status_code, response_text)
            )

        try:
            json_answer = json.loads(response_text)
        except Exception as er:
            json_answer = {"error": "ERROR_NOT_JSON", "body": response_text}
        if f is not None:
            text_to_file(json_answer, f)

        return json_answer

    def get_data(
        self,
        encoding="utf-8",
        cnt_tries=None,
        on_error=None,
        fun_kwargs={},
        seconds_sleep_on_error=None,
        **kwargs
    ):
        if cnt_tries is None:
            cnt_tries = self.cnt_tries_get_data
        if on_error is None:
            on_error = self.on_error_get_data
        if seconds_sleep_on_error is None:
            seconds_sleep_on_error = self.seconds_sleep_on_error

        r = fun_polube(
            fun=self.get_data_one,
            fun_kwargs=fun_kwargs,
            cnt_tries=cnt_tries,
            on_error=on_error,
            encoding=encoding,
            seconds_sleep_on_error=seconds_sleep_on_error,
            **kwargs
        )
        return r

    def get_data_one(self, encoding="utf-8", **kwargs):
        fun = "get_data_one"
        # data = json.loads('{"lat":444, "lon":555}')
        debug = False

        t_start = time.time()
        timeout = 0.0001
        timeout = 1
        timeout = 2
        timeout = 0.1
        timeout = 0.05

        u = self.get_url_to_get_data(**kwargs)

        response = requests_u(
            u, headers=self.headers, timeout=self.timeout_get_data
        )
        # response = requests.get(self.u_,
        #                         headers=self.headers,
        #                         # timeout = timeout,
        #                         timeout=self.timeout,
        #                         )
        duration_1 = time.time() - t_start

        t_start_2 = time.time()
        data = response.json()

        if encoding:
            data = deep_encode(data, encoding)

            # data = see_to_norm_dct(data)  # obj_to_utf8(my_bet_abb_)
            # if 'last_surebets' in data:
            #     data['last_surebets'] = see_to_norm_dct(data['last_surebets'])

        duration_2 = time.time() - t_start_2

        # print("got in %.2f duration_1, status code: %s" % (
        #     duration_1, response.status_code))

        if debug:
            print("     response: %s" % response)
            print("     text: %s" % response.text)
            print("     data: %s" % data)

        if 1 and debug:
            print_response_info(response)

        duration = duration_1 + duration_2
        if 1:
            logger.info(
                "%s duration %.2f = download %.2f + process(encode) %.2f"
                % (fun, duration, duration_1, duration_2)
            )

        return data

    def get_url_to_get_data(self, **kwargs):
        fun = "get_url_to_get_data"
        print("[%s: kwargs %s" % (fun, kwargs))
        # wait_for_ok(fun)

        url = self.u_get
        return url

    def __repr__(self):
        m = "%s u_main=%s" % (self.name, self.u_main)
        return m


if __name__ == "__main__":
    t = 0
    t = 1
    if t:
        _ = {
            "str": "hello",
            "int": 1,
            "float": 1.25,
        }
        data = [
            {
                "value": 1,
                "lst": ["a", "b"],
                # 'bunched': Bunch(_),
                "dict": _,
            }
        ]
        u_main = "http://[ip_148]"
        u_main = "http://localhost:8081"
        """
        http://localhost:8081/save_bet365_bets/
        http://[ip_148]/get_bet365_bets/
        """
        args = {
            "u_main": u_main,
            "u_save": "[u_main]/save_valuebets/",
            "u_get": "[u_main]/get_valuebets/",
            "mode_save_data": "json",
        }
        center = CenterKoordinator(**args)
        print("center=%s" % center)
        # wait_for_ok()

        t = 1
        t = 0
        if t:
            saved = center.save_data(data, f="temp/last_posted_data.html")
            # saved = center.save_data_one(data, f="temp/last_posted_data.html")
            # saved = center.save_data_one(data)
            print(type(saved), "saved=%s" % saved)
            wait_for_ok()

        t = 0
        t = 1
        if t:
            valuebets = center.get_data()
            print("result: ", type(valuebets), "valuebets=%s" % valuebets)

    os._exit(0)
