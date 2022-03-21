# -*- coding: utf-8 -*-
from no_war_project.settings import *

from no_war_project.tasks_reader import *
from no_war_project.model import *

from modules import *
from modules_html.html_text_functions import kl
from light_browser.control_browser import LightBrowser, Translator
from ky_telegram.telegramer import TelegramReporter

t = 0
if t:
    zsuv1 = 0
    zsuv = 2
    frmt = ""

    t = 1
    if t:
        zsuv = 2
        frmt = "print"

    want_format = False
    want_format = True

    setup_all_loggers(zsuv=zsuv, want_format=want_format, frmt=frmt)

    t = 0
    if t:
        check_logger(logger)
        os._exit(0)


class TelegramDisliker:
    def send_dislike_to_telegram(
        self, url="", dislike: TelegramDislike = None
    ):
        """
        """
        fun = "send_dislike_to_telegram"
        tr = self.translator.translate

        if not dislike:
            dislike = TelegramDislike(url=url)

        url = dislike.url
        logger.debug2(f"{tr('send_report')} {url}")
        one_zhaloba = rewrite(choice(dislike.zhaloba))

        reporter = self.telegram_reporter
        r_sent = reporter.send_report(
            channel=url,
            message=one_zhaloba,
            f_sent=dislike.get_file_with_done_file(),
        )
        logger.debug(f"{r_sent=}")
        details = r_sent["details"]  # r_sent, already_sent

        error = get_api_error(r_sent)

        final_status = details
        if details in ["sent"]:
            final_status = "success"

        elif error in [
            "user_not_exists",
            "entity_not_exists",
            "chat_not_exists",
            "join_group_and_retry",
        ]:  # по факту это не ошибка
            final_status = error
            error = ""

        return self.universal_answer(
            error=error, final_status=final_status, answer=r_sent
        )


class InstagramDisliker:
    def send_dislike_to_instagram(
        self, url="", dislike: InstagramDislike = None
    ):
        """
        https://telegra.ph/%D0%86nstrukc%D1%96ya-z-%D1%96nformac%D1%96jnoi-protid%D1%96i-okupantam-u-Instagram-03-03
        :param url:
        :param zhaloba:
        :param dislike:
        :return:
        """
        fun = "send_dislike_to_instagram"
        S = self.S
        tr = self.translator.translate

        if not dislike:
            dislike = YoutubeChanelDislike(url=url)

        url = dislike.url

        logger.debug(f"[{fun}: for {dislike=}")

        want_start_info = True
        want_open_url = True
        want_check_login = True
        want_3_dots = True
        want_skarga = True
        want_select_on_account = True
        want_inform_bad_content = True
        want_inform_nasylstvo = True
        want_inform_zagroza_or_osoba = True
        want_check_success = True

        t = 0
        if t:
            want_start_info = False
            want_open_url = False
            want_check_login = False
            want_3_dots = False
            want_skarga = False
            want_select_on_account = False
            want_inform_bad_content = False
            want_inform_nasylstvo = False
            want_inform_zagroza_or_osoba = False
            want_check_success = False

        kwargs_s = {
            "timeout": 20,
            "timeout": 5,
            "checking": "clickable",
        }
        error = ""
        xpath = ""
        final_status = None
        final_text = None
        while True:
            if want_start_info:
                S.set_html_body(
                    f"<h1>Жалоба на instagram</h1><h2>на {url}</h2>"
                )

            if want_open_url:
                logger.debug2(f"{tr('open_url')} {url}")
                r_sgp_quick = S.sgp(url, seconds_sleep=0)

                if r_sgp_quick == False:
                    error = "url_not_loaded"
                    logger.warning(tr(error))
                    break

                self.random_sleep()

            if want_check_login:
                while True:
                    xpath = self.xpath("insta_not_logined")
                    logger.debug2(f"{tr('checking_login')}")
                    element = S.wait_for_presence(xpath, **kwargs_s)
                    if element:
                        logger.debug1(f"    not logined, logining")
                        self.save_page_to_debug_situation(
                            name="insta_not_logined"
                        )

                        sending = [
                            [xpath, "click_js"],
                        ]
                        r_clicked = S.ssend_values_quick(sending)
                        logger.debug(f"{r_clicked=}")

                        m = tr("message_please_login")
                        logger.critical(m)
                        inform_me_one()

                        m = tr("message_please_login_instructions")
                        wait_for_ok(m)

                        error = "not_logined"
                        break

                    break

            if error:
                break

            if want_3_dots:
                error = self.action(
                    xpath="insta_3_dots",
                    message=tr(f"click_3_dots"),
                    error_not_exists="no_3_dots",
                    # click_method="click",
                )

                if error:  # проверим - возможно канал тупо недоступен в стране
                    xpath = self.xpath("insta_not_available")
                    logger.debug2(f"{tr('check_if_channel_is_available')}")
                    element = S.wait_for_presence(xpath, **kwargs_s)
                    if element:
                        logger.warning("instagram channel is not available")
                        final_status = "ip_restriction"
                        self.random_sleep()
                        break

                    break

            if want_skarga:
                error = self.action(
                    xpath="insta_skarga1",
                    message=tr(f"click_report"),
                    warning_not_exists="no buttons with skarga",
                    error_not_exists="no_skarga_button",
                    # click_method="click",
                )

                if error:
                    break

            if want_select_on_account:
                _ = {
                    "cnt_elements": 2,
                    "xpath": self.xpath("insta_buttons"),
                    "timeout": self.kwargs_search_element["timeout"],
                }
                found = self.S.wait_for_presence_cnt_elements(**_)
                if not found:
                    error = "no_2_buttons_to_select_on_account"
                    logger.warning(error)
                    break

                error = self.action(
                    xpath="insta_skarga_on_account",
                    message=tr(f"report_account"),
                    warning_not_exists="no button with 'on account'",
                    error_not_exists="no_button_skargaOnAccount",
                )

                if error:
                    break

            if want_inform_bad_content:
                # ждем 5 секунд - должно быть 3 элемента в списке
                _ = {
                    "cnt_elements": 3,
                    "xpath": self.xpath("insta_buttons"),
                    "timeout": self.kwargs_search_element["timeout"],
                }
                found = self.S.wait_for_presence_cnt_elements(**_)
                if not found:
                    error = "no_3_buttons_to_select_bad_content"
                    logger.warning(error)
                    break

                error = self.action(
                    xpath="insta_inform_bad_content",
                    message=tr(f"report_bad_content"),
                    error_not_exists="no_button_bad_content",
                )

                if error:
                    break

            if want_inform_nasylstvo:
                # ждем 5 секунд - должно быть 3 элемента в списке
                cnt_elements = 11
                _ = {
                    "cnt_elements": cnt_elements,
                    "xpath": self.xpath("insta_buttons"),
                    "timeout": self.kwargs_search_element["timeout"],
                }
                found = self.S.wait_for_presence_cnt_elements(**_)
                if not found:
                    error = f"no_{cnt_elements}_buttons_to_select_nasylstvo"
                    logger.warning(error)
                    break

                error = self.action(
                    xpath="insta_inform_nasylstvo",
                    message=tr(f"report_violence"),
                    error_not_exists="no_button_nasylstvo",
                )

                if error:
                    break

            if want_inform_zagroza_or_osoba:
                error = self.action(
                    xpath="insta_zagroza_or_osoba",
                    message=tr(f"report_violent_or_dangerousOrganizations"),
                    warning_not_exists="no buttons with zagroza-osoba",
                    error_not_exists="no_button_skarga",
                    select_random=True,
                )

                if error:
                    break

                error = self.action(
                    xpath="insta_nadislaty",
                    message=tr(f"submit_report"),
                    warning_not_exists="no button nadislaty",
                    error_not_exists="no_button_nadislaty",
                )

                if error:
                    break

            # теперь клик кнопки пожаловаться
            if want_check_success:
                logger.debug2(f"{tr('checking_success')}")
                element = S.wait_for_presence(
                    self.xpath("insta_success"), timeout=20
                )
                if element:
                    final_status = "success"
                self.random_sleep()

            break

        return self.universal_answer(
            error=error,
            final_status=final_status,
            final_text=final_text,
            xpath=xpath,
        )


class YoutubeChanelDisliker:
    def send_dislike_to_youtube_chanel(
        self,
        url="",
        bad_videos=[],
        zhaloba: list = [],
        dislike: YoutubeChanelDislike = None,
        cnt_random_videos_to_check: str = "1-5",
        cnt_last_videos=10,
    ):
        fun = "send_dislike_to_youtube_chanel"
        S = self.S
        tr = self.translator.translate

        if not dislike:
            dislike = YoutubeChanelDislike(
                url=url, bad_videos=bad_videos, zhaloba=zhaloba
            )

        url = dislike.url
        bad_videos = dislike.bad_videos
        one_zhaloba = rewrite(choice(dislike.zhaloba))

        video_id = find_from_to_one("watch?v=", "nahposhuk", url)

        logger.debug(f"[{fun}: {one_zhaloba=} for {video_id} {dislike=}")

        want_zhaloba_on_chanel_vmesto_video = True

        want_start_info = True
        want_start_info = False

        want_ipify = True
        want_ipify = False

        want_open_url = True
        want_mouse_move = True
        want_mouse_move = False
        want_check_login = True
        want_flazhok = True
        want_pozhalovatjsa = True
        want_click_prichina = True
        want_click_button_1 = True
        want_check_videos = True
        want_send_bad_videos = True
        want_send_message = True
        want_check_success = True
        want_final_text = True

        t = 0
        if t:
            want_zhaloba_on_chanel_vmesto_video = False

            want_start_info = False
            want_ipify = False
            want_open_url = False
            want_mouse_move = False
            want_check_login = False
            want_flazhok = False
            want_pozhalovatjsa = False
            want_click_prichina = False
            want_click_button_1 = False

            # want_check_videos = False

            want_send_bad_videos = False

            want_send_message = False
            want_check_success = False
            want_final_text = False

        kwargs_s = {
            "timeout": 20,
            "timeout": 5,
            "checking": "presence",
            "checking": "clickable",
        }
        kwargs_s_clickable = deepcopy(kwargs_s)
        kwargs_s_clickable["checking"] = "clickable"

        want_spoof_hidden = True
        want_spoof_hidden = False

        # S.set_window_position(2000, 0)
        # S.set_window_position(0, 0)
        # nah

        is_hidden = False
        if want_spoof_hidden:
            # S.make_browser_visible_in_chrome()
            S.set_window_position(0, 0)
            is_hidden = S.check_is_hidden()
            logger.debug(f"start {is_hidden=} {type(is_hidden)}")

        error = ""
        xpath = ""
        final_status = None
        final_text = None
        while True:
            if want_start_info:
                S.set_html_body(f"<h1>Жалоба на youtube</h1><h2>на {url}</h2>")

            if want_ipify:
                url_ip = "https://api.ipify.org?format=json"
                logger.debug2(f"{tr('open_url')} {url_ip}")
                r = S.sgp(url_ip)
                logger.debug(f"{r=}")
                # wait_for_ok("setup browser")

            if want_open_url:
                logger.debug2(f"{tr('open_url')} {url}")
                # r_sgp_quick = S.sgp(url, seconds_sleep=0)
                r_sgp_quick = S.sgp(url)

                if not r_sgp_quick:
                    error = "url_not_loaded"
                    logger.warning(tr(error))
                    break

                self.random_sleep()

            if want_mouse_move:
                logger.debug2(tr("mouse_move"))

                old_position = S.driver.get_window_position()

                # r = S.emulate_mouse_move()
                old_size = S.get_window_size()
                logger.debug(f"{old_position=} {old_size=}")

                t = 1
                if t:
                    S.driver.maximize_window()
                    S.make_window_visible_in_chrome()
                    S.set_window_position(2001, 2001, windowHandle="current")

                t = 0
                if t:
                    width, height = 1, 1
                    S.set_window_size(width, height)
                    sleep_(2)
                    S.set_window_size(old_size["width"], old_size["height"])

                # driver = self.driver
                # elem = driver.find_element_by_tag_name("body")
                #
                # total_height = elem.size["height"] + 1000
                # driver.set_window_size(1920, total_height)
                # logger.debug(f"emulate_mouse_move {r=}")

            if want_check_login:
                if want_spoof_hidden:
                    is_hidden = S.check_is_hidden()
                    old_position = S.driver.get_window_position()
                    logger.debug(
                        f"{is_hidden=} {type(is_hidden)} {old_position=}"
                    )
                    if is_hidden:
                        logger.debug0(f"make_window_visible_in_chrome")
                        S.set_window_position(-1, -1)
                        # os._exit(0)
                        # S.make_browser_visible_in_chrome()
                        S.make_browser_visible_in_chrome()

                    is_hidden = S.check_is_hidden()
                    logger.debug(f"after move: {is_hidden=} {type(is_hidden)}")
                    # nah

                # from windows_functions.windows_funcs import (
                #     pwa_mySetFocus_by_pid,
                # )
                # pwa_mySetFocus_by_pid(S.driver.browser_pid)

                while True:
                    logger.debug2(tr("checking_login"))
                    # проверяю - возможно уже залогинен
                    logger.debug0(tr("checking_logined"))
                    xpath = self.xpath("logined")
                    element = S.wait_for_presence(xpath, **kwargs_s)
                    if element:
                        logger.debug0(tr("message_logined"))
                        break

                    else:
                        logger.debug0(tr("checking_not_logined"))
                        xpath = self.xpath("not_logined")
                        element = S.wait_for_presence(xpath, **kwargs_s)
                        if element:
                            sending = [
                                [xpath, "click_js"],
                            ]
                            r_clicked = S.ssend_values_quick(sending)
                            logger.debug(f"{r_clicked=}")

                            m = tr("message_please_login")
                            logger.critical(m)
                            inform_me_one()

                            m = tr("message_please_login_instructions")
                            wait_for_ok(m)

                            error = "not_logined"
                            break
                        else:
                            error = "not_logined__unknown_status"
                            saved = self.save_page_to_debug_situation(
                                name=error
                            )
                            logger.error(
                                tr("message_check_browser_is_not_hidden")
                            )

                            # возможно 404
                            xpath = self.xpath("yt_deleted")
                            element = S.wait_for_presence(xpath, **kwargs_s)
                            if element:
                                error = ""
                                final_status = "deleted"
                                logger.warning(f"{tr('message_deleted')}")
                                break

                    break

            if error or final_status:
                break

            if want_zhaloba_on_chanel_vmesto_video and video_id:
                logger.debug2(
                    f"{tr('searching_url_to_channel')} ({video_id=})"
                )
                # xpath = self.xpath("channel_id")
                xpath = self.xpath("block_with_channel_url")
                element = S.wait_for_presence(xpath, **kwargs_s)
                if not element:
                    logger.warning(
                        f"{tr('message_channel_block_not_found__solving')}"
                    )
                    xpath = self.xpath("video_not_available")
                    element = S.wait_for_presence(xpath, **kwargs_s)

                    if not element:
                        xpath = self.xpath("error_video_nedostupno")
                        element = S.wait_for_presence(xpath, **kwargs_s)

                    if element:
                        logger.warning(f"{tr('message_ip_restriction')}")
                        final_text = kl(
                            S.js_get_html_from_xpath(xpath, mode="outer")
                        )
                        final_status = "ip_restriction"
                        break

                    saved = self.save_page_to_debug_situation(
                        name="not found block_with_channel_url"
                    )

                    error = "channelBlock_not_found"
                    break

                final_text = S.js_get_html_from_xpath(xpath, mode="outer")

                channel_url = find_from_to_one('href="', '"', final_text)
                # channel_id = find_from_to_one(' content="', '"', final_text).strip()
                # logger.debug(f'{channel_id=} from {final_text=}')
                if not channel_url:
                    logger.warning(
                        f"channel not found in this page with {video_id=}"
                    )
                    error = "channel_not_found"
                    break

                channel_url = f"https://youtube.com{channel_url}/about"
                channel_dislike = YoutubeChanelDislike(
                    url=channel_url,
                    bad_videos=[video_id],
                    zhaloba=dislike.zhaloba,
                )
                logger.debug(f"will send new {channel_dislike=}")
                # logger.debug(f'{channel_dislike.details=}')
                # nah
                return self.send_dislike_to_youtube_chanel(
                    dislike=channel_dislike
                )

            if not video_id and want_flazhok:
                xpath = self.xpath("flazhok")
                logger.debug2(
                    f"{tr('check_flazhok')}"
                )  # почему флажок не открывается
                element = S.wait_for_presence(xpath, timeout=20)
                if not element:
                    logger.error(tr("message_no_flazhok"))

                    # проверяю - возможно канал недоступен или уже удален
                    xpath = self.xpath("yt_chanel_not_available")
                    element = S.wait_for_presence(xpath, **kwargs_s)
                    if element:
                        final_text = S.js_get_html_from_xpath(xpath)
                        final_text = kl(final_text)

                        if " block" in final_text or " заблок" in final_text:
                            final_status = "deleted"
                            logger.warning(f"{tr('message_deleted')}")
                        else:
                            final_status = "ip_restriction"
                            logger.warning(f"{tr('message_ip_restriction')}")
                        break

                    # проверяю - возможно канал недоступен или уже удален
                    xpath = self.xpath("yt_deleted")
                    element = S.wait_for_presence(xpath, **kwargs_s)
                    if element:
                        final_status = "deleted"
                        logger.warning(f"{tr('message_deleted')}")
                        break

                    else:
                        saved = self.save_page_to_debug_situation(
                            name="not found check_flazhok"
                        )
                        logger.error(
                            tr(f"message_check_browser_is_not_hidden")
                        )

                    error = "no_flazhok"
                    break

                sending = [
                    [xpath, "click_js"],
                ]
                r_clicked = S.ssend_values_quick(sending)
                logger.debug(f"{r_clicked=}")
                self.random_sleep()

            if want_pozhalovatjsa:
                logger.debug2(f"{tr('report_user')}")
                xpath = self.xpath("pozhalovatjsa")
                element = S.wait_for_presence(xpath, **kwargs_s)
                # element = S.wait_for_presence(xpath, checking="presence")
                if not element:
                    error = "no_button_after_flazhok"
                    logger.error(tr(error))
                    break

                # r_clicked = element.click()
                # r_clicked = S.click_xpath(xpath)
                sending = [
                    [element, "click_js"],
                ]
                r_clicked = S.ssend_values_quick(sending)
                logger.debug(f"{r_clicked=}")
                self.random_sleep()

            # теперь клик на погрозы
            if want_click_prichina:
                logger.debug2(f"{tr('select_reason')}")
                xpath = self.xpath("prichina_zhaloby")
                element = S.wait_for_presence(xpath, **kwargs_s)
                if not element:
                    logger.warning("причина жалобы не найдена")
                    error = "no_prichina"
                    break

                # берем рандомный элемент
                elements = S.search_elements_xpath(xpath, only_visible=0)
                if not elements:
                    if not element:
                        logger.warning("рандомная причина жалобы не найдена")
                        error = "no_prichina_random"
                        break
                element = choice(elements)
                sending = [
                    [element, "click_js"],
                ]
                r_clicked = S.ssend_values_quick(sending)
                # r_clicked = S.click_xpath(xpath)
                logger.debug(f"{r_clicked=}")
                self.random_sleep()

            # теперь клик кнопки пожаловаться
            if want_click_button_1:
                logger.debug2(f"{tr('send_reason')}")
                xpath = self.xpath("button_dislike_chanel_1")
                element = S.wait_for_presence(xpath, **kwargs_s)
                if not element:
                    logger.warning("кнопка1 не найдена")
                    error = "no_button1"
                    break

                sending = [
                    [element, "click_js"],
                ]
                r_clicked = S.ssend_values_quick(sending)
                # r_clicked = element.click()
                # r_clicked = S.click_xpath(xpath)
                logger.debug(f"{r_clicked=}")
                self.random_sleep()

            # теперь клик кнопки пожаловаться
            videos_must_exists = []
            if want_check_videos and (
                not bad_videos and cnt_random_videos_to_check not in ["0", 0]
            ):
                cnt_videos = get_random_value_in_range(
                    cnt_random_videos_to_check
                )
                logger.debug2(
                    f"{tr('searching_videos_to_check')}, {cnt_videos}/{cnt_random_videos_to_check}"
                )

                if cnt_videos:
                    xpath = self.xpath("block_with_videos_to_check")
                    html = S.js_get_html_from_xpath(xpath)

                    t = 0
                    if t:
                        f = self.get_f("block_with_videos")
                        logger.debug(f"saving html with videos to {f}")
                        text_to_file(html, f)

                    all_videos = self.parse_checkboxes_videos(html)
                    all_videos = all_videos[
                        :cnt_last_videos
                    ]  # выбираем из последних 15
                    shuffle(all_videos)
                    bad_videos = all_videos[:cnt_videos]
                    videos_must_exists = bad_videos[:]
                    logger.debug(
                        f"found {len(bad_videos)} {bad_videos=} from {len(all_videos)}"
                    )

            cnt_checked = ""
            if want_check_videos and bad_videos:
                logger.debug2(f"{tr('checking_videos')}, {bad_videos=}")

                # xpath = self.xpath('button_dislike_chanel_final')
                # два элемента:
                # $x('//a[@id="thumbnail"][contains(@href, "s8Busn4ifYk") or contains(@href, "fSvMWlZJMOw") ]/../../../../../../div[@id="checkboxContainer"]')
                xpath_with_hrefs = " or ".join(
                    [f'contains(@href, "{_}")' for _ in bad_videos]
                )
                xpath_bad_videos = f'//a[@id="thumbnail"][{xpath_with_hrefs}]/../../../../../../div[@id="checkboxContainer"]'

                t_start_check_videos = time.time()
                step_check = 0
                while True:
                    step_check += 1
                    duration_check_videos = time.time() - t_start_check_videos
                    logger.debug(f"xpath with bad_videos={xpath_bad_videos}")
                    elements = S.search_elements_xpath(xpath_bad_videos)
                    logger.debug(
                        f"{step_check=} found {len(elements)} videos, duration checking videos {get_human_duration(duration_check_videos)}"
                    )
                    if duration_check_videos > 10 or step_check > 1:
                        error = "videos_not_checked"
                        logger.error(tr(error))
                        logger.warning(
                            tr("message_check_browser_is_not_hidden")
                        )
                        break

                    if not elements:
                        logger.debug(f"no elements, so break")
                        break

                    r_clicked = S.click_elements(elements)
                    logger.debug(
                        f"{r_clicked=}"
                    )  # r_clicked=(True, 'clicked')
                    self.random_sleep()

                    want_count_checked = True
                    if want_count_checked and videos_must_exists:
                        logger.debug0("count checked videos")
                        sleep_(3, 0)
                        xpath = self.xpath("cnt_checked_videos")
                        elements = S.search_elements_xpath(xpath)
                        cnt_checked = len(elements)
                        logger.debug0(f"found {cnt_checked} checked videos")
                        # os._exit(0)

                        if cnt_checked == 0:
                            error = "videos_not_checked"
                            logger.error(tr(error))
                            logger.warning(
                                tr("message_check_browser_is_not_hidden")
                            )
                            sleep_(1)
                            continue
                        else:
                            error = ""
                            break

                    break
            if error:
                break

            if want_send_bad_videos:
                logger.debug2(f"{tr('send_checked_videos')} / {cnt_checked}")
                # проверяем - есть вообще окно с чекбоксами?
                t = 1
                if t:
                    xpath = self.xpath("block_with_videos_to_check")
                    element = S.wait_for_presence(xpath, **kwargs_s)
                    if not element:
                        logger.warning("окна с чекбоксами нет")
                        error = "no_videos_with_checkboxes"
                        break

                xpath = self.xpath("button_send_bad_videos")

                element = S.wait_for_presence(xpath, **kwargs_s)
                if not element:
                    logger.warning("финальная кнопка не найдена")
                    error = "no_final_button"
                    break

                sending = [
                    [element, "click_js"],
                ]
                r_clicked = S.ssend_values_quick(sending)
                # r_clicked = element.click()
                # r_clicked = S.click_xpath(xpath)
                logger.debug(f"{r_clicked=}")
                self.random_sleep()

            # наконец пишем жалобу и отправляем
            if want_send_message:
                logger.debug2(f"{tr('input_message')}")

                is_hidden = S.check_is_hidden()
                logger.debug(f"{is_hidden=} {type(is_hidden)}")
                if is_hidden:
                    logger.debug0(f"make_window_visible_in_chrome")
                    S.make_browser_visible_in_chrome()

                xpath = self.xpath("dislike_message")

                t = 0
                if t:
                    # sending = [
                    #     [xpath, "click"],
                    # ]
                    # r = S.ssend_values_quick(sending)
                    # logger.debug(f"{r=}")

                    r_clicked = S.click_xpath_with_js(xpath)
                    logger.debug(f"{r_clicked=}")

                element = S.wait_for_presence(xpath, **kwargs_s_clickable)
                # element = S.find_element_by_xpath(xpath)
                if not element:
                    error = "no_window_for_zhaloba"
                    logger.error(tr(error))
                    logger.error(tr("message_check_browser_is_not_hidden"))
                    break

                mode_send_message = "js"
                mode_send_message = "send_keys"
                mode_send_message = "like_human"

                S.clear_like_human(element)
                # os._exit(0)

                if mode_send_message == "send_keys":
                    r_clicked = element.send_keys(one_zhaloba)

                elif mode_send_message == "js":
                    js = f"document.getElementById('textarea').value = '{one_zhaloba}';"
                    r_clicked = S.execute_script(js)

                elif mode_send_message == "like_human":
                    r_clicked = S.sel_send_keys_like_human(
                        element, one_zhaloba, sleep=0.05
                    )

                logger.debug(f"{mode_send_message=} {r_clicked=}")

                xpath = self.xpath("count_symbols_in_message")
                final_text = S.js_get_html_from_xpath(xpath)
                count_symbols_in_message = kl(final_text)
                logger.debug0(f"{count_symbols_in_message=}")

                if count_symbols_in_message == "0/300":
                    error = "message_not_entered"
                    logger.error(tr(error))
                    logger.warning(tr("message_check_browser_is_not_hidden"))
                    break

                # os._exit(0)

                self.random_sleep()

                # кликаем на кнопку
                logger.debug2(f"{tr('send_message')}")
                xpath = self.xpath("button_send_more_info")
                element = S.wait_for_presence(xpath, **kwargs_s)
                if not element:
                    logger.warning("нет кнопки для отправки жалобы жалобы")
                    error = "no_button_send_more_info"
                    break
                sending = [
                    [element, "click_js"],
                ]
                r_clicked = S.ssend_values_quick(sending)
                logger.debug(f"{r_clicked=}")
                self.random_sleep()

            # теперь клик кнопки пожаловаться
            if want_check_success:
                logger.debug2(f"{tr('checking_success')}")
                xpath = self.xpath("dislike_check_success")
                element = S.wait_for_presence(xpath, timeout=20)
                if element:
                    final_status = "success"

            if want_final_text:
                logger.debug2(f"{tr('message_search_final_text')}")
                xpath = self.xpath("dislike_final_text")
                final_text = S.js_get_html_from_xpath(xpath)
                final_text = kl(final_text)

                if (
                    "Ми отримали вашу скаргу" in final_text
                    or "жалоба принята" in final_text
                ):
                    final_status = "success"

            if final_status is None:
                logger.warning("финальный статус неизвестный")

            break

        # возвращаем браузер в точно видимое положение
        if is_hidden:
            logger.debug0("was hidden, so move browser to 0x0")
            S.set_window_position(0, 0)

        return self.universal_answer(
            error=error,
            final_status=final_status,
            final_text=final_text,
            xpath=xpath,
        )

    def parse_checkboxes_videos(self, html=""):
        """
          <ytd-thumbnail use-hovered-property="" class="style-scope ytd-video-renderer"><!--css-build:shady--><a id="thumbnail" class="yt-simple-endpoint inline-block style-scope ytd-thumbnail" aria-hidden="true" tabindex="-1" rel="null" href="http://youtu.be/pC-4nIl0Gws">
  <yt-image alt="" ftl-eligible="" class="style-scope ytd-thumbnail" disable-upgrade="" hidden="">
        """
        videos = []
        items = html.split("youtu.be/")

        for item in items:
            video = find_from_to_one("nahposhuk", '"', item)
            if "--" in video:
                continue
            videos.append(video)
        videos = unique_with_order(videos)
        return videos


class TaskManager(YoutubeChanelDisliker, InstagramDisliker, TelegramDisliker):
    def __init__(
        self, d=None, pwd=None, work_with=None, delays_between_reports={}
    ):
        if d is None:
            d = get_f_here()
        if not work_with:
            work_with = ["instagram", "youtube"]
        self.work_with = work_with
        tasks_reader = AllTasksReader(
            d=f"{d}",
            pwd=pwd,
            work_with=work_with,
            delays_between_reports=delays_between_reports,
        )
        self.tasks_reader = tasks_reader

    def no_war_mozg(
        self,
        tasks_za_raz=1,
        seconds_sleep_after_step: int = 5,
        seconds_sleep_after_task: int = 0,
        seconds_sleep_if_no_tasks: int = 60,
        max_step=0,
        max_duration=0,
        max_searching_duration=60,
        f_log=None,
    ):
        if not f_log:
            f_log = get_f_here("temp/!log.txt")

        t_start = time.time()
        stats = {
            "success": 0,
            "error": 0,
            "reported": 0,
        }
        step = 0
        S = self.S
        while True:
            duration = time.time() - t_start
            step += 1
            logger.info(
                f"\n\nStep {step}, duration from start {get_human_duration(duration)}"
            )

            if S:
                browser_is_controlled = S.check_browser_is_controlled()
                logger.debug(f"{browser_is_controlled=}")
                if not browser_is_controlled:
                    m = "browser not controlled - RESTART BROWSER AND PROGRAM\nОШИБКА - ПЕРЕЗАПУСТИТЕ БРАУЗЕР И ПРОГРАММУ"
                    logger.critical(m)
                    inform_critical(m)

            reason_to_stop = ""
            if max_step and step > max_step:
                reason_to_stop = f"{step=} reached {max_step=}, so exit"
            elif max_duration and duration > max_duration:
                reason_to_stop = (
                    f"{duration=} reached {max_duration=}, so exit"
                )
            if reason_to_stop:
                logger.warning(f"STOP EXECUTION, {reason_to_stop=}")
                break

            # tasks = self.tasks_reader.get_tasks(seconds_sleep_if_no_tasks=seconds_sleep_if_no_tasks, max_searching_duration=max_searching_duration)
            logger.debug0(f"reading tasks")
            tasks = self.tasks_reader.get_tasks_one()

            if not tasks:
                logger.debug2(
                    f"no tasks, will recheck in {seconds_sleep_if_no_tasks} seconds"
                )
                sleep_(seconds_sleep_if_no_tasks, 0)
                continue

            message_selected = ""
            if tasks_za_raz and len(tasks) > tasks_za_raz:
                # сортировка по приоритетам!
                # shuffle(tasks)
                tasks = shuffle_and_sort_list_by_priority(
                    tasks, columns=["-priority"]
                )
                message_selected = (
                    f"(SELECTED {tasks_za_raz}/{len(tasks)} tasks)"
                )
                tasks = tasks[:tasks_za_raz]
                # logger.debug(f"selected {tasks=}")
                # os._exit(0)

            for num_task, task in enumerate(tasks, 1):
                logger.debug3(
                    f"\n\n{step=}, execute {num_task}/{len(tasks)} task {message_selected }"
                )
                func = None
                func_kwargs = {}
                if task.tip == "YoutubeChanelDislike":
                    func = self.send_dislike_to_youtube_chanel
                    func_kwargs = {
                        "dislike": task,
                    }
                elif task.tip == "InstagramDislike":
                    func = self.send_dislike_to_instagram
                    func_kwargs = {
                        "dislike": task,
                    }
                elif task.tip == "TelegramDislike":
                    func = self.send_dislike_to_telegram
                    func_kwargs = {
                        "dislike": task,
                    }

                if func is None:
                    logger.error(f"unknown {task=}")
                    continue

                want_try = False
                want_try = True
                if want_try:
                    try:
                        res = func(**func_kwargs)
                    except Exception as er:
                        logger.error(f"ERROR {er=}")
                        res = api_error("GLOBAL_ERROR")
                else:
                    res = func(**func_kwargs)

                error = get_api_error(res)
                log_info = []

                if error:
                    log_info.append(f"ERROR: {error}")
                    stats["error"] += 1
                else:
                    log_info.append(f"SUCCESS")
                    res["task"] = task
                    task.mark_done(res)
                    stats["success"] += 1

                    # сколько реально удалили?
                    if res["final_status"] == "success":
                        stats["reported"] += 1
                        task.mark_reported()

                log_info += [res, task]
                add_to_full_log(log_info, f_log)

                logger.debug1(
                    f"real reported {stats['reported']}, success {stats['success']}, errors {stats['error']}"
                )

                sleep_(seconds_sleep_after_task)

            logger.debug1(
                f"{step} done, real reported {stats['reported']}, success {stats['success']}, errors {stats['error']}"
            )

            if step != max_step:
                sleep_(seconds_sleep_after_step)


class NoWarBrowser(LightBrowser, TaskManager):
    def __init__(self, *args, **kwargs):
        kwargs_search_element = {
            "timeout": 20,
            "timeout": 5,
            "checking": "clickable",
        }
        sett = {
            "seconds_random_sleep": "1-1",
            "kwargs_search_element": kwargs_search_element,
            "lang": "ru",
            "work_with": "instagram\nyoutube",
        }
        # kwargs.update(sett)
        kwargs = add_defaults(kwargs, sett)

        LightBrowser.__init__(self, *args, **kwargs)

        # wait_for_ok(self.xpath_dict)

        work_with = clear_list(kwargs.get("work_with"))
        self.work_with = work_with

        self.telegram_reporter = None
        # инициирую телеграм
        logger.debug(f"{work_with=}")
        if "telegram" in work_with:
            _ = {
                "d": f"{self.d}/data",
                "d_sent": f"{self.d}/temp/!sent_telegram_reports",
            }
            self.telegram_reporter = TelegramReporter(**_)
            logger.debug(f"telegram_reporter={self.telegram_reporter}")
        # os._exit(0)

        pwd = kwargs.get("pwd", None)
        delays_between_reports = kwargs.get("delays_between_reports", {})
        logger.debug(f"{pwd=} {delays_between_reports=} from {kwargs=}")
        TaskManager.__init__(
            self,
            d=self.d,
            pwd=pwd,
            delays_between_reports=delays_between_reports,
            work_with=self.work_with,
        )

    def start_browser_if_need(self):
        """если надо - браузер стартону"""
        work_with = clear_list(self.work_with)
        if "youtube" in work_with or "instagram" in work_with:
            want_start_browser = True
        else:
            want_start_browser = False
        if want_start_browser:
            logger.debug(f"{want_start_browser=} for {self.work_with}")
            more_extensions = [
                f"{self.d_dev}/chrome_extensions/ban_war_theme",
                f"{self.d_dev}/chrome_extensions/blank_tab",
            ]
            r = self.browser_start_or_reconnect(
                more_extensions=more_extensions
            )
            logger.debug0(f"+browser_start_or_reconnect {r=}")

            self.prepare_browser()
        else:
            logger.debug(f"do not need browser for {self.work_with}")

    def prepare_browser(self):
        """подготовить браузер - расширения поставить"""
        S = self.S
        tr = self.translator.translate
        extensions = [
            "https://chrome.google.com/webstore/detail/urban-free-vpn-proxy-unbl/eppiocemhmnlbhjplcgkofciiegomcon"
        ]
        for extension in extensions:
            name = find_from_to_one("detail/", "/", extension)
            f_done = self.get_f(f"setup_extension/{name}")
            if file_exists(f_done):
                logger.debug(f"extension {extension} already setuped")
                continue

            logger.debug(f"check extension at {f_done}, {extension=}")
            S.sgp(extension)
            m = f"{tr('install_extension')} {name} {tr('and_press_any_key')}"
            logger.info(m)
            inform_me_one()
            x = input()
            text_to_file("", f_done)

    def explore_function(self):
        special = "check_browser_is_controlled"
        special = "save_page_to_debug_situation"
        special = "send_dislike_to_instagram"
        special = "send_dislike_to_youtube_chanel"
        special = "no_war_mozg"

        if special == "":
            pass

        elif special == "check_browser_is_controlled":
            r = self.S.check_browser_is_controlled()
            logger.info(f"check_browser_is_controlled {r=}")

        elif special == "save_page_to_debug_situation":
            saved = self.save_page_to_debug_situation(name="insta_not_logined")
            logger.info(f"{saved=}")

        elif special == "no_war_mozg":
            kwargs = {
                # "max_step": 1,
                # "tasks_za_raz": 1,
                # 'max_duration': 60,
            }
            result = self.no_war_mozg(**kwargs)
            logger.info(f"no_war_mozg {result=}")

        elif special == "send_dislike_to_youtube_chanel":

            url = "https://www.youtube.com/watch?v=x0mEXifo8gU"

            url = "https://www.youtube.com/watch?v=I_39iooKCtQ"  # видео недоступно
            url = "https://www.youtube.com/user/rianovosti/about"  # Недоступное в стране
            url = "https://www.youtube.com/user/mikhailovetv/about"

            url = "https://www.youtube.com/c/Montyan2/channels"  # недоступно в стране
            url = "https://www.youtube.com/watch?v=x0mEXifo8gU"  # видео в стране заблокировано

            url = "https://www.youtube.com/c/PoedinokTV/about"  # реально удален канал
            url = "https://www.youtube.com/channel/UCQ4YOFsXjG9eXWZ6uLj2t2A/about"  # уже удален-заблокирован

            url = "https://www.youtube.com/channel/UC6qbvhfHYj2KK3NaIY7W_Ag/about"  # гавноканал живойоо

            url = "https://www.youtube.com/c/poedinoktv/about"  # 404

            zhaloba = "War propaganda in Ukraine | war proganda | пропаганда войны в Украине |"
            bad_videos = None

            task = {
                "url": url,
                "zhaloba": zhaloba,
                "bad_videos": bad_videos,
            }
            dislike = YoutubeChanelDislike(**task)

            max_steps = 10000
            max_steps = 1
            step = 0
            stats = {}
            while True:
                step += 1
                if step > max_steps:
                    break

                Show_step(f"send_dislike_to_youtube_chanel {step=}")
                r = self.send_dislike_to_youtube_chanel(dislike=dislike)
                final_status = r["final_status"]
                logger.info(f"{step=} send_dislike_to_youtube_chanel {r=}")
                stats[final_status] = stats.get(final_status, 0) + 1
                logger.info(f"{stats=}")
                sleep_(5)

        elif special == "send_dislike_to_instagram":
            url = "https://www.instagram.com/hardrock.reading/"
            url = "https://www.instagram.com/semchenko7378/"

            task = {
                "url": url,
            }
            dislike = InstagramDislike(**task)
            r = self.send_dislike_to_instagram(dislike=dislike)
            logger.info(f"send_dislike_to_instagram {r=}")

        else:
            logger.critical(f"unknown {special=}")

    def get_translator(self):
        translations = {
            "install_extension": {
                "ru": "Установите расширение",
                "en": "Setup extension",
            },
            "and_press_any_key": {
                "ru": "и нажмите любую клавишу",
                "en": "and press any key",
            },
            "send_dislike": {"ru": "Отправляю жалобу", "en": "Opening url"},
            "open_url": {"ru": "Открываю ссылку", "en": "Opening url"},
            "url_not_loaded": {
                "ru": "Ссылка не открылась",
                "en": "Url not opened",
            },
            "checking_login": {
                "ru": "Проверяю залогинен или нет",
                "en": "Checking LogIn",
            },
            "checking_logined": {
                "ru": "Проверяю что уже залогинился",
                "en": "Checking is already LogIned",
            },
            "checking_not_logined": {
                "ru": "Проверяю что Не залогинен",
                "en": "Checking is NOT already LogIned",
            },
            "check_if_channel_is_available": {
                "ru": "Проверяю доступность канала",
                "en": "Checking if channel is available",
            },
            "checking_success": {
                "ru": "Проверяю успешность исполнения задания",
                "en": "Checking if task is success finished",
            },
            "click_3_dots": {
                "ru": "Клик на 3 точки",
                "en": "Clicking on 3 dots",
            },
            "click_report": {"ru": "Пожаловаться", "en": "Report"},
            "report_account": {
                "ru": "Пожаловаться на аккаунт",
                "en": "Report account",
            },
            "report_bad_content": {
                "ru": "Публикация контента, которому не место в Instagram",
                "en": "It's posting content that shouldn't be on Instagram",
            },
            "report_violence": {
                "ru": "Насилие или опасные организации",
                "en": "Violence or dangerous organisations",
            },
            "report_violent_or_dangerousOrganizations": {
                "ru": "Угроза насилия ИЛИ Опасные организации или люди",
                "en": "Violent threat OR Dangerous organisations or individuals",
            },
            "submit_report": {"ru": "Отправить жалобу", "en": "Submit Report"},
            ### youtube
            "searching_url_to_channel": {
                "ru": "Это видео, ищу ссылку на канал",
                "en": "Searching url to chanel",
            },
            "message_logined": {
                "ru": "Вы успешно залогинены",
                "en": "Your are logined",
            },
            "message_please_login": {
                "ru": "Залогиньтесь пожалуйста",
                "en": "Please login",
            },
            "message_please_login_instructions": {
                "ru": "Залогиньтесь пожалуйста. Потом в программе нажмите 1 и Enter (Или просто перезапустите программу)",
                "en": "Please LogIn in the browser and restart the program.",
            },
            "message_not_entered": {
                "ru": "Сообщение пустое - ошибка",
                "en": "Message is empty - erro",
            },
            "videos_not_checked": {
                "ru": "Не смогли отметить видео",
                "en": "Could not check videos",
            },
            "": {"ru": "", "en": ""},
            "": {"ru": "", "en": ""},
            "check_flazhok": {"ru": "Ищу флажок", "en": "Searching Flag"},
            "report_user": {
                "ru": "Пожаловаться на пользователя",
                "en": "Click Report user",
            },
            "select_reason": {"ru": "Выбираю причину", "en": "Select reason"},
            "send_reason": {"ru": "Отправляю причину (Далее)", "en": "Next"},
            "searching_videos_to_check": {
                "ru": "Ищу видео, чтобы отметить",
                "en": "Searching videos to check",
            },
            "checking_videos": {
                "ru": "Отмечаю видео",
                "en": "Checking videos",
            },
            "send_checked_videos": {
                "ru": "Отправляю отмеченные видео (Далее)",
                "en": "Sending checked videos",
            },
            "input_message": {
                "ru": "Ввожу сообщение",
                "en": "Writing message",
            },
            "send_message": {
                "ru": "Отправляю сообщение",
                "en": "Sending message",
            },
            "no_button_after_flazhok": {
                "ru": "Кнопка 'Пожаловаться' после клика на флажок не появилась",
                "en": "No button after clicking on Report",
            },
            "": {"ru": "", "en": ""},
            "": {"ru": "", "en": ""},
            "": {"ru": "", "en": ""},
            "": {"ru": "", "en": ""},
            "": {"ru": "", "en": ""},
            "message_channel_block_not_found__solving": {
                "ru": "Не найден блок с информацией о канале, разбираюсь",
                "en": "Block with channel info not found, solving",
            },
            "message_ip_restriction": {
                "ru": "Канал недоступен с вашего айпи (но с руccкого айпи откроется), используйте VPN",
                "en": "Channel not available from your IP (use Russian IP and try again)",
            },
            "message_deleted": {"ru": "Удалено", "en": "Deleted"},
            "message_check_browser_is_not_hidden": {
                "ru": "Проверьте - возможно у вас браузер полностью свернут. Он должен как минимум выглядывать, нельзя сворачивать.",
                "en": "Сheck your browser - probably it is hidden by other apps. Maximize it.",
            },
            "message_no_flazhok": {
                "ru": "Флажок 'Пожаловаться' не найден",
                "en": "Flag not found",
            },
            "message_search_final_text": {
                "ru": "Беру ответ на жалобу",
                "en": "Get report answer",
            },
            "no_window_for_zhaloba": {
                "ru": "Окно для ввода жалобы не найдено",
                "en": "No window to enter report",
            },
            "": {"ru": "", "en": ""},
            "task_success_finished": {
                "ru": f"Успешно решили задачу. НЕТ ВОЙНЕ в Украине!",
                "en": "Task done. NO WAR IN UCRAINE!",
            },
        }
        kwargs = {
            "lang": self.lang,
            "translations": translations,
        }
        return Translator(**kwargs)

    def get_important_xpaths(self):
        last_button = '(//tp-yt-paper-button[@id="button"])[last()]'
        xpaths = {
            ######################## messages
            ######################## for YoutubeChanelDisliker
            # "not_logined": r'(//tp-yt-paper-button[@id="button"]/yt-formatted-string[@id="text"][text()="Увійти"])[1] | //a[@aria-label="Вхід"]', # ua
            "not_logined": r'(//div[@id="buttons"])[1]//yt-formatted-string',
            "logined": r'//button[@id="avatar-btn"][@aria-haspopup="true"]',
            "flazhok": r'(//div[@id="action-buttons"]//button) | (//c3-icon[@class="button-renderer-icon"])[1]',
            "pozhalovatjsa": r'(//tp-yt-paper-listbox[@id="items"]/*[@role="menuitem"])[last()]',
            "prichina_zhaloby": '//tp-yt-paper-radio-button[@name="0" or @name="3" or @name="5"]',
            "button_dislike_chanel_1": last_button,
            "block_with_videos_to_check": "//ytd-selectable-video-list-renderer",
            "cnt_checked_videos": '//div[@id="checkbox"][contains(@class, "checked ")]',
            # "select_bad_videos": '//div[@id="checkboxContainer"]',
            "button_send_bad_videos": last_button,
            "dislike_message": '//textarea[@id="textarea"]',
            "count_symbols_in_message": "//tp-yt-paper-input-char-counter",
            # "button_send_more_info": '//ytd-button-renderer[@id="next-button"]//yt-formatted-string[contains(text(), "Надіслати")]', #ua
            "button_send_more_info": '//ytd-button-renderer[@id="next-button"]//yt-formatted-string[text()]',
            "dislike_check_success": '//yt-button-renderer[@id="confirm-button"]',
            "dislike_final_text": '//tp-yt-paper-dialog-scrollable[@id="scroller"]',
            "yt_chanel_not_available": '(//div[@id="container"][contains(@class, "ERROR ")]/yt-formatted-string)',
            "yt_deleted": '(//iframe[contains(@src, "/error?src=404")])',
            # одиничное видео
            # "video_button_dislike": r'//yt-formatted-string[@id="text"][text()="Не подобається"]', # ua_todo
            # "video_other_options": r'(//button[@id="button"][contains(@aria-label, "Інші дії")])[1]', # ua_todo
            # "video_flazhok": r'//yt-formatted-string[text()="Поскаржитись"]', # ua_todo
            "channel_id": r'//meta[@itemprop="channelId"]',
            "block_with_channel_url": r'//yt-formatted-string[@id="text"]/a[@dir="auto"]',
            # "video_not_available": r'//div[contains(@class, "promo-title ")]',
            "video_not_available": '//img[@id="img"][contains(@src, "/unavailable/unavailable_video.png")]',  # r'<img id="img" class="style-scope yt-img-shadow" alt="" src="https://www.youtube.com/img/desktop/unavailable/unavailable_video.png'
            "error_video_nedostupno": '//div[@id="player-error-message-container"]//div[@id="reason"]',  # по странам закрывают
            ######################## for instagram
            "insta_not_logined": r'//span[contains(@class, "Dy2XU")]/a[@href="/accounts/emailsignup/"]',  # <a class="ENC4C" href="/accounts/emailsignup/" tabindex="0">Зареєструватися</a>,
            "insta_not_available": r'//*[@id="react-root"]/section/main/div[1]/div[1]/h2',  # канал недоступен
            "insta_3_dots": r'//section//button//*[local-name()="svg"][@role="img"][@color="#262626"][@width="32"]/..',
            "insta_skarga1": r'(//div[@class="mt3GC"]//button)[3]',
            "insta_skarga_on_account": r'(//div[@role="list"]/button)[2]',
            "insta_buttons": r'//div[@role="list"]/button',
            "insta_inform_bad_content": r'(//div[@role="list"]/button)[1]',
            "insta_inform_nasylstvo": r'(//div[@role="list"]/button)[7]',
            "insta_zagroza_or_osoba": r"(//fieldset//label)[position()=1 or position()=4]",
            "insta_nadislaty": r'(//div[@role="dialog"]//button)[last()]',
            "insta_success": r'//*[local-name()="svg"][@role="img"][@color="#58c322"]',
        }
        return xpaths

    def universal_answer(
        self, error="", final_status=None, final_text="", xpath="", answer={}
    ):
        """answer = {} - детали ответа"""
        res = {
            "final_status": final_status,
            "final_text": final_text,
        }
        if answer:
            res["answer"] = answer

        if error:
            res["error"] = error
            res["xpath"] = xpath

            status = False
        else:
            status = True
        res["status"] = status
        final_message = "Some error"
        if final_status in [
            "success",
            # "sent",
            "already_sent",
            "video_not_available",
            "ip_restriction",
            "deleted",
            # Ошибки телеграма
            "user_not_exists",
            "entity_not_exists",
            "chat_not_exists",
            "join_group_and_retry",
        ]:
            final_message = self.translator.translate("task_success_finished")
            logger.info(f"{final_message}")
            logger.debug0(f"{final_status} {res=}]")
        else:
            logger.info(f"{final_message}. {final_status} {res=}]")
        return res


def rewrite(tpl: str) -> str:
    rewriter = get_text_rewriter()
    one_zhaloba = rewriter.get_random_text_variation(tpl)
    logger.debug(f"rewriter created {one_zhaloba=} from {tpl=}")
    return one_zhaloba


if __name__ == "__main__":
    special = "open_browser"
    if special == "open_browser":
        d = r"s:\!kyxa\!code\no_war"
        d_dev = r"s:\!data\!no_war\installs\development"
        d_profile = r"s:\!chaos\!no_war\dist\data\development\GoogleChromePortable64\Data\profile"
        d_profile = r"s:\!data\!no_war\profiles\profile"

        f_settings = r"s:\!kyxa\!code\no_war\налаштування.txt"

        settings = get_default_settings(f=f_settings)

        kwargs = {
            "d": d,
            "d_profile": d_profile,
            "d_dev": d_dev,
            "want_start_browser": False,
            "pwd": "{eq  dfv f yt Erhf]ye",
            "lang": settings["lang"],
            "delays_between_reports": settings["delays_between_reports"],
            "work_with": settings["work_with"],
        }
        # klas = LightBrowser
        klas = NoWarBrowser

        browser = klas(**kwargs)
        logger.debug(f"{browser=}")
        # os._exit(0)

        browser.start_browser_if_need()

        logger.info("start debug")
        browser.explore_function()

        # sleep_(100000)
