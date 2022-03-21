#!/usr/bin/python
# -*- coding: utf-8 -*-

from modules import *

# from modules_mega import *


class HtmlState_Parser(object):
    def __init__(
        self,
        name="HtmlState_Parser",
        state_to_xpath=[],
        d_test="",  # 	все тесты-примеры сюда собираем
        S=None,
        # otl=0,
        want_save_page_if_state_unknown=1,
        # want_save_page_if_state_unknown=0,
        want_stop_if_state_unknown=0,
        otl=1,
        add_more_state_to_xpath=["google"],
    ):
        """
			register_stater = GmailRegisterState_Parser()
			r_state = register_stater.scrap_state(text, S)
			state_login = r_state['state']

		"""
        self.name = name
        self.add_more_state_to_xpath = add_more_state_to_xpath[:]
        self.init_state_to_xpath(state_to_xpath)
        self.d_test = d_test
        self.S = S
        self.otl = otl
        self.text_starts_with = "text "
        self.want_save_page_if_state_unknown = want_save_page_if_state_unknown
        self.want_stop_if_state_unknown = want_stop_if_state_unknown

        self.d_unknown_state = "%s/!add_pageWithState_for_test" % self.d_test

        # wait_for_ok(self.name)

        if self.otl:
            logger.debug("__init__ parser %s" % self.name)
            logger.debug("d_test: %s" % self.d_test)
            logger.debug("state_to_xpath:")
            show_list(state_to_xpath)
            self.print_states_info()
            # wait_for_ok()

    def init_state_to_xpath(self, state_to_xpath=[]):
        """
			для гугла может быть регалка, постилка, логинилка и т.д.
			И очень много states будут теми же. Вот я их и собираю.
			взяли все списки с возможными условиями
		"""
        list_with_state_to_xpath = []
        if "google" in self.add_more_state_to_xpath:
            list_with_state_to_xpath.append(self.more_state_to_xpath_google())

        list_with_state_to_xpath.append(state_to_xpath)

        full_state_to_xpath = []
        for state_to_xpath in list_with_state_to_xpath:
            for _ in state_to_xpath:
                full_state_to_xpath.append(_)

        self.state_to_xpath = full_state_to_xpath[:]
        return self.state_to_xpath

    def more_state_to_xpath_google(self):
        """
		"""
        more = [
            ["empty_selenium_page", is_empty_selenium_page,],
            [
                "choose_account",
                "//h1",
                {"tag": "text_kl", "value": "Choose an account"},
            ],
            ["settings_of_domain", "text You are a verified owner"],
            [
                "agree_new_features",
                "text <title>Some new features for your Google Account</title>",
            ],
            [
                "agree_new_features",
                "text <title>Новые функции в вашем аккаунте Google<",
            ],
            [
                "firefox_cookies_error",
                'text href="https://support.google.com/accounts/answer/61416',
            ],
            # <h1 data-a11y-title-piece="" id="headingText" jsname="r4nke"><span jsslot="">Sign in
            ["sign_in__verify", is_sign_in__verify],
            ["error_404", is_error_404],
            ["net_error", is_net_error],
            ["chrome_error", "text <title>Welcome to Chrome</title>",],
            [
                "popolni_inet",
                "text Нехватка для начала следующего периода</div>",
            ],
        ]
        return more

    def get_file_with_page_to_test_state(self, state=""):
        """
		"""
        f = "%s/%s.html" % (self.d_test, state)
        return f

    def print_states_info(self):
        states = self.get_known_states()
        logger.debug("known %s states" % len(states))
        show_list(states)

    def special_action_before_scraping(self):
        pass

    def explore(
        self, html="", detailed=1,
    ):
        """
		"""
        fun = "explore"
        logger.debug("[%s:" % fun)
        xpaths = [
            "//title",
            "//h1",
            "//h2",
            "//h3",
            "//form",
            "//section",
        ]
        t = 1
        if t:
            xpaths = [
                "//h1[text()='Account disabled']",
            ]
        parsed = {}
        for num, xpath in enumerate(xpaths):
            logger.debug(
                "\n	%s/%s isXpath for `%s`:" % (num + 1, len(xpaths), xpath)
            )
            elements = isXpath(html, xpath, detailed=detailed)
            parsed["xpath"] = elements[:]
            for num_element, element in enumerate(elements):
                logger.debug(
                    "	element %s/%s" % (num_element + 1, len(elements))
                )
                show_dict(element, "		")
            # show_list(elements)

        logger.debug("+%s]" % fun)
        return parsed

        wait_for_ok("explore done")

    def get_known_states(self):
        """
			получаем список всех известных состояний
		"""
        states = []
        for state_xpath in self.state_to_xpath:
            state = state_xpath[0]
            states.append(state)
        states = unique_with_order(states)
        return states

    def test_states_from_files(
        self,
        # files=[],
        file_names=[],
        # want_explore=1,
        want_explore=0,
    ):
        """
			тест всех состояний из файлов
		"""
        d_test = self.d_test

        if file_names != []:
            files = [
                self.get_filePath_in_test_directory(f_name)
                for f_name in file_names
            ]

        else:
            files = get_all_file_names(d_test)
            files = [
                f for f in files if f.find("add_pageWithState_for_test") == -1
            ]

        t = 1
        t = 0
        if t:
            f_name = "request_indexing.html"
            # f_name = 'click_got_it.html'
            # f_name = 'click_got_it#min.html'
            # f_name = 'overview.html'
            # f_name = 'indexing_request_rejected.html'
            f_name = "domain_not_my.html"
            f_name = "retrieving_data_from_google_index#3.html"
            f_name = "request_indexing#2.html"
            f_name = "indexing_requested.html"
            f_name = "request_indexing#3.html"
            f_name = "request_indexing#4.html"
            f_name = "request_indexing_with_error#1.html"
            f_name = "retrieving_data_from_google_index#4.html"
            f_name = "overview#2.html"
            f_name = "step_checking.html"
            files = ["%s/%s" % (d_test, f_name)]

        cnt_files = len(files)

        errors = []
        error_files = []

        for f in files:
            p = text_from_file(f)
            f_name = os.path.basename(f)

            logger.debug("\n" * 2 + f_name)

            state_must_be = f_name.split(".")[0]
            state_must_be = state_must_be.split("#")[0]

            if want_explore:
                r_state_found = self.explore(p)

            else:
                r_state_found = self.scrap_state(p)
            # wait_for_ok(r_state_found)

            state_found = r_state_found["state"]

            if state_found != state_must_be:
                er = '%s error = must_be "%s" != "%s" found' % (
                    f_name,
                    state_must_be,
                    state_found,
                )
                errors.append(er)
                error_files.append(os.path.basename(f_name))

            logger.debug("%s %s" % (state_must_be, f_name))
            logger.debug("r_state_found:")
            show_dict(r_state_found)

        cnt_errors = len(errors)
        if cnt_errors == 0:
            Show_step("full %s success" % cnt_files)
        else:
            Show_step("have %s/%s errors" % (cnt_errors, cnt_files))
            show_list(errors)
            logger.debug("file names:")
            show_list(error_files)

    def find_state_from_xpath(
        self, p="", state_to_xpath=[], S=None, special_values=[]
    ):
        if S is None:
            S = self.S

        found_state = None

        for num_check, state_xpath in enumerate(state_to_xpath):
            if self.otl:
                logger.debug(
                    "	%s/%s check state_xpath	`%s`"
                    % (num_check + 1, len(state_to_xpath), state_xpath)
                )

            condition = {}
            if len(state_xpath) == 2:
                state, xpath = state_xpath
                condition = {
                    "checking": "xpath_exists",
                }

            elif len(state_xpath) == 3:
                state, xpath, condition = state_xpath
                d_conditions = {
                    "checking": "check_xpath_value",
                }
                condition = add_defaults(condition, d_conditions)
                # condition = {'tag': 'text_kl', 'value': 'Account disabled'}

            else:
                wait_for_ok("ERROR - len(state_xpath) not in [2, 3]")

            # wait_for_ok('condition %s' % condition)

            if condition["checking"] == "check_xpath_value":
                elements = isXpath(p, xpath, detailed=1, otl=0)
                if self.otl:
                    logger.debug("	state %s, isXpath" % state, elements)

                if len(elements) > 0:
                    if (
                        S != None
                    ):  # проверяем что точно есть такой путь и видимый (в селениуме)
                        logger.debug("check visibility...")
                        if S.xpath_is_visible(xpath):
                            logger.debug("selenium found visible element")
                        else:
                            elements = []
                        logger.debug("+checkedVisibility")
                    else:
                        logger.debug("no selenium to checks visibility")

                for element in elements:
                    if element[condition["tag"]] == condition["value"]:
                        if self.otl:
                            logger.debug("	found condition %s" % condition)
                        found_state = state
                        break

                if found_state is not None:
                    break

            elif condition["checking"] == "xpath_exists":
                if xpath in special_values:
                    found_state = state
                    break

                xpath_type = analyze_xpath_type(xpath, self.text_starts_with)
                # logger.debug('xpath_type %s' % xpath_type)
                # wait_for_ok(xpath_type)

                if xpath_type == "text_exists":
                    parts = xpath.split(self.text_starts_with)
                    text_to_find = parts[-1]
                    if p.find(text_to_find) != -1:
                        found_state = state
                        break

                elif xpath_type == "xpath":
                    elements = isXpath(p, xpath, detailed=1, otl=0)
                    if self.otl:
                        logger.debug("	state %s, isXpath" % state)

                        # если слишком длинно - обрезаем и выводим
                        elements_str = str(elements)
                        if len(elements_str) > 2000:
                            logger.debug(elements_str[:300])
                        else:
                            logger.debug("elements %s" % elements)

                    if (
                        len(elements) > 0
                    ):  # проверяем что точно есть такой путь и видимый (в селениуме)
                        if (
                            S != None
                        ):  # проверяем что точно есть такой путь и видимый (в селениуме)
                            logger.debug("check visibility...")
                            if S.xpath_is_visible(xpath):
                                logger.debug("selenium found visible element")
                            else:
                                elements = []
                            logger.debug("+checkedVisibility")
                        else:
                            logger.debug("no selenium to checks visibility")

                    if len(elements) > 0:
                        show_list(elements)
                        found_state = state
                        break

                elif xpath_type == "function":
                    func = xpath
                    # если ф-я получает аргумент S = хочу чтобы с аргументом и вызывалось
                    function_result = execute_funcions_with_selenium_if_exists(
                        func, p, S
                    )
                    if function_result:
                        found_state = state
                        break

                else:
                    wait_for_ok("unknown xpath type for %s" % xpath)

        # wait_for_ok('found state `%s`' % found_state)
        return found_state

    def scrap_state(self, p="", S=None):
        """
			парсим состояние консоли
			https://search.google.com/search-console/inspect?resource_id=http%3A%2F%2F68d0299ae3d6f96dfaac464ac8841ea3.indexfullworld.ru%2F&id=AbZsthtrN9t3yNONntsIKw&hl=en
		"""
        if S is not None:
            self.S = S

        self.special_action_before_scraping()

        fun = "scrap_state"
        otl = self.otl

        state = ""
        # details = ''

        # 	testing
        t = 1
        t = 0
        if t:
            # так тоже можно, но типа сложнее ищем имя таблицы, которая висит выше всего
            xpath = "//div[@aria-level='1']"
            xpath = "//title"
            xpath = "//title[text()='У вас нет доступа к этому ресурсу']"

            f = r"d:\kyxa\!code\!actual\google_addurl_selenium\data\!new_console\states_console\domain_not_my.html"
            p = text_from_file(f)

            # xpath = "//title"
            # xpath = "//title[text()='У вас нет доступа к этому ресурсу']"

            p = "<title>У вас нет доступа к этому ресурсу</title>"
            logger.debug("	isXpath %s" % isXpath(p, xpath, detailed=1))

            ##title_warning: Indexing request rejected
            ##isXpath [{
            #'text': '',
            #'tag': 'div',
            #'tostring': '<div aria-level="1" role="heading" class="PNenzf" jsname="YASyvd" id="dwrFZd2"><div class="NEqwFd"><span aria-hidden="true" class="DPvwYc rQEKCd">\xc3\xae\xc2\x97\xc2\x89</span><div>Indexing request rejected</div></div></div>',
            #'text_c': '\xc3\xae\xc2\x97\xc2\x89Indexing request rejected'}]
            wait_for_ok()

        # 	start out work
        special_values = self.scrap_special_values(p)

        # wait_for_ok('have %s condition for state_to_xpath: %s' % (len(self.state_to_xpath), self.state_to_xpath))
        found_state = self.find_state_from_xpath(
            p,
            state_to_xpath=self.state_to_xpath,
            special_values=special_values,
        )
        more_state_info = self.scrap_more_state_info(
            p, found_state=found_state
        )

        if found_state is not None:
            state = found_state
            if otl:
                logger.debug('found state "%s" by xpath' % state)

        if state == "" and self.want_save_page_if_state_unknown:
            self.save_page_for_manual_checking(p)
            if self.want_stop_if_state_unknown:
                wait_for_ok("empty state?")

        state, more_state_info = self.deeper_checks_of_state(
            state, more_state_info
        )

        r = {
            "state": state,
        }
        r = add_defaults(r, more_state_info)
        return r

    def scrap_state_min(self, p="", S=None):
        """
			парсим состояние консоли
			https://search.google.com/search-console/inspect?resource_id=http%3A%2F%2F68d0299ae3d6f96dfaac464ac8841ea3.indexfullworld.ru%2F&id=AbZsthtrN9t3yNONntsIKw&hl=en
		"""
        fun = "scrap_state"
        otl = self.otl

        # text_to_file(p, 'temp/last_%s.html' % fun)
        state = ""
        # details = ''

        r = {
            "state": state,
            #'details':details,
        }
        return r

    def deeper_checks_of_state(self, state="", more_state_info={}):
        return state, more_state_info

    def scrap_special_values(self, p=""):
        special_values = []
        return special_values

    def scrap_more_state_info(self, p="", found_state=""):
        # title_warning = self.scrap_title_warning(p)
        _ = {
            #'title_warning': title_warning,
        }
        return _

    def save_page_with_state_if_state_is_unknown(self, state="", page=""):
        """
			для перевода старых прог в новый вид - состояния сохраняем
		"""
        fun = "save_page_with_state_if_state_is_unknown"
        logger.debug("[%s state `%s`" % (fun, state))
        f_test = self.get_file_with_page_to_test_state(state)
        if file_exists(f_test):
            logger.debug(
                "already exists test file `%s` for state `%s`]"
                % (f_test, state)
            )
            return False

        f_full = "%s/%s/%s#%s.html" % (
            self.d_unknown_state,
            state,
            state,
            to_hash(page),
        )
        text_to_file(page, f_full)
        logger.debug("+saved to `%s`" % f_full)
        return True

    def save_page_for_manual_checking(self, page="", f_part=None, f_full=None):
        """
			сохраняем страницы, чтобы потом их вручную обработать
		"""
        fun = "save_page_for_manual_checking"

        if f_full is None:
            if f_part is None:
                f_part = self.name

            f_full = "data/!page_for_manual_checking/%s/%s.html" % (
                f_part,
                to_hash(page),
            )
            f_full = "%s/%s/%s.html" % (
                self.d_unknown_state,
                fun,
                to_hash(page),
            )

        print("[%s - ERROR - save to %s]" % (fun, f_full))
        text_to_file(page, f_full)
        return f_full

    def get_filePath_in_test_directory(self, f_name=""):
        return "%s/%s" % (self.d_test, f_name)

    def is_logined_in_search_console(self, p=""):
        phrases = [
            "<title>Search Console - Crawl URL</title>",
            'href="https://accounts.google.com/SignOutOptions',
        ]
        return found_phrase_in_text(phrases, p)


class LoginState_Parser(HtmlState_Parser):
    def __init__(
        self,
        name="LoginState_Parser",
        d_test=None,
        S=None,
        otl=0,
        want_save_page_if_state_unknown=1,
    ):
        """
		"""
        if d_test is None:
            d_test = get_directory_with_stateParserTests("states_login")

        state_to_xpath = [
            # ['test_always_true', func_always_true],
            ["logined_in_search_console", self.is_logined_in_search_console],
            [
                "account_disabled",
                "//h1",
                {"tag": "text_kl", "value": "Account disabled"},
            ],
            [
                "account_not_found",
                """text Couldn't find your Google Account</div>""",
            ],
            ["enter_email", self.is_enter_email],
            ["enter_email", '//input[@id="identifierId"]'],
            ["enter_password", '//input[@name="password"]'],
            ["protect_account", '//div[text()="Protect your account"]'],
            [
                "verify_its_you",
                "//h1",
                {"tag": "text_kl", "value": "Verify it's you"},
            ],
            [
                "sms_verification",
                '//input[@name="SendCode"][@value="Get code"]',
            ],
            ["loading_please_wait", is_loadingPlease_wait,],
            ["logined_in_youtube", '//button[@id="avatar-btn"]',],
            ["youtube", "text <title>YouTube</title>",],
            [
                "privacy_reminder",
                "text <title>A privacy reminder from Google</title>",
            ],
            ["use_different_browser", "text >Try using a different browser.",],
        ]

        # logger.debug('d_test: %s' % d_test)
        HtmlState_Parser.__init__(
            self,
            name=name,
            state_to_xpath=state_to_xpath,
            d_test=d_test,
            S=S,
            otl=otl,
            want_save_page_if_state_unknown=want_save_page_if_state_unknown,
        )

    def is_enter_email(self, p):
        # <input type="email" class="whsOnd zHQkBf" jsname="YPqjbf" autocomplete="username" spellcheck="false" tabindex="0" aria-label="Email or phone" name="identifier" value="" autocapitalize="none" id="identifierId" dir="ltr" data-initial-dir="ltr" data-initial-value="">

        # а это когда введен но невидим
        # 	<input type="email" name="identifier" class="VwCw" tabindex="-1" aria-hidden="true" spellcheck="false" value="x@.gmail.com" jsname="KKx9x" autocomplete="off" id="hiddenEmail">

        xpath_email = '//input[@type="email"][@name="identifier"][not(@id="hiddenEmail")]'
        xpath_button = '//*[text()="Next"]'
        return found_all_xpaths([xpath_email, xpath_button], p)

    def scrap_phone(self, page=""):
        # phone = find_from_to_one(' dir="ltr"', '</span>', page)
        phone = find_from_to_one('><span dir="ltr"', "</span>", page)
        # logger.debug(phone)
        phone = find_from_to_one(">", "nahposhuk", phone)
        return phone


class ConsoleState_Parser(HtmlState_Parser):
    def __init__(
        self,
        name="ConsoleState_Parser",
        d_test=None,
        S=None,
        otl=0,
        want_save_page_if_state_unknown=0,
    ):
        """
		"""
        if d_test is None:
            d_test = get_directory_with_stateParserTests("states_console")

        xpath_for_request_indexing = "//c-wiz[@aria-hidden='false']"
        xpath_for_request_indexing = "//div[@jscontroller='QeBYfc']"
        state_to_xpath = [
            ["test_reload_module_V1", "text test_reload_module"],
            ["test_reload_module_V2", "text test_reload_module"],
            ["pure_spam", "text >Pure spam<"],
            ["pure_spam", "text >Manual actions: <"],
            ["welcome_to_the_new_console", self.is_welcome_to_the_new_console],
            # ['manual_ban', 'text Manual actions: <span class="LbvObc">1</span> issue detected</div></div><div class="NyaQMc">Open report'],
            # 	previous_captcha
            [
                "indexing_requested",
                "//div[@role='dialog']//span[contains(., 'URL was added to a priority crawl queue')]",
            ],
            ["old_panel_fetch_as_google", is_old_panel_fetch_as_google],
            # ['indexing_request_rejected', "//div[@aria-level='1' and text()[contains(.,'%s')]]" % 'Indexing request rejected'],#а 2 вместе - нет
            # ['indexing_request_rejected', "//div[@aria-level='1']"],#ищет
            # ['indexing_request_rejected', "//div[text()[contains(.,'%s')]]" % 'Indexing request rejected'],#и так ищет
            ["indexing_request_rejected", "text Indexing request rejected"],
            # ['retrieving_data_from_google_index', 'text Retrieving data from Google Index'],
            [
                "retrieving_data_from_google_index",
                "//div[text()='Retrieving data from Google Index']",
            ],
            # названия окон вылазящих
            ["click_got_it", "//span[text()='Got it']"],
            # <div class="pTyUxe aIHXNb" jscontroller="XD6nVd" jsaction="rcuQ6b:npT2md;" aria-hidden="true"
            [
                "loading_overview",
                "//div[@class='pTyUxe aIHXNb'][@aria-hidden='true']",
            ],
            ["overview", "//span[@title='Overview']"],
            [
                "domain_not_my",
                "//title[text()='У вас нет доступа к этому ресурсу']",
            ],
            # previous request_indexing
            ###################хочу сделать и для локальной проверки - пока не могу
            # ['indexing_requested', "%s//div[@aria-level='1' and contains(., '%s')]" % (xpath_for_request_indexing, 'Indexing requested')],#а 2 вместе - нет
            # ['indexing_requested', "%s//span[text()='Indexing requested']" % xpath_for_request_indexing],
            # ['request_indexing', "%s//span[text()='Request indexing']" % xpath_for_request_indexing],
            # ['request_indexing', self.is_visible_requestIndexing],
            # ['indexing_requested', self.is_visible_requestAgain],
            ["testing_can_be_indexed", is_testing_can_be_indexed],
            ###################для селениума это работает
            [
                "indexing_requested",
                "%s//div[@aria-level='1' and contains(., '%s')]"
                % (xpath_for_request_indexing, "Indexing requested"),
            ],  # а 2 вместе - нет
            [
                "indexing_requested",
                "%s//span[contains(., 'URL was added to a priority crawl queue')]"
                % xpath_for_request_indexing,
            ],
            [
                "indexing_requested",
                "%s//span[text()='Request again']"
                % xpath_for_request_indexing,
            ],
            ["captcha", is_captcha],
            [
                "request_indexing",
                "%s//span[text()='Request indexing']"
                % xpath_for_request_indexing,
            ],
            ["test_live_url", "//span[text()='Test live URL']"],
            ["old_panel_fetch_as_google", is_old_panel_fetch_as_google],
            [
                "ownership_auto_verified",
                '//span[text()="Ownership auto verified"]',
            ],
            ["select_property", '//div[text()="Please select a property"]'],
            ["ru", "text >Обзор<"],
        ]

        # logger.debug('d_test: %s' % d_test)
        HtmlState_Parser.__init__(
            self,
            name=name,
            state_to_xpath=state_to_xpath,
            d_test=d_test,
            S=S,
            otl=otl,
            want_save_page_if_state_unknown=want_save_page_if_state_unknown,
        )

    def scrap_special_values(self, p=""):
        title_warning = self.scrap_title_warning(p)
        special_values = [
            title_warning,
        ]
        return special_values

    def scrap_more_state_info(self, p="", found_state=""):
        title_warning = self.scrap_title_warning(p)
        url_in_console = self.scrap_url_in_console(p)
        _ = {
            "title_warning": title_warning,
            "url_in_console": url_in_console,
            "console_type": "new",
        }
        return _

    def deeper_checks_of_state(self, state="", more_state_info={}):
        if state == "old_panel_fetch_as_google":
            more_state_info["console_type"] = "old"

        need_check_url_in_console = 0

        if state in [
            #'retrieving_data_from_google_index',
            "test_live_url",
            "request_indexing",
            "testing_can_be_indexed",
            "indexing_request_rejected",
            "indexing_requested",
        ]:

            need_check_url_in_console = 1

        logger.debug(
            "state=%s, need_check_url_in_console %s, console_type %s]"
            % (
                state,
                need_check_url_in_console,
                more_state_info["console_type"],
            )
        )

        if need_check_url_in_console:
            if more_state_info["url_in_console"] == "":
                wait_for_ok("%s error - empty url" % fun)

        if (
            state in ["request_indexing"]
            and more_state_info["title_warning"].find(
                "Oops! Something went wrong"
            )
            != -1
        ):
            state = "request_indexing_with_error"

        return state, more_state_info

    def scrap_url_in_console(self, p=""):
        url_in_console = ""
        xpath = '//span[@class="PuCZwf"]'
        elements = isXpath(p, xpath, detailed=1)
        if len(elements) > 0:
            url_in_console = elements[0]["text_kl"]
        return url_in_console

        # гавняно вручную делал
        url_in_console = find_from_to_one('data-url="', '"', p)
        if url_in_console == "":
            url_in_console = find_from_to_one(
                "AF_initDataCallback({key: 'ds:4',", "\n", p
            )
            last = url_in_console.split(',["')[-1]
            url_in_console = find_from_to_one("nahposhuk", '"', last)
            if url_in_console.find("isError:  false ,") != -1:
                url_in_console = ""

        if url_in_console == "":
            url_in_console = find_from_to_one(
                "Button that controls the shown version of the inspected URL",
                "</div></div></div>",
                p,
            )
            url_in_console = url_in_console.split(">")[-1]

        if url_in_console == "":
            url_in_console = find_from_to_one(
                'id="/search-console/inspect-V1"', "</span></div>", p
            )
            url_in_console = url_in_console.split(">")[-1]

        # wait_for_ok(url_in_console)
        return url_in_console

    def scrap_title_warning(self, p=""):
        fun = "scrap_title_warning"
        title_warning = get_cleared_part_in_tags(' aria-level="1"', "</div", p)

        if title_warning != "" and title_warning[0] in ["'"]:
            title_warning = ""
        # wait_for_ok(title_warning)

        if title_warning == "":
            title_warning = get_cleared_part_in_tags(
                'id="headingText"', "</h1", p
            )
            # wait_for_ok(title_warning)

        heading_parts = get_cleared_parts_in_tags(
            'role="heading" aria-level="1"', "</div", p
        )  # //на потом

        if self.otl:
            logger.debug("[%s " % fun)
            logger.debug("		title_warning: `%s`" % title_warning)
            logger.debug("		heading parts: `%s`" % heading_parts)
            logger.debug("]")
        return title_warning

    def is_visible_requestAgain(self, text=""):
        style = scrap_css_style_by_class_name("IbfkTd", text)
        # wait_for_ok(style)
        return not found_phrase_in_text("display:none", style)

    def is_visible_requestIndexing(self, text=""):
        style = scrap_css_style_by_class_name("cTsG4", text)
        # wait_for_ok(style)
        return not found_phrase_in_text("display:none", style)

    def is_welcome_to_the_new_console(self, text=""):
        xpaths = [
            '//div[text()="Welcome to the new Google Search Console"]',
            '//span[text()="Start"]',
        ]
        return found_all_xpaths(xpaths, text)


def func_always_true(text=""):
    return 1


def analyze_xpath_type(xpath="", text_starts_with="text "):
    """
	return:
		xpath
		text_exists
		function
	"""
    fun = "analyze_xpath_type"
    # logger.debug('%s %s' % (type(xpath), xpath))
    m = "what_is_xpath? type %s, xpath %s" % (type(xpath), xpath)
    # print(m)

    type_str = str(type(xpath))
    xpath_type = "unknown"

    if isinstance(xpath, str):
        parts = xpath.split(text_starts_with)

        if (
            len(parts) == 2 and parts[0] == ""
        ):  # если начинается на text ... - значит ищем просто вхождение
            xpath_type = "text_exists"

        elif xpath.find(r"//") != -1:
            xpath_type = "xpath"

        else:
            wait_for_ok(
                "%s ERROR - xpath `%s` is string but unknown type"
                % (fun, xpath)
            )

    elif (
        type_str.find("<type 'function'>") == 0
        or type_str.find("<type 'instancemethod'>") == 0
    ):
        xpath_type = "function"

    if xpath_type == "unknown":
        m = "what_is xpath_type? type %s, xpath %s" % (type(xpath), xpath)
        logger.error(m)
        wait_for_ok()

    return xpath_type


def get_directory_with_stateParserTests(parser_name=""):
    d_test = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "data",
        "!state_parser",
        parser_name,
    )
    return d_test


def is_empty_selenium_page(text=""):
    return is_chrome_welcome_page(text) or is_firefox_welcome_page(text)


def is_firefox_welcome_page(text=""):
    phrases = [
        '<html xmlns="http://www.w3.org/1999/xhtml"><head></head><body></body></html>',
        "<html><head></head><body></body></html>",
        "<title>Добро пожаловать в Chrome!</title>",
    ]
    return found_phrase_in_text(phrases, text)


def is_chrome_welcome_page(text=""):
    phrases = [
        "<title>Добро пожаловать в Chrome!</title>",
    ]
    return found_phrase_in_text(phrases, text)


def is_old_panel_fetch_as_google(text):
    phrases = [
        "<title>Search Console - Fetch as Google - ",
        'id="add-url-disabled">To submit a URL to the Google index, either',
    ]
    return found_phrase_in_text(phrases, text)


def is_error_404(text):
    # wait_for_ok()
    phrases = [
        "<title>Not Found</title>",
        "<h1>Not Found</h1>",
        "<h2>Error 404</h2>",
    ]

    phrases_one = [
        "<title>Error 404 (Not Found)!!1</title>",
    ]

    return found_all_phrases_in_text(phrases, text) or found_phrase_in_text(
        phrases_one, text
    )


def is_net_error(text):
    phrases = [
        "<title>Сервер не найден</title>",
        "<title>Проблема при загрузке страницы</title>",
    ]
    return found_phrase_in_text(phrases, text)


def is_testing_can_be_indexed(text, S=None):
    xpaths = [
        "//div[@aria-level='1'][text()='Testing if live URL can be indexed']",
        "//div[@aria-level='1'][contains(., 'Testing live URL')]",
    ]
    if not is_captcha(text, S) and found_atLeastOne_xpath(xpaths, text):
        return 1
    return 0


def is_captcha(text, S=None):
    xpaths = [
        # 			#<iframe frameborder="0" title="recaptcha challenge"
        "//div[contains(@style,'visibility: visible')]//div[contains(@style,'z-index: 2000000000')]//iframe[@title='recaptcha challenge']",
    ]

    good = 0
    if found_all_xpaths(xpaths, text):
        if S is None:
            good = 1
        else:
            good = S.all_xpaths_are_visible(xpaths)

    # wait_for_ok('is_captcha %s' % good)
    return good


def is_sign_in__verify(text, S=None):
    # , {'tag': 'text_kl', 'value': 'Sign in'}],
    xpath = "//h1[@id='headingText']"
    elements = isXpath(text, xpath, detailed=1)
    if (
        len(elements) == 1
        and elements[0]["text_kl"] == "Sign in"
        and found_all_xpaths(
            ["""//div[text()="To continue, first verify it's you"]"""], text
        )
    ):
        return 1
    return 0


def is_loadingPlease_wait(text=""):
    all_phrases = [
        "<title>Google Accounts</title>",
        "<p>Loading, please wait ...</p>",
    ]
    return found_all_phrases_in_text(all_phrases, text)


def demo_function_to_test_reload():
    return 2


def execute_funcions_with_selenium_if_exists(func, p="", S=None):
    argdict = {
        #'p': p,
        "S": S,
    }
    return run_function_with_available_arguments(
        func, argdict, start_values=[p], default=p
    )


if __name__ == "__main__":
    spec = "test_parse"
    spec = "HtmlState_Parser"

    if spec == "test_parse":
        f = r"d:\server\usr\local\python\Lib\site-packages\modules_mega\data\!state_parser\states_login\state.html"
        f = r"d:\server\usr\local\python\Lib\site-packages\modules_mega\data\!state_parser\states_login\verify_its_you#phone2.html"
        f = r"d:\server\usr\local\python\Lib\site-packages\modules_mega\data\!state_parser\states_login\verify_its_you#phone3.html"
        page = text_from_file(f)
        phone = LoginState_Parser().scrap_phone(page)
        wait_for_ok("phone `%s`" % phone)
        os._exit(0)

    elif spec == "HtmlState_Parser":
        otl = 0
        otl = 1
        _ = {
            "otl": otl,
            "want_save_page_if_state_unknown": 0,
        }
        # stater = HtmlState_Parser(**_)
        stater = LoginState_Parser(**_)
        # stater = ConsoleState_Parser(**_)

        file_names = [
            #'request_indexing.html',
            #'domain_not_my.html',
            #'captcha.html',
            #'overview#ne_recaptcha.html',
            #'',
            #'indexing_requested#2.html',
            #'click_got_it#2.html',
            #'request_indexing#4.html',
            #'panel.html',
            #'testing_can_be_indexed.html',
            #'testing_can_be_indexed#2.html',
            #'retrieving_data_from_google_index.html',
            #'loading_overview.html',
            #'settings_of_domain.html',
            #'enter_password.html',
            #'empty_selenium_page#chrome_welcome_page.html',
            #'welcome_to_the_new_console.html',
            #'overview#222bf04ac6ff23e10071597e37b38561.html',
            #'protect_account.html',
            #'ca614390d6ec510361eabd6421097905.html',
            #'verify_its_you.html',
            #'ownership_auto_verified.html',
            #'old_panel_fetch_as_google#222c7abf8600c8a090edabc472a8e8c3.html',
            #'indexing_requested#hidden.html',
            #'9738392b78f76ae18254570731fd2758.html',
            #'testing_can_be_indexed#4.html',
            #'agree_new_features.html',
            #'agree_new_features#ru.html',
            #'choose_account.html',
            #'select_property.html',
            #'firefox_cookies_error.html',
            #'sms_verification.html',
            #'loading_please_wait.html',
            #'account_not_found.html',
            #'pure_spam.html',
            #'pure_spam#manual_actions.html',
            #'ru#overview.html',
            #'error_404.html',
            #'state.html',
            #'privacy_reminder.html',
            #'use_different_browser.html',
            # 2019.12.02
            #'net_error#loading_problem.html',
            #'net_error#server_ne_naiden.html',
            #'net_error#server_ne_naiden2.html',
            #'privacy_reminder#2.html',
            #'chrome_error.html',
            #'error_404#all_we_know.html',
            "popolni_inet.html",
        ]

        file_names0 = clear_list(
            """

		"""
        )

        _ = {
            "file_names": file_names,
        }

        t = 0
        t = 1
        if t:
            stater.test_states_from_files(**_)
            os._exit(0)

        t = 1
        t = 0
        if t:
            states = [
                "new state",
            ]
            for state in states:
                stater.save_page_with_state_if_state_is_unknown(state, state)
            wait_for_ok()

        t = 1
        t = 0
        if t:
            stater.print_states_info()
