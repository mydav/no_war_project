#!/usr/bin/python
# -*- coding: utf-8 -*-

from modules import *
from modules_mega_23.xpath_functions import Xpather


class Helpers_human_emulator(Xpather):
    def __init__(self):
        Xpather.__init__(self, special=["youtube"])

    def open_main_page(self, u_main="main", polube=True):
        """
        """
        fun = "open_main_page"

        S = self.S
        if u_main == "main":
            u_main = self.u_main

        print
        "[%s url=%s" % (fun, u_main),
        need_open = True
        if not polube:
            url = S.url(1)
            if url == u_main:
                need_open = False

        if need_open:
            p = S.sgp(u_main)
            print
            "+%s]" % fun
        return p

    def get_f(self, name="", rash=".html", d_to=""):
        if not d_to:
            d_to = self.d_temp
        f = "%s/%s%s" % (os.path.abspath(d_to), name, rash)
        return f

    def sleep_(self, cnt=1):
        sleep_(self.sleep_more * cnt)

    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<work with xpath
    def click_xpathHuman(
        self,
        xpath_key="skip_ads",
        want_random=1,
        want_scroll_to_element=0,
        page="",
    ):
        """
            кликаем как человек
            проверяем, и если есть видимый путь - его кликаем
        """
        fun = "click_xpathHuman"
        xpath = self.xpath(xpath_key)
        print
        "[%s: xpath_key=`%s`, xpath=`%s`)" % (fun, xpath_key, xpath),

        if page == "":
            page = self.S.sgp()

        clicked = self.S.speed_select_and_click_existing_xpath(
            page,
            xpath,
            want_scroll_to_element=want_scroll_to_element,
            mode_elements="any_first_element",
        )
        print
        "+%s]" % fun
        return clicked

    def random_scroll(self, *args, **kwargs):
        return self.S.random_scroll(*args, **kwargs)
