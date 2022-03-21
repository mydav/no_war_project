#!/usr/bin/python
# -*- coding: utf-8 -*-

from modules import *
from modules_mega_23.xpath_functions import Xpather

t = 0  # для py2exe это жопа - нафик
if t:
    try:
        from windows_functions.search_processes import get_pid_by_port
        from windows_functions.windows_funcs_min import (
            find_handle_for_pid,
            pwa_handle_to_window,
            pwa_mySetFocus,
        )
    except Exception as er:
        pass

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import tempfile

import selenium.webdriver.support.ui as ui
from selenium.webdriver.support.ui import Select

# import Image
# from PIL import Image

from selenium.webdriver.common.action_chains import ActionChains

from modules_mega_23.project_funcs import class_info_saved

logger = get_logger(__name__)

# from selenium_recaptcha import *


class SessionRemote(webdriver.Remote):
    def start_session(self, desired_capabilities, browser_profile=None):
        # Skip the NEW_SESSION command issued by the original driver
        # and set only some required attributes
        self.w3c = True


def del_recaptcha(S):
    fun = "del_recaptcha"
    logger.debug("[%s" % fun)

    S.driver.switch_to_default_content()

    # удаляем то что висело
    xpath = "//iframe"
    xpath = "//div[contains(@style, 'z-index: 2000000000')]"
    elements = S.driver.find_elements_by_xpath(xpath)
    logger.debug("found %s recaptcha elements" % len(elements))
    if len(elements) > 0:
        k = 0
        for element in elements:
            logger.debug("	%s deleting %s" % (k, element)),
            r = S.delete_element(element)
            logger.debug("deleted=%s" % r)

    logger.debug("+%s]" % fun)
    return 1


def recaptcha_tupo_hack(task={}):
    fun = "recaptcha_tupo_hack"
    # тупо хакаем рекапчу
    # use:
    # user['p'] = p
    # user['driver'] = S.driver
    # user['rucaptcha_key'] = sett['rucaptcha_key']
    # captcha_clicked = recaptcha_tupo_hack(user)
    # if captcha_clicked in [0]:
    # 	mess = 'recaptcha_bad_guessed'
    # 	add_to_full_log(mess)
    # 	return False, mess
    # add_to_full_log('captcha guessed')
    task = hitro_dict(task, "p")
    d = {
        "p": "",  # страница с рекапчей
        "rucaptcha_key": "",
        "driver": "",
    }
    task = add_defaults(task, d)
    T = Bunch(task)

    driver = T.driver
    p = T.p

    googlekey = find_from_to_one('''sitekey' : "''', '"', p)
    if googlekey == "":
        googlekey = find_from_to_one('data-sitekey="', '"', p)
    logger.debug("googlekey: %s" % googlekey)
    if googlekey == "":
        return 0, "no googlekey"

    t = 1
    if t:
        post = {
            "googlekey": googlekey,
            "recaptcha": 1,
        }

        cap_id = rucaptcha_send_cap(T.rucaptcha_key, post)
        logger.debug("cap_id:" % cap_id)

        r = rucaptcha_get_cap_text(T.rucaptcha_key, cap_id)
        logger.debug("r: %s" % r)

        try:
            status, mess = r
        except Exception as er:
            mes = "ERROR AUTOCAPTCHA (%s)" % str(er)
            logger.error(mes)
            return 0, mes

        if status == "OK":
            add_to_full_log([googlekey, mess], "data/recaptcha_hack.txt")
            # return 'good', rez
            count_recaptcha_send("recaptcha_answered")

        else:
            mess = "no_guessed"
            logger.error(mess)
            return 0, mess

        logger.debug("hack guessed, inserting %s" % mess)
        driver.switch_to_default_content()

        id = "g-recaptcha-response"
        elem = driver.find_element_by_id(id)
        if not elem:
            return False, "hask - no id %s" % id

        js = "document.getElementById('%s').style.display = 'visible';" % id

        logger.debug("js=%s" % js)
        driver.execute_script(js)
        # js.executeScript("",element);

        js = "arguments[0].setAttribute('style', 'border:5px solid red;')"
        driver.execute_script(js, elem)

        elem.clear()
        # elem.send_keys(T.url)
        elem.send_keys(mess)

        # wait_for_ok('guessed main sposob')

        return 1


def get_rand(v="before_mail_click"):
    if v == "before_mail_click":
        # t = randint(10, 15)
        t = randint(5, 10)
    elif v == "rand_sleep":
        t = randint(0, 1)
        t = randint(1, 5)
    else:
        logger.error(v)
        wait_for_ok("unknown get_rand")
    return t


def rand_sleep(sleep=None):
    fun = "rand_sleep"
    # return
    sleep = get_rand("rand_sleep")
    logger.debug("sleep %d seconds" % sleep)
    time.sleep(sleep)


def proxy_propuskaem(proxy, task={}):
    """фильтр проксей - возможно их уже мы использовали"""
    d = {
        "popular_ports": [],
    }
    task = add_defaults(task, d)
    T = Bunch(task)

    f_log_proxy = get_f_ip(proxy)

    x, port = proxy.split(":")
    if port in T.popular_ports:
        logger.debug("%s - popular port, propusk" % proxy)
        return 1

    # logger.debug('f_log_proxy=%s' % f_log_proxy)
    # wait_for_ok()
    if os.path.isfile(f_log_proxy):
        t = text_from_file(f_log_proxy)
        propuski = [
            #'registered',
            '"ban"',
            '"ban_ip"',
        ]
        bad = 0
        for propusk in propuski:
            if t.find(propusk) != -1:
                logger.debug(
                    'we have already used proxy %s (found "%s" in log)'
                    % (proxy, propusk)
                )
                # wait_for_ok()
                return 1

    logger.debug("proxy selected: %s" % proxy)
    return 0


def change_proxy_and_create_pac(task={}):
    fun = "change_proxy_and_create_pac"
    d_ = os.path.realpath(os.path.dirname(__file__))
    d = {
        "s_only_socks_proxies": 1,  # только соксы?
        "s_proxy": "",
        "s_cached_proxies": [],
        "s_proxy_only_one_success": 0,  # хз что
        "s_f_pac": "",  # куда пак сохраняем
        "s_f_pac_template": "%s/data/proxy_template_china_gmail.pac" % d_,
    }
    task = add_defaults(task, d)
    T = Bunch(task)

    logger.debug("[%s" % fun)

    # show_dict(task)
    if T.s_f_pac == "":
        logger.error("no pac file")
        return ""

    t = 0
    if t:
        if T.s_proxy in ["", []] and T.s_cached_proxies == []:
            logger.debug("no proxies")
            return ""

    t_start = time.time()
    i = 0
    while True:
        i += 1
        logger.debug("	%s" % i)
        seconds = time.time() - t_start
        if seconds > 10:
            logger.error("too many seconds %s, sleep" % fun)
            time.sleep(10)
            t_start = time.time()
            continue

        t = 0
        t = 1
        if t:
            pr = change_proxy_and_create_pac_one(task)
            if T.s_proxy == "":
                if T.s_only_socks_proxies:
                    if pr.find("socks") == -1:
                        logger.debug("%s is not socks proxy" % pr)
                        continue

        add_to_full_log(["new proxy: %s" % pr])
        return pr


def change_proxy_and_create_pac_one(task={}):
    d_ = os.path.realpath(os.path.dirname(__file__))
    d = {
        "s_proxy": "",
        "s_cached_proxies": [],
        "s_proxy_only_one_success": 0,  # хз что
        "s_f_pac": "",  # куда пак сохраняем
        "s_f_pac_template": "%s/data/proxy_template_china_gmail.pac" % d_,
    }
    task = add_defaults(task, d)
    T = Bunch(task)
    # return 0

    fun = "change_proxy_and_create_pac_one"
    logger.debug("[%s" % fun)

    # show_dict(task)
    # wait_for_ok(fun)

    # logger.debug('proxy %s, cached_proxies %s' % (T.s_proxy, T.s_cached_proxies))
    # wait_for_ok()
    if T.s_proxy not in ["", []] or T.s_cached_proxies != []:
        while True:

            if T.s_proxy != "":
                proxy = T.s_proxy
            else:
                # proxy = my_proxy.new_proxy()
                proxy = T.s_cached_proxies.get()

            logger.debug("proxy: %s" % proxy)
            # wait_for_ok()

            if T.s_proxy_only_one_success:
                if proxy_propuskaem(proxy):
                    continue

            v = extract_proxy(proxy)
            if v == False:
                continue
            break
    else:
        proxy = "0:0 socks4"
        v = extract_proxy(proxy)

    pr, port, tip = v

    if pr == "direct":
        rmfile(T.s_f_pac)
    else:
        template = text_from_file(T.s_f_pac_template)

        if tip == "socks5":
            pristavka = "SOCKS5"
        elif tip in ["socks", "socks4"]:
            pristavka = "SOCKS"
        elif tip.find("socks") != -1:
            pristavka = "SOCKS5"
        elif tip in ["http", "https"]:  # https загадочный вообще
            pristavka = "PROXY"
        else:
            join_text_to_file(tip, "!unknown_tips.txt")
            pristavka = "PROXY"
        # wait_for_ok('unknown tip for %s' % tip)

        pr = "%s %s:%s" % (pristavka, pr, port)
        _ = {
            "[proxy]": pr,
        }
        t = no_probely(template, _)
        text_to_file(t, T.s_f_pac)
    logger.debug("new proxy: " % proxy)
    task["ip"] = proxy
    # wait_for_ok()
    return proxy


#####################################################с других либ
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<подсчет по рекапче делаю
def count_recaptcha_send(status=""):
    # хочу вести статистику, чтобы знать сколько ж капч просираю и нужно ли ип например менять
    fun = "count_recaptcha_send"
    logger.debug("[%s" % fun)
    logger.warning("zaglushka")
    return

    if not sett["cr_want"]:
        logger.debug("do not want count recaptcha]")
        return 0

    posting = {
        "from": sett["name_addurler"],
        "action": status,
    }
    _ = {
        "u": sett["cr_u"],
        #'u':'http://skirda.net/' + 'mozg.php?no_rewrite=0&otladka=1',
        "post": posting,
        #'post':posting2,
        "sposob": "requests",
    }
    show_dict(_)

    r = pycus_u(_)
    if r["kod"] != 200:
        logger.error("-]")
        return False

    logger.debug("+]")
    text_to_file(r["html"], f_temp)


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def recaptcha_guesser(user={}, want_try=0):
    fun = "recaptcha_guesser"
    limit = 1
    i = 0

    while True:
        i += 1
        if i > limit:
            logger.error("%s - ERROR, too much tries" % fun)
            return 0

        if want_try:
            try:
                r = recaptcha_guesser_one(user)
                return r
            except Exception as er:
                logger.error("%s error_%s:" % (fun, i))
        else:
            r = recaptcha_guesser_one(user)
            return r


def recaptcha_guesser_one(user={}):

    # главный угадывальщик рекапчи!
    fun = "recaptcha_guesser_one"
    d_sett = {
        "rc_max_recaptcha_reload": 50,  # сколько можно кнопкой "релоад" рекапчи нерезагружать рекапчу максимально раз
        "rc_cnt_max_errors_with_captcha": 20,
        "rc_exit_if_ban_captcha": 1,  # выход если капча не разгадана?
        "rc_want_recaptcha_image": 1,
        "rc_recaptcha_hack": 0,  # хакаем рекапчу?
        "rc_return_hack": 0,  # возвращать ответ?
        "rc_emulate_guess_recaptcha": 0,  # емулируем рандомный клик?
        "rc_recaptcha_after_long_mp3": 1,
        "rc_recaptcha_bad_question_exit": 2,  # 2 - если у рекапчи вылез "мигающий" вопрос - уходим. 3 - разгадываем
        "rc_recaptcha_bad_questions": "nahposhuk",
        "rc_recaptcha_bad_questions": "street number|with rivers|store front|shop front|verify once there are none left|Когда изображения закончатся",  # мигающие вопросы, через |
        "rc_recaptcha_bad_questions_polube": "store front|shop front|магазин|витрин",  # полюбе плохие, перезагружаем
        "rc_recaptcha_bad_questions_polube": "nahposhuk",  # полюбе плохие, перезагружаем
        "rc_d_recaptcha_img_guessed": "",  # куда картинки
        "rc_rucaptcha_key": "",  # ключ рекапчи второй, партнер себя
        "rc_cnt_tries_redownload_mp3": 10,  #
        "rc_bad_captcha_after": 2,
        "rc_long_captcha_size": 40,  # kb - больше скольких килобайт капча считается длинной
        "rc_want_cut_mp3_captcha": 1,  # хочу ли я обрезать капчу при вводе? Обычно и краткая капча катила
        "rc_captcha_cnt_max_symbols": 7,  # сколько макс. символов в ответе капчи
        "rc_captcha_mp3_vruchnu": 0,  # вручную капчу угадывать? Даже нет такой опции пока в апи.
        "rc_max_miga": 20,  # сколько раз максимально мигаем
    }
    d = {
        "S": "",  # класс селениума
        "sett": d_sett,
    }
    user["sett"] = add_defaults(user["sett"], d_sett)

    keys_int = [
        "rc_max_recaptcha_reload",
        "rc_cnt_max_errors_with_captcha",
        "rc_return_hack",
        "rc_recaptcha_hack",
    ]
    # делаем int
    for k in user["sett"]:
        v = user["sett"][k]
        if k in keys_int or type(d_sett.get(k, "")) == type(
            111
        ):  # type(k)==type(111) or
            v = int(v)
        user["sett"][k] = v

    user = add_defaults(user, d)
    # logger.debug('user %s' % user)
    # wait_for_ok()
    T = Bunch(user)

    S = user["S"]
    sett = user["sett"]

    # current_url = S.driver.current_url
    # logger.debug('current_url1 %s' % current_url)

    ip = ""

    # useragent = user['useragent']

    d_log = os.path.join("log", fun)

    # try:
    # 	shutil.rmtree(d_log)
    # except Exception as er:
    # 	pass

    f_start = os.path.join(d_log, "start.html")
    f_step00 = os.path.join(d_log, "step00.html")
    f_step000 = os.path.join(d_log, "step000.html")

    f_step01 = os.path.join(d_log, "step01.html")
    f_step02 = os.path.join(d_log, "step02.html")
    f_step03 = os.path.join(d_log, "step03.html")
    f_step04 = os.path.join(d_log, "step04.html")

    f_spec01 = os.path.join(d_log, "spec01.html")
    f_spec02 = os.path.join(d_log, "spec02.html")
    f_spec03 = os.path.join(d_log, "spec03.html")

    f_check01 = os.path.join(d_log, "check01.html")
    f_check02 = os.path.join(d_log, "check02.html")
    f_check03 = os.path.join(d_log, "check03.html")

    # 	f_step01_profile = 'log/04_profile_final.html'

    f_step11 = os.path.join(d_log, "step11.html")

    # 	f_step20 = 'log/step20.html'

    # 	f_step21 = 'log/step21.html'

    logger.debug("[%s	" % (fun))

    show_dict(user["sett"])

    logger.debug("step 1")
    rand_sleep()
    i = 0
    need_reload = False
    er_max = sett["rc_cnt_max_errors_with_captcha"]
    while True:
        i += 1
        if i > er_max:
            return (
                False,
                "too many rc_cnt_max_errors_with_captcha - %s" % er_max,
            )

        logger.info("\n" * 2 + "try captcha%d" % i)

        if need_reload:
            # ip = tor_change_ip_potok({'tor':sett['num_tor']}, polube=False)
            sett["ip"] = ip
            # if ip!=sett['ip']:
            # 	add_to_full_log(['acc_log', user['acc']['login'], 'ip %s' % ip])
            j = 0
            while True:
                j += 1
                # if j>3:
                if j > 3:
                    return False, "sgp"

                logger.debug("reload_%d" % j)
                driver.switch_to_default_content()
                # driver.select_window('null')
                p = S.sgp(sett["u_register"])
                # sleep_(3)
                if p == False:
                    continue
                break
        # text_to_file(p, f_step00)

        else:
            sleep_(3)
            p = S.sgp()

        text_to_file(p, f_start)
        if 1:
            # logger.debug('T=%s' % t)
            user["S"] = S
            user["T"] = T
            status0 = select_captchas(p, user)
            logger.debug("status_select_captchas0: " % status0)
            # wait_for_ok()

            status = status0
            mess = ""
            if type(status0) != type("str"):
                status, mess = status0

            if mess == "bad_ip":
                return False, "bad_ip"

            if mess == "rc_max_miga" or mess == "rc_max_recaptcha_reload":
                logger.debug(
                    "max rc_max_miga or rc_max_recaptcha_reload, so close recaptcha"
                )

                # вернулись в главный фрейм и выключили рекапчу
                S.driver.switch_to_default_content()

                t = 0
                t = 1
                if t:
                    _ = {
                        #'only_click_recaptcha':1,
                        "delete_recaptcha_iframe": 1,
                    }
                    status0 = select_captchas(p, user, _)
                    logger.debug("status0=%s" % status0)

                # удаляем все ифреймы которые есть
                return False, "rc_max_miga"

            if sett["rc_recaptcha_hack"]:
                if status == "good":

                    logger.debug("hack guessed, inserting %s" % mess)
                    S.driver.switch_to_default_content()

                    id = "g-recaptcha-response"
                    elem = S.find_element_by_id(id)
                    if not elem:
                        return False, "hask - no id %s" % id

                    js = (
                        "document.getElementById('%s').style.display = 'visible';"
                        % id
                    )
                    logger.debug(js)
                    S.driver.execute_script(js)
                    # js.executeScript("",element);

                    js = "arguments[0].setAttribute('style', 'border:5px solid red;')"
                    S.driver.execute_script(js, elem)

                    id_to_value = []

                    id_to_value.append(
                        {"tip": "input", "id": id, "value": mess}
                    )

                    task_send_values = {
                        "id_to_value": id_to_value,
                        #'want_move_points':0,#хочу ли я обводить элемент для проверки
                        #'sleep_ot':0,#сколько ждать после ввода
                        #'sleep_do':0,
                    }
                    r = S.send_all_values(task_send_values)
                    if not r:
                        return False, "bito, bad task_send_values"

                    logger.debug("uraaa, hacked]")

                    if sett["rc_return_hack"]:
                        return mess

                    return 1

                else:
                    logger.error("wrong answer %s" % status0)
                    add_to_full_log(["acc_log", "ERROR", mess])
                    return 0

            if mess in ["rc_max_recaptcha_reload"]:
                add_to_full_log(["acc_log", "ERROR", mess])
                return 0

            # отправляем статус
            if status in ["lucky_no_captcha", "good"]:
                count_recaptcha_send(status)
                return 1

            if status in ["ban_captcha"]:
                er_max += 1
                # ip = tor_change_ip_potok({'tor':sett['num_tor']}, polube=True)
                sett["ip"] = ip
                # add_to_full_log(['acc_log', user['acc']['login'], 'ip %s' % ip])
                add_to_full_log(["acc_log", "ban_captcha", "ip %s" % ip])

            logger.debug(
                'status_select_captchas: "%s", mess: "%s"' % (status, mess)
            )
            errors_continue = [
                "ban_captcha",
                "no_button",
                "error search_element",
            ]

            # бан капчи - перезагр. страницу и опять пробуем :)
            if status in errors_continue or mess in errors_continue:
                er_full = str(status0)

                # if status in ['ban_captcha']:
                if 1:
                    # add_to_full_log(['acc_log', user['acc']['login'], er_full])
                    add_to_full_log(["acc_log", er_full])

                if sett["rc_exit_if_ban_captcha"]:
                    return False, status
                # 	S.good_exit()

                need_reload = True
                # wait_for_ok()
                continue

            # if status=='too_much_long_captchas':
            # 	#continue
            # 	acc_mark_ban(user['acc'], 'too_much_long_captchas')
            # 	add_to_full_log(['acc_log', user['acc']['login'], status])
            # 	restart_with_the_same_settings()
            # 	return False, status

            if status not in ["good", "lucky_no_captcha"]:
                return False, status
            # elif status==False and mess!='':
            else:
                logger.debug("good, guessed audio captcha :)")
            # cookies_save_hitro(user['acc'])

        # 	return True, status
        # wait_for_ok('audio captcha!')


def online_guess_recaptcha(task={}):
    """guess recaptcha online"""
    fun = "online_guess_recaptcha"
    logger.debug("[%s" % fun)

    t_start = time.time()

    d = {
        "f": "",  # файл с картинкой. Если пусто - берем с bin
        "bin": "",
        "question": "",
        "img_instruction": "",  # если есть пример картиночки
        "previousID": 0,
        "sett": {},
    }
    task = add_defaults(task, d)
    # show_dict(task)
    T = Bunch(task)

    sett = task["sett"]

    if T.bin == "":
        T.bin = text_from_file(T.f, "rb")

    t = 1
    if t:
        post = {
            # path=T.f,
            "img": T.bin,
            "recaptcha": 1,
            "textinstructions": T.question,
            "previousID": T.previousID,
            # imginstructions=T.img_instruction,
        }
        cap_id = rucaptcha_send_cap(sett["rc_rucaptcha_key"], post)
        logger.debug("cap_id: %s" % cap_id)

        if not cap_id:
            return 0, 0

        try:
            status, rez = rucaptcha_get_cap_text(
                sett["rc_rucaptcha_key"], cap_id
            )
        except Exception as er:
            mes = "ERROR AUTOCAPTCHA (%s)" % str(er)
            logger.debug(mes)
            return 0, mes

    # return status, rez

    else:
        ru_captcha = RUCaptcha(apikey=sett["rc_rucaptcha_key"])

        value = ru_captcha.parse(
            path=T.f,
            recaptcha=1,
            textinstructions=T.question,
            # imginstructions=T.img_instruction,
        )

        gs["ru_captcha"] = ru_captcha
        cap_id = ru_captcha.captcha_id
        logger.debug("cap_id: %s" % cap_id)
        #
        print("{value!r}".format(value=value))
        #
        i = 0
        while not value.is_ready():
            i += 1
            logger.debug("%s_%s not ready" % (i, func))
            time.sleep(1)
        #
        print("{value!r}".format(value=value))
        # click:2/4/6/8

        # gs['ru_captcha_id_captcha'] =

        rez = value.get_value()
        if rez == 0:
            return 0, 0

    count_recaptcha_send("recaptcha_answered")

    if rez.find("click:") != -1:
        click = find_from_to_one("click:", "nahposhuk", rez)
        return click, cap_id

    return 0, cap_id

    return answer

    f_name = os.path.basename(T.f)
    f_hash = f_name.split(".")[0]

    posting = {
        "task": "create_file",
        "f": f_name,
        "content": text_from_file(T.f, "rb"),
    }

    _ = {
        "u": T.u_guess_online + "mozg.php",
        "post": posting,
    }

    r = pycus_u(_)
    if r["kod"] != 200:
        return False

    # show_dict(r)

    text_to_file(r["html"], "temp/%s.html" % fun)
    # wait_for_ok()

    step = 0
    t_now = time.time()
    while True:
        step += 1
        logger.debug("step%d" % step)
        _ = {
            "u": T.u_guess_online,
        }

        if step > T.max_steps:
            logger.error("ups, too much steps")
            return False

        r = pycus_u(_)
        if r["kod"] != 200:
            continue
            return False

        html = r["html"]

        if html.find(f_hash) == -1:
            logger.error("ups, no file %s in tasks" % f_hash)
            return False

        # logger.debug('html=%s' % html)

        # items = text.split(" <a href='")
        items = find_from_to_all("href='", "'>", html)
        # show_list(items)
        guessed = ""
        for item in items:
            if item.find(f_hash) != -1:
                guessed = find_from_to_one(T.mark_done, ".", item)
                if guessed != "":
                    seconds_full = int(time.time() - t_start)
                    seconds = int(time.time() - t_now)
                    logger.debug(
                        "uraa, guessed in %s seconds, seconds_full %s!"
                        % (seconds, seconds_full)
                    )
                    # return guessed
                    break

        if guessed != "":
            break
        time.sleep(3)

    logger.debug("+guessed %s]" % guessed)
    return guessed


def select_captchas(p, user={}, more={}):
    fun = "select_captchas"
    d = {
        "only_click_recaptcha": 0,
        "delete_recaptcha_iframe": 0,
    }
    more = add_defaults(more, d)

    d_log = os.path.join("log", fun)
    d_mp3 = os.path.join("log", "mp3")

    d_mp3_guessed = os.path.join("log", "mp3_guessed")

    f_iframe = os.path.join(d_log, "iframe.html")
    f_iframe2 = os.path.join(d_log, "iframe2.html")
    f_step00 = os.path.join(d_log, "step00.html")

    f_step01 = os.path.join(d_log, "step01.html")

    f_step02 = os.path.join(d_log, "step02.html")

    f_temp1 = os.path.join(d_log, "temp1.html")

    f_temp2 = os.path.join(d_log, "temp2.html")

    f_temp = os.path.join(d_log, "temp.html")

    f_final = os.path.join(d_log, "final.html")

    f_step_reload_captcha = os.path.join(d_log, "reload_captcha.html")

    f_captcha = os.path.join(d_log, "captcha.jpg")

    f_captcha2 = os.path.join(d_log, "captcha2.jpg")

    f_captcha_miga = os.path.join(d_log, "captcha_miga.jpg")

    f_screenshot = os.path.join(d_log, "screenshot.jpg")

    f_screenshot_sized = os.path.join(d_log, "screenshot_sized.jpg")

    f_entered_captcha = os.path.join(d_log, "entered_captcha.html")

    # f_mp3= os.path.join(d_log, 'mp3.mp')

    acc = user.get("acc", {})

    logger.debug("[%s" % fun)

    S = user["S"]
    sett = user["sett"]

    sgp = S.sgp
    p = sgp()
    if p == False:
        return False, "sgp"
    text_to_file(p, f_step00)

    current_url = S.driver.current_url
    logger.debug("current_url2 %s" % current_url)

    sleep_(1)

    limit = 100
    log_captcha_size = []  # много длинных капч - фигня, считай что бот!
    for step in range(limit):
        need_full_reload = 0

        # first click
        logger.debug("%s - step %s" % (fun, step), 1)

        if sett["rc_recaptcha_hack"]:
            logger.info("HACK!")
            _ = {
                "name": "iframe",
                "attr": "src",
                "searching": "/recaptcha/api2",
                #'searching':'/recaptcha/api',
            }
            elem = S.search_element(_)
            # logger.debug('elem: %s %s' %( type(elem), elem))

            if S.not_found_search_element(elem):
                return False, "error search_element"
            src = elem.get_attribute("src")
            logger.debug("src: %s" % src)

            dct = get_vars_from_url(src)
            show_dict(dct)
            googlekey = dct["k"]
            logger.debug("googlekey: %s" % googlekey)

            post = {
                "googlekey": googlekey,
                "recaptcha": 1,
                "pageurl": current_url,
            }

            cap_id = rucaptcha_send_cap(sett["rc_rucaptcha_key"], post)
            logger.debug("cap_id: %s" % cap_id)

            r = rucaptcha_get_cap_text(sett["rc_rucaptcha_key"], cap_id)
            logger.debug("r: %s" % r)

            try:
                status, rez = r
            except Exception as er:
                mes = "ERROR AUTOCAPTCHA (%s)" % str(er)
                logger.error(mes)
                return 0, mes

            if status == "OK":
                add_to_full_log([googlekey, rez], "data/recaptcha_hack.txt")
                return "good", rez

            else:
                mess = "no_guessed"
                logger.error(mess)
                return 0, mess

            wait_for_ok()

        if more["delete_recaptcha_iframe"]:
            # driver.switch_to_frame(driver.find_element_by_tag_name("iframe"))
            logger.debug("deleting iframe...")
            _ = {
                "name": "iframe",
                "attr": "src",
                "searching": "/recaptcha/api2/frame",
                #'searching':'/recaptcha/api',
            }
            _ = {
                "name": "div",
                "attr": "style",
                "searching": "z-index: 2000000000",
            }
            elem = S.search_element(_)
            # logger.debug('elem: %s %s' % ( type(elem), elem ))

            if S.not_found_search_element(elem):
                return False, "error search_element"

            r = S.delete_element(elem)
            logger.debug("  +deleted %s" % r)
            # wait_for_ok()
            return True, "deleted"

        # driver.switch_to_frame(driver.find_element_by_tag_name("iframe"))
        _ = {
            "name": "iframe",
            "attr": "src",
            #'searching':'/recaptcha/api2',
            "searching": "/recaptcha/api",
        }
        elem = S.search_element(_)

        if S.not_found_search_element(elem):
            return False, "error search_element"

        location_iframe = elem.location
        logger.debug("location_iframe: %s" % location_iframe)
        # wait_for_ok()

        S.driver.switch_to_frame(elem)
        # driver.switch_to_frame(driver.find_element_by_tag_name("iframe"))#inogda working
        # driver.switch_to_frame(driver.find_elements_by_tag_name("iframe")[0])
        p = sgp()

        # p = elem.get_attribute("outerHTML")
        if p == False:
            return False, "sgp"
        text_to_file(p, f_iframe)

        # wait_for_ok('check %s' % f_iframe1)

        t = 1
        t = 0
        if t:
            id = "recaptcha-anchor"
            S.find_element_by_id(id).click()
        else:  # ne nashlo

            found = False

            # хочу для любого языка
            succ = "I'm not a robot"
            succ = "recaptcha-anchor"
            if p.find(succ) != -1:
                # _ = "//div[@class='rc-anchor-content']"
                # _ = '''//*[]'''
                # _ = '''//*[text()="I'm not a robot"]'''
                _ = """//span[@id="recaptcha-anchor"]"""
                logger.debug(_)
                logger.debug("clicking recaptcha button...")
                sleep_(2)
                # wait_for_ok()
                try:
                    elem = S.find_element_by_xpath(_)
                    elem.click()
                    found = True
                    logger.debug("	clicked %s" % _)
                except Exception as er:
                    logger.debug("ups, not found. Er: %s" % er)
                # explore_iframes()
                # wait_for_ok('why no %s' % _)
                # continue

            if not found:
                logger.debug("search2")
                _ = {
                    "name": "input",
                    "attr": "value",
                    "searching": "audio challenge",
                }
                elem = S.search_element(_)
                if S.not_found_search_element(elem):
                    return False, "error search_element"

                elem.click()

                if S.not_found_search_element(elem):
                    continue

        if more["only_click_recaptcha"]:
            return True, "only_clicked_recaptcha"
        j = 0
        while True:
            j += 1
            if j > 1:
                break

            to_wait = '<span aria-atomic="true" aria-live="assertive" id="recaptcha-accessible-status">Opening verification challenge</span></section>'
            sleep_(5)
            p3 = sgp()
            if p3 == False:
                return False, "sgp"
            text_to_file(p3, f_step01)
            break

            # <span aria-atomic="true" aria-live="assertive" id="recaptcha-accessible-status">Opening verification challenge</span></section></div><div style="display:none" class="rc-anchor-error-msg-container"><span class="rc-anchor-error-msg"></span></div><div class="rc-anchor-content"><div class="rc-inline-block"><div class="rc-anchor-center-container"><div class="rc-anchor-center-item rc-anchor-checkbox-holder"><span dir="ltr" id="recaptcha-anchor" aria-checked="false" role="checkbox" class="recaptcha-checkbox goog-inline-block recaptcha-checkbox-unchecked rc-anchor-checkbox recaptcha-checkbox-clearOutline" aria-labelledby="recaptcha-anchor-label" aria-disabled="false" tabindex="0"><div role="presentation" class="recaptcha-checkbox-border" style=""></div><div role="presentation" class="recaptcha-checkbox-borderAnimation" style=""></div><div role="presentation" class="recaptcha-checkbox-spinner" style=""></div><div role="presentation" class="recaptcha-checkbox-spinnerAnimation" style=""></div><div role="presentation" class="recaptcha-checkbox-checkmark"></div></span></div></div></div><div class="rc-inline-block"><div class="rc-anchor-center-container"><label class="rc-anchor-center-item rc-anchor-checkbox-label" id="recaptcha-anchor-label">I'm not a robot</label>
            if p3.find(to_wait) != -1:
                logger.debug("try %d, found %s, retry" % (j, to_wait))
                sleep_(3)
                continue
            break

        # if srazu verified!
        mess_srazu_verified = '<span aria-atomic="true" aria-live="assertive" id="recaptcha-accessible-status">You are verified</span>'
        if p3.find(mess_srazu_verified) != -1:
            mess = "lucky_no_captcha"
            logger.debug(mess)
            # add_to_full_log(	['acc_log', acc.get('login', 'unknown_login'), mess]	)
            # wait_for_ok(mess)
            S.driver.switch_to_default_content()
            p3 = sgp()
            if p3 == False:
                return False, "sgp"
            text_to_file(p3, f_final)

            return mess  #'good'

        # wait_for_ok('verified srazu?')

        # second click
        t = 1
        t = 0
        if t:
            explore_iframes()
            wait_for_ok()

        t = 0
        t = 1
        if t:
            t = 0
            t = 1
            if t:
                logger.debug("up")
                S.driver.switch_to_default_content()
                time.sleep(3)
                p = sgp()
                text_to_file(p, f_temp1)

            # magia = with otladka works?
            # explore_iframes()
            # wait_for_ok('explored?')

            logger.debug("iframe")
            _ = {
                "name": "iframe",
                "attr": "src",
                "searching": "recaptcha/api2/frame?c=",
            }
            elem = S.search_element(_)

            if S.not_found_search_element(elem):
                return False, "error search_element"

            S.driver.switch_to_frame(elem)
            # driver.switch_to_frame(driver.find_elements_by_tag_name("iframe")[4])
            p = sgp()
            text_to_file(p, f_temp2)

        # wait_for_ok()

        want_recaptcha_image = 1  # хочу ли я разгадывать именно картинку	#test
        want_recaptcha_image = 0  # хочу ли я разгадывать именно картинку	#test

        # умно - если был бан капчи мп3, то угадываю картинку
        logger.debug("log_captcha_size: %s" % log_captcha_size)
        if (
            sett["rc_recaptcha_after_long_mp3"]
            and len(log_captcha_size) > 0
            and log_captcha_size[-1] in [1, -1]
        ):
            want_recaptcha_image = (
                1  # хочу ли я разгадывать именно картинку	#test
            )

        if sett["rc_want_recaptcha_image"]:
            want_recaptcha_image = 1

        img_guessed = 0
        if want_recaptcha_image:
            # http://scraping.pro/recaptcha-solve-selenium-python/ - тут решали похожую задачу
            need_reload = 1
            need_reload = 0
            cnt_img_tries = 0
            cnt_question_empty = 0
            while True:
                cnt_img_tries += 1

                if cnt_img_tries > sett["rc_max_recaptcha_reload"]:
                    mess = "too_much cnt_img_tries	%s" % cnt_img_tries
                    logger.debug(mess)
                    return False, "rc_max_recaptcha_reload"

                logger.debug("need_reload: %s" % need_reload)
                if need_reload:
                    id = "recaptcha-reload-button"
                    S.find_element_by_id(id).click()
                    sleep_(1)
                    p = sgp()
                    if p == False:
                        return False, "sgp"
                    text_to_file(p, f_step_reload_captcha)

                    # continue
                    need_reload = 0
                # wait_for_ok('reloaded?')

                log_captcha_size.append(-1)
                question = find_from_to_one(
                    '<div class="rc-imageselect-instructions">',
                    '<div class="rc-imageselect-clear"',
                    p,
                )
                question = kl(question)
                if question == "":
                    mess = "question empty, reload"
                    logger.debug(mess)
                    cnt_question_empty += 1
                    logger.debug("cnt_question_empty: %s" % cnt_question_empty)

                    if cnt_question_empty > 5:
                        logger.error("bad ip")
                        return False, "bad_ip"
                    need_reload = 1
                    continue
                    wait_for_ok("todo: empty question")

                logger.debug(
                    "%s/%s, question: %s"
                    % (
                        cnt_img_tries,
                        sett["rc_max_recaptcha_reload"],
                        question,
                    )
                )

                # если надо - здаемся сразу
                if sett["rc_recaptcha_bad_question_exit"]:
                    bads_polube = sett[
                        "rc_recaptcha_bad_questions_polube"
                    ].split("|")

                    need_reload = 0
                    for bad in bads_polube:
                        if question.find(bad) != -1:
                            status = (
                                "recaptcha_bad_question_exit_POLUBE because found recaptcha_bad_questions_polube with %s"
                                % bad
                            )
                            logger.debug(status)
                            need_reload = 1
                            status = "reload " + status
                            add_to_full_log(
                                [
                                    "acc_log",
                                    acc.get("login", "unknown"),
                                    status,
                                ]
                            )

                    if need_reload:
                        continue

                    bads = sett["rc_recaptcha_bad_questions"].split("|")
                    need_reload = 0
                    guess_miga = 0
                    for bad in bads:
                        if question.find(bad) != -1:
                            status = (
                                "recaptcha_bad_question_exit because found recaptcha_bad_questions with %s"
                                % bad
                            )

                            # можно выбрать - перезагрузить или выйти вообще
                            if sett["rc_recaptcha_bad_question_exit"] == 2:
                                logger.debug("status=%s" % status)
                                need_reload = 1
                                status = "reload " + status
                                logger.debug(status)
                                add_to_full_log(
                                    [
                                        "acc_log",
                                        acc.get("login", "unknown"),
                                        status,
                                    ]
                                )
                                break
                            elif sett["rc_recaptcha_bad_question_exit"] == 3:
                                guess_miga = 1

                                status = (
                                    "guess migajuschuju %s" % cnt_img_tries
                                    + status
                                )
                                logger.debug(status)
                                add_to_full_log(
                                    [
                                        "acc_log",
                                        acc.get("login", "unknown"),
                                        status,
                                    ]
                                )
                                break

                            add_to_full_log(
                                [
                                    "acc_log",
                                    acc.get("login", "unknown"),
                                    status,
                                ]
                            )
                            restart_with_the_same_settings()

                    if need_reload:
                        continue

                # wait_for_ok(que)
                need_continue = 0
                zahod = 0
                miga_image = 0
                answers_sizes = []
                while True:
                    zahod += 1
                    logger.debug(
                        "	guess with recaptcha, guess_miga %s (miga_image %s), zahod %s"
                        % (guess_miga, miga_image, zahod)
                    )

                    logger.debug("	answers_sizes: %s" % answers_sizes)
                    if len(answers_sizes) >= 2 and answers_sizes[-2:] == [
                        1,
                        1,
                    ]:
                        logger.debug("odinichnie kliki, hvatit")
                        need_continue = 0
                        break

                    if zahod > sett["rc_max_miga"]:
                        break
                    # mess = 'limit, zahod %s, rc_max_miga=%s' % (zahod, sett['rc_max_miga'])
                    # return False, 'rc_max_miga'

                    if miga_image:
                        rb_captcha = text_from_file(f_captcha_miga, "rb")
                        logger.debug("spec_captcha from %s" % f_captcha_miga)
                    # wait_for_ok()

                    else:

                        # это части картинки
                        _ = {
                            "name": "img",
                            "attr": "src",
                            "searching": "/recaptcha/api2/payload",
                            #'searching':'/recaptcha/api',
                        }
                        elem = S.search_element(_)
                        img_elements = S.search_elements(_)

                        if S.not_found_search_element(elem):
                            logger.error("ups, no captcha image")
                            need_reload = 1
                            break
                            wait_for_ok("todo: no_captcha_image")

                        u_img = elem.get_attribute("src")

                        # join_text_to_file(u_img, 'temp/u_img.txt')
                        # p = sgp(u_img)
                        ##if p==False:
                        ##	continue
                        # text_to_file(p, f_captcha, 0, 'wb')

                        r = pycus_u(u_img)
                        if r["kod"] != 200:
                            logger.error("ups, bad img")
                            need_reload = 1
                            break
                            wait_for_ok("todo: bad_img")

                        rb_captcha = r["html"]

                        h = to_hash(rb_captcha)
                        f_captcha = os.path.join(d_log, "captcha_%s.jpg" % h)

                        text_to_file(rb_captcha, f_captcha, 0, "wb")

                        # если решаем мигающую - дергаем размер нашей, и делаем такой же размер
                        t = 0
                        if t and guess_miga:
                            # f_captcha =
                            im = Image.open(f_captcha)
                            width, height = im.size
                            logger.debug("img size: %s" % (width, height))

                            xpath = '//table[@class="rc-imageselect-table-33"]'
                            xpath = '//div[@class="rc-imageselect-target"]'
                            xpath = '//div[@class="rc-imageselect-challenge"]'
                            element = S.search_element_xpath(xpath)
                            if not element:
                                logger.error("ups, no image?")
                                wait_for_ok()

                                need_reload = 1
                                break

                            sel_highlight_element(element, 10)

                            _ = {
                                "element": element,
                                "f_to": f_screenshot,
                                #'size_img':(width, height),
                                #'zsuv':location_iframe,
                            }
                            r = S.screenshot_element(_)
                            logger.debug("status_saved_screenshot: %s" % r)
                            wait_for_ok(
                                "saved screenshot to %s?" % f_screenshot
                            )

                            wait_for_ok("miga - downloaded image?")

                    if sett["rc_emulate_guess_recaptcha"]:
                        answers = "1,2,3,4,5,6,7,8".split(",")
                        shuffle(answers)
                        answer = "/".join(answers[:3])
                        # answer = '1/3/5'
                        logger.debug("emulated answer: %s" % answer)
                        answer, cap_id = answer, -1

                    else:
                        t = 0
                        t = 1
                        if t:
                            _ = {
                                #'f':f_captcha,
                                "bin": rb_captcha,
                                "question": question,
                                "sett": sett,
                            }

                            if miga_image:
                                _["previousID"] = cap_id

                            answer, cap_id = online_guess_recaptcha(_)
                        else:
                            answer, cap_id = "1/3/5"

                    if answer == 0:  # плохая капча, перезагружаем
                        logger.debug("answer==0")
                        need_reload = 1
                        break

                    # wait_for_ok('answer good?')

                    if (
                        answer.find("No_matching_images") != -1
                    ):  # значит мигающие - откликали!
                        wait_for_ok("No_matching_images?")
                        break

                    # выбираем на что кликаем
                    nums_to_click = answer.split("/")
                    shuffle(nums_to_click)  # зашафлим
                    answers_sizes.append(len(nums_to_click))

                    _ = {
                        "name": "div",
                        "attr": "class",
                        "searching": "rc-image-tile-target",
                        #'searching':'/recaptcha/api',
                        "first": 0,
                    }
                    elems = S.search_element(_)
                    logger.debug("found %s positions to click" % len(elems))
                    # nums_to_click = [

                    found_bad_num = 0  # работник иногда даже номер 9 присылают для сетки из 8 штук
                    for num in nums_to_click:
                        num = int(num)
                        logger.debug("	click %s" % num)
                        try:
                            elems[num - 1].click()
                        except Exception as er:
                            logger.error("%s" % er)
                            found_bad_num = 1
                        sleep_(0.5)
                    # wait_for_ok()

                    if found_bad_num:
                        rucaptcha_mark_captcha_bad_guessed(
                            sett["rc_rucaptcha_key"], cap_id
                        )
                        logger.debug("found_bad_num")
                        need_reload = 1
                        break

                    if not guess_miga:
                        break
                    else:
                        # прокликали - ждем чтобы загрузилось
                        sleep_(3)

                        # теперь собираем все эти картинки, которые обновились
                        _ = {
                            "name": "img",
                            "attr": "src",
                            "searching": "/recaptcha/api2/payload",
                            #'searching':'/recaptcha/api',
                        }
                        img_elements = S.search_elements(_)

                        logger.debug(
                            "know %s image elements" % len(img_elements)
                        )

                        num_to_file = {}
                        for num in nums_to_click:
                            num = int(num)
                            logger.deubg("	get picture for %s" % num)
                            elem = img_elements[num - 1]
                            u_img = elem.get_attribute("src")
                            logger.debug(u_img)

                            r = pycus_u(u_img)
                            if r["kod"] != 200:
                                logger.debug("ups, bad img")
                                need_reload = 1
                                break
                                wait_for_ok("todo: bad_img")

                            rb_captcha = r["html"]

                            # h = to_hash(rb_captcha)
                            f = os.path.join(
                                d_log, "captcha_small_%s.jpg" % num
                            )
                            rmfile(f)

                            text_to_file(rb_captcha, f, 0, "wb")

                            num_to_file[num] = f

                        logger.debug("redownloaded images:")
                        show_dict(num_to_file)

                        miga_image = generate_miga_image(
                            f_captcha, num_to_file, f_captcha_miga
                        )
                        # wait_for_ok('miga generated')
                        # webbrowser.open(f_captcha_miga)
                        if not miga_image:
                            logger.debug("not miga_image")
                            need_reload = 1
                            need_continue = 0
                            break

                        logger.debug("continue with miga!")
                        continue
                    # need_continue = 1

                    # wait_for_ok('miga done?')

                if need_continue:
                    continue

                # а теперь - верифай
                logger.debug("send verify!")
                sending = [
                    ["recaptcha-verify-button", -555],
                ]
                t = S.ssend_values(sending)
                if t == False:
                    return False, "error ssend_values"

                sleep_(3)
                p = sgp()
                if p == False:
                    return False, "sgp"
                text_to_file(p, f_entered_captcha)

                # ищем ошибки
                t = find_from_to_one("</tbody></table>", "nahposhuk", p)
                items = t.split('<div style="" class="')[1:]
                errors = []
                for item in items:
                    clas = find_from_to_one("nahposhuk", '"', item)
                    descr = find_from_to_one('">', "<", item)
                    errors.append(descr)

                all_errors = "\n".join(errors)

                txt_success = 'rc-button-reload rc-button-disabled"'

                show_list(errors)
                logger.debug("all_errors: %s" % all_errors)

                if all_errors.find("Please also check the new images") != -1:
                    status = "check_new_images"
                    logger.debug(status)
                    count_recaptcha_send(status)
                    # acc_mark_ban(user['acc'], status)
                    add_to_full_log(
                        ["acc_log", acc.get("login", "unknown"), status]
                    )

                    need_reload = 1  # todo - точно коментить?
                    # need_reload = 0
                    continue

                # restart_with_the_same_settings()
                # return False, status

                # возможно и этот вариант стоит обдумать
                elif (
                    all_errors.find("Multiple correct solutions required")
                    != -1
                ):
                    t = "Multiple correct solutions required"
                    logger.debug(t)
                    # pass
                    need_reload = 0
                    continue

                if p.find(txt_success) != -1:
                    # wait_for_ok('unknown situation?')
                    # move good captcha to new place
                    logger.debug("guessed (found txt_success %s" % txt_success)
                    img_guessed = 1
                    t = 0
                    t = 1
                    if t and sett["rc_d_recaptcha_img_guessed"] != "":
                        # f_mp3_guessed = os.path.join(d_mp3_guessed, '%s.mp3' % captcha)
                        f_guessed = os.path.join(
                            sett["rc_d_recaptcha_img_guessed"],
                            "%s__%s.jpg"
                            % (answer.replace("/", "-"), filename(question)),
                        )
                        move_file(f_captcha, f_guessed)
                    # wait_for_ok('moved?')
                    # return good
                    break

                elif all_errors != "" or 1:
                    if all_errors == "":
                        all_errors = "unknown_recaptcha_error"
                        h = to_hash(p)
                        text_to_file(p, "data/%s/%s.html" % (all_errors, h))

                    add_to_full_log(
                        [
                            "acc_log",
                            acc.get("login", "unknown_login"),
                            "image_bad_guessed",
                            all_errors,
                        ]
                    )
                    if all_errors != "":
                        count_recaptcha_send(all_errors)

                    if (
                        all_errors.find("Please select all matching images.")
                        != -1
                    ):
                        t = "Please select all matching images."
                        logger.debug(t)
                        need_reload = 1

                    elif all_errors.find("please solve more") != -1:
                        pass

                    else:
                        add_to_full_log(
                            [all_errors], "!unknown_recaptcha_errors.txt"
                        )

                    rmfile(f_captcha)
                    logger.debug("	RETRY")

                    # обозначаем капчку плохой
                    rucaptcha_mark_captcha_bad_guessed(
                        sett["rc_rucaptcha_key"], cap_id
                    )
                    # if gs['ru_captcha']!='':
                    # gs['ru_captcha'].reportbad(cap_id)
                    # wait_for_ok('reported_bad don?')

                    if all_errors.find("Please try again") != -1:
                        need_reload = 0

                    continue

                rmfile(f_captcha)

        # wait_for_ok('todo')
        # if img_guessed:
        # 	break

        else:
            want_recaptcha_image = 0
            id = "recaptcha-audio-button"
            loggr.debug("2 %s" % id)

            try:
                S.find_element_by_id(id).click()
            except Exception as er:
                logger.error("error: " % er)
                mess = "no_button"
                logger.debug(mess)
            # return False, mess
            # return mess

            sleep_(3)
            p3 = sgp()
            if p3 == False:
                return False, "sgp"
            text_to_file(p3, f_step02)

            # wait_for_ok()

            # cnt_mp3 = 10
            cnt_mp3 = 1000

            need_reload = 0
            for step in range(cnt_mp3):
                logger.debug("	download mp3, step %d" % step)
                logger.debug("log_captcha_size: %s" % log_captcha_size)

                if step >= sett["rc_cnt_tries_redownload_mp3"]:
                    mess = "too_much_tries_redownload"
                    # wait_for_ok('check %s' % mess)
                    return mess

                if len(log_captcha_size) > 0 and log_captcha_size[
                    -sett["rc_bad_captcha_after"] :
                ] == sett["rc_bad_captcha_after"] * [
                    1
                ]:  # последние несколько проверок - плохих
                    return "too_much_long_captchas"

                t = 0
                if need_reload or (t and step > 0):
                    logger.debug("reload")
                    id = "recaptcha-reload-button"
                    S.find_element_by_id(id).click()
                    sleep_(1)
                    p3 = sgp()
                    if p3 == False:
                        return False, "sgp"
                    text_to_file(p3, f_step_reload_captcha)

                t = 1
                if t:
                    # u_mp3 = find_from_to_one('<img style="top:0%; left: 0%" src="', '"', p3)
                    # u_mp3 = u_mp3.replace('payload?c', 'payload/audio.mp3?c')
                    u_mp3 = find_from_to_one(
                        '<div class="rc-audiochallenge-download"><a title="Alternatively, download audio as MP3" href="',
                        '"',
                        p3,
                    ).replace("&amp;k=", "&k=")
                    logger.debug("u_mp3: %s" % u_mp3)
                    if (
                        u_mp3 == ""
                        and p3.find('img alt="reCAPTCHA challenge image"')
                        != -1
                    ):
                        return "ban_captcha"
                    elif (
                        u_mp3 == ""
                        and p3.find('img alt="reCAPTCHA challenge image"')
                        == -1
                    ):
                        # wait_for_ok('check ban_captcha2')
                        return "ban_captcha"
                    elif u_mp3 == "":
                        wait_for_ok("check ban_captcha3")
                        return "ban_captcha"
                        continue

                    f_mp3 = os.path.join(d_mp3, "%s.mp3" % to_hash(u_mp3))
                    t = 0
                    t = 1
                    if t:
                        r = pycus_u(u_mp3)
                        rb = r["html"]
                    # wait_for_ok()
                    else:
                        rb = sgp(u_mp3)

                    logger.debug("len: %s" % len(rb))

                    need_reload = 0
                    if (
                        len(rb) > sett["rc_long_captcha_size"] * 1000
                    ):  # длинная капча полюбе галимая
                        log_captcha_size.append(1)
                        need_reload = 1

                        if sett[
                            "rc_recaptcha_after_long_mp3"
                        ]:  # если надо - выходим на капчу картиночную
                            want_recaptcha_image = 1
                            break

                        continue

                    if len(rb) > 1000:
                        text_to_file(rb, f_mp3, 0, "wb")

                    t = 0
                    t = 1
                    if t:
                        captcha = online_guess_mp3({"f": f_mp3})
                        # captcha = '11111'
                        if captcha == False:
                            continue

                        # captcha = captcha[:3]

                        # 5 длинных капч подряд - это жопка
                        _ = len(captcha)
                        captcha_analize = 0
                        if _ > sett["rc_captcha_cnt_max_symbols"]:
                            logger.error(
                                "there are too much symbols in captcha"
                            )
                            captcha_analize = 1
                            if sett[
                                "rc_recaptcha_after_long_mp3"
                            ]:  # если надо - выходим на капчу картиночную
                                want_recaptcha_image = 1
                                break

                        log_captcha_size.append(captcha_analize)

                        time.sleep(5)

                        # use shorter captcha
                        t = 0
                        if t or sett["rc_want_cut_mp3_captcha"]:
                            new_len = int(
                                _ * 0.6
                            )  # ЭТО ТОЧНО РАБОТАЛО, НО ВРОДЕ ПЕРЕСТАЛО, ТЕСТИРУЮ длиннее
                            new_len = int(_ * 0.7)  # ura!!!
                            new_len = max(3, new_len)
                            logger.debug("new captcha size: %s" % new_len)
                            captcha = captcha[:new_len]
                        else:
                            ml = 9
                            logger.debug("just max size: %s" % ml)
                            captcha = captcha[:ml]

                        sending = [
                            ["audio-response", captcha],
                            ["recaptcha-verify-button", -555],
                        ]
                        t = S.ssend_values(sending)
                        if t == False:
                            return False, "error ssend_values"
                        sleep_(3)
                        p3 = sgp()
                        if p3 == False:
                            return False, "sgp"
                        text_to_file(p3, f_entered_captcha)

                        txt_success = 'rc-button-reload rc-button-disabled" title="Get a new challenge" role="button" style="-moz-user-select: none;" id="recaptcha-reload-button" aria-disabled="true">'
                        txt_success = 'rc-button-reload rc-button-disabled"'

                        if (
                            p3.find("Multiple correct solutions required")
                            != -1
                        ):
                            add_to_full_log(
                                [
                                    "acc_log",
                                    acc.get("login", "unknown_login"),
                                    "resolve_%s" % _,
                                ]
                            )
                            f_mp3_guessed = f_mp3.replace(
                                ".mp3", "_%s.mp3" % captcha
                            )
                            move_file(f_mp3, f_mp3_guessed)
                            logger.info("\n" * 2 + "solve more...")
                            continue

                        elif p3.find(txt_success) != -1:
                            # wait_for_ok('unknown situation?')
                            # move good captcha to new place
                            t = 0
                            t = 1
                            if t:
                                # f_mp3_guessed = os.path.join(d_mp3_guessed, '%s.mp3' % captcha)
                                f_mp3_guessed = os.path.join(
                                    d_mp3, "+%s.mp3" % captcha
                                )
                                move_file(f_mp3, f_mp3_guessed)
                                # text_to_file(text_from_file(f_mp3, 'rb'), f_mp3_guessed, 0, 'wb')
                                # rmfile(f_mp3)
                                # wait_for_ok('moved?')
                                break
                        else:
                            logger.error("ups, some error")
                            need_full_reload = 1
                            break

                        seconds = 10 + step * 5
                        seconds = min(60 * 3, seconds)
                        # seconds = 61
                        seconds = 3
                        seconds = 3 + step * 2
                        seconds = 0
                        logger.debug("sleep %d seconds" % seconds)
                        time.sleep(seconds)
                    # logger.debug('check %s' % f_mp3)

            if want_recaptcha_image:
                mess = "mp3 too long, CHANGE TO RECAPTCHA_IMAGE"
                logger.warning(mess)
                add_to_full_log(
                    ["acc_log", acc.get("login", "unknown_login"), mess]
                )

                id = "recaptcha-image-button"
                S.find_element_by_id(id).click()
                sleep_(1)
                p = sgp()
                if p == False:
                    return False, "sgp"
                text_to_file(p, f_step_reload_captcha)

                S.driver.switch_to_default_content()

                continue

        # return 'good'

        logger.debug("	switch_to_default_content")
        S.driver.switch_to_default_content()
        p3 = sgp()
        if p3 == False:
            return False, "sgp"
        text_to_file(p3, f_final)

        if need_full_reload:
            continue

        # wait_for_ok('all is done?')
        return "good"


def guess_captcha():

    d_log = os.path.join("log")

    f_captcha0 = os.path.join(d_log, "captcha.html")

    f_captcha = os.path.join(d_log, "1_captcha.jpg")

    cap_id = ""
    if True:
        while True:
            try:
                u_captcha = driver.find_element_by_xpath(
                    "//div[@id='recaptcha_image']/img"
                ).get_attribute("src")
            except Exception as er:
                mess = "no_captcha"
                logger.error(mess)
                return False, mess
            # elem = driver.find_element_by_id('recaptcha_image')
            # logger.debug('%s' % elem)
            # page = elem.get_attribute("outerHTML")
            # logger.debug('%s' % page)
            ##page = elem.page_source
            ##logger.debug('%s' % page)
            # u_captcha = 'https://www.google.com/recaptcha/api/image?c='+challenge

            logger.debug("\t captcha url: %s" % u_captcha)

            try:

                p1 = Pycus()  # g.clone()  # клонируем пикус

                p1.request(u_captcha, unicode_body=False)

                text_captcha = p1.body

                text_to_file(text_captcha, f_captcha, 0, "wb")

                if hand_captcha:

                    text_to_file(text_captcha, f_captcha, 0, "wb")

            except Exception as er:

                mes = "ERROR OPEN captcha %s er=%s" % (u_captcha, er)

                logger.error(mes)

                return False, mes

            # 	ВРУЧНУЮ КАПЧУ ОТГАДЫВАЕМ
            # 	logger.debug(f_captcha)
            if hand_captcha:
                webbrowser.open(f_captcha)
                captcha_value = raw_input("\tinput captcha: ")
            else:

                # отправляем капчу

                cap_id = send_cap(key, text_captcha)

                logger.debug("cap id: %s" % cap_id)

                if not cap_id:

                    mes = "ERROR CAPTCHA NOT SEND"

                    logger.debug(mes)

                    return False, mes

                # получаем результат

                try:

                    status, captcha_value = get_cap_text(key, cap_id)

                except Exception as er:
                    mes = "ERROR AUTOCAPTCHA (%s)" % str(er)
                    logger.error(mes)
                    return False, mes

            logger.debug("captcha guessed: %s" % captcha_value)

            if captcha_value == "ERROR_NO_SUCH_CAPCHA_ID":
                continue

            break

        return captcha_value, cap_id
    else:
        logger.warning("NO RECAPTCHA?")

    return "", ""


def my_react(message):
    fun = "my_react"
    logger.debug("[%s" % fun)
    f_message = os.path.abspath("temp/reaction.html")

    t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    message = "%s %s" % (message, t)

    add_to_full_log(["acc_log", "", message], "all")
    text_to_file(message, f_message)

    if sett["my_react_action"] in ["webbrowser", ""]:
        webbrowser.open(f_message)
        wait_for_ok()

    elif sett["my_react_action"] in ["email"]:
        _ = {
            "message": message,
            "subject": "addurl_selenium-NEED-ACTION",
        }
        reaction(_)

    elif sett["my_react_action"] in ["propusk"]:
        pass
    logger.debug("+]")


def s_get_f_cookie(profile_path):
    # получаем путь к файлу с куками
    return "%s/%s" % (profile_path, "cookies.sqlite")


#####################################################чисто селениум
def proxy_write_to_settings_firefox(task={}):
    fun = "proxy_write_to_settings_firefox"
    logger.debug("[%s" % fun)
    d = {
        "s_proxy": [],  # [[proxy, port, tip]],
        "s_autoconfig_url": "",
        "s_profile_path": "",  # r'c:\Users\kyxa\AppData\Roaming\Mozilla\Firefox\Profiles\elfdknqk.selenium_tumblr',
        "no_proxies_on": "",  # 	'media.tumblr.com, clients1.google.com, ocsp.digicert.com, gtglobal-ocsp.geotrust.com, .quantserve.com, .quantserver.com, .yahoo.com'
        "continue_if_no_prefs": 1,
    }
    task = add_defaults(task, d)

    if str(task["s_proxy"]).count(".") == 3:
        task["s_proxy"] = [task["s_proxy"]]

    show_dict(task)

    T = Bunch(task)

    profile_path = T.s_profile_path

    proxy_default = {
        "[http]": "",
        "[http_port]": "0",
        "[ssl]": "",
        "[ssl_port]": "",
        "[ftp]": "",
        "[ftp_port]": "0",
        "[socks]": "",
        "[socks_port]": "0",
        "[socks_version]": "4",
        "[no_proxies_on]": T.no_proxies_on,
        "[proxy_type]": "1",
        "[autoconfig_url]": "",
    }

    all_proxy_settings = {}

    for proxy in T.s_proxy:
        logger.debug("	%s" % proxy)
        if type(proxy) == type("str"):
            proxy = extract_proxy(proxy)
        pr, port, tip = proxy

        if tip == "https":
            tip = "ssl"

        version = ""
        if tip.find("socks") != -1:
            version = find_from_to_one("socks", "nahposhuk", tip)
            tip = "socks"

        _ = {
            "[%s]" % tip: pr,
            "[%s_port]" % tip: port,
            "[%s_version]" % tip: version,
        }
        all_proxy_settings = add_defaults(all_proxy_settings, _)

    if T.s_autoconfig_url != "":
        all_proxy_settings["[proxy_type]"] = "2"
        all_proxy_settings["[autoconfig_url]"] = T.s_autoconfig_url

    # show_dict(all_proxy_settings)

    all_proxy_settings = add_defaults(all_proxy_settings, proxy_default)
    # logger.info('-'*10 + 'using settings:')
    # show_dict(all_proxy_settings)
    # wait_for_ok()

    f_template = "%s/prefs_template.js" % profile_path

    if not os.path.isfile(f_template):
        if T.continue_if_no_prefs:
            return True
        else:
            logger.error("	%s error - no file %s" % (fun, f_template))
            return False
    # if pr=='127.0.0.1':
    # 	f_template = '%s/prefs_template_tor.js'%profile_path
    # elif tip.find('socks')!=-1:
    # 	f_template = '%s/prefs_template_socks.js'%profile_path
    # elif tip.find('https')!=-1:
    # 	f_template = '%s/prefs_template_ssl.js'%profile_path

    # f_template =

    f = "%s/prefs.js" % profile_path
    t = text_from_file(f_template)
    t = no_probely(t, all_proxy_settings)

    # text_to_file(t, 'temp/temp_proxy.txt')

    # t = t.replace('89.189.142.250', pr).replace(', 3128', ', %s'%port)
    # t = t.replace('media.tumblr.com', )

    logger.debug("autoconfig_url '%s'" % T.s_autoconfig_url)
    if T.s_autoconfig_url != "":
        # if 1:
        bad = find_from_to_one("all_proxies_start", "all_proxies_end", t)
        t = t.replace(bad, "")
    # else:
    # 	bad = find_from_to_one('all_proxies_start', 'all_proxies_end', t)
    # 	t = t.replace(bad, '')

    text_to_file(t, f)
    logger.debug("+]")


def get_random_useragent(tipa="Firefox"):
    """
		получаю рандомный юзерагент
		самые популярные нашел тут:
			https://techblog.willshouse.com/2012/01/03/most-common-user-agents/
	"""
    fun = "get_random_useragent"
    logger.debug("[%s" % fun)

    items = r"""
#15.5%	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36
#6.1%	Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36
#3.9%	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36
3.1%	Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0
#2.9%	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36
2.7%	Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0
2.7%	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36
2.2%	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/604.4.7 (KHTML, like Gecko) Version/11.0.2 Safari/604.4.7
1.9%	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/604.5.6 (KHTML, like Gecko) Version/11.0.3 Safari/604.5.6
1.6%	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36
1.5%	Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36
1.4%	Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0
1.3%	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299
1.3%	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36
1.2%	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0
1.2%	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36
1.1%	Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36
1.0%	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36
1.0%	Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko
0.9%	Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0
0.9%	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 OPR/50.0.2762.67
0.9%	Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36
0.9%	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36
0.9%	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0
0.8%	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:58.0) Gecko/20100101 Firefox/58.0
0.7%	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36
0.6%	Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko
0.6%	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:57.0) Gecko/20100101 Firefox/57.0
0.6%	Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:52.0) Gecko/20100101 Firefox/52.0
0.6%	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36
0.6%	Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0
0.5%	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36
0.5%	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/604.5.6 (KHTML, like Gecko) Version/11.0.3 Safari/604.5.6
0.5%	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36
0.5%	Mozilla/5.0 (X11; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0
0.4%	Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36
0.4%	Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36
0.4%	Mozilla/5.0 (X11; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0
0.4%	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 OPR/50.0.2762.58
0.4%	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36
0.4%	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:57.0) Gecko/20100101 Firefox/57.0
0.4%	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/604.3.5 (KHTML, like Gecko) Version/11.0.1 Safari/604.3.5
0.4%	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36
0.4%	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36
0.4%	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/604.4.7 (KHTML, like Gecko) Version/11.0.2 Safari/604.4.7
0.4%	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36
0.4%	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/604.5.6 (KHTML, like Gecko) Version/11.0.3 Safari/604.5.6
0.4%	Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36
0.3%	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36
0.3%	Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36
0.3%	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/63.0.3239.84 Chrome/63.0.3239.84 Safari/537.36
0.3%	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:58.0) Gecko/20100101 Firefox/58.0
0.3%	Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0
0.3%	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36
0.3%	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36
0.3%	Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36
0.3%	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063
0.3%	Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0
0.3%	Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0
0.3%	Mozilla/5.0 (Windows NT 6.1; rv:52.0) Gecko/20100101 Firefox/52.0
0.3%	Mozilla/5.0 (Windows NT 6.1; rv:57.0) Gecko/20100101 Firefox/57.0
0.3%	Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36
0.3%	Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0; Trident/5.0)
0.3%	Mozilla/5.0 (Windows NT 10.0; WOW64; rv:56.0) Gecko/20100101 Firefox/56.0
0.3%	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36
0.3%	Mozilla/5.0 (Windows NT 6.1; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0
0.2%	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36
0.2%	Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0; Trident/5.0)
0.2%	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:58.0) Gecko/20100101 Firefox/58.0
0.2%	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36
0.2%	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36
0.2%	Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:57.0) Gecko/20100101 Firefox/57.0
0.2%	Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko
0.2%	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/604.4.7 (KHTML, like Gecko) Version/11.0.2 Safari/604.4.7
0.2%	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36
0.2%	Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0
0.2%	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36
0.2%	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36
0.2%	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8
0.2%	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36
0.2%	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8
0.2%	Mozilla/5.0 (Windows NT 6.1; rv:58.0) Gecko/20100101 Firefox/58.0
0.2%	Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36
0.2%	Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0
0.2%	Mozilla/5.0 (Windows NT 5.1; rv:52.0) Gecko/20100101 Firefox/52.0
""".split(
        "\n"
    )
    items = clear_list(items)
    good_agents = []
    for item in items:
        if item[0] in ["#"]:
            continue
        parts = item.split("	")
        ua = parts[1]
        if ua.find("Chrome") != -1:
            continue
        if item.find(tipa) != -1:
            good_agents.append(ua)
    agent = choice(good_agents)
    logger.debug('%s good, selected "%s"]' % (len(good_agents), agent))
    return agent


class selenium_class:
    description = "Класс для работы с селениумом"

    def __init__(self, task={}, debug=False):
        fun = "selenium_class"
        if debug:
            logger.debug3("[%s" % fun)
        d_ = os.path.realpath(os.path.dirname(__file__))
        d_chrome_arguments = [
            #'--profile-directory=Guest',
            #'--profile-directory=Profile3',
            "--disable-extensions",
            "--incognito",
            "--disable-plugins-discovery",
            # "--start-maximized",
            # "user-data-dir=",
        ]
        d = {
            "s_name": "empty_name",
            #'s_seconds_wait':25,
            "s_seconds_wait": 20,
            "s_maximize_window": 0,  # максимизировать окно?
            "s_maximize_f11": 0,  # f11?
            "s_window_position": -2000,
            "s_window_position": -1,
            "s_browser": "firefox",  # chrome
            "s_autostart": 1,  # автостарт селениума?
            # 	firefox settings
            "firefox_extensions": [],
            # chrome settings
            #'f_chrome_driver': r'c:\chromedriver.exe',
            "f_chrome_driver": r"c:\chromedrivers\chromedriver76.exe",
            "f_chrome_driver": r"c:\chromedrivers\chromedriver.exe",
            "debuggerAddress": "",
            "chrome_arguments": d_chrome_arguments,
            "chrome_experimental_options": [],
            # если со старого работаем
            "s_from_old_selenium": 0,  # со старого селениума?
            "s_driver": 0,
            "s_potok_num": 0,
            "s_want_phantom": 0,  # фантом?
            "s_ff_binary": "",  # спец-бинарник есть?
            "s_ff_binary_annex": "",  # приставка к имени есть?
            "s_chrome_binary": r"c:\Program Files (x86)\Google\Chrome\Application\chrome.exe",  # спец-бинарник есть?
            "s_want_random_useragent": 0,  # рандомный юзер-агент?
            "s_special_user_agent": "",  # специальный юзер-агент?
            "firefox_with_marionette": 0,  # фаерфокс с марионете?
            "s_f_with_id": "",  # файл с айди селениума
            "s_save_seleinum_pids": 1,  # сохранять айдишники селениума?
            "s_d_selenium_pids": "temp/selenium_pids",  # сюда айдишники сохраняем
            # настройки пака
            "s_profile_path": "",
            "s_clear_cookies": 0,  # чистить куки с профиля?,
            "s_proxy": [],
            "s_autoconfig_url": "",
            "s_f_pac": "",  # куда пак сохраняем
            "s_f_pac_template": "%s/data/proxy_template_china_gmail.pac" % d_,
            "s_only_socks_proxies": 1,  # только соксы?
            "s_cached_proxies": [],
            "s_proxy_only_one_success": 0,  # хз что
            "s_sleep_ot": 0,  # когда отправляю значения - сколько ждать
            "s_sleep_do": 0,
            # таймауты
            "s_sleep_sgp_long": 5,
            "s_sleep_after_send_values": 3,  # сколько спим после отпр. значений
            # подключение существующей сессии
            "s_hitro_session": 0,  # хитросессия?
            "s_f_driver_obj": 0,  # файл с объектом
            "s_command_executor_url": 0,
            "s_session_id": 0,
            "want_cookies": 1,  # хочу куки сохранять?
            "s_d_cookies": "data/cookies",  # куки сюда сохраняем
            "s_selenium_pid": 0,
            "f_IG": "",
            "want_non_detectable": 0,  # хочу чтобы меня не детектили?
            "generated_non_detectable": 0,  # уже генерил нон-детектбл?
            # рандомный размер браузера?
            "want_random_browser_size": "random",
            "want_random_browser_size": "",  # пусто значит не хочу
            "minimum_debug_level": "info",  # уровень отладки
        }
        task = add_defaults(task, d)

        f_IG = "temp/global_info/%s.txt" % filename(task["s_name"])
        if task["f_IG"] == "":
            task["f_IG"] = f_IG

        if task["s_autoconfig_url"] == "" and task["s_f_pac"] != "":
            task["s_autoconfig_url"] = r"file://%s" % task["s_f_pac"]

        if isinstance(task["chrome_arguments"], str):
            task["chrome_arguments"] = task["chrome_arguments"].split("|")

        self.selenium_pid = None
        self.browser_window = None
        self.browser_handle = None
        # wait_for_ok('setuped selenium_pid')
        self.debugger_port = None  # ==chrome
        self.marionette_port = None
        self.geckodriver_port = None
        self.minimum_debug_level = task["minimum_debug_level"]

        # если хитросессия - используем
        _ = {
            "f": task["f_IG"],
        }
        if debug:
            logger.debug3("get global info from %s" % task["f_IG"])
        IG = class_info_saved(_)
        self.IG = IG

        # if task['s_f_driver_obj'] != '':
        if task["s_hitro_session"]:
            print("using histrosession")
            session_id = IG.get("s_session_id")
            command_executor_url = IG.get("s_command_executor_url")
            with_old_session = 0
            if session_id != None:
                logger.debug("HITROSESSION, exists session_id, reuse")
                more = {
                    "s_session_id": session_id,
                    "s_command_executor_url": command_executor_url,
                }
                task = add_defaults(more, task)
                with_old_session = 1
            else:
                logger.debug("NO session_id, start new selenium")

        T = Bunch(task)
        self.task = task
        self.T = T
        self.proxy = ""

        self.driver = {}
        self.status = "init"
        self.s_sleep_sgp_long = self.T.s_sleep_sgp_long
        self.s_sleep_after_send_values = self.T.s_sleep_after_send_values

        self.command_executor_url = T.s_command_executor_url
        self.session_id = T.s_session_id

        # if T.s_from_old_selenium:
        if T.s_driver != 0:
            self.driver = T.s_driver
            if T.s_selenium_pid:
                self.sett["selenium_pid"] = pid

        if T.s_autostart:

            self.selenium_start_polube(self.task)

        # self.selenium_pid = self.get_selenium_pid()
        # wait_for_ok(self.selenium_pid)

    # def set_attribute(*args):
    # 	driver.execute_script("arguments[0].setAttribute(arguments[1], arguments[2]);", *args)

    # elm = driver.find_element_by_class_name("shot-circle")
    # set_attribute(elm, "cx", "150")
    # set_attribute(elm, "cy", "150")

    def js_get_html_from_xpaths(
        self,
        xpaths=[],
        mode="inner",
        encoding="utf-8",
        check_visibility=False,
        with_empty=False,
        f=None,
    ):
        """
        mode : inner outer
        """
        fun = "js_get_html_from_xpaths"
        debug = True
        debug = False
        logger.debug("[%s mode=%s xpaths=%s" % (fun, mode, xpaths))

        elements = self.js_find_elements_by_xpaths(
            xpaths,
            mode=mode,
            check_visibility=check_visibility,
            with_empty=with_empty,
            debug=debug,
        )

        if elements is None:
            return "empty"

        if debug:
            logger.debug("%s elements" % len(elements))
            show_list(elements)

        if encoding:
            if debug:
                logger.debug("elements 0: %s" % elements)
            elements = [
                unicode_to_text(_, encoding) for _ in elements if _ is not None
            ]
            if debug:
                logger.debug("elements encoded: %s" % elements)

        html = "<hr>\n\n".join(elements)

        if f is not None:
            text_to_file(html, f)

        # wait_for_ok(html)

        logger.debug("  +%s]" % (fun))
        return html

    # positions
    def setup_browser_position(
        self, position_x=0, position_y="top", *args, **kwargs
    ):
        return self.setup_browser_size_and_position(
            position_x=position_x, position_y=position_y, *args, **kwargs
        )

    def setup_browser_size_and_position(
        self,
        position_x=None,
        position_y=None,
        width=None,
        height=None,
        debug=False,
    ):
        fun = "setup_browser_size_and_position"
        monitor_width, monitor_height = get_monitor_size()
        if debug:
            logger.debug(
                "[{fun} position_x={position_x} position_y={position_y}, width={width}, height={height} for monitor {monitor_width}*{monitor_height}".format(
                    **locals()
                )
            )

        if position_y == "top":
            position_y = 0

        elif position_y == "middle":
            position_y = int(monitor_height / 2)

        if position_x is not None:
            self.set_window_position(position_x, position_y)

        if width is not None:
            self.set_window_size(width, height)

    def set_window_size(self, width, height):
        fun = "set_window_position"
        driver = self.driver
        try:
            driver.set_window_size(width, height)
        except Exception as er:
            logger.error("ERROR %s: er %s" % (fun, er))
        # wait_for_ok(mess)

    def click_on_xpath_with_position(
        self, xpath="//html", x=20, y=20, element=None, cnt_clicks=1
    ):
        fun = "click_on_xpath_with_position"
        t_start = time.time()
        logger.debug(
            "[%s %s clicks, xpath=`%s` x=%s y=%s (element=%s)"
            % (fun, cnt_clicks, xpath, x, y, element)
        )

        driver = self.driver
        if not element:
            try:
                element = driver.find_elements_by_xpath(xpath)[0]
            except Exception as er:
                logger.debug("no element with xpath %s" % xpath)
                return False

        action = webdriver.common.action_chains.ActionChains(driver)
        clicked = None
        try:
            action.move_to_element_with_offset(element, x, y)
            for i in range(cnt_clicks):
                action.click()
            clicked = action.perform()
        except Exception as er:
            logger.error("error %s: %s" % (fun, er))

        duration = time.time() - t_start
        logger.debug("   +%s=%s in %.2f seconds" % (fun, clicked, duration))
        return clicked

    def set_window_position(self, position_x, position_y):
        fun = "set_window_position"
        driver = self.driver
        try:
            driver.set_window_position(position_x, position_y)
        except Exception as er:
            logger.error("ERROR %s: %s" % (fun, er))

    def make_browser_visible_in_chrome(self, x=2000, y=2000):
        """оказывается - если окно посунуть, оно станет видимым!"""
        t = 0
        if t:
            x, y = 1920, 1080
            x = x - 1
            y = y - 1

        t = 1
        if t:
            x, y = -1, -1
        logger.debug(
            f"make_browser_visible_in_chrome with set_window_position {x}*{y}"
        )
        self.set_window_position(x, y)

    def check_is_hidden(self, debug=True):
        """проверяю - окно видиом ил"""
        old_position = ""
        if debug:
            old_position = self.driver.get_window_position()

        js = f"return document.visibilityState"
        js = f"return document.hidden"
        try:
            is_hidden = self.execute_script(js)
        except Exception as er:
            logger.error(f"ERROR {er=}")
            is_hidden = False
        if debug:
            logger.debug(f"{old_position=} {is_hidden=}")
        return is_hidden

    def get_xpath_mode_list(self, xpaths, mode=None):
        xpaths_with_mode = []
        if mode is None:
            mode = "innder"

        for xpath in xpaths:
            mode_special = mode
            if isinstance(xpath, list):
                xpath, mode_special = xpath
            if not xpath:
                continue
            xpaths_with_mode.append([xpath, mode_special])
        return xpaths_with_mode

    def js_get_html_from_xpath(
        self, xpath="", mode="inner", encoding="utf-8", f=None
    ):
        """
        mode : inner outer
        """
        html = self.js_find_element_by_xpath(xpath, mode=mode)
        # wait_for_ok()
        if encoding:
            html = unicode_to_text(html, encoding)

        if f is not None:
            text_to_file(html, f)

        # wait_for_ok(html)

        return html

    def get_html_from_xpath(
        self, xpath="", mode=None, encoding="utf-8", f=None
    ):
        # innerHTML = sel.get_eval(
        #     "window.document.getElementById('prodid').innerHTML")

        if mode == "js_inner":
            html = self.js_get_html_from_xpath(xpath, mode="inner")
        elif mode == "js_outer":
            html = self.js_get_html_from_xpath(xpath, mode="outer")

        else:
            element = self.find_element_by_xpath(xpath)
            if not element:
                return None

            # logger.debug('element=%s' % element)
            # wait_for_ok()

            html = self.get_html_from_element(
                element, mode=mode, encoding=encoding
            )

        if f is not None:
            text_to_file(html, f)

        return html

    def get_html_from_element(self, element, mode=None, encoding="utf-8"):
        """
        https://stackoverflow.com/questions/7263824/get-html-source-of-webelement-in-selenium-webdriver-using-python
        :param element: 
        :param mode: 
        :return: 
        """
        if mode is None:
            mode = "inner"
        fun = "get_html_of_element"

        if mode == "inner":
            # html = element.get_attribute('innerHTML')
            html = self.get_attribute(element, "innerHTML")

        elif mode == "outer":
            html = element.get_attribute("outerHTML")

        elif mode == "javascript_inner":
            js = "return arguments[0].innerHTML;"
            html = self.execute_script(js, element)

        elif mode == "javascript_outer":
            js = "return arguments[0].outerHTML;"
            html = self.execute_script(js, element)

        elif mode == "text":  # returns only text
            html = element.text

        else:
            wait_for_ok("%s ERROR: unknown mode=%s" % (fun, mode))
        # нужно encode?
        if encoding:
            html = unicode_to_text(html, encoding)
        return html

    def wait_for_presence_cnt_elements(
        self,
        cnt_elements=3,
        xpath="",
        timeout=5,
        poll_frequency=0.1,
        **kwargs,
    ):
        """жду чтобы появилось x элементов"""
        status = False
        t_start = time.time()
        while True:
            duration = time.time() - t_start
            if duration > timeout:
                break

            elements = self.search_elements_xpath(xpath=xpath,)
            logger.debug(f"{len(elements)} {elements=}")
            if len(elements) == cnt_elements:
                status = True
                break

            sleep_(poll_frequency, 0)

        return status

    def wait_for_presence_now(
        self, xpath="", timeout=0, poll_frequency=0.01, *args, **kwargs
    ):
        return self.wait_for_presence(
            xpath=xpath,
            timeout=timeout,
            poll_frequency=poll_frequency,
            *args,
            **kwargs,
        )

    def wait_for_presence(
        self, xpath="", timeout=10, poll_frequency=0.2, checking="presence"
    ):
        """
        https://selenium-python.readthedocs.io/waits.html
            http://allselenium.info/work-with-expected-conditions-explicit-waits/
            http://allselenium.info/working-with-expected-conditions-explicit-wait-part-2/

        Так подождать что старый елемент пропал:
            element = driver.find_element_by_id("elementID")
            # do something that refreshes the element
            self.wait.until(EC.staleness_of(element))
            element = self.wait.until(EC.visibility_of_element_located((By.ID, "elementID")))
            # do something with element
        """
        fun = "wait_for_presence"

        fun_check = "until"

        if checking == "presence":
            condition = EC.presence_of_element_located

        elif checking == "no_presence":
            # fun_check = until_not
            # condition = EC.presence_of_element_located
            condition = EC.invisibility_of_element_located

        # check - не существует
        elif checking == "no_element":
            fun_check = "no_element"
            condition = EC.staleness_of

        elif checking == "clickable":
            condition = EC.element_to_be_clickable

        else:
            wait_for_ok("ERROR %s - unknown checking=%s" % (fun, checking))

        logger.debug(
            "     [%s checking=%s %ss xpath='%s'"
            % (fun, checking, timeout, xpath)
        )
        t_start = time.time()
        try:
            if fun_check == "until":
                element = WebDriverWait(
                    self.driver, timeout, poll_frequency=poll_frequency
                ).until(condition((By.XPATH, xpath)))
            elif fun_check == "no_element":
                element = WebDriverWait(
                    self.driver, timeout, poll_frequency=poll_frequency
                ).until(condition(xpath))

            else:
                wait_for_ok(
                    "ERROR %s - unknown fun_check=%s" % (fun, fun_check)
                )
        except Exception as er:
            logger.debug(f"error {fun}: `{er=}`")
            element = False

        duration = time.time() - t_start
        logger.debug("  +%s in %.3f seconds]" % (element, duration))
        return element

    def click_xpath_with_js(self, xpath="", node_order="first"):
        """
        node_order='first' - кликаем на первый елемент, 'any' значит на любой

        :param xpath:
        :param node_order:
        :return:
        """
        fun = "click_xpath_with_js"
        logger.debug("  [%s xpath=%s node_order=%s" % (fun, xpath, node_order))

        js = generate_js_for_click_xpath_with_js(xpath, node_order=node_order)

        t_start = time.time()
        r = self.execute_script(js)
        duration = time.time() - t_start
        logger.debug("    [+%s=%s in %.3f seconds]" % (fun, r, duration))
        # wait_for_ok('clicked, check')
        return r

    def click_xpath_quick_if_exists(self, xpath=""):
        fun = "click_xpath_quick_if_exists"
        logger.debug(fun)

        sending = [
            [xpath, "click"],
        ]
        r_clicked = 0
        try:
            r_clicked = self.ssend_values_quick(sending)
            logger.debug("  r_clicked=%s" % r_clicked)
        except Exception as er:
            # error = 'can_not_click_odds_button'
            logger.debug("      no xpath to click %s" % er)

        return r_clicked

    def click_xpath(self, xpath="", mode="first"):
        fun = "click_xpath"
        elements = self.driver.find_elements_by_xpath(xpath)
        if len(elements) == 0:
            mess = '%s error - found %s elements - no elements for "%s"?' % (
                fun,
                len(elements),
                xpath,
            )
            logger.error(mess)
            # wait_for_ok(
            return False, "no_links"

        element = None
        if mode == "first":
            element = elements[0]

        elif mode == "click_like_human":
            position = select_position_like_human(len(elements))
            element = elements[position]

        elif mode == "random":
            shuffle(elements)
            element = elements[0]

        elif mode == "all":
            pass

        else:
            wait_for_ok("ERROR %s - unknown mode=%s" % (fun, mode))

        if element is not None:
            elements = [element]

        # sel_highlight_element(element, T.seconds_highlight)

        return self.click_elements(elements)

    def click_elements(self, elements):
        """
        Клик всех элементов
        """
        fun = "click_elements"
        if not isinstance(elements, list):
            elements = [elements]

        cnt_errors = 0
        cnt_clicked = 1
        for num, element in enumerate(elements, 1):
            logger.debug("		%s %s/%s" % (fun, num, len(elements)))
            try:
                element.click()
                logger.debug("  +")
            except Exception as er:
                logger.error("  -")
                cnt_errors += 1

        if cnt_errors:
            return False, cnt_errors
        else:
            return True, "clicked"

    def clear_all_data_in_firefox(self):
        fun = "clear_all_data_in_firefox"
        logger.debug2(fun)

        driver = self.driver

        t = 1
        if t:
            logger.debug("open preferences...")
            u = "about:preferences#privacy"
            self.sgp(u)

            logger.debug("click clearData...")
            xpath = '//*[@id="clearSiteDataButton"]'  #
            clicked = self.click_xpath(xpath)
            # logger.debug('clicked=%s' % clicked)
            sleep_(1)

        logger.debug("click clear...")

        # посылать таб в окно?
        actions = ActionChains(driver)
        actions.send_keys(Keys.TAB)
        actions.pause(0.1)
        actions.send_keys(Keys.TAB)
        actions.pause(0.1)
        actions.send_keys(Keys.ENTER)
        clicked = actions.perform()

        t = 0
        if t:
            # не смог очистить через хпас, решил нажатием клавиш
            driver.switch_to_default_content()

            xpath_window = '//*[local-name() = "vbox"][@role="dialog"]'  #
            xpath_window = (
                '//*[local-name() = "browser"][@name="dialogFrame-11"]'
            )

            # iframe = self.find_element_by_xpath(xpath_window)
            iframe = driver.find_element_by_xpath(xpath_window)
            logger.debug("iframe=%self" % iframe)

            switched = driver.switch_to.frame(iframe)
            logger.debug("switched=%self" % switched)

            p = self.sgp()
            f_ifr = os.path.abspath("temp/firefox_settings.html")
            text_to_file(p, f_ifr)
            logger.debug("check in %self" % f_ifr)

            xpath = '//*[@label="Clear"]'  # <button xmlns="http://www.mozilla.org/keymaster/gatekeeper/there.is.only.xul" dlgtype="accept" label="Clear" accesskey="l" default="true"><hbox class="box-inherit button-box" align="center" pack="center" flex="1" anonid="button-box"><image class="button-icon"/><label class="button-text" value="Clear" accesskey="l"/></hbox></button>
            clicked = self.click_xpath(xpath)
            logger.debug("clicked=%self" % clicked)

            driver.switch_to_default_content()

            logger.debug("click alert...")

        clicked = self.accept_alert()
        logger.debug("clicked=%self" % clicked)

        logger.debug1("+%s]" % fun)
        return clicked

    def send_to_body(self, cmd="new"):
        """
        Часто нужно ввести инфу в главное окно - для этого просто выбираю главный body и туда посылаем все
        """
        fun = "send_to_body"
        # или так попробовать:
        # 			from selenium.webdriver.common.action_chains import ActionChains
        # 			from selenium.webdriver.common.keys import Keys

        ## before correction from  DMfll:
        ## ActionChains(driver).send_keys(Keys.COMMAND, "t").perform()

        ## correct method
        # 			ActionChains(driver).key_down(Keys.COMMAND).send_keys("t").key_up(Keys.COMMAND)‌​‌​.perform()

        logger.debug("[%s" % fun)
        try:
            body = self.driver.find_element_by_tag_name("body")
        except Exception as er:
            logger.error(er)
            logger.debug("-]")
            return 0

        if cmd != "":
            try:
                logger.debug("send to body `%s`" % cmd)
            except Exception as er:
                logger.error("send cmd to body error %s" % er)

            body.send_keys(cmd)

        logger.debug("+]")

    # def zoom_0(self):
    #     """
    #     в фаерфоксе ничего не работает
    #         t = 1
    #         t = 0
    #         if t:
    #             ctrl = Keys.LEFT_CONTROL
    #             ctrl = Keys.CONTROL
    #             # body.send_keys(ctrl, '0')
    #             body.send_keys(Keys.LEFT_CONTROL+Keys.ADD)
    #             body.send_keys(ctrl, '0', ctrl)
    #             body.send_keys(ctrl)
    #             body.send_keys('0')
    #
    #
    #             actions = ActionChains(self.driver)
    #             actions.send_keys(ctrl, '+')
    #             actions.perform()
    #
    #             ActionChains(self.driver) \
    #                 .key_down(Keys.CONTROL) \
    #                 .key_down('0') \
    #                 .key_up(Keys.CONTROL) \
    #                 .key_up('0') \
    #                 .perform()
    #
    #             sleep_(1)
    #
    #             for i in range(5):
    #                 body.send_keys(ctrl, Keys.SUBTRACT)
    #                 body.send_keys(ctrl, '-')
    #             wait_for_ok('zoomed-?')
    #
    #         t = 1
    #         t = 0
    #         if t:
    #             logger.debug(body)
    #             ctrl = Keys.LEFT_CONTROL
    #             ctrl = Keys.CONTROL
    #             # body.send_keys(ctrl, '0')
    #             body.send_keys(Keys.LEFT_CONTROL+Keys.ADD)
    #             body.send_keys(ctrl, '0', ctrl)
    #             body.send_keys(ctrl)
    #             body.send_keys('0')
    #
    #
    #             actions = ActionChains(self.driver)
    #             actions.send_keys(ctrl, '+')
    #             actions.perform()
    #
    #             ActionChains(self.driver) \
    #                 .key_down(Keys.CONTROL) \
    #                 .key_down('0') \
    #                 .key_up(Keys.CONTROL) \
    #                 .key_up('0') \
    #                 .perform()
    #
    #             sleep_(1)
    #
    #             for i in range(5):
    #                 body.send_keys(ctrl, Keys.SUBTRACT)
    #                 body.send_keys(ctrl, '-')
    #             wait_for_ok('zoomed-?')
    #
    #
    #     :return:
    #     """
    #     # self.driver.set_context("chrome")
    #     # sending = Keys.CONTROL + '0'
    #     sending = Keys.CONTROL + '0'
    #     r = self.send_to_body(sending)
    #     # self.driver.set_context("content")
    #
    # def zoom_minus(self, cnt=5):
    #     sending = Keys.CONTROL + Keys.SUBTRACT  #+==Keys.add
    #     # sending = ''.join([sending for _ in range(cnt)])
    #     # sending = Keys.chord(Keys.CONTROL, Keys.SUBTRACT)
    #     return self.send_to_body(sending)

    def tab_cmd(self, cmd="new"):
        cmd_to_symbols = {
            "new": Keys.CONTROL + "t",
            "close": Keys.CONTROL + "w",
            "esc": Keys.ESCAPE,
        }
        sending = cmd_to_symbols.get(cmd, None)
        if sending is None:
            logger.debug('unknown cmd: "%s", try CONTROL+%s' % (cmd, cmd))
            sending = Keys.CONTROL + cmd
        return self.send_to_body(sending)

    def tab_new(self, cmd="new"):
        return self.tab_cmd("new")

    def minimize_window(self, debug=False):
        fun = "minimize_window"
        # driver = self.driver
        # driver.minimize_window()
        debug = True

        t_start = time.time()
        if debug:
            logger.debug("[%s" % fun)

        browser_window = self.get_browser_window()
        browser_window.minimize()

        duration = time.time() - t_start
        if debug:
            logger.debug("+ in %.3fs]" % duration)

    def pwa_do_browser_top(
        self, handle=None, actions=[], mode="handle", debug=False
    ):
        """
			физически окно вывожу выше всех и что-то делаю
			например ескей нужно нажать
			
			что через хендл, что через пид оказалось одинаково окно дергать
		"""
        debug = True
        t_start = time.time()
        fun = "pwa_do_browser_top"
        if debug:
            logger.debug("[%s" % fun)

        browser_window = self.get_browser_window()
        logger.debug("browser_window=%s " % browser_window)

        res = self.window_to_front_and_do_actions(browser_window, actions)

        duration = time.time() - t_start
        if debug:
            logger.debug("+ in %.3fs, res=%s]" % (duration, res))

    def get_browser_window(self, handle=None, mode=None):
        fun = "get_browser_window"
        logger.debug(fun)

        if self.browser_window:
            return self.browser_window

        if not mode:
            mode = "handle"

        pid = None
        if handle is None:
            handle = self.browser_handle

        logger.error("handle=%s" % handle)

        if handle is None:
            pid = self.get_selenium_pid()
            # wait_for_ok('%s pid=%s' % (fun, pid))
            # pid = 18396
            # logger.debug('pid %s' % pid)

            if mode == "handle":
                handle = find_handle_for_pid(pid)
                self.browser_handle = handle

        logger.debug1(
            "%s have pid %s, handle %s, mode=%s" % (fun, pid, handle, mode)
        )

        if mode == "pid" and pid is not None:
            pwa_mySetFocus_by_pid(pid)

        elif mode == "handle":
            if handle is None:
                er = "ups, no window :("
                logger.error(er)
                return 0
                wait_for_ok(er)

            logger.debug("ura, found handle!")
            # obj_to_file_p(handle, 'temp/window.obj')
            # wait_for_ok('saved handle?')
            window = pwa_handle_to_window(handle)
            # logger.debug('window=%s %s' % (type(window), window))
            self.browser_window = window

        return self.browser_window

    def __getstate__(self):
        """для pickle надо
            https://realpython.com/python-pickle-module/
        """
        attributes = self.__dict__.copy()
        del attributes["browser_window"]

        t = 1
        if t:
            # show_list(attributes)
            for k, v in attributes.items():
                logger.debug("%s k=%s" % (type(v), k))

        t = 1
        t = 0
        if t:
            logger.debug(
                "before picklking handle: %s %s"
                % (
                    type(attributes["browser_handle"]),
                    attributes["browser_handle"],
                )
            )
            del attributes["browser_handle"]

        return attributes

    def __setstate__(self, state):
        self.__dict__ = state
        self.browser_window = None
        # self.browser_handle = None

    def window_to_front_and_do_actions(self, window, actions=[]):
        # window = pwa_get_real_window(window)
        pwa_mySetFocus(
            window
        )  # TypeError: The object is not a PyHANDLE object
        # wait_for_ok()

        for button in actions:
            # pwa_tvvod('{ESC}', window)
            pwa_tvvod(button, window)

    def reload_and_sleep(self, seconds=5):
        """
			перезагружаю страницу и жду
		"""
        self.tab_cmd("r")
        sleep_(seconds)

    def send_all_values(self, task={}, cnt_tries=2):
        fun = "send_all_values"
        logger.debug("	[%s" % fun)
        # cnt_tries = 2

        want_try = 0
        want_try = 1

        i = 0
        while True:
            i += 1
            if i > cnt_tries:
                logger.error("%s ERROR - too much tries with error]" % fun)
                return 0

            if want_try:
                try:
                    r = self.send_all_values_one(task)
                    logger.debug("+]")
                    return 1

                except Exception as er:
                    logger.error("er: %s" % er)
                    sleep_(3)
            else:
                r = self.send_all_values_one(task)
                logger.debug("	+]")
                return 1

    def send_all_values_one(self, task={}):
        # посылаем словарь с тем что нужно кликать
        fun = "send_all_values_one"
        d = {
            "id_to_value": [],
            "want_move_points": 0,  # хочу ли я обводить элемент для проверки
            "sleep_ot": self.task["s_sleep_ot"],  # сколько ждать после ввода
            "sleep_do": self.task["s_sleep_do"],
        }
        task = hitro_dict(task, "id_to_value")
        task = add_defaults(task, d)
        T = Bunch(task)
        logger.debug("		[%s:" % fun)

        i = 0
        for _ in T.id_to_value:
            i += 1
            logger.debug("			%s/%s %s" % (i, len(T.id_to_value), _))
            id = _.get("id", 0)
            xpath = _.get("xpath", 0)
            element = _.get("element", 0)
            js = _.get("js", "")
            keys = _.get("keys", "")

            sleep = int(
                _.get("sleep", 0)
            )  # после ввода - подождать? Или просто подождать

            tip = _.get("tip", "input")

            value = _.get("value", "")
            if type(value) == type(3) or type(value) == type(1.0):
                value = str(value)

            if type(value) == type("str"):
                value = see(value)

            text_closest = _.get("text_closest", "")
            propusk = _.get("propusk", [])
            text = _.get("text", "")

            # возможно нужно просто подождать

            if sleep != 0 and id == 0 and xpath == 0:
                sleep_(sleep)
                continue

            # элемент должен быть видимым. Ищем все, и среди них ищем видимый
            elements = []
            if id != 0:
                element = self.find_element_by_id(id)
            # elements = self.find_elements_by_id(id)
            # xpath = ".//*[@id='%s']" % id

            if xpath != 0:
                element = self.find_element_by_xpath(xpath)
            # elements = self.driver.find_elements_by_xpath(xpath)
            # find_element_by_xpath(".//input[@type='radio' and @value='SRF']").click

            t = 0
            if t:
                if elements != []:
                    visibles = []
                    for elem in elements:
                        if self.elem_is_visible(elem):
                            visibles.append(elem)
                    logger.debug(
                        '"%s %s" - found %s/%s visibles'
                        % (id, xpath, len(visibles), len(elements))
                    )
                    if len(visibles) > 0:
                        element = visibles[0]

            if not element:
                logger.error("%s error, no element" % fun)
                return 0

            t = 1
            t = 0
            if t or T.want_move_points:
                if element:
                    rectangle = self.get_element_rectangle(element)
                    x0, y0, x1, y1 = rectangle
                    window_move_points([[x0, y0], [x1, y1]])

            # выделяем красным
            t = 1
            if t and element:
                js = "arguments[0].setAttribute('style', 'border:5px solid red;')"
                self.execute_script(js, element)

            if tip == "input":
                if value != "":
                    self.send_keys(element, value)
                else:
                    logger.debug("empty value")

            elif tip == "select":
                self.select_dropdown(
                    element,
                    value=value,
                    text_closest=text_closest,
                    text=text,
                    propusk=propusk,
                )

            elif tip == "radio":
                self.driver.find_elements_by_css_selector(
                    "input[type='radio'][value='%s']" % value
                )[0].click()

            elif tip == "submit":
                element.submit()

            elif tip == "execute_js":
                logger.debug("execute_js %s" % js)
                self.execute_script(js)

            elif tip == "send_keys0":
                element.send_keys(keys)

            elif tip == "send_keys":
                ActionChains(self.driver).send_keys(keys).perform()

            elif tip == "click":
                element.click()

            elif tip == "click_js":
                logger.debug(
                    str(
                        [
                            "click_js",
                            self.elem_is_visible(element),
                            type(element),
                            element,
                        ]
                    )
                )

                # js = "arguments[0].setAttribute('style', 'border:5px solid red;')"
                # self.driver.execute_script(js, element)

                # ActionChains(self.driver).move_to_element(element).click().perform()
                # ActionChains(self.driver).move_to_element(element).double_click().perform()

                self.execute_script("arguments[0].click();", element)

            ##http://stackoverflow.com/questions/11676790/click-command-in-selenium-webdriver-does-not-work
            # element.send_keys(Keys.RETURN)
            # element.send_keys(Keys.ENTER)

            elif tip == "checkbox":
                # with javascript
                # checked = driver.execute_script(("return document.getElementById('%s').checked") % item)
                # browser.find_element_by_xpath(".//*[@id='C179003030-ORNL_DAAC-box']").get_attribute('checked')

                checked = element.is_selected()
                logger.debug("  checked: %s" % checked)

                # сначала снимаем чекбокс
                if checked and value == "check":
                    pass
                else:
                    if checked:
                        element.click()

                    # а потом если надо - ставим
                    if value == "check":
                        element.click()

            else:
                wait_for_ok('unknown tip "%s"' % tip)

            if sleep != 0:
                sleep_(sleep)

            sleep = randint(T.sleep_ot, T.sleep_do)
            sleep_(sleep)

        # seconds = 5
        # window_move_mouse_in_rectangle(x0, y0, x1, y1, seconds=seconds)

        # rand_sleep()
        logger.debug("			+%s]" % fun)
        return 1

    def double_click(self, element):
        """
        нужно было в хроме - так ничего и не сработало
        :param element:
        :return:
        """
        mode = "actionchains"
        mode = "ctrl_a"

        if mode == "actionchains":
            # create action chain object
            action = ActionChains(self.driver)
            # double click the item
            action.double_click(on_element=element).perform()
            # perform the operation
            action.perform()

        elif mode == "ctlr_a":
            action = ActionChains(self.driver)
            action.key_down(Keys.CONTROL).send_keys("a").key_up(
                Keys.CONTROL
            ).perform()

        else:
            js = """
            arguments[0].click();
            arguments[0].click();
            """
            self.execute_script(js, element)

    def js_click_all_elements(self, elements=[]):
        """
        клик по всем элементам?
        :param elements: 
        :return: 
        """
        js = """
        var items = arguments[0];
        for (var i = 0; i < items.length; i++) {
            if (1) {
                items[i].click();
            }
        }
        """
        self.execute_script(js, elements)

    def xpath_elements_with_text(
        self, xpath="//button", button_text="Place Bet", return_xpath=0
    ):
        """
			ищу элементы с текстом
				потратил час на поиск решения тут https://stackoverflow.com/questions/23078308/selenium-and-xpath-locating-a-link-by-containing-text
			например хочу все кнопки с текстом hello

			если захочу независимо от регистра:
					https://stackoverflow.com/questions/8474031/case-insensitive-xpath-contains-possible/23388974#23388974
					XPath 2.0 Solutions

					Use lower-case():

					/html/body//text()[contains(lower-case(.),'test')]
					Use matches() regex matching with its case-insensitive flag:

					/html/body//text()[matches(.,'test', 'i')]

		"""
        fun = "xpath_elements_with_text"
        logger.debug("[%s" % fun)

        #
        # xpath = '//button[contains(text(), "%s")]' % button_text	#!!!это не работает
        xpath = "//button[text()[contains(.,'%s')]]" % button_text
        if return_xpath:
            logger.debug(xpath)
            return xpath

        elements = self.driver.find_elements_by_xpath(xpath)
        logger.debug("elements with xpath %s: %s]" % (xpath, len(elements)))

        return elements

    def speed_select_and_click_existing_xpath(
        self,
        page="",
        xpath="",
        want_scroll_to_element=0,
        mode_elements="any_first_element",  # мне не надо проверять видимость 1000 элементов, чтобы кликнуть на первый видимый
        # mode_elements='all_elements',
    ):
        """
			быстро выбрали и кликнули на путь
		"""
        fun = "speed_select_and_click_existing_xpath"

        logger.debug("	[%s..." % fun)

        if page == "":
            page = self.sgp("")

        elements = self.speed_select_existing_xpath(
            page, xpath, returning="elements", mode_elements=mode_elements
        )

        logger.debug("	+%s elements" % (len(elements)))

        clicked = 0
        if elements:
            clicked = self.click_random_element(
                elements, want_scroll_to_element=want_scroll_to_element
            )
        logger.debug("	+%s]" % fun)

        return clicked

    def speed_select_existing_xpath(self, *args, **kwargs):

        """
			просто переименовать
		"""
        return self.select_existing_xpath(*args, **kwargs)

    def select_existing_xpath(
        self,
        p="",
        xpaths=[],
        check_visible=1,  # проверяем на видимость?
        returning="xpath",
        mode_elements="any_first_element",  # мне не надо проверять видимость 1000 элементов, чтобы кликнуть на первый видимый
        # mode_elements='all_elements',
        otl=0,
        # otl=1,
    ):
        """
		проверяю какой xpath видимый
			xpath1 = '//*[text()="Далее"]'
			xpath2 = '//*[text()="Next"]'
			xpaths = [xpath1, xpath2]
			xpath = self.S.select_existing_xpath()

		вывожу первый попавшийся
			returning == 'elements', #возврат элементов
			returning == 'xpath' #возврат пути

		"""

        xpaths = convert_to_list(xpaths)

        if p == "":
            p = self.sgp("")

        found = 0
        found_elements = []

        if p != False:

            for xpath in xpaths:
                elements = isXpath(p, xpath, otl=otl, otstup=1)
                if elements != []:
                    if not check_visible:
                        found = xpath
                        found_elements = elements[:]
                        break
                    else:
                        elements = self.search_elements_xpath(
                            xpath, mode_elements=mode_elements
                        )
                        if elements:
                            found = xpath
                            found_elements = elements[:]
                            break

        if returning == "elements":
            return found_elements
        else:
            return found

    def click_existing_xpaths(self, xpaths_want=[], p="", sleep_after=2):
        fun = "click_existing_xpaths"

        xpaths_want = convert_to_list(xpaths_want)

        logger.debug("[%s %s" % (fun, xpaths_want))
        cnt_clicked = 0
        for num_xpath, xpath in enumerate(xpaths_want):
            logger.debug(
                "	clicking xpath %s/%s `%s`"
                % (num_xpath + 1, len(xpaths_want), xpath)
            )

            if type(xpath) in [type(0.1), type(5)]:
                sleep_(xpath)
                continue

            xpath_exists = self.select_existing_xpath(p, xpaths=[xpath])
            if not xpath_exists:
                logger.warning("ups, no button with xpath %s" % xpath)
            else:
                logger.debug("clicking")
                # id_to_value = []

                # id_to_value.append(	{'tip':'click', 'xpath':xpath} )

                # _ = {
                # 	'id_to_value':id_to_value,
                # }
                # task_send_values = _
                # show_dict(task_send_values)
                # wait_for_ok()
                # self.send_all_values(task_send_values)

                task_send_values = []
                task_send_values.append([xpath, "click"])
                self.ssend_values(task_send_values)
                cnt_clicked += 1

                # wait_for_ok('clicked?')

                sleep_(sleep_after)

        logger.debug("%s/%s success clicks]" % (cnt_clicked, len(xpaths_want)))
        return cnt_clicked

    def xpath_explore_elements(self, xpath="//button"):
        """
			разбираюсь с атрибутами xpath
		"""
        fun = "xpath_explore_elements"
        logger.debug("[%s" % fun)

        # elements = self.driver.find_elements_by_xpath(xpath)
        elements = []
        logger.debug("elements with xpath %s: %s" % (xpath, len(elements)))

        i = 0
        for element in elements:
            i += 1
            logger.info("\n" * 2 + "-" * 10 + "%s/%s" % (i, len(elements)))
            logger.debug("text: %s" % element.text)
            attrs = self.driver.execute_script(
                """
					var items = {};
					for (index = 0; index < arguments[0].attributes.length; ++index)
						{
							items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value
						};
					return items;""",
                element,
            )
            logger.debug("	attrs:")
            show_dict(attrs, "	")

        t = 1
        t = 0
        if t:
            logger.info("WITH BUTTON:")
            button_text = "Place Bet"
            xpath = '//button[contains(text(), "%s")]' % button_text

            xpath = "//button[text()[contains(.,'%s')]]" % button_text

            elements = self.driver.find_elements_by_xpath(xpath)
            logger.debug("elements with xpath %s: %s" % (xpath, len(elements)))

        logger.debug("+")

    def get_element_css_style(self, element):
        """
        получить стиль элемента
            https://stackoverflow.com/questions/50601267/how-to-get-all-css-styles-from-a-dom-element-using-selenium-c-sharp
        """
        js = "var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) { items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; return items;"
        return self.execute_script(js, element)

    def screenshot_element(self, task={}):
        # now that we have the preliminary stuff out of the way time to get that image :D
        fun = "screenshot_element"
        d = {
            "element": "",
            "f_to": "temp/screenshot.png",
            "size_img": "",  # (x, y)
            "zsuv": "",
            # {'x':'', 'y':''} - надо например когда мы ссовываемся относительно чего-то
            "xpath_longest": "",  # самый длинный елемент
            "want_maximum_height": False,  # хочу окно на максимум?
            "mode_maximum_height": "longest_element",  # муторно - но работает
            "maximum_height": 5000,  #
            "sleep_after_maximum_height": 2,
        }
        """
        mode_maximum_height = 'get_full_page_screenshot_as_file'
        mode_maximum_height = 'body'
        mode_maximum_height = 'width_height'
        mode_maximum_height = 'longest_element'  # муторно - но работает
        """
        task = add_defaults(task, d)
        T = Bunch(task)

        driver = self.driver

        logger.debug("[%s" % fun)

        show_dict(task)

        mode_maximum_height = T.mode_maximum_height

        rash = T.f_to.split(".")[-1]
        f_temp = T.f_to.replace("." + rash, "__temp." + rash)
        logger.debug("f_temp: %s" % f_temp)

        rmfile(f_temp)

        old_size = self.get_window_size()

        want_return_to_old_size = False

        if T.want_maximum_height:

            logger.debug(
                "mode_maximum_height %s to file %s"
                % (mode_maximum_height, f_temp)
            )

            if mode_maximum_height == "body":
                # bet365 - не сработало
                element = driver.find_element_by_tag_name("body")
                element_png = element.screenshot_as_png
                with open(f_temp, "wb") as file:
                    file.write(element_png)

            elif mode_maximum_height == "width_height":
                # bet365 - не сработало
                want_return_to_old_size = True
                required_width = driver.execute_script(
                    "return document.body.parentNode.scrollWidth"
                )
                required_height = driver.execute_script(
                    "return document.body.parentNode.scrollHeight"
                )
                driver.set_window_size(required_width, required_height)
                # driver.save_screenshot(path)  # has scrollbar
                driver.find_element_by_tag_name("body").screenshot(
                    f_temp
                )  # avoids scrollbar

            elif (
                mode_maximum_height == "get_full_page_screenshot_as_file"
            ):  # тупо нет такой ф-ии
                driver.get_full_page_screenshot_as_file(f_temp)
                """
                geckodriver (Firefox)
                    If you're using geckodriver, you can hit these functions:

                    driver.get_full_page_screenshot_as_file
                    driver.save_full_page_screenshot
                    driver.get_full_page_screenshot_as_png
                    driver.get_full_page_screenshot_as_base64 
                    """

            elif mode_maximum_height == "longest_element":
                want_return_to_old_size = True
                maximum_height = T.maximum_height
                """
                можно искать самый длинный элемент:
                    @ihightower you can try getting it with driver.execute_script("return document.scrollingElement.scrollHeight;") – Hrisimir Dakov Apr 18 '20 at 7:23

                """
                xpath_longest = '//div[contains(@class, "ipe-EventViewDetail_ContentContainer")]'
                xpath_longest = T.xpath_longest
                if xpath_longest:
                    ele = self.wait_for_presence_now(xpath=xpath_longest)
                    if ele:
                        maximum_height = ele.size["height"] + 1000
                        logger.debug("found_element %s" % ele.size)
                    else:
                        logger.warning("highest element not found")

                driver.set_window_size(old_size["width"], maximum_height)
                sleep_(T.sleep_after_maximum_height)

                driver.save_screenshot(
                    f_temp
                )  # saves screenshot of entire page
            else:
                wait_for_ok(
                    "ERROR %s: unknown mode_maximum_height=%s "
                    % (fun, mode_maximum_height)
                )

        else:
            driver.save_screenshot(f_temp)  # saves screenshot of entire page

        if want_return_to_old_size:
            driver.set_window_size(old_size["width"], old_size["height"])

        t = 0
        if t:
            webbrowser.open(os.path.abspath(f_temp))
            wait_for_ok("made screenshot?")

        if not T.element:
            return

        # element = fox.find_element_by_id('hlogo') # find part of the page you want image of
        location = T.element.location
        logger.debug("location: %s" % location)
        size = T.element.size
        logger.debug("size: %s" % size)
        # fox.quit()

        im = Image.open(f_temp)  # uses PIL library to open image in memory

        left = location["x"]
        top = location["y"]
        if T.zsuv != "":
            left = T.zsuv["x"] + left
            top = T.zsuv["y"] + top

            logger.debug("new left, top: %s %s" % (left, top))

        right = left + size["width"]
        bottom = top + size["height"]

        task_crop = (left, top, right, bottom)
        logger.debug("task_crop: %s" % task_crop)
        im = im.crop(task_crop)  # defines crop points
        logger.debug("+")

        if T.size_img != "":
            logger.debug("resizing %s" % T.size_img)
            # im.thumbnail(T.size_img, Image.ANTIALIAS)
            im.resize(T.size_img, Image.ANTIALIAS)

        im.save(T.f_to)  # saves new cropped image

        if os.path.isfile(T.f_to):
            status = 1
        else:
            status = 0
        logger.debug("%s %s]" % (fun, status))
        return status

    def hover_xpath(
        self, xpath="", element=None, seconds_highlight=1, mode="", style=""
    ):
        if not element:
            element = self.find_element_by_xpath(xpath)
        self.hover_element(
            element,
            seconds_highlight=seconds_highlight,
            mode=mode,
            style=style,
        )

    def hover_element(self, element, seconds_highlight=1, mode="", style=""):
        fun = "hover_element"
        if not element:
            logger.debug("no element")
            return

        if mode == "":
            mode = "scroll_to_element"

        # self.element_scroll(element)
        self.highlight(element, seconds_highlight, style=style)

        if mode == "move_to_element":
            self.move_to_element(element)

        elif mode == "scroll_to_element":
            self.scroll_to_element(element)

        else:
            logger.error("ERROR %s unknown mode=%s" % (fun, mode))

    def move_to_element(self, element):
        """
        используй scroll_to_element
        иногда глючит 
            Message: (184, 649) is out of bounds of viewport width (1010) and height (625)
        :param element:
        :return:
        """
        fun = "move_to_element"
        hover = ActionChains(self.driver).move_to_element(element)
        try:
            hover.perform()
        except Exception as er:
            logger.error("ERROR %s - %s" % (fun, er))

    def scroll_to_element(self, element, scroll_to="center"):
        """
        прокрутка к центру - рулит!
            https://stackoverflow.com/questions/24665602/scrollintoview-scrolls-just-too-far
        
        еще так можно попробовать:
            Get correct y coordinate and use window.scrollTo({top: y, behavior: 'smooth'})
            const id = 'profilePhoto';
            const yOffset = -10; 
            const element = document.getElementById(id);
            const y = element.getBoundingClientRect().top + window.pageYOffset + yOffset;

            window.scrollTo({top: y, behavior: 'smooth'});

        https://github.com/mozilla/geckodriver/issues/776#issuecomment-330362624
        """
        if scroll_to == "center":
            js = 'arguments[0].scrollIntoView({ behavior: "smooth", block: "center" });'
            js = 'arguments[0].scrollIntoView({ block: "center" });'

        elif scroll_to == "start":
            # от верху - element.scrollIntoView({ behavior: 'smooth', block: 'start' });
            js = 'arguments[0].scrollIntoView({ block: "start" });'

        elif scroll_to == "end":
            js = 'arguments[0].scrollIntoView({ block: "end" });'

        else:
            js = "arguments[0].scrollIntoView(true);"
        self.driver.execute_script(js, element)

    def emulate_mouse_move(self, element=None):

        if not element:
            element = self.find_element_by_xpath("//body")
        # logger.debug(f"{element=}")
        # element.send_keys(Keys.CONTROL + Keys.SHIFT + "M")

        # r = S.scroll_to_element(element, scroll_to="top")
        # sleep_(1)
        # r = S.scroll_to_element(element, scroll_to="center")
        # logger.debug(f"scroll_to_element {r=}")

        driver = self.driver

        t = 0
        if t:
            action = webdriver.common.action_chains.ActionChains(driver)
            action.move_to_element(element)
            action.perform()
            action.move_by_offset(10, 20)  # 10px to the right, 20px to bottom
            action.move_by_offset(
                100, 200
            )  # 10px to the right, 20px to bottom
            clicked = action.perform()
            logger.debug(f"{clicked=}")

        clicked = self.click_on_xpath_with_position()
        logger.debug(f"{clicked=}")

    def delete_element(self, element):
        # удаляем элемент
        fun = "delete_element"
        javascript = """
		var element = arguments[0];
		element.parentNode.removeChild(element);
		"""
        try:
            self.driver.execute_script(javascript, element)
            return 1
        except Exception as er:
            logger.error("%s ERROR: %s" % (fun, er))
            return 0

    def get_special_windowhandles(
        self, url="https://www.allbestbets.com/valuebets/live"
    ):
        """Нахожу специальные окна"""
        fun = "get_special_windowhandles"
        logger.debug("[%s: url=%s" % (fun, url))
        driver = self.driver
        current_handle = driver.current_window_handle

        handles = driver.window_handles
        filtered = []
        # current_name = driver.execute_script('return window.name')
        # logger.debug('current_handle %s, current_name=%s' % (current_handle, current_name))
        logger.debug(
            " current_handle%s, have %s handles: %s "
            % (current_handle, len(handles), handles)
        )

        for num, handle in enumerate(handles, 1):
            # handle = driver.window_handles[1]
            logger.debug(" handle %s/%s %s" % (num, len(handles), handle))
            # driver.switch_to_window(handle)
            self.switch_to_window(handle)
            url_current = driver.current_url
            logger.debug("url=%s" % url_current)

            if url_current in [
                url,
                "%s#" % url,
            ]:  # google.com/ or google.com/#
                filtered.append(handle)

        self.switch_to_window(current_handle)
        logger.debug("+%s]" % filtered)
        return filtered

    def switch_to_window(self, handle=""):
        driver = self.driver
        try:
            driver.switch_to.window(handle)
        except Exception as er:
            logger.error("error %s" % er)
            return None

    def get_windows_handles(self):
        # получаем все окна
        # работа с дочерними окнами, объяснение:
        # 	http://seleniumtutorialpoint.com/2015/02/how-to-handle-child-browser-pop-up-in-selenium-webdriver/
        # driver.switch_to.window(signin_window_handle)
        fun = "get_windows_handles"
        driver = self.driver
        main_window_handle = None
        while not main_window_handle:
            main_window_handle = driver.current_window_handle

        more_windows = []
        for handle in driver.window_handles:
            if handle != main_window_handle:
                more_windows.append(handle)

        self.main_window_handel = main_window_handle
        logger.debug("[%s - found %s more windows]" % (fun, len(more_windows)))
        return main_window_handle, more_windows

    def refresh(self):
        fun = "refresh"
        logger.debug("[%s" % fun)
        driver = self.driver
        # driver.currentUrl = 'https://sede.administracionespublicas.gob.es/icpco/acCitar?[random]'.replace('[random]', str(randint(1, 1000)))
        driver.refresh()

        # после ф5 просит подтвердить отправку инфы - подтверждаю
        sleep_(0.5)
        self.accept_alert()
        logger.debug("+%s]" % fun)

    def wait_while_page_is_loading(
        self, max_wait=60, seconds_sleep=0.2, otl=1
    ):
        """
		Ждем пока страница не загрузится
		"""
        fun = "wait_while_page_is_loading"
        t_start = time.time()
        step = 0
        while True:
            step += 1
            seconds = time.time() - t_start

            if seconds > max_wait:
                if otl:
                    logger.error(
                        "%s ERROR: not loaded in %.2f seconds" % (fun, seconds)
                    )
                return False

            if self.page_has_loaded():
                if otl:
                    logger.debug(
                        "loaded in %.2f seconds and %s steps" % (seconds, step)
                    )

                return True
            else:
                sleep_(seconds_sleep, fun="wait_while_page_is_loading_")

    def page_has_loaded(self, otl=1):
        """
		Проверка - загрузилась страница уже?
			https://stackoverflow.com/questions/26566799/wait-until-page-is-loaded-with-selenium-webdriver-for-python
		"""
        if otl:
            logger.debug(
                "		Checking if %s page is loaded..." % self.driver.current_url
            )

        page_state = self.driver.execute_script("return document.readyState;")
        res = page_state == "complete"

        if otl:
            logger.debug("`%s`" % page_state)

        return res

    def accept_alert(self):
        """
		refresh page and get alert - accept it
		https://stackoverflow.com/questions/8714659/selenium-refresh-page-and-resend-data
		:return:
		"""
        try:
            self.driver.switch_to.alert.accept()
        except Exception as er:
            print("ERROR accept_alert: %s" % er)

    # or, executing JavaScript
    # driver.execute_script("location.reload()")

    def sgp_long(
        self,
        u,
        f="temp/sgp_long.html",
        phrases=[],
        cnt=10,
        otl=1,
        recheck_sleep=0.1,
        phrases_bad=[],
        sleep_after_bad=0,
        ignore_bad=0,
        seconds_sleep=2,
    ):
        """
			качаем страницу, и ищем фразы на ней
		"""
        fun = "sgp_long"

        if otl:
            logger.debug("		[%s" % fun)

        if type(phrases) == type("str"):
            phrases = [phrases]

        if type(phrases_bad) == type("str"):
            phrases_bad = [phrases_bad]

        # проверяем долгое открытие
        i = 0
        while True:
            i += 1
            if i > cnt:
                return False, p

            if i == 1:
                if otl:
                    logger.debug("	phrases: %s" % phrases)

            if i > 1:
                u = ""
                # logger.debug('sleep %s' % sleep)
                sleep_(recheck_sleep)

            p = self.sgp(u, f, seconds_sleep=seconds_sleep)
            if p == False:
                logger.error("error %s: %s/%s, page==False" % (fun, i, cnt))
                continue

            found_bad = 0
            for phrase in phrases_bad:
                if p.find(phrase) != -1:
                    found_bad = 1
                    if otl:
                        logger.debug(
                            "			%s - found phrase_bad %s" % (fun, phrase)
                        )
            if found_bad:
                sleep_(sleep_after_bad)
                if ignore_bad:
                    i = i - 1
                continue

            # wait_for_ok()

            if phrases == []:
                return True, p

            for phrase in phrases:
                # logger.debug(f"{type(p)=} {type(phrase)=}")
                if p.find(phrase) != -1:
                    if otl:
                        logger.debug(
                            "			%s - found phrase %s]" % (fun, phrase)
                        )
                    # break
                    return True, p

            logger.debug("		%s_retry_%s/%s" % (fun, i, cnt))

        # wait_for_ok()
        # if i==1:
        # 	logger.debug('		phrases %s' % phrases)
        # wait_for_ok()

    def click_while_exists(self, xpath="", sleep=3):
        # xpath = '//span[text()="%s"]' % 'Confirm'
        step = 0
        while True:
            step += 1
            logger.debug("step_%s" % step)
            try:
                elem = self.driver.find_element_by_xpath(xpath)
                elem.click()
                sleep_(sleep)
            # rand_sleep()
            except Exception as er:
                try:
                    logger.debug(
                        "click_while_exists: ups, xpath `%s` not found. Er: `%s`"
                        % (xpath, er)
                    )
                except Exception as er2:
                    logger.debug(
                        "click_while_exists: ups, xpath not found. Er: `%s` `%s`"
                        % (er, er2)
                    )

                break

    def ssend_values_quick(self, sending=[], task={}, sleep=0):
        """Иногда надо максимально быстро все делать, не эмулируя человека - вот оно"""
        return self.ssend_values(sending=sending, task=task, sleep=sleep)

    def ssend_values(self, sending=[], task={}, sleep=None):
        fun = "ssend_values"
        # logger.debug('%s sleep=%s' % (fun, sleep))

        d = {
            "sleep_after_send": 2,
        }
        task = add_defaults(task, d)
        T = Bunch(task)

        t_start = time.time()

        # sending = T.sending
        if sleep is not None or sleep == 0:
            sleep_after_send = sleep
        else:
            sleep_after_send = T.sleep_after_send
        # logger.debug('sleep_after_send=%s' % sleep_after_send)

        t = []
        if type(sending) == type({}):
            for k in sending:
                v = sending[k]
                t.append([k, v])
            # sending = list(sending)
            sending = t[:]

        t = 1
        t = 0
        if t:
            logger.debug("[%s" % fun)
            logger.debug("task:")
            show_dict(task)

            logger.debug("sending: %s" % sending)
            show_list(sending)

            wait_for_ok(fun)

        #'selenium send values'
        all_is_clicked = 1  # все кликнули что должны были?
        super_name = False
        num = 0
        for t in sending:
            # tip = False
            num += 1
            if num > 1:
                logger.debug("sleep_after_send %s" % sleep_after_send)
                sleep_(sleep_after_send)

            is_element = check_is_selenium_element(t)

            try:
                ln = len(t)
            except Exception as er:
                ln = -1
            ##logger.debug('%s' % isinstance(t, WebElement))
            if (
                is_element
            ):  # если указали один елемент - мы на него просто кликаем
                try:
                    t.click()
                except Exception as er:
                    logger.error("ERROR WITH ELEMENT %s" % er)
                    all_is_clicked = 0
                    continue
                rand_sleep()
                super_name = True

            elif ln == 2:
                k, v = t
                # v = sending[k]

                ##тут что за супер-нейм?
                # if v==-555:
                # 	super_name = v
                # 	#continue

                elem = None
                j = 0
                while True:
                    j += 1
                    logger.debug("	%s step %s, searching %s..." % (fun, j, k))
                    if j > 1:
                        sleep_(3)

                    if j > 2:
                        break

                    is_element = check_is_selenium_element(k)
                    if is_element:
                        elem = k
                        break

                    elif k is None:
                        elem = None

                    elif k.find(r"//") != -1:
                        logger.debug("	key is xpath %s" % k)

                        # могу вводить номер елемента!
                        # 'search_button': "//input[@name='btnK'] #number=1|",
                        number = find_from_to_one("#number=", "|", k)
                        if number == "":
                            number = 0
                        else:
                            k = find_from_to_one("nahposhuk", "#number=", k)
                            print(
                                "	real xpath=%s, but number=%s" % (k, number)
                            )

                        try:
                            ##Находит первый любой - может быть некликабельный
                            # elem = self.driver.find_element_by_xpath(k)

                            # нужно найти один видимый кликабельный елемент
                            elem = self.search_element_xpath(
                                k, element_number=number
                            )
                            logger.debug(
                                "  found element %s from xpath %s" % (elem, k)
                            )

                            break
                        except Exception as er:
                            logger.error("er_id: %s" % er)
                    else:

                        try:
                            elem = self.find_element_by_id(k)
                            break
                        except Exception as er:
                            logger.error("er_id: %s" % er)
                        # time.sleep(2)
                        # continue

                        try:
                            elem = self.find_element_by_name(k)
                            break
                        except Exception as er:
                            logger.error("er_name: %s" % er)
                            time.sleep(2)
                            continue

                if elem is None:
                    all_is_clicked = 0
                    continue

                if elem is False:
                    logger.error("    error, no element")
                    all_is_clicked = 0
                    continue

                logger.debug("   action `%s`" % (v))

                if v in [-1111, -555, "click", "_CLICK"]:
                    logger.debug("     click on %s" % elem)
                    try:
                        elem.click()
                    except Exception as er:
                        try:
                            logger.error("error %s" % er)
                        except Exception as er:
                            logger.error("error click %s" % er)
                        all_is_clicked = 0
                        continue

                elif v in ["click_js"]:
                    self.execute_script("arguments[0].click();", elem)

                elif v in ["double_click"]:
                    self.double_click(elem)

                elif v == "_HIGHLIGHT_FOREVER":
                    self.highlight_forever(elem)

                elif v == "_HIGHLIGHT" or (
                    isinstance(v, str) and v.startswith("_HIGHLIGHT ")
                ):
                    seconds = find_from_to_one(
                        "_HIGHLIGHT", "nahposhuk", v
                    ).strip()
                    if seconds == "-1":
                        seconds = -1
                    elif seconds:
                        seconds = float(seconds)
                    else:
                        seconds = 1

                    self.highlight(elem, seconds)

                elif v in ["_HOVER"]:
                    self.hover_element(elem)

                elif v in ["_SCROLL"]:
                    self.element_scroll(elem)

                elif v != -1111:  # check button
                    logger.debug("     sending %s %s..." % (type(v), v))
                    sent_data = 0
                    j = 0
                    while True:
                        j += 1
                        if j > 3:
                            # return i%0
                            return False

                        want_try = 0
                        want_try = 1
                        if want_try:
                            try:
                                # if 1:
                                if v in ["enter"]:
                                    logger.debug("send_keys enter")
                                    # elem.send_keys(Keys.RETURN)
                                    # elem.send_keys(Keys.ENTER)
                                    elem.submit()

                                else:
                                    self.clear_element(elem)
                                    elem.send_keys(v)
                                    # rand_sleep(sleep)
                                logger.debug("+")
                                if v == "test":
                                    wait_for_ok("entered test?")
                                sent_data = 1
                                break
                            except Exception as er:
                                # else:
                                try:
                                    logger.error("error=%s" % er)
                                except Exception as er:
                                    logger.error("error click %s" % er)
                                time.sleep(10)
                                continue

                        else:
                            if v in ["enter"]:
                                logger.debug("send_keys enter")
                                # elem.send_keys(Keys.RETURN)
                                # elem.send_keys(Keys.ENTER)
                                elem.submit()

                            else:
                                self.clear_element(elem)
                                elem.send_keys(v)
                                rand_sleep()
                            logger.debug("+")
                            if v == "test":
                                wait_for_ok("entered test?")
                            sent_data = 1
                            break

                    if not sent_data:
                        all_is_clicked = 0

                else:
                    wait_for_ok("unknown v %s" % v)

        duration = time.time() - t_start
        logger.debug("%s done in %.2f seconds" % (fun, duration))
        return all_is_clicked

    def clear_element_with_backspaces(self, element, key=None, cnt=4):
        """
        почистили элемент бекспейсом
        """
        if key is None:
            key = Keys.BACKSPACE
        return self.send_keys_to_element(element, key=key, cnt=cnt)

    def clear_element(self, element):
        fun = "clear_element"
        try:
            element.clear()
        except Exception as er:
            logger.error("        ERROR %s: %s" % (fun, er))

    def send_keys_to_element(self, element, key=None, cnt=3):

        # отправляю несколько команд одновременно
        if key is None:
            key = Keys.BACKSPACE
        sequence = [key] * cnt
        return element.send_keys(*sequence)

        return

        logger.debug(
            "send_keys_to_element: element=%s, key=%s" % (element, key)
        )
        for i in range(cnt):
            element.send_keys(key)

    def get_element_rectangle(self, element):
        # получаем "прямоугольник" елемента
        fun = "get_element_rectangle"
        location = element.location
        size = element.size

        # print(location)
        # print(size)

        x = location["x"]
        y = location["y"]
        # {'y': 202, 'x': 165}
        # {'width': 77, 'height': 22}
        rectangle = [x, y, x + size["width"], y + size["height"]]
        logger.debug("[%s %s]" % (fun, rectangle))
        return rectangle

    def good_exit(self, seconds=3, real_exit=0, kill_pid=0):
        fun = "good_exit"

        logger.debug("[%s" % fun)

        # wait_for_ok('good exit?')

        t = 0
        t = 1
        if t and kill_pid:

            pid = self.task.get("selenium_pid", -1)
            if pid != -1:
                kill_with_id(pid)
                rmfile(self.f_pid(pid))
                self.task["selenium_pid"] = -1

            try:
                pid = self.get_selenium_pid()
                kill_with_id(pid)
            except Exception as er:
                logger.error("%s ERROR %s" % (fun, er))

        # wait_for_ok('killed with selenium_pid ?')

        self.selenium_stop()
        sleep_(seconds)

        # if real_exit:

        # 	t = 0
        # 	if t:
        # 		f_settings = settings_args.get('f_settings', '')
        # 		if os.path.isfile(f_settings):
        # 			restart_with_the_same_settings()

        # 	#wait_for_ok('%s done?'%fun)
        # 	os._exit(0)

        logger.debug("+]")

    def explore_iframes(self, task={}):
        fun = "explore_iframes"
        d = {
            "switch_to_default_content": 0,
        }
        task = add_defaults(task, d)
        T = Bunch(task)
        logger.debug("[%s" % fun)
        d_log = os.path.join("log", fun)

        if T.switch_to_default_content:
            self.driver.switch_to_default_content()

        elems = self.driver.find_elements_by_tag_name("iframe")
        logger.debug("have %d elems" % len(elems))
        for ifr in range(len(elems)):
            p = sgp()
            f_temp1 = os.path.join(d_log, "f_parent_%d.html" % ifr)

            text_to_file(p, f_temp1)

            elem = elems[ifr]
            src = elem.get_attribute("src")
            logger.debug("	iframe%d, src %s" % (ifr, src))
            p = sgp()
            f_ifr = os.path.join(d_log, "f_ifr_%d.html" % ifr)

            text_to_file(p, f_ifr)

            if T.switch_to_default_content:
                self.driver.switch_to_frame(elem)
        # wait_for_ok('check all iframes')
        logger.debug("+]")

    def elem_is_visible(self, elem, debug=False):
        fun = "elem_is_visible"
        t1 = 0
        t2 = 0
        try:
            t1 = elem.is_displayed()
            t2 = elem.is_enabled()
        except Exception as er:
            logger.error("error %s: %s for element %s" % (fun, er, elem))
        if t1 and t2:
            status = 1
        else:
            status = 0
        log = "	    elem_is_visible: %s (is_displayed: %s, is_enabled: %s)" % (
            status,
            t1,
            t2,
        )
        logger.debug(log)
        return status

    def not_found_search_element(self, elem):
        """check if search_element has found element"""
        if type(elem) == type(False) and elem == False:
            return True
        return False

    def click_random_element_xpath(self, xpath="", want_scroll_to_element=1):
        fun = "click_random_element_xpath"
        logger.debug("[%s" % fun)
        clicked = False

        element = self.search_random_element_xpath(xpath)
        if element != False:
            clicked = self.click_random_element(elements)
        logger.debug("+%s]" % (fun))

        return clicked

    def click_random_element(self, elements=[], want_scroll_to_element=1):
        fun = "click_random_element"
        logger.debug("[%s" % fun)
        clicked = False

        if len(elements) == 0:
            pass
        else:
            element = random_element(elements)

            self.highlight(element, 1)

            if want_scroll_to_element:
                self.element_scroll(element)
                sleep_(1)

                self.highlight(element, 1)

            posting = [
                [element, "click"],
            ]

            clicked = self.ssend_values(posting)

        logger.debug("+clicked=%s %s]" % (clicked, fun))
        return clicked

    def search_random_element_xpath(
        self, xpath="", only_visible=1, max_cnt_elements=1000
    ):
        fun = "search_random_element_xpath"
        element = False
        elements = self.search_elements_xpath(
            xpath=xpath,
            only_visible=only_visible,
            max_cnt_elements=max_cnt_elements,
        )
        if elements != []:
            shuffle(elements)
            element = elements[0]
            logger.debug(
                "[%s - found %s elements for xpath `%s`, selected random %s]"
                % (fun, len(elements), xpath, element)
            )
        return element

    def search_elements_xpath(
        self,
        xpath="",
        only_visible=1,
        max_cnt_elements=1000,
        # mode_elements='any_first_element',	#мне не надо проверять видимость 1000 элементов, чтобы кликнуть на первый видимый
        mode_elements="all_elements",
        elems=None,
        debug=False,
        # debug = True,
    ):
        # ищем елементы все по xpath
        # очень часто надо только 1 видимый элемент и мы с ним работаем (не надо все) - тогда например max_cnt_elements=1
        fun = "search_elements_xpath"
        logger.debug(
            "		[%s `%s` mode_elements=%s" % (fun, xpath, mode_elements)
        )
        if elems is None:
            elems = self.driver.find_elements_by_xpath(xpath)

        logger.debug("  found %s elements for xpath=%s" % (len(elems), xpath))

        # оставляем только видимые елементы
        if only_visible:
            if mode_elements == "any_first_element":
                max_cnt_elements = 1
                shuffle(elems)

            visibles = []
            i = 0
            for elem in elems:
                i += 1

                if len(visibles) >= max_cnt_elements:
                    logger.debug(
                        "	need only %s elements (total %s), so enough"
                        % (max_cnt_elements, len(elems))
                    )
                    break

                logger.debug("	check visibility %s/%s..." % (i, len(elems)))
                is_visible = self.elem_is_visible(elem)
                logger.debug("          is_visible=%s" % is_visible)
                if is_visible:
                    visibles.append(elem)

            logger.debug("  %s/%s visible" % (len(visibles), len(elems)))

            elems = visibles[:]

        logger.debug("  %s elements]" % len(elems))
        return elems

    def search_element_xpath(
        self, xpath="", only_visible=1, no_wait=0, element_number=0, debug=True
    ):
        # ищем елемент по xpath no_wait - значит не ждем
        fun = "search_element_xpath"

        if no_wait:
            self.setup_wait()

        elems = self.search_elements_xpath(xpath, only_visible)

        rez = False
        if len(elems) == 0:
            rez = False

        else:
            if element_number <= len(elems):
                el_number = element_number
            else:
                el_number = 0

            rez = elems[el_number]

            if len(elems) > 1:
                if debug:
                    logger.debug(
                        '%s - found %s elems for xpath "%s", but get number %s'
                        % (fun, len(elems), xpath, element_number)
                    )

        if no_wait:
            self.setup_wait("default")

        return rez

    def all_xpaths_are_visible(self, xpaths=[]):
        good = 1
        for xpath in xpaths:
            if not self.xpath_is_visible(xpath):
                good = 0
                break
        return good

    def xpath_is_visible(self, xpath=""):
        logger.debug("check visibility...")
        element = self.search_element_xpath(xpath, no_wait=1)
        if element != False:
            return 1
        else:
            return 0

    def clear_like_human(self, element):
        """
			в реальности человек чистит так: выделили все, подождали (может не успеть выделиться все, а только часть), и потому нажали "удалить"
		"""
        element.send_keys(Keys.CONTROL, "a")
        time.sleep(1)
        element.send_keys(Keys.DELETE)

        # если вдруг и за секунду не очистилось - подстраховываемся
        element.clear()

    def sel_send_keys_like_human(
        self, elem, value, sleep=0.3, want_clear=True
    ):
        fun = "sel_send_keys_like_human"
        if want_clear:
            try:
                elem.clear()
                # self.clear_element_with_backspaces(elem, cnt=1)
            except Exception as er:
                logger.error("ERROR %s: er %s" % (fun, er))
                pass

        for i in range(len(value)):
            v = value[i]
            elem.send_keys(v)
            sleep_(sleep)

    def search_element(self, task={}):
        """searching element"""
        fun = "search_element"
        d = {
            "name": "",
            "attr": "",
            "searching": "recaptcha",
            "first": 1,  # возвращать первый? Иначе список
        }
        task = add_defaults(task, d)
        T = Bunch(task)

        logger.debug("[%s %s" % (fun, task))
        elems = self.driver.find_elements_by_tag_name(T.name)
        logger.debug("  have %s %s elements" % (T.name, len(elems)))
        found = []
        for ifr in range(len(elems)):
            elem = elems[ifr]
            src = ""
            if T.attr != "":
                src = elem.get_attribute(T.attr)
            # logger.debug('	num_%s, attr=%s' % (ifr, src))
            if src.find(T.searching) != -1 or T.searching == "":
                logger.debug("	+found")  # , src
                if T.first:
                    return elem
                else:
                    found.append(elem)

        if T.first:
            logger.warning("-no_found!]")
            return False

        return found

    def search_elements(self, task={}):
        # ищем все элементы
        d = {
            "first": 0,
        }
        t = add_defaults(task, d)
        return self.search_element(t)

    def select_dropdown(
        self, elem, value="", text="", text_closest="", propusk=[]
    ):
        # ищем или по :
        # value
        # text
        # text_closest - самый похожий по написанию текст

        # S.driver.find_element_by_xpath("//select[@name='element_name']/option[text()='option_text']").click()
        # element = self.find_element_by_name(name)
        # driver.find_element_by_id('fruits01')

        if type(propusk) != type([]):
            propusk = [propusk]

        propusk_unicode = []
        for p in propusk:
            if type(p) == type("str"):
                p = see(p)
            propusk_unicode.append(p)
        propusk = propusk_unicode[:]
        logger.debug("propusk: %s" % propusk)

        value = str(value)
        text = str(text)
        select = Select(elem)
        if value != "":
            # select by value
            select.select_by_value(value)
        elif text != "":
            # select by visible text
            select.select_by_visible_text(text)

        elif text_closest != "":
            # https://sqa.stackexchange.com/questions/1355/what-is-the-correct-way-to-select-an-option-using-seleniums-python-webdriver
            logger.debug(0)
            texts = [o.text for o in select.options]  # these are string-s
            # texts = list_minus_list(texts, propusk)
            logger.debug(1)
            texts = [_.encode("utf8", "delete") for _ in texts]
            logger.debug(2)
            texts = list_minus_list(texts, propusk)
            logger.debug(3)
            try:
                uni("searching text_closest for")
                uni(text_closest)
            except Exception as er:
                logger.error("error %s" % er)
            logger.debug(4)
            logger.debug("texts=%s" % texts)
            # ищем самый похожий текст
            logger.debug(5)
            closest = select_closest_phrase(text_closest, texts, 1)
            select.select_by_visible_text(closest)
            try:
                logger.debug("found closest: %s" % closest)
            except Exception as er:
                logger.error("error=%s" % er)
        # wait_for_ok()

    def get_value_by_id(self, id):
        # по айдишнику получаем значение поля
        element = self.find_element_by_id(id)
        return get_attribute(element, "value")
        return value

    def get_attribute(self, element, attribute="href"):
        # по айдишнику получаем значение поля
        value = element.get_attribute(attribute)
        return value

    def find_element_by_name(self, name=""):
        element = self.driver.find_element_by_name(name)
        return element

    def find_element_by_id(self, id=""):
        element = self.driver.find_element_by_id(id)
        return element

    # def find_html_by_xpath(self, xpath=''):
    #     WebElement
    #     element = driver.findElement(By.id("foo"));
    #     String
    #     contents = (String)((JavascriptExecutor)
    #     driver).executeScript("return arguments[0].innerHTML;", element);

    def wait_for_first_existing_situation(
        self, situation_to_xpath=[], timeout=20, debug=False
    ):
        """
        на вход 
        [
            ["markets_loaded", xpath],
            ["game_not_actual", xpath]
        ]
        дожидаемся появления хоть одного элемента
        """
        fun = "wait_for_first_existing_situation"
        if isinstance(situation_to_xpath, dict):
            situation_to_xpath = [
                [k, v] for k, v in situation_to_xpath.items()
            ]

        debug = True
        t_start = time.time()

        if not situation_to_xpath:
            return api_success("no elements to search")

        logger.debug(f"[{fun} {timeout=} {situation_to_xpath=}")

        if debug:
            logger.debug(f"wait any of {len(situation_to_xpath)} elements:")
            show_list(situation_to_xpath)

        xpaths = [_[-1] for _ in situation_to_xpath]
        joined_xpath = " | ".join(["(%s)" % _ for _ in xpaths])
        element = self.wait_for_presence(
            xpath=joined_xpath, timeout=timeout, checking="presence"
        )
        logger.debug(f"final {element=}" % (fun, element))
        if not element:
            return api_error("no_elements")

        if debug:
            logger.debug(" found from joined_xpath element %s" % element)

        xpaths_to_download = [[_, "outer"] for _ in xpaths]
        # elements = self.S.js_get_elements_from_xpaths(xpaths_to_download)
        elements = self.js_find_elements_by_xpaths(
            xpaths_to_download, with_empty=True
        )

        duration = time.time() - t_start
        if debug:
            # logger.debug(' %s elements: %s' % (len(elements), elements))
            logger.debug(" %s elements:" % (len(elements)))
            for element in elements:
                logger.debug("    ")
                try:
                    logger.debug("%s ..." % element[:100])
                except Exception as er:
                    try:
                        logger.debug("      element=%s" % element)
                    except Exception as er:
                        logger.debug("ERROR printing element")

        situations = []
        for num_element, element in enumerate(elements):
            possible_situation = situation_to_xpath[num_element][0]
            if element is not None:
                situations.append([possible_situation, element])

        logger.debug(
            "%s possible situations: %s"
            % (len(situations), plist(situations, limit=200))
        )

        logger.debug("%s +%.3f seconds]" % (fun, duration))
        return api_success(situations=situations)

    def js_getElementByXPath(self, xpath=""):
        elements = self.js_getElementsByXPath(xpath)
        if elements:
            return elements[0]
        else:
            return False

    def js_getElementsByXPath(self, xpath=""):
        fun = "js_getElementsByXPath"
        debug = True
        debug = False

        logger.debug("     [%s xpath=`%s`" % (fun, xpath))
        started = time.time()
        js = self.get_javascript_getElementsByXPath(xpath)
        elements = self.execute_script(js)
        # logger.debug(str([type(elements), elements]))

        if debug:
            print(elements)
            show_list(elements)
            # wait_for_ok()

        seconds = time.time() - started
        logger.debug(
            "  +%s elements in %.3f seconds]" % (len(elements), seconds)
        )
        return elements

    def js_find_elements_by_xpaths(
        self,
        xpaths=[],
        mode="element",
        check_visibility=False,
        with_empty=False,
        debug=False,
    ):
        """получить несколько элементов через xpath"""
        fun = "js_find_elements_by_xpaths"
        debug = True
        debug = False

        xpaths_with_mode = self.get_xpath_mode_list(xpaths, mode=mode)
        logger.debug(
            "     [%s %s xpaths=`%s`"
            % (fun, len(xpaths_with_mode), xpaths_with_mode)
        )
        started = time.time()
        js = self.get_javascript_for_xpaths_with_modes(
            xpaths_with_mode,
            check_visibility=check_visibility,
            with_empty=with_empty,
        )
        # print(js)
        # wait_for_ok()

        elements = self.execute_script(js)
        if elements is None:
            logger.error("elements=%s, but must be list" % elements)
            elements = []
        logger.debug("type %s, elements %s" % (type(elements), elements))
        # wait_for_ok()

        if debug:
            print(elements)
            show_list(elements)
            # wait_for_ok()

        seconds = time.time() - started
        try:
            info_elements = len(elements)
        except Exception as er:
            info_elements = elements
        logger.debug(
            "+%s elements in %.3f seconds]" % (info_elements, seconds)
        )
        return elements

    def linfo(self, message="", **kwargs):
        self.log(message, level="info", **kwargs)

    def ldebug(self, message="", **kwargs):
        self.log(message, level="debug", **kwargs)

    def log(
        self,
        message="",
        level="",
        end="",
        duration=0,
        max_duration=1,
        fun="",
        **kwargs,
    ):
        level_to_number = {
            "debug": 3,
            "info": 2,
            "warning": 1,
            "error": 0,
            "critical": -1,
        }

        default_num = 10
        max_level = self.minimum_debug_level
        num_max_level = level_to_number.get(max_level, default_num)  # info==2
        num_level = level_to_number.get(level, default_num)  # debug==3
        # logger.debug('max_level=%s=%s, level=%s=%s' % (max_level, num_max_level, level, num_level))

        duration_info = ""
        if duration > max_duration:
            duration_info = "       log: %s is long: %.2f seconds" % (
                fun,
                duration,
            )
            logger.debug(duration_info)

        elif num_level > num_max_level:  #
            return

        otstup = ""
        if level == "debug":
            otstup = "    "

        if 1:
            logger.debug("%s %s %s" % (otstup, message, duration_info))

        elif end == ",":
            print(otstup, message, duration_info)

        else:
            print(otstup, message, duration_info)

    def js_find_element_by_xpath(self, xpath="", mode="element", debug=False):
        """https://developer.mozilla.org/en-US/docs/Web/XPath/Introduction_to_using_XPath_in_JavaScript"""
        fun = "js_find_element_by_xpath"

        logger.debug("     [%s mode=%s xpath=`%s`" % (fun, mode, xpath))
        started = time.time()
        js = self.get_javascript_for_xpath(xpath, mode)
        if debug:
            logger.debug("     js=%s" % js)
        element = self.execute_script(js)
        seconds = time.time() - started
        logger.debug("  +%.3f seconds]" % (seconds))
        return element

    def get_javascript_getElementsByXPath(self, xpath=""):
        debug = False

        js_code = self.get_saved_js_code_to_parse_elements()

        xpath_prepared = self.prepare_text_for_javasript(xpath)

        # js_code = ''
        js = """
%s
var xpath = '%s';
return getElementsByXPath(xpath);
        """ % (
            js_code,
            xpath_prepared,
        )

        if debug:
            logger.debug("final_js: %s" % js)
            # wait_for_ok(fun)
        return js

    def get_javascript_for_xpaths_with_modes(
        self, xpaths_with_mode=[], check_visibility=False, with_empty=False
    ):
        fun = "get_javascript_for_xpaths_with_modes"
        debug = True
        debug = False

        js_code = self.get_saved_js_code_to_parse_elements()

        all_js = []
        for xpath, mode in xpaths_with_mode:
            # js = self.get_javascript_for_xpath(xpath, mode, with_return=False)
            xpath_prepared = self.prepare_text_for_javasript(xpath)
            all_js.append("['%s', '%s']" % (xpath_prepared, mode))

        all_js = ", ".join(all_js)

        # js_code = ''
        if check_visibility:
            want_check_visibility = "true"
        else:
            want_check_visibility = "false"

        if with_empty:
            want_with_empty = "true"
        else:
            want_with_empty = "false"

        js = """
%s
var xpaths_with_modes = [%s];
return getElementsByXPaths_with_modes(xpaths_with_modes, %s, %s);
        """ % (
            js_code,
            all_js,
            want_check_visibility,
            want_with_empty,
        )

        if debug:
            logger.debug("final_js: " % js)
            wait_for_ok(fun)
        return js

    def get_saved_js_code_to_parse_elements(self):
        try:
            js_code = self.js_code_parse_bet365
        except Exception as er:
            f_js = "%s/data/parse_elements.js" % os.path.dirname(__file__)
            if not file_exists(f_js):
                m = (
                    "no file for searching elements (should exists file %s)"
                    % f_js
                )
                logger.critical(m)
                inform_critical(m)
            js_code = text_from_file(f_js)
            self.js_code_parse_bet365 = js_code
        return js_code

    def get_javascript_for_xpath(
        self, xpath="", mode="element", with_return=True
    ):
        fun = "get_javascript_for_xpath"
        xpath_prepared = self.prepare_text_for_javasript(xpath)
        repl = {
            "[xpath]": xpath_prepared,
        }
        if mode == "element":
            js = """document.evaluate('[xpath]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue"""
        elif mode == "elements":
            js = """document.evaluate('[xpath]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null)"""
        elif mode == "inner":
            js = """document.evaluate('[xpath]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.innerHTML"""
        elif mode == "outer":
            js = """document.evaluate('[xpath]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.outerHTML"""
        else:
            wait_for_ok("ERROR %s - unknown mode %s" % (fun, mode))

        if with_return:
            js = "return %s;" % js

        js = no_probely(js, repl)
        return js

    def prepare_text_for_javasript(self, text=""):
        """
        https://stackoverflow.com/questions/16134910/how-do-i-escape-a-single-quote-in-javascript
        :param text: 
        :return: 
        """
        prepared = text.replace("'", r"\'")
        return prepared

    def find_element_by_xpath(self, xpath=""):
        fun = "find_element_by_xpath"
        try:
            element = self.driver.find_element_by_xpath(xpath)
        except Exception as er:
            logger.error(
                "     ERROR %s for xpath %s : er=%s" % (fun, xpath, er)
            )
            element = None
        return element

    def is_displayed(self, element):
        return element.is_displayed()

    def send_keys(self, elem, v=""):
        elem.clear()
        elem.send_keys(v)

    def selenium_start(self, task={}):
        want_try = 0  # todo
        want_try = 1
        fun = "selenium_start"
        step = 0
        while True:
            step += 1
            logger.debug("%s, try %s" % (fun, step))
            if step > 1:
                logger.error("ERROR SELENIUM - BAD START")
                self.status = "bad_start"  # значит плохой старт
                # wait_for_ok()
                return 0

            if want_try:
                try:
                    r = self.selenium_start_one(task)
                    logger.debug(
                        "%s step %s, result for selenium_start_one: %s"
                        % (fun, step, r)
                    )
                    self.status = "started"  # значит плохой старт
                    return r
                except Exception as er:
                    logger.error("%s ERROR_%s: %s" % (fun, step, er))
                    try:
                        logger.error("error %s" % er)
                    except Exception as er:
                        logger.error("ups, can not print error")

                self.good_exit()
            # sleep_(10)
            else:
                r = self.selenium_start_one(task)
                logger.debug("r: %s" % r)
                return r

    def selenium_start_polube(self, task={}):
        fun = "selenium_start_polube"
        IG = self.IG

        step = 0
        while True:
            step += 1
            logger.debug("%s - step %s" % (fun, step))

            self.selenium_start(task)
            status = self.status

            logger.debug("%s - step %s, status %s" % (fun, step, status))
            # wait_for_ok(fun)

            if status == "bad_start":
                # то же, но без переподключения
                IG.delete("s_session_id")
                IG.delete("s_command_executor_url")

                logger.debug("restarting without old session")
                more = {
                    "s_command_executor_url": 0,
                    "s_session_id": 0,
                }
                task = add_defaults(more, task)

                self.command_executor_url = 0
                self.session_id = 0

                self.task = add_defaults(task, self.task)

            elif status not in ["bad_start"]:
                self.main_window_handle = None
                try:
                    self.main_window_handle = self.driver.current_window_handle
                except Exception as er:
                    logger.error("ERROR, NO main_window_handle")

                IG.add("s_session_id", self.session_id)
                IG.add("s_command_executor_url", self.command_executor_url)

                # wait_for_ok('saved session?')
                break

        logger.info("[%s done in %s steps]" % (fun, step))
        return status

    def check_inet(
        self,
        u_check="https://members.bet365.es/Members/Helpers/DefaultAff.aspx?affiliate=&uguid=&bctid=",
        success="bet365.members",
    ):
        fun = "check_inet"

        logger.debug("[%s" % fun)

        self.tab_new()

        p = self.sgp(u_check, "temp/sel_%s.html" % fun)

        logger.debug("p: %s" % p)

        if p == False:
            status = 0

        elif p.find(success) != -1:
            status = 1
        elif p.find("</html>") != -1:
            status = -1
        else:
            status = 0

        logger.debug("+%s]" % status)

        self.tab_cmd("close")

        return status

    def random_scroll(self, *args, **kwargs):
        fun = "random_scroll"
        logger.debug("[%s" % fun)
        # steps_range = '3-30'
        # offset_range = '100-300'
        # sleep_range = '0-3'
        # max_seconds_range = '10-60'
        # direction_probabilities = {1:4, -1:1,}
        self.scroll_down(*args, **kwargs)
        # steps_range=steps_range,
        # offset_range=offset_range,
        # sleep_range=sleep_range,
        # max_seconds_range=max_seconds_range,
        logger.debug("+%s]" % fun)

    def scroll_down(
        self,
        steps_range="3-10",
        offset_range="100-150",
        sleep_range="0-3",
        max_seconds_range="10-120",
        direction_probabilities={1: 4, -1: 1,},
    ):
        """
			плавная прокрутка рандомная
			причем дергаемся вверх-вниз
			максимум max_seconds
		"""
        fun = "scroll_down"
        steps = get_random_value_in_range(steps_range)
        max_seconds = get_random_value_in_range(max_seconds_range)

        logger.debug(
            "[%s steps %s (steps_range %s), max_seconds %s (max_seconds_range %s)"
            % (fun, steps, steps_range, max_seconds, max_seconds_range)
        )
        seconds_start = time.time()
        pixels = 0
        for step in range(steps):
            logger.debug("%s" % steps - step)
            seconds_from_start = int(time.time() - seconds_start)

            if seconds_from_start >= max_seconds:
                logger.warning(
                    "seconds_from_start = %s >= %s = max_seconds, so exit"
                    % (seconds_from_start, max_seconds)
                )
                break

            znak = probability_dict_value(direction_probabilities)
            offset = get_random_value_in_range(offset_range)
            offset = offset * znak

            pixels = pixels + offset
            # pixels = offset
            self.execute_script("window.scrollBy(0, %s);" % pixels)

            m = "	step %s/%s, seconds_from_start %s, pixels %s, offset %s" % (
                step,
                steps,
                seconds_from_start,
                pixels,
                offset,
            )
            logger.debug(m)

            seconds_sleep = get_random_value_in_range(sleep_range)
            sleep_(seconds_sleep)

        # wait_for_ok(m)
        logger.debug("+%s]" % fun)

    def selenium_start_one(self, task={}):
        # wait_for_ok()

        fun = "selenium_start_one"
        logger.debug("[%s" % fun)
        # show_dict(task)
        # wait_for_ok()

        self.task = add_defaults(self.task, task)

        driver = self.driver
        sett = self.task
        T = self.T

        # и пак тут же создаем
        t = 0
        if t:
            show_dict(sett)
            wait_for_ok()

        proxy = change_proxy_and_create_pac(sett)
        self.proxy = str(proxy)

        # wait_for_ok('created pac?')

        potok_num = sett["s_potok_num"]
        # if potok_num!=1:
        if 1:
            sleep = min(0, potok_num * 10)
            logger.debug("potok_num %s, sleep %s" % (potok_num, sleep))
            time.sleep(sleep)

        # хотел научиться переиспользовать браузер - не вышло, вылетает ошибка и новый запускается
        s_nulja = 1  # нужно с нуля?
        if self.session_id:
            logger.debug("reuse browser")
            logger.debug(
                "	command_executor_url: %s, session_id: %s"
                % (self.command_executor_url, self.session_id)
            )
            # wait_for_ok()

            driver_connector = webdriver.Remote
            driver_connector = SessionRemote

            want_try = 0
            if want_try:
                try:
                    driver = driver_connector(
                        command_executor=self.command_executor_url,
                        desired_capabilities={},
                    )
                    # wait_for_ok()
                    driver.session_id = self.session_id

                    s_nulja = 0
                except Exception as er:
                    logger.error(
                        "ERROR WITH reuse browser. So need restart browser."
                    )

            else:
                driver = driver_connector(
                    command_executor=self.command_executor_url,
                    desired_capabilities={},
                )
                # wait_for_ok()
                driver.session_id = self.session_id
                s_nulja = 0

        # wait_for_ok('%s - reused browser?' % fun)

        if s_nulja:
            non_detectable_extension = None  # если надо - потом удалим

            t = 1
            t = 0
            if t:
                selenium_grid_url = "http://127.0.0.1:4444/wd/hub"

                # Create a desired capabilities object as a starting point.
                capabilities = DesiredCapabilities.FIREFOX.copy()
                # capabilities['platform'] = 'WINDOWS'
                # capabilities['version'] = '10'
                capabilities = DesiredCapabilities.FIREFOX

                # Instantiate an instance of Remote WebDriver with the desired capabilities.
                driver = webdriver.Remote(
                    desired_capabilities=capabilities,  # DesiredCapabilities.FIREFOX,
                    command_executor=selenium_grid_url,
                )

                return True

            if sett["s_browser"] == "chrome":

                f_chrome_driver = sett["f_chrome_driver"]

                # f_exe = r'g:\Program Files\chromiums\chrome-win32\chrome.exe'
                # f_exe = r'g:\Program Files\chromiums\chrome-win32 245195\chrome.exe'
                # f_exe = r'g:\Program Files\chromiums\chrome-win32 459988\chrome.exe'
                # f_exe = ''
                # f_exe = r'g:\Program Files\chromiums\chrome-win32\chrome.exe'
                # f_exe = r'c:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
                # f_exe = r'g:\Program Files\chromiums\chrome-win32\chrome.exe'
                # f_exe = r'g:\Program Files\chromiums\ChromiumPortable\ChromiumPortable.exe'
                # f_exe = r'g:\Program Files\chromiums\chrome-win32\chrome.exe'
                # f_exe = r'g:\Program Files\chromiums\chrome-win32 245195\chrome.exe'
                # f_exe =
                f_exe = sett["s_chrome_binary"]

                logger.debug(
                    "CHROME!	f_chrome_driver %s, f_exe %s"
                    % (f_chrome_driver, f_exe)
                )

                chrome_options = webdriver.ChromeOptions()
                chrome_experimental_options = sett[
                    "chrome_experimental_options"
                ]

                if sett["debuggerAddress"] != "":
                    chrome_experimental_options.append(
                        ["debuggerAddress", sett["debuggerAddress"]]
                    )
                    m = "setuped debuggerAddress %s" % sett["debuggerAddress"]
                    logger.debug(m)

                # wait_for_ok(m)

                # adding options
                if len(chrome_experimental_options) > 0:
                    logger.debug("\nadding chrome_experimental_options:")
                    for i, _ in enumerate(chrome_experimental_options):
                        key, value = _
                        logger.debug(
                            "	%s	add option `%s`=`%s`" % (i, key, value)
                        )
                        chrome_options.add_experimental_option(key, value)

                # wait_for_ok('added options?')

                want_options = 0
                want_options = 1
                want_options = 2
                if want_options == 2:
                    # if sett['want_non_detectable']:
                    # 	chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])

                    chrome_arguments = sett["chrome_arguments"]
                    logger.debug("chrome_arguments:")
                    # show_list(chrome_arguments)
                    for argument in chrome_arguments:
                        logger.debug("	add_argument `%s`" % argument)
                        chrome_options.add_argument(argument)

                # chrome_options.add_argument('--disable-extensions')
                # chrome_options.add_argument('--profile-directory=Default')
                # chrome_options.add_argument("--incognito")
                # chrome_options.add_argument("--disable-plugins-discovery");
                # chrome_options.add_argument("--start-maximized")
                # chrome_options.add_argument("user-data-dir=") #Path to your chrome profile

                # wait_for_ok(f_exe)

                t = 0
                t = 1
                if t:  # работает!
                    # driver = webdriver.Chrome()
                    # driver = webdriver.Chrome(chrome_options=chrome_options)
                    logger.debug2("start driver...")
                    driver = webdriver.Chrome(
                        f_chrome_driver, chrome_options=chrome_options,
                    )

                    # wait_for_ok('started chrome?')
                    logger.debug("+")

            # return True

            elif sett["s_browser"] == "ie":
                logger.debug2("ie!")
                driver = webdriver.Ie()
                return True

            elif sett["s_want_phantom"] or sett["s_browser"] == "phantom":
                logger.debug2("phantom...")
                t = 1
                if t:
                    dcap = dict(DesiredCapabilities.PHANTOMJS)
                    ua = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36"
                    ua = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:44.0) Gecko/20100101 Firefox/44.0"  # как в фаерфоксе
                    # ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.57 Safari/537.36'
                    # dcap["phantomjs.page.settings.userAgent"] = (ua)

                    phantom_headers = {
                        #'Accept':'*/*',
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                        #'Accept-Encoding':'gzip, deflate, sdch, br',#нужно потом специально раскодировать
                        "Accept-Language": "en-US,en;q=0.8",
                        "Cache-Control": "max-age=0",
                        "User-Agent": ua,
                    }
                    logger.debug("phantom headers:")
                    show_dict(phantom_headers)

                    for key in phantom_headers:
                        value = phantom_headers[key]
                        dcap["phantomjs.page.customHeaders.%s" % key] = value

                # flash in phantom:
                # 		http://www.ryanbridges.org/2013/05/21/putting-the-flash-back-in-phantomjs/

                # service_args = [
                # 	'--proxy=127.0.0.1:9999',
                # 	'--proxy-type=http',
                # 	'--ignore-ssl-errors=true'
                # 	]

                # driver = init_phantomjs_driver(service_args=service_args)

                # service_args = [
                #    '--proxy=5.135.176.41:3123',
                #    '--proxy-type=http',
                # ]
                # phantom = webdriver.PhantomJS(js_path, desired_capabilities=dcap, service_args =service_args)

                driver = webdriver.PhantomJS(
                    "C:\phantomjs.exe", desired_capabilities=dcap
                )
                driver.capabilities["acceptSslCerts"] = True
                driver.capabilities[
                    "phantomjs.page.settings.javascriptEnabled"
                ] = True

                # driver.set_window_size(1024, 768)
                # driver.set_window_size(1920, 1080)

                # driver.capabilities["proxy"] = {"proxy": "5.135.176.41:3123", "proxy-type": "http"}

                logger.debug("+")

            elif sett["s_browser"] in ["", "firefox"]:

                firefox_extensions0 = sett["firefox_extensions"]
                # чистим несуществующие
                firefox_extensions = [
                    f for f in firefox_extensions0 if file_exists(f)
                ]
                if len(firefox_extensions0) != len(firefox_extensions):
                    removed_extension = list_minus_list(
                        firefox_extensions0, firefox_extensions
                    )
                    logger.warning(
                        "oppa, no files for extensions %s" % removed_extension
                    )
                    sett["generated_non_detectable"] = 0
                    non_detectable_extension = None

                # добавляем хитрый плугин
                if (
                    sett["want_non_detectable"]
                    and non_detectable_extension is None
                    and not sett["generated_non_detectable"]
                ):
                    logger.warning(
                        "want_non_detectable, so generating non_detectable_extension... "
                    )
                    non_detectable_extension = (
                        generate_non_detectable_extension()
                    )
                    logger.debgu("generated %s" % non_detectable_extension)
                    firefox_extensions.append(non_detectable_extension)
                    sett["generated_non_detectable"] = 1

                # wait_for_ok()

                _ = {}
                _ = {
                    "s_profile_path": T.s_profile_path,
                    "s_proxy": T.s_proxy,
                    "s_autoconfig_url": T.s_autoconfig_url,
                }
                proxy_write_to_settings_firefox(_)

                if T.s_clear_cookies:
                    f_cookies = s_get_f_cookie(T.s_profile_path)
                    logger.debug("	clear cookies - file %s" % f_cookies)
                    rmfile(f_cookies)
                    logger.debug("+")

                # wait_for_ok('written?')

                # пишем темп-папку. Но она почему-то не используется самим селениумом
                t = 1
                t = 0
                if t:
                    dir_for_tempdir = "c:/temp_selenium"
                    create_dir(dir_for_tempdir)
                    tempdir = tempfile.mkdtemp(
                        suffix="foo", prefix="bar", dir=dir_for_tempdir
                    )
                    logger.debug("tempdir: %s" % tempdir)
                    tempdir2 = tempfile.gettempdir()
                    logger.debug("tempdir2: %s" % tempdir2)
                    os.environ["TMPDIR"] = tempdir

                # From Windows command line:
                # set PYTHONPATH=%PYTHONPATH%;C:\My_python_lib

                # capabilities = DesiredCapabilities.FIREFOX
                # capabilities['name'] = sett['potok']

                # todo
                t = 0
                t = 1

                fun_firefox_profile = webdriver.FirefoxProfile

                if 0:
                    pass

                elif T.s_profile_path == "":
                    logger.debug("firefox without profile")
                    profile = fun_firefox_profile()

                elif T.s_profile_path != "":
                    logger.debug(
                        'firefox with profile "%s"' % T.s_profile_path
                    )
                    profile = fun_firefox_profile(T.s_profile_path)

                # wait_for_ok('added extensions?')

                # wait_for_ok('loaded extensions?')

                # profile = webdriver()

                # profile.setPreferences("foo.bar", 23);

                # driver = webdriver.Firefox(profile)
                # wait_for_ok('setuped proxy?')

                if 0:
                    # тестяю - возможно сработает сохранение кук и на моем профайле
                    t = 1
                    t = 0
                    if t:
                        # https://developer.mozilla.org/en-US/docs/Cookies_Preferences_in_Mozilla  - все о куках
                        profile.set_preference(
                            "network.cookie.cookieBehavior", 0
                        )  # 2 - не сохранять куки
                        profile.set_preference(
                            "network.cookie.lifetimePolicy", 0
                        )  # 2 - не сохранять куки
                        ua = get_useragent()
                        ua = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0"  # good
                    #     Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0
                    # profile.set_preference("general.useragent.override",ua)

                    # юзерагент пробую менять
                    t = 1
                    t = 0
                    if t or sett["s_want_random_useragent"]:
                        ua_rand = "Mozilla/5.0 (Windows NT 6.[rand]; WOW[rand]; rv:[rand].0) Gecko/[rand] Firefox/44.[rand]"

                        ua_thinkpad_chrome = "Mozilla/5.0 (iPhone; CPU iPhone OS 9_0 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13A342 Safari/601.1"
                        ua1 = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36"

                        ua2 = "Mozilla/5.0 (compatible; MSIE 10.0; Windows Phone 8.0; Trident/6.0; IEMobile/10.0; ARM; Touch; Microsoft; Lumia 640 XL)"
                        ua = choice(
                            [
                                ua_rand,
                                ua_thinkpad_chrome,
                                ua1,
                                ua2,
                                "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0",
                                "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36",
                                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.5.2171.95 Safari/537.36",
                            ]
                        )

                        # ua = ua_rand
                        rand = randint(0, 1000)
                        repl = {
                            "[rand]": str(rand),
                        }
                        ua = no_probely(ua, repl)
                        # ua = get_useragent()
                        logger.debug("useragent %s" % ua)
                        # wait_for_ok()
                        add_to_full_log(["useragent:", ua])
                        # wait_for_ok()
                        profile.set_preference(
                            "general.useragent.override", ua
                        )

                if T.s_special_user_agent != "":
                    ua = T.s_special_user_agent
                    logger.debug("s_special_user_agent: %s" % ua)
                    add_to_full_log(["useragent:", ua])
                    # wait_for_ok()
                    profile.set_preference("general.useragent.override", ua)

                # http://stackoverflow.com/questions/8885137/selenium-using-python-enter-provide-http-proxy-password-for-firefox
                t = 1
                t = 0
                if t:
                    profile.set_preference("network.proxy.type", 1)
                    profile.set_preference("network.proxy.http", PROXY_HOST)
                    profile.set_preference(
                        "network.proxy.http_port", PROXY_PORT
                    )
                    profile.set_preference("network.proxy.http", PROXY_HOST)
                    profile.set_preference(
                        "network.proxy.http_port", PROXY_PORT
                    )

                t = 1
                if t:
                    profile.set_preference(
                        "network.http.phishy-userpass-length", 255
                    )
                    profile.set_preference(
                        "network.automatic-ntlm-auth.trusted-uris",
                        "google.com",
                    )
                    profile.set_preference(
                        "browser.safebrowsing.malware.enabled", "true"
                    )

                t = 1
                t = 0
                if t:
                    profile.set_preference(
                        "network.http.phishy-userpass-length", 255
                    )
                    profile.set_preference(
                        "network.automatic-ntlm-auth.trusted-uris",
                        "google.com",
                    )
                # selenium = new WebDriverBackedSelenium(driver, "http://<user>:<password>@<host>")

                if len(firefox_extensions) > 0:
                    logger.warning("\nadding extensions:")
                    for i, extension in enumerate(firefox_extensions):
                        logger.debug("	%s	add extension `%s`" % (i, extension))
                        profile.add_extension(extension)

                # webdriver.minimizeWindow()
                # driver = webdriver.Firefox()
                logger.debug2("\n" * 2 + "-" * 10, "1 - run driver:")
                i = 0
                cnt_critical = 0
                while True:
                    i += 1
                    # if i>5:
                    if cnt_critical >= 3 or i > 10:
                        f_log_restart = "log_restart.txt"
                        add_to_full_log(
                            ["error with selenium, restart"], f_log_restart
                        )

                        # reboot_computer()
                        self.good_exit()

                    logger.debug('profile from path: "%s"' % T.s_profile_path)

                    # log_file = 'temp/log_file_%s/%s.txt' % (fun, potok_num)
                    # logger.debug('log_file: %s' % log_file)
                    ##создали папку
                    # text_to_file('', log_file)
                    # rmfile(log_file)

                    # запускаем драйвер
                    if sett["s_ff_binary"] != "":
                        annex = sett["s_ff_binary_annex"]

                        logger.debug(
                            "have binnary `%s` with annex `%s`, analyzing:"
                            % (sett["s_ff_binary"], annex)
                        )

                        ff_binary = self.prepare_binary_with_annex(
                            sett["s_ff_binary"], annex
                        )

                        logger.debug('binary: "%s"' % ff_binary)
                        binary = FirefoxBinary(firefox_path=ff_binary)
                        # wait_for_ok()

                        # capabilities = DesiredCapabilities.FIREFOX
                        capabilities = DesiredCapabilities.FIREFOX.copy()
                        service_args = []

                        if sett["firefox_with_marionette"]:

                            geckodriver_port = 1234
                            marionette_port = 12349

                            t = 1
                            if t:

                                capabilities["marionette"] = True
                                capabilities["acceptInsecureCerts"] = True
                                capabilities["acceptSslCerts"] = True

                                capabilities[
                                    "webdriverFirefoxPort"
                                ] = geckodriver_port
                                service = webdriver.firefox.service.Service(
                                    "geckodriver", port=geckodriver_port
                                )
                                profile.set_preference(
                                    "webdriver.firefox.port", geckodriver_port
                                )
                                profile.set_preference(
                                    "firefox.port", geckodriver_port
                                )
                                profile.set_preference(
                                    "webdriver_firefox_port", geckodriver_port
                                )
                                profile.set_preference(
                                    "--port", geckodriver_port
                                )
                                profile.set_preference(
                                    "port", geckodriver_port
                                )
                                profile.set_preference(
                                    "PORT_PREFERENCE", geckodriver_port
                                )
                                profile.set_preference(
                                    "network.proxy.http_port", geckodriver_port
                                )

                                # profile.set_preference("--marionette-port", marionette_port)

                                service_args = [
                                    #'--port',
                                    #'%s' % geckodriver_port,
                                    "--marionette-port",
                                    "%s" % marionette_port,
                                    #'--proxy=5.135.176.41:3123',
                                    #'--proxy-type=http',
                                ]

                        # wait_for_ok(service_args)
                        print("service_args : %s" % service_args)

                        # Instantiate an instance of Remote WebDriver with the desired capabilities.

                        special_start = "test_spec_run"
                        special_start = ""
                        if special_start != "":
                            Show_step(special_start)
                            # Custom profile folder to keep the minidump files
                            # profile = tempfile.mkdtemp(".selenium")
                            profile = T.s_profile_path
                            print("*** Using profile: {}".format(profile))

                            # Use the above folder as custom profile
                            opts = webdriver.FirefoxOptions()
                            opts.add_argument("-profile")
                            opts.add_argument(T.s_profile_path)
                            # opts.binary = "/Applications/Firefox.app/Contents/MacOS/firefox"
                            opts.binary = sett["s_ff_binary"]
                            logger.debug('binary: "%s"' % sett["s_ff_binary"])

                            driver = webdriver.Firefox(
                                options=opts,
                                # hard-code the Marionette port so geckodriver can connect
                                # service_args=["--marionette-port", "2828"]
                            )

                        else:
                            driver = webdriver.Firefox(
                                profile,
                                firefox_binary=binary,
                                capabilities=capabilities,
                                # port=geckodriver_port,
                                # service=service,
                                service_args=service_args,
                                # service_args=service,
                            )

                        # driver = webdriver.Firefox(profile, firefox_binary=binary)

                        t = 1
                        if t:
                            driver_capabilities = driver.capabilities
                            logger.debug("driver_capabilities:")
                            show_dict(driver_capabilities)

                        t = 1
                        t = 0
                        if t:
                            self.driver = driver
                            pid = self.get_selenium_pid()
                            wait_for_ok("good pid %s ?" % pid)

                    # wait_for_ok('started firefox?')

                    else:
                        driver = webdriver.Firefox(profile)
                    # wait_for_ok()
                    # driver = webdriver.Firefox()

                    break

                if non_detectable_extension is not None:
                    logger.debug(
                        "remove temporary non_detectable_extension %s"
                        % non_detectable_extension
                    )
                    rmdir(non_detectable_extension)
                # wait_for_ok()

                logger.debug(2)

            else:
                wait_for_ok("ERROR - unknown s_browser")

            m = "CREATED DRIVER"
            print(m)

            want_more_settings = 1
            want_more_settings = 0
            if want_more_settings:
                m = "created driver, adding more settings..."
                print(m)

                ##Resize the window to the screen width/height
                t = 1
                t = 0
                if t:
                    mess = changed_position()
                    size_x = randint(600, 1800)
                    size_y = randint(500, 1200)
                    driver.set_window_size(size_x, size_y)
                    wait_for_ok(mess)

                # Move the window to position x/y
                t = 1
                t = 0
                if t or T.s_window_position != -1:
                    driver.set_window_position(T.s_window_position, 0)

                if sett["s_maximize_window"]:
                    driver.maximize_window()

                if sett["s_maximize_f11"]:
                    elem = driver.find_element_by_xpath("/html/body")
                    elem.send_keys(Keys.F11)

                t = 0
                if t:
                    if T.s_autoconfig_url.find("_uni.pac") != -1:
                        i = 0
                        while True:
                            i += 1
                            if i > 3:
                                logger.error("ups :(")
                                logger.error("uni is not setupped, die")
                                self.good_exit()

                            logger.error("[have uni, logining %s..." % i)
                            randsleep = 0  # randint(0, 15)
                            logger.debug("randsleep: %s" % randsleep)
                            time.sleep(randsleep)

                            u = "http://www.google.com/recaptcha/api.js?render=explicit&hl=en"
                            try:
                                driver.get(u)
                            # p = sgp(u)
                            except Exception as er:
                                logger.error("driver_error: %s" % er)

                            login_vsegda({"limit": 1})

                            p = sgp()

                            if (
                                p.find(
                                    "PLEASE DO NOT COPY AND PASTE THIS CODE"
                                )
                                != -1
                            ):
                                logger.debug("uraaaa!")
                                # return True
                                break

                # sleep = 10
                self.setup_wait(
                    "default"
                )  # ==#driver.implicitly_wait(T.s_seconds_wait)
                driver.set_page_load_timeout(T.s_seconds_wait)
                socket.setdefaulttimeout(100)

                # non-detectable?
                if sett["want_non_detectable"]:
                    driver = self.make_driver_non_detectable(driver)

        if sett["want_random_browser_size"] != "":
            size_x = randint(600, 1200)
            size_y = randint(500, 700)
            logger.debug("want_random_browser_size: %sx%s" % (size_x, size_y))
            driver.set_window_size(size_x, size_y)
        # wait_for_ok('good size?')

        # wait_for_ok()

        self.driver = driver

        pid = self.get_selenium_pid()
        sett["selenium_pid"] = pid

        if sett["s_f_with_id"] != -1:
            text_to_file(str(pid), sett["s_f_with_id"])
        # wait_for_ok('saved pid to %s ?' % sett['s_f_with_id'])

        if sett["s_save_seleinum_pids"]:
            text_to_file(
                sett["selenium_pid"], self.f_pid(sett["selenium_pid"])
            )  # сохраняем айдишник процесса, потом чистить можно

        self.task["selenium_pid"] = pid
        logger.debug("selenium_pid:", sett["selenium_pid"])

        # беру еще размеры окна
        self.window_size = r
        logger.debug("window_size:", self.window_size)
        # wait_for_ok()

        self.command_executor_url = (
            driver.command_executor._url
        )  # "http://127.0.0.1:60622/hub"
        self.session_id = (
            driver.session_id
        )  #'4e167f26-dc1d-4f51-a207-f761eaf73c31'
        logger.debug(
            "command_executor_url: %s, session_id: %s"
            % (self.command_executor_url, self.session_id)
        )

        # wait_for_ok('%s check - good?' % fun)

        logger.debug("+%s]" % fun)

    # wait_for_ok('done?')

    def get_window_size(self):
        r = self.driver.get_window_size()  # {u'width': 1341, u'height': 810}
        return r

    def make_driver_non_detectable(self, driver):
        ## solution found here https://stackoverflow.com/questions/17385779/how-do-i-load-a-javascript-file-into-the-dom-using-selenium
        """
			таким макаром, напрямую, не сработало
		"""
        fun = "make_driver_non_detectable"
        return driver
        logger.debug("[%s" % fun)
        js_non_detectable = """
// overwrite the `languages` property to use a custom getter
const setProperty = () => {
Object.defineProperty(navigator, "languages", {
get: function() {
    return ["en-US", "en", "es"];
}
});

// Overwrite the `plugins` property to use a custom getter.
Object.defineProperty(navigator, 'plugins', {
get: () => [1, 2, 3, 4, 5],
});

// Pass the Webdriver test
Object.defineProperty(navigator, 'webdriver', {
get: () => false,
});
callback();
};
setProperty();

		"""
        driver.execute_script(
            "var s=window.document.createElement('script'); s.src='c:\\javascriptFirefox.js';window.document.head.appendChild(s);"
        )
        # driver.execute_script(js_non_detectable)
        # wait_for_ok('want_non_detectable done?')
        logger.debug("+]")
        return driver

    def setup_wait(self, value=0):
        # устанавливаем ожидание
        # бывает удобно
        # 	https://stackoverflow.com/questions/9567069/python-selenium-webdriver-checking-element-exists
        if value == "default":
            value = self.task["s_seconds_wait"]

        if type(self.driver) not in [type({}), int]:
            self.driver.implicitly_wait(value)

    def setup_wait_0(self):
        self.driver.implicitly_wait(T.s_seconds_wait)

    def selenium_stop(self, task={}):
        fun = "selenium_stop"
        logger.debug("[%s" % fun)

        try:
            self.driver.close()
        except Exception as er:
            logger.error("error driver.close %s" % er)

        try:
            self.driver.quit()
        except Exception as er:
            logger.error("error driver.quit %s" % er)

        self.S = 0

        logger.debug("+%s]" % fun)

    def url(self, cnt_tries=10):
        fun = "selenium_url"
        current_url = ""
        for i in range(cnt_tries):
            try:
                current_url = self.driver.current_url
                break
            except Exception as er:
                logger.error("%s error %s" % (fun, er))
                # sleep_(2)

        return current_url

    def download_url_with_cookies(self, url="", headers_txt=""):
        """TODO - скачать страницу
        """
        cookie = self.get_cookie_txt()
        # logger.debug('cookie: %s' % cookie)
        # wait_for_ok()
        headers = {
            "User-Agent": self.get_user_agent(),
            "Cookie": cookie,
        }
        headers_from_txt = parse_headers_from_text(headers_txt)
        headers = add_defaults(headers_from_txt, headers)

        t = 1
        t = 0
        if t:
            headers_txt = """
            GET /members/services/History/SportsHistory/GetBetConfirmation?displaymode=&Id=22085466219&BetStatus=0&Bcar=0&Bash=5254640e95688495c5c636ad65db0326&Pebs=0 HTTP/1.1
Host: members.bet365.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Connection: keep-alive
Cookie: aps03=oty=2&lng=1&ct=14&tzi=4&cst=0&cg=1; aaat=di=30ad4ccd-6ee8-4507-9011-ea8f8d47854e&un=filimorisboggy&ts=27-11-2020 14:31:51&v=2&am=0&at=ecdf069a-716e-4cbc-8698-1ef8e6d4ea4e; usdi=uqid=6EDFF07F-BCC9-476D-9C1C-1146BFD093CD; platform=1; session=processform=0; pstk=0DA3509B87964AAF890A492D82AC6124000004; __RequestVerificationToken_L21lbWJlcnMvc2VydmljZXMvaG9zdA2=Kl6MyZFOGmi1tV1L7MVX3qeYckQAOvKdPvZjBBLN6HkVCrBCjqZdlvK5rTgyBqKzqs6OWcERRTBBCfgypibSggXQ6qg1; __RequestVerificationToken_L21lbWJlcnMvc2VydmljZXMvSGlzdG9yeQ2=O-uRB6hlZqVnv88PRgZfJtXyRRh3V99D_IhrH3nReJeASuGpO71FJQx9rcRdCng4qW-HfOW3R5xwVgXWuMXtO0j0HwA1
Upgrade-Insecure-Requests: 1
Cache-Control: max-age=0
"""
            headers = parse_headers_from_text(headers_txt)
        show_dict(headers)

        step = 0
        while True:
            step += 1
            _ = {
                "u": url,
                "limit": 1,
                "headers": headers,
                "f": "temp/last_download_url_with_cookies.html",
                "sposob": "requests",
            }
            r = pycus_u(_)

            show_dict(r)

            # html = r['html']
            # error = r['error']
            # kod = r['kod']

            wait_for_ok("check")

    def get_user_agent(self):
        return self.driver.execute_script("return navigator.userAgent;")

    def get(self, url=""):
        fun = "get"
        logger.debug(" get %s" % url)
        try:
            self.driver.get(url)
            r = True
        except Exception as er:
            logger.error("%s error" % fun)
            r = False
        logger.debug("+%s]" % r)
        return r

    def just_open_url(
        self,
        url="",
        seconds_wait_for_url_change=10,
        seconds_recheck=0.2,
        debug=False,
    ):
        """
        просто открыть урл не дожидаясь никакой загрузки
        :param url: 
        :return: 
        """
        fun = "just_open_url"
        debug = True

        old_url = self.url()
        if debug:
            logger.debug("[%s, old_url=`%s`" % (fun, old_url))

        js = 'window.location.replace("[url]");'  # Не дожидается?
        js = 'location.href = "[url]"'  # chrome - Ждет пока не откроется
        js = 'window.open("[url]","_self")'  # дожидается!!!

        js = js.replace("[url]", url)

        r = self.execute_script(js)

        t = 1
        if t:
            t_start = time.time()
            step = 0
            while True:
                step += 1
                current_url = self.url()
                changed = False
                if current_url == url or old_url != current_url:
                    changed = True

                if changed:
                    break

                duration = time.time() - t_start
                if duration >= seconds_wait_for_url_change:
                    break

                if debug:
                    logger.debug(
                        "%s step %s, duration %.2f" % (fun, step, duration)
                    )
                sleep_(seconds_recheck)

            if debug:
                logger.debug(
                    "%s: changed=%s, want %s, current_url=%s"
                    % (fun, changed, url, current_url)
                )
        return r

    def sgp_quick(self, u_download="", f_to="", **kwargs):
        return self.sgp(
            u_download=u_download, f_to=f_to, seconds_sleep=0, **kwargs
        )

    def sgp(
        self,
        u_download="",
        f_to="",
        seconds_sleep=2,
        want_source=True,
        debug=False,
        **kwargs,
    ):
        #'get selenium page'
        # try:
        fun = "sgp"

        # logger.debug('       [%s  want_source=%s, kwargs %s' % (fun, want_source, kwargs))

        t_start = time.time()

        if u_download != "":
            i = 0
            while True:
                # logger.debug('  .')
                i += 1
                if i > 3:
                    logger.error(
                        "%s error %s - with %s" % (fun, i, u_download)
                    )
                    return False
                try:
                    logger.debug("			[%s try_%d, %s" % (fun, i, u_download))
                    self.driver.get(u_download)
                    break
                except Exception as er:
                    logger.error("error %s: %s)" % (fun, er))
            sleep_(
                seconds_sleep, fun="sleep_%s" % fun
            )  # Пусть страница загрузится. Вдруг у нас медленный интернет...

        if not want_source:
            return "do not want source"

        # logger.debug('%s get source...' % fun)

        # page = self.driver.page_source
        try:
            page = self.driver.page_source
            page = bytes_to_str(page, "utf-8")
            # wait_for_ok('good page?')
            if f_to != "":
                logger.debug(f"    saving to {f_to}...")
                text_to_file(page, f_to)

            seconds = time.time() - t_start

            logger.debug(f"  +{fun} {type(page)} in {seconds:.2f} sec]")
            return page

        except Exception as er:
            logger.error("error in %s %s" % (fun, er))
            return False

    def get_selenium_pid(self):
        fun = "get_selenium_pid"
        if self.selenium_pid:
            pid = self.selelenium_pid
        else:

            # print(self.debugger_port, self.marionette_port)
            # wait_for_ok(fun)

            if self.debugger_port:
                pid = get_pid_by_port(self.debugger_port)

            elif self.marionette_port:
                pid = get_pid_by_port(self.marionette_port)

            else:
                pid = get_selenium_pid_from_driver(self.driver)

            pid = int(pid)
            if pid and pid not in ["-1"]:
                self.selelenium_pid = pid
            # wait_for_ok('%s selenium_pid=%s' % (fun, self.selelenium_pid ))
            logger.error("%s selenium_pid=%s" % (fun, self.selelenium_pid))
            # wait_for_ok()

        return pid

    def f_pid(self, pid):
        f = "%s/%s" % (self.task["s_d_selenium_pids"], pid)
        return f

    def add_css(
        self,
        style=".market-filter-wrapper .bvs-button-card {font-size: 5px; width: 10px; min-width: 0px;margin: 0px; padding:0px;};",
    ):
        """
        mode = 'one_sheet'
            просто в документ отправляю нужные стили
        
        mode = 'stylesheets'
            https://davidwalsh.name/add-rules-stylesheets
            Оказалось что лист может быть внешним - поэтому создаю свой стиль
        """
        styles = clear_list(style)

        mode = "stylesheets"
        mode = "one_sheet"
        if mode == "one_sheet":
            styles_txt = ";".join(styles)
            script = (
                """
        var sheet = document.createElement('style');
        sheet.innerHTML = "%s;";
        document.body.appendChild(sheet);
                """
                % styles_txt
            )

        elif mode == "stylesheets":

            script = """
    function getStyleSheet(unique_title) {
      for(var i=0; i<document.styleSheets.length; i++) {
        var sheet = document.styleSheets[i];
        if(sheet.title == unique_title) {
          return sheet;
        }
      }
    }

    sheet_title = 'my_fixed_sheet';
    var sheet = document.createElement('style');
    sheet.title = sheet_title;
    sheet.innerHTML = "div {}";
    document.body.appendChild(sheet);

    /*
    var sheets = document.styleSheets;
    var last_sheet = sheets[sheets.length-1];

    var last_sheet = getStyleSheet(sheet_title);
    */

    var last_sheet = sheet;
    //console.log(last_sheet)
            """
            for style in styles:
                script = (
                    script + '\nlast_sheet.insertRule("%s", 1 );' "" % style
                )

        logger.debug("script=%s" % script)
        self.execute_script(script)
        # wait_for_ok('changed font size?')

    def go_back(self):
        """возврат на предыдущую страницу"""
        r = self.execute_script("window.history.go(-1)")

    def setup_title(self, title=""):
        js = "document.title = '%s'" % title
        self.execute_script(js)

    def execute_script(self, *args):
        """
			хитро исполняю скрипт
		"""
        fun = "execute_script"
        debug = True
        debug = False
        # wait_for_ok(fun)
        if debug:
            logger.debug(f"[{fun} {args=}")
        try:
            new_args = []
            for arg in args:
                # logger.debug(type(arg))
                if type(arg) in [type(""), type("")] and " $x(" in arg:
                    repl = {
                        " $x(": " getElementsByXPath(",
                    }
                    js_code = self.get_saved_js_code_to_parse_elements()
                    arg = js_code + "\n" + no_probely(arg, repl)

                    if debug:
                        logger.debug(f"new_arg: {arg}")
                    # wait_for_ok('replacing')
                new_args.append(arg)

            if debug:
                logger.debug("new_args:")
                show_list(new_args)
                # wait_for_ok()
            new_args = tuple(new_args)
            # logger.debug('execute_script args=%s' % new_args)
            r = self.driver.execute_script(*new_args)
            # r = 1
        except Exception as er:
            logger.error(f"error {fun}: {er}")
            r = None
        # wait_for_ok(fun)
        return r

    def element_scroll(self, element, height=-150):
        fun = "element_scroll"
        logger.debug("[%s to %s" % (fun, element))
        # прокручиваем к нашему элементу
        # http://blog.likewise.org/2015/04/scrolling-to-an-element-with-the-python-bindings-for-selenium-webdriver/
        r = self.execute_script(
            "return arguments[0].scrollIntoView();", element
        )
        # self.driver.execute_script("return arguments[0].scrollIntoView();", element)

        # self.driver.execute_script("window.scrollBy(0, %s);" % height)
        r = self.execute_script("window.scrollBy(0, %s);" % height)
        # time.sleep(.3)

        # to check:
        # Find the element you want to focus on (in my case link text was : Welcome Everyone) and then send NULL key to that element.
        # element.send_keys(Keys.NULL)

        # http://www.emalis.com/2013/10/scroll-list-with-keys-arrow_down-to-a-visible-element-selenium-python/
        # 	другой тип прокрутки
        logger.debug("+%s %s]" % (r, fun))
        return r

    def apply_class(self, element, s):
        return self.apply_attribute(element, s, "class")

    def apply_style(self, element, s):
        return self.apply_attribute(element, s, "style")
        # self.driver.execute_script("arguments[0].setAttribute('style', arguments[1]);", element, s)
        # r = self.execute_script("arguments[0].setAttribute('style', arguments[1]);", element, s)
        # return r
        # return self.set_attribute(element, 'style', s)

    def apply_attribute(self, element, s, attribute_name="style"):
        return self.set_attribute(element, attribute_name, s)

    def set_html_body(self, html=""):
        """
        телу жестко прописываем код
        """
        js = 'document.body.parentElement.innerHTML = "[html]";'
        js = 'document.documentElement.innerHTML = "[html]";'
        js = js.replace("[html]", html)
        r = self.execute_script(js)

    def set_innerhtml(self, element, value=""):
        return self.set_value(element, value=value, name="innerHTML")

    def set_value(self, element, value="", name="value"):
        r = self.execute_script(
            "arguments[0].%s= arguments[1]" % name, element, value
        )
        return r

    def set_attribute(self, element, name="", value=""):
        " element.setAttribute(attributeName, attributeValue)"
        r = self.execute_script(
            "arguments[0].setAttribute(arguments[1], arguments[2])",
            element,
            name,
            value,
        )
        return r

    def clear_marked_xpath(self, xpath="", attribute="mymarking"):
        """
			находим и чистим все элементы
		"""
        fun = "clear_marked_xpath"
        logger.debug("[%s %s" % (fun, xpath))
        status = 1

        if type(xpath) == type([]):
            elements = xpath
        else:
            elements = self.search_elements_xpath(xpath)
        for element in elements:
            cleared = self.clear_marked(element, "mymarking")
            if not cleared:
                status = 0
        return status

    def clear_marked(self, element, attribute="mymarking"):
        """
			чистем отмеченное
		"""
        r = self.remove_attribute(element, attribute)
        return r

    def mark_element(self, element, s="marked"):
        r = self.set_attribute(element, "mymarking", s)
        # self.driver.execute_script("arguments[0].setAttribute('mymarking', arguments[1]);", element, s)
        return r

    def set_attribute(self, element, name="", value=""):
        # r = self.driver.execute_script("arguments[0].setAttribute(arguments[1], arguments[2]);", element, name, value)
        r = self.execute_script(
            "arguments[0].setAttribute(arguments[1], arguments[2]);",
            element,
            name,
            value,
        )
        return r

    def remove_attribute(self, element, attribute=""):
        # removeAttribute
        # r = self.driver.execute_script("arguments[0].removeAttribute(arguments[1]);", element, attribute)
        r = self.execute_script(
            "arguments[0].removeAttribute(arguments[1]);", element, attribute
        )
        return r

    def highlight_xpath(self, xpath="", sleep=2, element=None):
        if not element:
            element = self.find_element_by_xpath(xpath)
        if element:
            self.highlight(element, sleep=sleep)
        else:
            logger.warning("no element with xpath %s" % xpath)

    def highlight_forever(self, element):
        self.highlight(element, -1)

    def highlight(self, element, sleep=2, style=""):
        """Highlights (blinks) a Selenium Webdriver element"""
        fun = "highlight_element"

        logger.debug("[%s %s" % (fun, element))

        try:
            self.highlight_one(element, sleep, style=style)
        except Exception as er:
            logger.error("er %s: %s" % (fun, er))
            return 0
        logger.debug("+%s]" % (fun))
        return 1

    def element_hide(self, element):
        """hiding element"""
        fun = "element_hide"
        logger.debug("[%s" % fun)
        self.apply_style(element, "display:none;")
        logger.debug("+]")

    def element_display(self, element):
        """displaying element"""
        fun = "element_display"
        logger.debug("[%s" % fun)
        self.apply_style(element, "display:;")
        logger.debug("+]")

    def highlight_one(self, element, sleep=1.3, style=""):
        """Highlights (blinks) a Selenium Webdriver element"""
        fun = "highlight_one"
        if not sleep:
            return

        logger.debug("[%s" % fun)
        original_style = element.get_attribute("style")
        logger.debug("	original_style: %s" % original_style)
        background_color = "yellow"
        background_color = "rgba(255, 255, 0, .4)"  # /*  40% opaque yellow */
        # self.apply_style(element, "background: %s; border: 2px solid red;" % background_color)
        # style = "border: 15px solid red; padding: 10px; font-size: 130%;"
        if style == "":
            style = "border: 15px solid red;"

        self.apply_style(element, style)

        if sleep in [-1]:
            return 1

        # wait_for_ok('style?')
        # logger.debug('highlight_sleep:%s' % sleep)
        time.sleep(sleep)
        self.apply_style(element, original_style)
        logger.debug("+]")

    # <<<<<<<<<<<работа с куками
    def delete_all_cookies(self):
        logger.debug("delete_all_cookies")
        self.driver.delete_all_cookies()
        logger.debug("+]")

    def get_f_cookie(self, task={}):
        task = hitro_dict(task, "login")
        d_cookies = task.get("d_cookies", self.T.s_d_cookies)
        return "%s/%s" % (d_cookies, filename(task["login"]))

    def get_cookie_txt(self, encoding="utf8"):
        # куки в строчку
        # aps03=oty=2&lng=1&ct=14&tzi=4&cst=0&cg=1; aaat=di=30ad4ccd-6ee8-4507-9011-ea8f8d47854e&un=filimorisboggy&ts=27-11-2020 14:31:51&v=2&am=0&at=ecdf069a-716e-4cbc-8698-1ef8e6d4ea4e; usdi=uqid=6EDFF07F-BCC9-476D-9C1C-1146BFD093CD; platform=1; session=processform=0; pstk=0DA3509B87964AAF890A492D82AC6124000004; __RequestVerificationToken_L21lbWJlcnMvc2VydmljZXMvaG9zdA2=Kl6MyZFOGmi1tV1L7MVX3qeYckQAOvKdPvZjBBLN6HkVCrBCjqZdlvK5rTgyBqKzqs6OWcERRTBBCfgypibSggXQ6qg1; __RequestVerificationToken_L21lbWJlcnMvc2VydmljZXMvSGlzdG9yeQ2=O-uRB6hlZqVnv88PRgZfJtXyRRh3V99D_IhrH3nReJeASuGpO71FJQx9rcRdCng4qW-HfOW3R5xwVgXWuMXtO0j0HwA1
        debug = False
        items = self.get_cookies()
        cookies = []
        for item in items:
            name = item["name"]
            value = item["value"]
            line = "%s=%s" % (name, value)
            if debug:
                logger.debug("item = %s" % item)
                logger.debug("      line=%s" % line)
            cookies.append(line)
        cookies = "; ".join(cookies)
        # cookies = cookies.encode('utf8')
        if encoding:
            cookies = unicode_to_text(cookies, encoding)
        return cookies

    def get_cookies(self):
        cookies = []
        try:
            cookies = self.driver.get_cookies()
        except Exception as er:
            logger.error("er: %s" % er)
        return cookies

    def save_cookies_after_successfull_login(self, acc):
        fun = "save_cookies_after_successfull_login"
        t = 1
        if t:
            self.save_cookies_after_successfull_login_one(acc)
        else:
            try:
                self.save_cookies_after_successfull_login_one(acc)
            except Exception as er:
                logger.error("%s_error: " % (fun, er))

    def save_cookies_after_successfull_login_one(
        self, acc={}, more_urls=["http://accounts.google.com/[random]?hl=en"]
    ):
        # сохраняем куки после успешного логина
        # селениум не умеет сохранять куки со всего фаерфокса. Поэтому можно приложение поставить http://stackoverflow.com/questions/22200134/make-selenium-grab-all-cookies, а можно просто открыть страничку и посмотреть что там
        fun = "save_cookies_after_successfull_login_one"
        logger.debug("[%s " % fun)
        cookies = self.get_cookies()
        current_url = self.url()
        # r = cookies_save_hitro(acc)

        t = 0
        t = 1
        if t:  # и куки именно с аккаунта еще нужны
            for u in more_urls:
                repl = {
                    "[random]": to_hash(acc),
                }
                u = no_probely(u, repl)
                logger.debug("	get more cookies from %s" % u)
                p = self.sgp(u)
                # sleep_(5)
                # cookies_save_hitro(acc)
                # wait_for_ok('retry %s - found cookies?' % i)
                cookies2 = self.get_cookies()
                cookies = slitj_list_listov([cookies, cookies2])

            logger.debug("return to first url %s" % current_url)
            p = self.sgp(current_url)
        else:
            cookies2 = []

        t = 1
        if t:
            logger.debug("cookies:")
            show_list(cookies)
        acc["cookies"] = cookies
        self.cookies_save_hitro(acc)
        # wait_for_ok('saved cookies?')
        logger.debug("+]")

    def cookies_save_hitro(self, task={}):
        # хитроф-ии, только если в настройках стоит юзать тогда юзаем
        # _ = {
        # 	'login':T.login,
        # 	#'domain':'accounts.google.com',
        # 	'u':u_404,
        # }

        # f_cookie = self.get_f_cookie(_)
        ##куки можно вставить только для конкретного домена
        # r = cookies_install_hitro(_)

        task = hitro_dict(task, "login")
        save_polube = 1  # полюбе сохраняю?
        if not save_polube and not self.T.want_cookies:
            return 0
        r = self.cookies_save(task)
        return r

    def cookies_install_hitro(self, task={}):
        # хитроф-ии, только если в настройках стоит юзать тогда юзаем
        task = hitro_dict(task, "login")
        if not self.T.want_cookies:
            return 0
        r = self.cookies_install(task)
        return r

    def cookies_install(self, task={}):
        # устанавливаем куки для ака
        fun = "cookies_install"
        d = {
            #'domain':'',#нужно ли только какого-то одного домена инсталить куки?
            "u": "",  # для какого урла мы их хотим инсталить
        }
        task = add_defaults(task, d)
        T = Bunch(task)

        u = T.u
        if u == "":
            u = self.url()

        domain = ""
        if u != "":
            domain = get_domen_from_url(u)

        logger.debug('[%s, domain "%s" from url "%s"' % (fun, domain, u))
        f = self.get_f_cookie(task)
        if not os.path.isfile(f):
            logger.debug("no file %s with cookies" % f)
            return 0

        try:
            cookies = obj_from_file(f)
            if type(cookies) == type({}) and cookies.has_key("cookies"):
                cookies = cookies["cookies"]

            i = 0
            for cookie in cookies:
                t = str(cookie)
                i += 1
                logger.debug("	%s/%s %s %s" % (i, len(cookies), fun, cookie))

                # проверка - инсталим только для некоторого спецурла
                propusk = 0
                cookie_domain = cookie["domain"]
                if domain != "":
                    if domain.find(cookie_domain) == -1:
                        propusk = 1

                if propusk:
                    logger.debug("	propusk cookie %s" % cookie)
                    continue

                try:
                    self.driver.add_cookie(cookie)
                except Exception as er:
                    logger.error("%s error: %s" % (fun, er))
            return 1
        except Exception as er:
            logger.error("%s error" % (fun, er))
            return 0

    def cookies_save(self, task={}):
        # сохраняем куки ака
        f = self.get_f_cookie(task)
        fun = "cookies_save"
        logger.debug("[%s" % fun, f)
        try:
            # посмотреть куки вручную - javascript:alert(document.cookie);
            # к сожалению парсит куки только домена текущей страницы
            cookies = task.get("cookies", self.get_cookies())
            logger.debug("	cookies: %s" % cookies)
            show_list(cookies)

            # если я хочу фильтровать куки
            want_filter = 1
            want_filter = 0
            if want_filter:
                cookies_good = []
                for kuka in cookies:
                    t = str(kuka)
                    if t.find("accounts.google.com") == -1:
                        continue
                    cookies_good.append(kuka)

                if len(cookies_good) == 0:
                    logger.warning("ups, no good cookies")
                    wait_for_ok()
                    return 0
                else:
                    cookies = cookies_good[:]
                logger.debug("%s good cookies" % len(cookies))
                show_list(cookies)

            obj_to_file(cookies, f)
            logger.debug("+]")
            return 1
        except Exception as er:
            logger.error("%s error: %s" % (fun, er))
            return 0

    # >>>>>>>>>>>>>>>>работа с куками

    # <<<<<<<<<<<<<<<<annex
    def prepare_binary_with_annex(self, f, annex=""):
        fun = "prepare_binary_with_annex"
        logger.debug("[%s (f=`%s`, annex==`%s`)" % (fun, f, annex))
        if annex == "":
            return f

        ff_binary = self.generate_path_with_annex(f, annex)

        if annex != "":
            self.kill_process(ff_binary)

        self.create_binary_if_necessary(f, ff_binary)
        logger.debug("+%s %s]" % (fun, ff_binary))
        # wait_for_ok()
        return ff_binary

    def generate_path_with_annex(self, f="", annex=""):
        """
			уникальный путь, например каждый поток может свой фаерфокс запускать
		"""
        fun = "generate_path_with_annex"

        logger.debug("[%s: " % (fun))
        f_new = f
        m = "not changed"
        if annex != "":
            f_new = f.replace(".exe", "_%s.exe" % annex)
            m = "changed to %s" % f_new
        logger.debug("%s]" % m)

        return f_new

    def kill_process(self, ff_binary=""):
        """
			удалить все процессы с именем
		"""
        f_name = os.path.basename(ff_binary)
        kill_werfault(programs=[f_name])

    def create_binary_if_necessary(self, f_old, f_new):
        """
		todo:
			бинарник должен быть достаточно свежим (раз в час пересоздаем - авось)
		"""
        if f_new == f_old:
            return

        size_new = get_file_size(f_new)
        size_old = get_file_size(f_old)
        life = file_life(f_new)

        logger.debug(
            """binary info:
			size_old %s, f_old = %s
			size_new %s, f_new = %s (life=%s)"""
            % (size_old, f_old, size_new, f_new, life)
        )

        if size_new != size_old or size_new == -1 or life > 60 * 60 * 1:
            logger.debug("COPY")
            # wait_for_ok()
            rmfile(f_new)
            copy_file_new(f_old, f_new)
        else:
            logger.debug("no need to copy")

        # wait_for_ok()

        return 1

    def check_browser_is_controlled(self):
        return check_browser_is_controlled(self.driver)


def check_browser_is_controlled(driver):
    fun = "check_browser_is_controlled"
    controlled = True
    try:
        title = driver.title
    except Exception as er:
        error = str(er)
        logger.error(f"error={er}")
        if 1 or (
            "Tried to run command without establishing a connection" in error
            or "no such window" in error
        ):
            controlled = False
    logger.debug(f"   +{fun}={controlled}")
    return controlled


# >>>>>>>>>>>>annex


def element_scroll(element):
    # прокручиваем к нашему элементу
    # http://blog.likewise.org/2015/04/scrolling-to-an-element-with-the-python-bindings-for-selenium-webdriver/
    driver = element._parent
    driver.execute_script("return arguments[0].scrollIntoView();", element)
    driver.execute_script("window.scrollBy(0, -150);")
    time.sleep(0.3)

    # http://www.emalis.com/2013/10/scroll-list-with-keys-arrow_down-to-a-visible-element-selenium-python/
    # 	другой тип прокрутки
    return 1


def sel_highlight_element(element, sleep=2):
    """Highlights (blinks) a Selenium Webdriver element"""
    fun = "highlight_element"
    try:
        sel_highlight_element_one(element, sleep)
    except Exception as er:
        logger.error("error %s: %s" % (fun, er))
        return 0
    return 1


def sel_highlight_element_one(element, sleep=1.3):
    """Highlights (blinks) a Selenium Webdriver element"""
    fun = "sel_highlight_element_one"
    logger.debug("[%s" % fun)
    driver = element._parent

    def apply_style(s):
        driver.execute_script(
            "arguments[0].setAttribute('style', arguments[1]);", element, s
        )

    original_style = element.get_attribute("style")
    logger.debug("	original_style: %s" % original_style)
    background_color = "yellow"
    background_color = "rgba(255, 255, 0, .4)"  #    /*  40% opaque yellow */
    apply_style("background: %s; border: 2px solid red;" % background_color)

    if sleep == -1:
        return 1

    time.sleep(sleep)
    apply_style(original_style)
    logger.debug("+]")


def selenium_test_screenshot():
    f_step00 = "temp/screenshot.html"
    _ = {}
    S = selenium_class(_)  # берем класс селениума
    p = S.sgp("http://www.google.com/recaptcha/api2/demo", f_step00)

    rc_sett = {
        "rc_recaptcha_bad_question_exit": 3,
        "rc_recaptcha_hack": 1,  # хакаем рекапчу?
    }
    rc_sett = {
        "rc_recaptcha_hack": 0,
        "rc_max_miga": 1,
        "rc_max_recaptcha_reload": 1,  # макс. перезагрузок капчи
        "rc_cnt_max_errors_with_captcha": 1,  # сколько раз вообще пытаемся перезагрузить картинку
        "rc_emulate_guess_recaptcha": 1,
    }
    user = {
        "S": S,
        "sett": rc_sett,
    }
    # t = find_from_to_one('<div data-sitekey=', '</textarea>', p)
    t = "1"
    if t != "":
        captcha_clicked = recaptcha_guesser(user)
        logger.debug(
            "captcha_clicked: %s %s" % (type(captcha_clicked), captcha_clicked)
        )


def generate_miga_image(f_captcha, num_to_file, f_rezult):
    # сначала берем размер картинки всей
    fun = "generate_miga_image"
    logger.debug("[%s" % fun)
    rmfile(f_rezult)

    im = Image.open(f_captcha)
    width_, height_ = im.size
    logger.debug("img size: %s %s" % (width_, height_))

    if len(num_to_file) == 0:
        return f_captcha

    cols = -1
    rows = -1
    cels = -1

    num_to_cel = {}
    for num in num_to_file:
        fimg = num_to_file[num]
        im_small = Image.open(fimg)
        width, height = im_small.size
        logger.debug("img size: %s %s" % (width, height))
        if cols == -1:
            cols = width_ / width
            rows = height_ / height
            cels = cols * rows

            # logger.debug('cols %s, rows %s, cels %s' % ( cols, rows, cels) )

            nc = 0
            for j in range(rows):
                for i in range(cols):
                    nc += 1
                    num_to_cel[nc] = [i, j]

            show_dict(num_to_cel)

        x, y = num_to_cel[num]
        # logger.debug('num: %s, col %s, row %s' % (num, x, y))

        offset = (x * width, y * height)
        im.paste(im_small, offset)

    # wait_for_ok()
    im.save(f_rezult)

    if os.path.isfile(f_rezult):
        logger.debug("+%s]" % fun)
        return 1
    # return f_rezult

    return 0


def clear_temp_directories(task={}):
    """
	чистка темповских папок
	"""
    fun = "clear_temp_directory"

    d = {
        "chistka_max_temp_directories": 10,
    }
    task = add_defaults(task, d)
    T = Bunch(task)

    logger.debug("[%s" % fun)

    t = 1
    t = 0
    if t:
        logger.debug("propusk")
        return True

    all_dirs = r"c:\Users\kyxa\AppData\Local\Temp".split("\n")

    dir_to_seconds = []
    for d in all_dirs:
        d = d.strip()
        if d == "":
            continue

        logger.debug("search in %s" % d)
        t = 0
        t = 1
        if t:
            # delete = 0
            files = get_all_file_names(d)
            good_names = ["driver_log", "profiler_log"]
            for f in files:
                name = os.path.basename(f)
                if name.find("tmpaddon") != -1 and file_life(f) > 60 * 10:
                    logger.debug("		deleting %s" % f)
                    rmfile(f)
                    continue

                continue

                for good_name in good_names:
                    if name.find(good_name) != -1:
                        # delete = 1
                        logger.debug("deleting %s" % f)
                        rmfile(f)

        dirs = get_dirs(d)
        for d0 in dirs:
            d_full = "%s/%s" % (d, d0)
            life = file_life(d_full)
            # wait_for_ok()

            # f = '%s/driver_log' % (d_full)
            d2 = "%s/%s" % (d_full, "webdriver-py-profilecopy")
            f_prefs = "%s/prefs.js" % (d_full)

            # logger.debug('%s %s' % (d0, d2))
            delete = 0
            if (
                d_full.find(".webdriver.xpi") > 0
                or os.path.isdir(d2)
                or os.path.isfile(f_prefs)
            ):
                # logger.debug('    %s %s' % (d_full, life))
                # delete = 1

                if life > 60 * 20:
                    delete = 1

                if delete:
                    logger.debug(
                        "delete directory %s, life %s" % (d_full, life)
                    )
                    rmdir(d_full)
                # wait_for_ok()
                else:
                    dir_to_seconds.append([life, d_full])

    # если надо - удаляю даже тех которых слишком много
    dir_to_seconds.sort()
    dir_to_seconds.reverse()
    show_list(dir_to_seconds)
    cnt_leave = T.chistka_max_temp_directories
    if len(dir_to_seconds) > cnt_leave:
        for i in range(len(dir_to_seconds) - cnt_leave):
            d_ = dir_to_seconds[i]
            seconds, d = d_
            logger.debug(
                '    deleting with seconds %s - dir "%s"' % (seconds, d)
            )
            rmdir(d)

    t = 0
    if t:
        # еще чищу капчи мусорные плохие
        dirs = ["log/select_captchas"]
        i = 0
        for d in dirs:
            i += 1
            logger.debug("\n" * 2 + "clear dir %s/%s %s" % (i, len(dirs), d))
            files = get_all_file_names(d)
            logger.debug("	found %s files" % len(files))
            j = 0
            for f in files:
                j += 1
                if j % 100 == 0:
                    logger.debug(len(files) - j)
                name = os.path.basename(f)
                if name.find("captcha_") != -1:
                    life = file_life(f)
                    if life > 60 * 60:
                        rmfile(f)

    logger.debug("+]")


def clear_temp_directories_timed(task={}):
    # wait_for_ok('no_clear_temp_directory:"%s"'%sett['no_clear_temp_directory'])
    d = {
        "func": clear_temp_directories,
        "seconds": 60 * 10,
        "seconds": 60 * 6,
        #'seconds':sett['chistka_seconds_directory_timed'],
    }
    task = add_defaults(task, d)
    timed_func(task)


def selenium_test_min(u_download="http://google.com"):
    fun = "selenium_test_min"

    f_firefox = r"c:\Program Files\Mozilla Firefox UA\firefox.exe"
    f_firefox = r"c:\Program Files\Mozilla Firefox44\firefox.exe"
    t = 1
    t = 0
    if t:
        profile = webdriver.FirefoxProfile()
        # binary = ''
        binary = FirefoxBinary(f_firefox)

        logger.debug(1)
        driver = webdriver.Firefox(profile, firefox_binary=binary)
    # driver = webdriver.Firefox(profile)
    else:

        from selenium import webdriver
        from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

        binary = FirefoxBinary(f_firefox)
        driver = webdriver.Firefox(firefox_binary=binary)

    # переход на гугл?
    t = 1
    if t:
        logger.debug("download %s" % u_download)
        driver.get(u_download)
        logger.debug("+")
        page = driver.page_source

        logger.debug("page_len: %s" % len(page))

        text_to_file(page, "temp/%s.html" % fun)

    return driver


def check_is_selenium_element(k):
    """
		проверяем - это елемент селениума?
	"""
    tip = str(type(k))
    # logger.debug('tip %s' % tip)
    if (
        tip == "<class 'selenium.webdriver.remote.webelement.WebElement'>"
        or tip.find("FirefoxWebElement") != -1
    ):
        return 1
    return 0


def parse_cookies_from_txt_buyaccs(txt=""):
    """
		buyaccs дает к аккам куки вида
			.google.com	TRUE	/	FALSE	04/23/2021 08:34:33	SID	Vwd2s9aJi1sxbJaWNtE_DK7MJSkdn2i5118ecIpVoVZDZLe133ukSx6lpf5UrmeBIQXTeg.	FALSE	FALSE


		мне их нужно привести в вид
			{"domain":".google.com", "name":"HSID", "value":"AQ01BTrLQ4vnGdrRx", "expiry":1597330369, "path":"/", "httpOnly":True, "secure":False}
	"""
    cookies = []
    items = clear_list(txt.split("\n"))
    for item in items:
        parts = item.split("	")
        # show_list(parts)
        # 0       .google.com
        # 1       TRUE
        # 2       /
        # 3       FALSE
        # 4       04/23/2021 08:34:33
        # 5       SID
        # 6       Vwd2s9aJi1sxbJaWNtE_DK7MJSkdn2i5118ecIpVoVZDZLe133ukSx6lpf5UrmeBIQXTeg.
        # 7       FALSE
        # 8       FALSE

        # .google.com - domain
        # TRUE - hostOnly
        # / - cookie будут доступны во всем домене
        # FALSE - secure
        # 04/15/2021 05:29:05 [expires] "Mon/DD/YYYY HH:MM:SS"
        # SID Twcfs5Ptwxzx2hr2oD2dNW0tBErbkiPipjGIWzqL0-KPutKS_aCHqmWl_BeKfgG-7Iu-JA.
        # FALSE - httpOnly
        # FALSE - session

        # {"domain":".google.com", "name":"HSID", "value":"AQ01BTrLQ4vnGdrRx", "expiry":1597330369, "path":"/", "httpOnly":True, "secure":False}

        num_to_key = {
            0: "domain",
            1: "hostOnly",
            2: "path",
            3: "secure",
            4: "expiry",
            5: "name",
            6: "value",
            7: "httpOnly",
            8: "session",
        }
        t_f = "%m/%d/%Y %H:%M:%S"
        kuka = {}
        for num, key in num_to_key.iteritems():
            value = parts[num]
            # logger.debug(' %s %s %s' % ( num, key, value ) )
            if key in "expiry":
                value = int(time.mktime(time.strptime(value, t_f)))

            if value in ["FALSE"]:
                value = False
            if value in ["TRUE"]:
                value = True

            kuka[key] = value
        cookies.append(kuka)

    # wait_for_ok()

    return cookies


def get_any_cookies_from_file(f=""):
    """
	парсим куки или из обычного текстового файла, или из объекта сериализированного
	"""
    fun = "get_any_cookies_from_file"
    cookies = []
    if not os.path.isfile(f):
        logger.error("[%s error: no file with cookies: %s" % (fun, f))
        return cookies

    is_error = 0
    try:
        cookies = obj_from_file(f)
        logger.debug("  cookies from file %s: %s" % (f, cookies))
    except Exception as er:
        logger.error("error %s" % er)
        is_error = 1

    if cookies == 666 or is_error:
        m = "todo: work with text file"
        logger.warning(m)
        # wait_for_ok(m)

        txt = text_from_file(f)
        logger.debug("txt: %s" % txt)
        cookies = parse_cookies_from_txt_buyaccs(txt)

    return cookies


# searching recaptcha variables


def sel_get_javascript_variable(driver="", name=""):
    fun = "sel_get_javascript_variable"
    logger.debug('[%s for name "%s" (driver %s)' % (fun, name, driver))
    # sleep_(10)

    t = 1
    t = 0
    if t:
        js_temp = "return window.name;"
        js_temp = "return window.location;"
        logger.debug(" run js_temp: %s" % js_temp)
        r = driver.execute_script(js_temp)
        logger.debug("result: %s" % r)

    js = "%s" % name
    js = "return %s" % name
    js = "alert(%s);" % name
    js = "print %s;" % name
    js = "return %s;" % name

    logger.debug("run js: `%s`" % js)
    r = driver.execute_script(js)

    logger.debug("type %s]" % type(r))
    return r


def get_recaptcha_containerPath_from_variable(dct={}):
    """
		real_dct = {
			'sitekey': 'nah',
		}
		dct = {
			'V0': {},
			'id': 0,
			'JM': '<div#GzWUuf.STPjcd>',
			'vm': '<div#GzWUuf.STPjcd>',
			'V_real': {
					'o': real_dct,
					},
			}
	"""
    found = False
    if not isinstance(dct, dict):
        logger.debug("error - not dictionary")
        return found

    found_keys = []
    i = 0
    for k in dct:
        i += 1
        logger.debug('	%s, check key "%s"' % (i, k))

        dct2 = dct[k]
        # ищем первый словарь
        if not isinstance(dct2, dict):
            continue

        for k2 in dct2:
            dct3 = dct2[k2]
            if not isinstance(dct3, dict):
                continue

            logger.debug("	checking key `%s.%s` in `%s`" % (k, k2, dct3))
            if "sitekey" in dct3:
                found = "%s.%s" % (k, k2)
                found_keys.append(found)
                break

    logger.debug("found keys: %s" % found_keys)

    if len(found_keys) == 1:
        found = found_keys[0]
    elif len(found_keys) > 1:
        logger.debug("ups, get last key")
        found = found_keys[-1]
    else:
        logger.error("ups, no keys found")
        found = False

    return found


def test_reconnect(_):
    """
	проверяем умеем ли переподключаться
		window.navigator.webdriver
	"""
    fun = "test_reconnect"
    S = selenium_class(_)  # берем класс селениума

    wait_for_ok("%s started" % fun)
    f_temp = "temp/test_reconnect.html"

    u_driver_test = "%s/session/%s/url" % (
        S.command_executor_url,
        S.session_id,
    )
    logger.debug("u_driver_test: %s" % u_driver_test)
    urls = [
        # u_driver_test,
        "http://beta777.com/data/test_detectable/test_my/test_detectable.html",
        S.command_executor_url,
    ]
    for u_check in urls:
        p = S.sgp(u_check, f_temp)
        sleep_(1)
        wait_for_ok("opened page?")

    t = 1
    t = 0
    if t:
        S.good_exit()

    wait_for_ok("started browser, try to relogin")

    # wait_for_ok('opened?')
    return


def test_non_detectable(_):
    """
	проверяем детектабельность
		window.navigator.webdriver
	"""
    u_check = "https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html"
    u_check = (
        "http://beta777.com/data/test_detectable/test0/test_detectable.html"
    )
    u_check = (
        "http://beta777.com/data/test_detectable/test1/test_detectable.html"
    )
    u_check = (
        "http://beta777.com/data/test_detectable/test_my/test_detectable.html"
    )
    f_step00 = "temp/screenshot.html"
    S = selenium_class(_)  # берем класс селениума
    f_temp = "temp/test_non_detectable.html"
    p = S.sgp(u_check, f_temp)
    sleep_(1)
    # S.scroll_down()

    names = [
        "window.navigator.webdriver",
    ]

    non_detectable = 1
    for name in names:
        value = sel_get_javascript_variable(S.driver, name)
        logger.debug(
            "	name `%s`, value: `%s`, type %s" % (name, value, type(value))
        )
        if value == True:
            non_detectable = 0

    t = 1
    t = 0
    if t:
        S.good_exit()

    wait_for_ok("started browser, try to relogin")

    # wait_for_ok('opened?')
    return non_detectable


def generate_non_detectable_extension():
    """
		для того, чтобы гмейл не понял что мы используем селениум, нужно вкручивать спецрасширение
		делаю его уникальным для каждого запуска, чтобы не догадался потом гугль что у всех аков одного расширение
	"""
    fun = "generate_non_detectable_extension"
    base_extension = os.path.join(
        os.path.realpath(os.path.dirname(__file__)),
        "data",
        "!firefox_extensions",
        "non_detectable_1",
    )
    if not dir_exists(base_extension):
        wait_for_ok(
            "%s ERROR - no base_extension directory %s" % (fun, base_extension)
        )

    new_extension_name = generate_markov_phrase(1)[0]
    # new_extension_name = 'demo_name'

    new_extension = os.path.abspath("temp/extensions/%s" % new_extension_name)

    # new_extension = r'd:\server\usr\local\python\Lib\site-packages\gmail_register\data\!extensions\generated\%s' % new_extension_name
    files = get_all_file_names(base_extension)
    for f in files:
        f_name = os.path.basename(f)

        text = text_from_file(f)

        # шифруем расширение
        replaces = []

        if f_name == "manifest.json":
            manifest_version = randint(1, 10)
            manifest_version = 1
            ver1 = randint(0, 10)
            ver2 = randint(0, 100)
            ver3 = randint(0, 100)
            replaces = [
                [
                    '"name": "non_detectable_1",',
                    '"name": "%s",' % new_extension_name,
                ],
                [
                    '"id": "non@intoli.com"',
                    '"id": "%s@_gmail.com"' % new_extension_name,
                ],
                [
                    '"version": "1.0.0",',
                    '"version": "%s.%s.%s",' % (ver1, ver2, ver3),
                ],
                # ['"manifest_version": 2,', '"manifest_version": %s,' % manifest_version],	#нельзя менять?
                # ['', '' % ],
            ]

        elif f_name == "content.js":
            replaces = [
                [
                    'script.src=browser.extension.getURL("myscript.js");',
                    'script.src=browser.extension.getURL("%s.js");'
                    % new_extension_name,
                ],
            ]

        elif f_name == "myscript.js":
            pass
            f_name = "%s.js" % new_extension_name

        text = no_probely(text, replaces)

        f_new = "%s/%s" % (new_extension, f_name)
        text_to_file(text, f_new)

    return new_extension


def get_selenium_pid_from_driver(driver, want_pid_from_driver_capabilities=1):
    fun = "get_selenium_pid_from_driver"
    logger.debug("[%s " % fun)

    pid = "-1"
    reason = ""
    while True:
        reason = "driver_capabilities"
        if want_pid_from_driver_capabilities:
            # driver_capabilities = driver.capabilities
            # wait_for_ok(driver_capabilities)
            try:
                driver_capabilities = driver.capabilities
                # show_dict(driver_capabilities)
                # wait_for_ok(driver_capabilities)
                pid = driver_capabilities.get("moz:processID", pid)
                break
            except Exception as er:
                logger.error("error %s" % er)

        if pid == "-1":
            logger.debug(1)
            try:
                pid = driver.binary.process.pid
            except Exception as er:
                er = str(er)
                if er not in [
                    "'WebDriver' object has no attribute 'binary'",
                    "'FirefoxBinary' object has no attribute 'process'",
                ]:
                    logger.error("error %s: %s" % (fun, er))

        if pid == "-1":
            logger.debug(2)
            try:
                pid = driver.service.process.pid
            except Exception as er:
                er = str(er)
                if er != "'WebDriver' object has no attribute 'binary'":
                    logger.error("error %s: %s" % (fun, er))
                pid = "-1"

        break
    logger.debug("pid=%s, reason=%s" % (pid, reason))

    t = 1
    t = 0
    if t:
        lst = parse_tasklist()

        for _ in lst:
            if _["pid"] in [int(pid)]:
                show_dict(_)
            # [parse_tasklist in 0.51 seconds]
            # 	image
            # 			"geckodriver.exe"
            # 	mem_usage
            # 			"8 984 КБ"
            # 	pid
            # 			13092
            # 	session_name
            # 			"RDP-Tcp#0"
            # 	session_num
            # 			"2"

    logger.debug("+%s (pid %s)]" % (fun, pid))
    # wait_for_ok('have pid?')

    return pid


def connect_to_chrome(port=6813,):
    _ = {
        "s_browser": "chrome",
        "debuggerAddress": "127.0.0.1:%s" % port,
        "s_hitro_session": 0,
    }
    S = selenium_class(_)  # берем класс селениума
    return S


def wrap_selenium_class(task={}):
    """
		я люблю класс селениума :)
		это селениум по драйверу, но без автостарта
	"""
    d = {
        "s_driver": "",
        "s_from_old_selenium": 1,
        "s_autostart": 0,
    }
    task = add_defaults(task, d)
    S = selenium_class(task)  # берем класс селениума
    return S


def save_selenium_driver(driver, f=""):
    fun = "save_selenium_driver"
    logger.debug("[%s driver %s to %s]" % (fun, driver, f))

    obj_to_file_p(driver, f)
    # try:
    #    obj_to_file_p(driver.driver, f) #если селениум отправил сюда
    # except Exception as er:
    #    obj_to_file_p(driver, f)


def save_selenium(S, f=""):
    obj_to_file_p(S, f)


def reconnect_with_savedDriver(f=""):
    """
		переконнектиться использую файл с драйвером
	"""
    driver = obj_from_file_p(f)
    _ = {
        "s_driver": driver,
    }
    S = wrap_selenium_class(_)
    return S


def element_to_html(element="", mode="innerHTML"):
    fun = "element_to_html"
    html = None
    if element:
        try:
            html = element.get_attribute(mode)
        except Exception as er:
            html = None
            logger.error("ERROR %s: %s" % (fun, er))
        # html = element.get_attribute('outerHTML')
    return html


def generate_js_for_click_xpath_with_js(
    xpath="", node_order="first", mode="real_random"
):
    """
    в идеале хочу, чтобы кликало на
        first
        any
        all
    """
    node_orders = {
        "first": "XPathResult.FIRST_ORDERED_NODE_TYPE",
        "any": "XPathResult.ANY_UNORDERED_NODE_TYPE",
    }
    node_order_js = node_orders.get(node_order, node_order)
    js = (
        """
    function shuffle(array) {
      let currentIndex = array.length,  randomIndex;

      // While there remain elements to shuffle...
      while (currentIndex != 0) {

        // Pick a remaining element...
        randomIndex = Math.floor(Math.random() * currentIndex);
        currentIndex--;

        // And swap it with the current element.
        [array[currentIndex], array[randomIndex]] = [
          array[randomIndex], array[currentIndex]];
      }

      return array;
    }
    
    var node_order = '[node_order]';
    var mode = '[mode]';
    var elements = [];
    var cnt_elements = 0;
    var cnt_clicks = 0;
    if (mode == 'old') {
        var xPathRes = document.evaluate ('[xpath]', document, null, [node_order_js], null);
        element = xPathRes.singleNodeValue;
    }
    else{
        let query = document.evaluate('[xpath]', document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
        for (let i = 0, length = query.snapshotLength; i < length; ++i) {
            elements.push(query.snapshotItem(i));
        }
        cnt_elements = elements.length;
        if (cnt_elements==0) {
            var element = false;
        }
        else {
           if (node_order == 'any') {
               shuffle(elements);
           }
           for (j = 0; j < elements.length; ++j) {
                element = elements[j];
                console.log(`click ${j+1}/${elements.length} element ${element}`);
                console.log(element);
                cnt_clicks = cnt_clicks + 1;
                element.click();
                if (node_order != 'all') {
                    break;
                }
            }
        }
    }

    console.log(`click_xpath_js cnt_clicks=${cnt_clicks}/${cnt_elements} for xpath=[xpath] with node_order=${node_order}`);
    return cnt_clicks;
    """.replace(
            "[xpath]", xpath
        )
        .replace("[node_order]", node_order)
        .replace("[node_order_js]", node_order_js)
        .replace("[mode]", mode)
    )
    # self.execute_script(js)
    return js


def generate_js_for_click_xpath_with_js_without_all(
    xpath="", node_order="first", mode="real_random"
):
    """
    в идеале хочу, чтобы кликало на
        first
        any
        all
    """
    node_orders = {
        "first": "XPathResult.FIRST_ORDERED_NODE_TYPE",
        "any": "XPathResult.ANY_UNORDERED_NODE_TYPE",
    }
    node_order_js = node_orders.get(node_order, node_order)
    js = (
        """
    var node_order = '[node_order]';
    var mode = '[mode]';
    var elements = [];
    var cnt_elements = 0;
    if (mode == 'old') {
        var xPathRes = document.evaluate ('[xpath]', document, null, [node_order_js], null);
        element = xPathRes.singleNodeValue;
    }
    else{
        let query = document.evaluate('[xpath]', document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
        for (let i = 0, length = query.snapshotLength; i < length; ++i) {
            elements.push(query.snapshotItem(i));
        }
        cnt_elements = elements.length;
        if (cnt_elements==0) {
            var element = false;
        }
        else {
            if (node_order == 'first') {
                var element = elements[0];
            }
            else{
                var element = elements[Math.floor(Math.random()*elements.length)];
            }
        }
    }

    console.log(`click_xpath_js element=${element} for xpath=[xpath] with ${cnt_elements} for node_order=${node_order}`);
    console.log(element);
    // console.log(xPathRes);

    if (element){
        element.click();
        return 1;
        }
    else {
        return 0;
    }
    """.replace(
            "[xpath]", xpath
        )
        .replace("[node_order]", node_order)
        .replace("[node_order_js]", node_order_js)
        .replace("[mode]", mode)
    )
    # self.execute_script(js)
    return js


def turn_on_responsive_responsive_design_mode(S):
    driver = S.driver
    # sent = S.send_to_body(Keys.CONTROL + Keys.SHIFT + 'M')

    # Не отправляет горячих клавиш?
    t = 0
    if t:
        element = S.find_element_by_xpath("//body")
        logger.debug("element=%s" % element)
        sent = element.send_keys(Keys.CONTROL + Keys.SHIFT + "M")
        # logger.debug('sent=%s to element' % (sent, element))

    t = 0
    if t:
        mobile_emulation = {
            "deviceMetrics": {"width": 360, "height": 640, "pixelRatio": 3.0},
            "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19",
        }

        chrome_options = webdriver.ChromeOptions()

    t = 1
    if t:
        width = 1280
        height = 950
        # r = driver.set_window_size(width, height)

        t = 1
        if t:
            js = """
             window.innerHeight = [height];
             window.innerWidth = [width];
             console.log('changed window sizes to [width]*[height]');
            """
            js = no_probely(js, {"[width]": width, "[height]": height,})
            r = driver.execute_script(js)
            logger.debug("r=%s" % r)


def setup_official_extension_to_selenium_NOT_POSSIBLE(
    S,
    extension_url=r"https://chrome.google.com/webstore/detail/urban-free-vpn-proxy-unbl/eppiocemhmnlbhjplcgkofciiegomcon",
):
    """ставлю расширение в браузер
    оказалось невозможно
    уже стоит:
        <div role="button" class="dd-Va g-c-wb g-eg-ua-Uc-c-za g-c" aria-label="Видалити з Chrome" tabindex="0" style="user-select: none;"><div class="g-c-Hf"><div class="g-c-x"><div class="g-c-R  webstore-test-button-label">Видалити з Chrome</div></div></div></div>

    поставить:
        <div role="button" class="dd-Va g-c-wb g-eg-ua-Uc-c-za g-c-Oc-td-jb-oa g-c" aria-label="Додати в Chrome" style="user-select: none;" tabindex="0"><div class="g-c-Hf"><div class="g-c-x"><div class="g-c-R  webstore-test-button-label">Додати в Chrome</div></div></div></div>
    """
    want_open_url = True
    want_setup = True

    debug = True
    if debug:
        want_open_url = False
        # want_setup = False

    xpaths = {
        # "installed": r'//div[@role="button"][contains(@class, "g-c-Oc-td-jb-oa")]',
        # "to_install": r'//div[@role="button"][contains(@class, "g-c-Oc-td-jb-oa")]',
        "to_install": r'//div[@role="button"][contains(@aria-label, "Додати")]',
        "installed": r'//div[@role="button"][contains(@aria-label, "Видалити")]',
    }
    xpather = Xpather(dct=xpaths)

    if want_open_url:
        opened = S.sgp(extension_url)

    if want_setup:
        S.wait_for_first_existing_situation(
            situation_to_xpath=xpaths, timeout=20, debug=False
        )


if __name__ == "__main__":
    # os._exit(0)

    spec = "want_test_detectable"
    spec = "test_binary_annex"
    spec = "portable_browser"
    spec = "portable_browser_min"
    spec = "want_test_reconnect"
    spec = "test_connect_to_existing_chrome"
    spec = "generate_js_for_click_xpath_with_js"
    spec = "min_chrome"

    logger.info("spec=%s" % spec)

    f_chrome_driver = r"s:\!data_main\chromedrivers\chromedriver_90.exe"
    f_chrome_driver = r"s:\!data_main\chromedrivers\chromedriver_85.exe"
    f_chrome_driver = r"s:\!data_main\chromedrivers\chromedriver_89.exe"
    s_chrome_binary = r"s:\!installs\!portable_browsers\GoogleChromePortable\App\Chrome-bin\chrome.exe"

    if spec == "generate_js_for_click_xpath_with_js":
        xpath = '//div[not(contains(@class, "Suspended"))]/span[contains(@class, "_Odds")][normalize-space(text()) > 0]'
        mode = "any"
        print(generate_js_for_click_xpath_with_js(xpath, mode))

    elif spec == "min_chrome":
        # driver = webdriver.Chrome()
        # simple_pickle(driver)
        # wait_for_ok('pickled1?')

        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = s_chrome_binary

        # chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:6814")
        logger.info("chrome_options=%s" % chrome_options)

        # desired_capabilities = {
        #     'goog:chromeOptions': {'debuggerAddress': '127.0.0.1:6814', 'args': [],
        #                            'extensions': []}, 'platform': 'ANY',
        #     'browserName': 'chrome', 'version': ''
        # }
        args = {
            "executable_path": f_chrome_driver,
            "chrome_options": chrome_options,
            # "desired_capabilities": desired_capabilities,
        }
        driver = webdriver.Chrome(**args)
        logger.info("driver=%s" % driver)

        executor_url = driver.command_executor._url
        session_id = driver.session_id
        logger.info(
            "session_id %s, executor_url %s" % (session_id, executor_url)
        )

        driver2 = webdriver.Remote(
            command_executor=executor_url, desired_capabilities={}
        )
        driver2.session_id = session_id
        logger.info("driver2: %s %s" % (driver2, driver2.current_url))

        simple_pickle(driver)
        wait_for_ok("pickled?")

    elif spec == "test_connect_to_existing_chrome":
        from selenium.webdriver.chrome.options import Options

        # chrome_options = Options()
        chrome_options = webdriver.ChromeOptions()

        chrome_options.add_experimental_option(
            "debuggerAddress", "127.0.0.1:6814"
        )

        logger.info("chrome_options=%s" % chrome_options)

        desired_capabilities = {
            "goog:chromeOptions": {
                "debuggerAddress": "127.0.0.1:6814",
                "args": [],
                "extensions": [],
            },
            "platform": "ANY",
            "browserName": "chrome",
            "version": "",
        }
        args = {
            "executable_path": f_chrome_driver,
            "chrome_options": chrome_options,
            # "desired_capabilities": desired_capabilities,
        }
        driver = webdriver.Chrome(**args)

        wait_for_ok("created driver?")

        num = randint(1, 1000)
        r = driver.get("https://google.com/search?q=%s" % num)
        title = driver.title
        logger.debug(str([num, title, driver.current_url, r]))
        if str(title) == str(num):
            logger.info("success!")
        else:
            logger.error("error, different titles")

    elif spec == "portable_browser_min":
        from selenium import webdriver
        from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

        s_ff_binary = r"s:\!installs\!portable_browsers\bukvarix.com_2019-2020__Copy\App\Firefox\firefox.exe"
        s_ff_binary = r"s:\!installs\!portable_browsers\bukvarix.com_2019-2020__Copy\firefox.exe"
        firefox_binary = FirefoxBinary(s_ff_binary)
        exec_path = "s:\!data_main\chromedrivers\geckodriver_0.18.0__32.exe"
        args = {
            "executable_path": exec_path,
            "firefox_binary": firefox_binary,
        }
        browser = webdriver.Firefox(**args)

        url = "https://pixelscan.net/"
        browser.get(url)

    if spec == "portable_browser":
        # s_ff_binary_annex = 'potok_0'
        s_ff_binary = r"s:\!installs\!portable_browsers\bukvarix.com_2019-2020__Copy\FirefoxPortable.exe"
        s_ff_binary = r"s:\!installs\!portable_browsers\bukvarix.com_2019-2020__Copy\firefox.exe"
        _ = {
            "s_ff_binary": s_ff_binary,
            # 's_ff_binary_annex': s_ff_binary_annex,
            "firefox_with_marionette": 0,  # фаерфокс с марионете?
        }
        S = selenium_class(_)

        url = "https://pixelscan.net/"
        S.sgp(url)

        os._exit(0)

    # переименование экзешника слету - работает?
    if spec == "test_binary_annex":
        s_ff_binary_annex = "potok_0"
        s_ff_binary = r"C:\Program Files\Firefox Developer Edition\firefox.exe"  #!!!только девелопер-версия катит
        _ = {
            "s_ff_binary": s_ff_binary,
            "s_ff_binary_annex": s_ff_binary_annex,
        }
        S = selenium_class(_)
        os._exit(0)

    if spec == "want_test_reconnect":
        s_browser = "firefox"
        s_browser = "chrome"

        special = ""
        special = "just_profile"

        want_non_detectable = 0
        want_non_detectable = 1

        more_settings = {}

        s_ff_binary = r"C:\Program Files\Firefox Developer Edition\firefox.exe"  #!!!только девелопер-версия катит
        s_profile_path = r""

        if special == "just_profile":
            want_non_detectable = 0
            s_profile_path = (
                r"g:\!data\!firefox_profiles\rust_mozprofile.fQ6mvxDgBPDy"
            )

        elif special == "":
            pass

        else:
            wait_for_ok("unknown special %s" % special)

        command_executor_url = "http://127.0.0.1:50471"
        session_id = "6bec97ee-99ef-46fe-987f-fad89eaef049"

        _ = {
            "want_non_detectable": want_non_detectable,
            "s_hitro_session": 1,  # хитросессия?
            "s_hitro_session": 0,  # хитросессия?
            #'s_command_executor_url': command_executor_url,
            #'s_session_id': session_id,
            "s_ff_binary": s_ff_binary,
            "s_profile_path": s_profile_path,
            "want_random_browser_size": 1,
        }
        # selenium_to_chrome_with_debugger
        if s_browser == "chrome":
            more_settings = {
                "s_browser": "chrome",
                "debuggerAddress": "127.0.0.1:6813",
                "debuggerAddress": "127.0.0.1:6814",
                "s_hitro_session": 0,
                "f_chrome_driver": r"s:\!data_main\chromedrivers\chromedriver_89.exe",
                "s_chrome_binary": r"s:\!installs\!portable_browsers\GoogleChromePortable\App\Chrome-bin\chrome_demo.exe",
            }

        _ = add_defaults(more_settings, _)
        # wait_for_ok(_)

        r = test_reconnect(_)

        print("FINAL RESULT: %s" % r)
        wait_for_ok()
        os._exit(0)

    if spec == "want_test_detectable":
        # учусь тестировать, чтобы гугль не вычислял наш браузер :)
        s_browser = "chrome"
        s_browser = "firefox"

        want_headless = 1
        want_headless = 0
        if want_headless:
            os.environ["MOZ_HEADLESS"] = "1"

        more_settings = {}

        if s_browser == "firefox":
            s_ff_binary = ""
            s_ff_binary = (
                r"c:\Program Files (x86)\Mozilla Firefox 41\firefox.exe"
            )
            s_ff_binary = (
                r"c:\Program Files (x86)\Mozilla Firefox 40\firefox.exe"
            )
            s_ff_binary = r"c:\Program Files\Mozilla Firefox 44.0.2 win64 en-US\firefox.exe"
            s_ff_binary = (
                r"c:\Program Files (x86)\Mozilla Firefox beta 41\firefox.exe"
            )
            s_ff_binary = r"c:\Program Files\Mozilla Firefox\firefox.exe"
            s_ff_binary = r"C:\Program Files\Firefox Developer Edition\firefox.exe"  #!!!только девелопер-версия катит

            s_profile_path = r"c:\Users\kyxa\AppData\Roaming\Mozilla\Firefox\Profiles\awv27khu.hand_made"
            s_profile_path = r"c:\Users\kyxa\AppData\Roaming\Mozilla\Firefox\Profiles\nydkk17r.default-release"
            s_profile_path = r""

            firefox_extensions = [
                # r'd:\server\usr\local\python\Lib\site-packages\gmail_register\data\!extensions\minimum',
                # r'd:\server\usr\local\python\Lib\site-packages\gmail_register\data\!extensions\non_detectable_1',
            ]

            # firefox_extensions = []

            more_settings = {
                "s_browser": "firefox",
                "s_ff_binary": s_ff_binary,
                #'s_profile_path': r'c:\Users\kyxa\AppData\Roaming\Mozilla\Firefox\Profiles\elfdknqk.selenium_tumblr',
                "s_profile_path": s_profile_path,
                "firefox_extensions": firefox_extensions,
            }

        elif s_browser == "chrome":
            more_settings = {
                "s_browser": "chrome",
                "f_chrome_driver": r"c:\chromedrivers\chromedriver_edited.exe",
            }

        _ = {
            "want_non_detectable": 1,
            "s_hitro_session": 0,  # хитросессия?
            "s_hitro_session": 1,  # хитросессия?
        }
        _ = add_defaults(_, more_settings)
        non_detectable = test_non_detectable(_)

        mess = "AAAA - DETECTABLE"
        if non_detectable:
            mess = "URA! NON detectable"

        Show_step(mess)

        os._exit(0)

    t = 1
    t = 0
    if t:
        real_dct = {
            "sitekey": "nah",
        }
        dct = {
            "V0": {},
            "id": 0,
            "JM": "<div#GzWUuf.STPjcd>",
            "vm": "<div#GzWUuf.STPjcd>",
            "V_real": {
                #'o': real_dct,
            },
        }
        name_recaptcha_container = get_recaptcha_containerPath_from_variable(
            dct
        )
        logger.debug("name_recaptcha_container: %s" % name_recaptcha_container)
        os._exit(0)

    t = 1
    t = 0
    if t:
        files = []
        i = 0
        for f in files:
            i += 1
            logger.info("%s/%s %s" % (i, len(files), f))
            r = get_any_cookies_from_file(f)
            logger.info("r: %s" % r)

            logger.info("	%s cookies" % len(r))
            show_list(r[:2])
            wait_for_ok()
        os._exit(0)

    t = 1
    t = 0
    if t:
        u_download = "https://www.google.com/recaptcha/api2/demo"
        driver = selenium_test_min(u_download)
        name_recaptcha_container = guess_recaptcha_containerPath(driver)
        logger.info("name_recaptcha_container: %s" % name_recaptcha_container)
        os._exit(0)

    t = 1
    t = 0
    if t:
        u_download = ""
        driver = selenium_test_min(u_download)
        os._exit(0)

    t = 1
    t = 0
    if t:
        html = """
			<div aria-level="1" role="heading" class="PNenzf" jsname="YASyvd" id="dwrFZd5">
				<div class="NEqwFd">
					<span aria-hidden="true" class="DPvwYc fxCcn sWvkTd"></span>
					<div>Indexing requested</div>
				</div>
			</div>
			"""
        html = """
			<div aria-level="1" role="heading" class="PNenzf" jsname="YASyvd" id="dwrFZd5">
			I0ndexing requested in div
			<span>
					Indexing requested in span
			</span>
			</div>
			"""
        xpath = "//div[@aria-level='1' and contains(text(), 'Indexing requested')]"  # не работает
        xpath = "//div[@aria-level='1' and contains(., 'Indexing requested')]"  # работает

        # xpath2 = '//button[contains(., "%s")]' % button_text  #!!!not working
        # xpath4 = "//button[text()[contains(.,'%s')]]" % button_text #!!!working
        # xpath31 = "//button[text()[contains(.,'%s')]]" % button_text #!!!working

        # xpath1 = '//button[contains(text(), "%s")]' % button_text  #!!!not working
        # xpath3 = "//button[text()[contains(text(),'%s')]]" % button_text #!!!working

        # xpath_ = "//span[contains(@class,'fre')]"#!!!working

        logger.info("isXpath: %s" % isXpath(html, xpath))
        os._exit(0)

    t = 1
    t = 0
    if t:
        for i in range(10):
            ua = get_random_useragent()
        os._exit(0)

    t = 1
    t = 0
    if t:
        t = 1
        t = 0
        if t:
            content = """<html>
				<head>
				</head>
				<body>
					<div class="start">
						<p>I am P</p>
					<div/>
					<div class="start">
						<p>I am P</p>
					<div/>
				</body>
			</html>"""

            logger.info(
                "Debug 1: %s" % isXpath(content, "//div[@class='start']")
            )

            logger.info("Debug 2: %s" % isXpath(content, "//div[@id='start']"))

            os._exit(0)

        tip = "bet365"
        tip = "from_gmail"

        detailed = 1
        otl = 0
        otl = 1

        if tip == "bet365":
            content = """
	    <button>
	    <span class="totalStake">0.00</span> <span class="isocode">USD</span>
	    <span class="freeStake"></span>&nbsp;Place Bet
	    </button>
	"""
            button_text = "Place Bet"
            xpath2 = (
                '//button[contains(., "%s")]' % button_text
            )  #!!!not working
            xpath4 = (
                "//button[text()[contains(.,'%s')]]" % button_text
            )  #!!!working
            xpath31 = (
                "//button[text()[contains(.,'%s')]]" % button_text
            )  #!!!working

            xpath1 = (
                '//button[contains(text(), "%s")]' % button_text
            )  #!!!not working
            xpath3 = (
                "//button[text()[contains(text(),'%s')]]" % button_text
            )  #!!!working

            xpath_ = "//span[contains(@class,'fre')]"  #!!!working

            xpath = '//span[@class="errormsg"]'
            xpath2 = '//*[@class="errormsg"]'
            xpath2 = '//*[@role="alert"]'

            xpaths = [
                xpath2,
                xpath4,
                xpath31,
                xpath1,
                xpath3,
                xpath_,
            ]

        elif tip == "from_gmail":
            f = r"d:\kyxa\!code\!actual\!regilki\gmail_2018\my_gmail\temp\class_gmail_selenium\get_current_page.html"
            content = text_from_file(f)

            t = 1
            t = 0
            if t:
                content = find_from_to_one("<body>", "nahposhuk", content)

            xpath2 = '//*[@class="errormsg"]'
            xpath2 = '//*[@role="alert"]'
            xpath = "//span"
            xpath = "//div"
            xpath = "//body"
            xpath = "/input"

            xpath = '//span[@class="errormsg"]'

            xpaths = [
                xpath,
                # xpath2,
            ]

        i = 0
        for xpath in xpaths:
            i += 1
            logger.info(
                "\n" * 2
                + "Debug %s/%s %s:	%s"
                % (
                    i,
                    len(xpaths),
                    xpath,
                    isXpath(content, xpath, otl=otl, detailed=detailed),
                )
            )

        os._exit(0)

    t = 1
    t = 0
    if t:
        d = "log\select_captchas"

        f_captcha = "captcha_9cf44dafeefac5e733586741a24b0e34.jpg"
        nums = [1, 3]

        f_captcha = "%s/%s" % (d, f_captcha)
        f_captcha_miga = "%s/%s" % (d, "captcha_miga.jpg")
        num_to_file = {}
        for num in nums:
            f = "%s\captcha_small_%s.jpg" % (d, num)
            num_to_file[num] = f

        r = generate_miga_image(f_captcha, num_to_file, f_captcha_miga)
        logger.debug("r: %s" % r)
        os._exit(0)

    t = 1
    t = 0
    if t:
        f_step00 = "temp/scroll.html"
        _ = {}
        S = selenium_class(_)  # берем класс селениума
        u = "https://en.wikipedia.org/wiki/Syrian_Democratic_Forces"
        p = S.sgp(u)
        S.scroll_down()
        os._exit(0)

    t = 1
    t = 0
    if t:
        r = selenium_test_screenshot()
        logger.debug(r)

        t = 0
        if t:
            logger.debug("Image=%s" % Image)

            f_captcha = r"log\select_captchas\captcha_b2464cc4a07d28fab1922eaf481cb36a.jpg"
            logger.debug(f_captcha)

            im = Image.open(f_captcha)
            logger.debug("im=%s" % im)
        os._exit(0)

    t = 1
    t = 0
    if t:
        value = "Islas Baleares"
        variants = """
Andalucía
Aragón
Asturias
Canarias
Cantabria
Castilla - La Mancha
Castilla y León
Cataluña
Ceuta
Diputación Foral de Álava
Diputación Foral de Guipúzcoa
Diputación Foral de Navarra
Diputación Foral de Vizcaya
En el extranjero
Extremadura
Galicia
Illes Balears
La Rioja
Madrid
Melilla
Murcia
Valencia
""".split(
            "\n"
        )
        # variants = ['isla1', 'nonono', 'madrid']
        closest = select_closest_phrase(value, variants, 1)
        logger.debug("closest: %s" % closest)
        os._exit(0)

    t = 1
    t = 0
    if t:
        new_extension = generate_non_detectable_extension()
        logger.debug("new_extension: %s" % new_extension)
        os._exit(0)


# селениум - серьезные вложения
#'//button[@type="button"]/span[@class="ui-button-text"]').click()


##размер браузера берем
# 	logger.debug("example grabbing size with wx (wxWidgets)")
# 	nav = webdriver.Firefox()
# 	app = wx.App(False) #wx.App(False) # the wx.App object must be created first.
# 	screenxy = wx.GetDisplaySize()  # returns a tuple
##	nav.set_window_size(screenxy[0], screenxy[1])

# 	еще так можно:
# 		selenium.getEval("window.resizeTo(X, Y); window.moveTo(0,0);")
#
# 	а так клаву посылать:
# 		from selenium.webdriver.common.keys import Keys

# 		br = webdriver.Firefox()
# 		zoomAction = ActionChains(br)
# 		body = br.find_element_by_tag_name('body')
# 		for i in range(2):
# 		    zoomAction.send_keys_to_element(body,Keys.CONTROL,"+").perform()


# позиция элемента в яваскрипте:
# 	In Javascript, I can get the offsetTop and offsetLeft values of any element in the DOM:

# 	var element    = document.getElementById("some_id");
# 	var offsetTop  = element.offsetTop;
# 	var offsetLeft = element.offsetLeft;

# позиции в ифрейме:
# http://grokbase.com/t/gg/webdriver/124s6sgkce/get-absolute-position-of-a-webelement

# A generic answer might be a little tricky. Generally speaking, if you
# are trying to find an element you have to do the following:

# - find the iframe
# - switch to the iframe
# - find the element

# If the element is in an iframe, inside an iframe, inside an iframe,
# etc. this is where a generic solution gets tricky. If you are looking
# for a solution to a specific application then the algorithm is:

# - find the iframe
# - get the iframe Location
# - get the X value
# - get the Y value
# - switch to the iframe
# - find the element
# - get the element Location
# - add the X value to the above X value
# - add the Y value to the above Y value

# The indented lines are additions to the original algorithm. In actual
# code:

# WebElement iframe = driver.findElement(iframeLocator);
# Point iframeLoc = iframe.getLocation();
# int x = iframeLoc.getX();
# int y = iframeLoc.getY();
# driver.switchTo().frame(iframe);
# WebElement element = driver.findElement(elementLocator);
# Point elementLoc = element.getLocation();
# x += elementLoc.getX();
# y += elementLoc.getY();
# p = new Point(x, y);
# return p;

# если скролили:
# I was able to get the scrolling offset like
# so:

# JavascriptExecutor je = (JavascriptExecutor) webDriver();
# Object pageYOffset = je.executeScript("return window.pageYOffset;");
# scrollHeight = ((Long) pageYOffset).intValue();

# 2:
# The general principle is to check the value of window.scrollY in the browser. If your button scrolls completely back to the top then window.scrollY should have a value of 0. Assuming the driver variable holds your WebDriver instance:

# JavascriptExecutor executor = (JavascriptExecutor) driver;
# Long value = (Long) executor.executeScript("return window.scrollY;");
# You can then check that value is 0. executeScript is used to run JavaScript code in the browser.


# просто скролим:
# jse.executeScript("scroll(0, 250);");
# For Scroll up:

# jse.executeScript("window.scrollBy(0,-250)", "");
# OR,
# jse.executeScript("scroll(0, -250);");

# к елементу:
# 	je.executeScript("arguments[0].scrollIntoView(true);",element);

# 1:
# JavaScript get window X/Y position for scroll
# 		var doc = document.documentElement;
# 		var left = (window.pageXOffset || doc.scrollLeft) - (doc.clientLeft || 0);
# 		var top = (window.pageYOffset || doc.scrollTop)  - (doc.clientTop || 0);

# 2 sposob:
# var top  = window.pageYOffset || document.documentElement.scrollTop,
# left = window.pageXOffset || document.documentElement.scrollLeft;


# проверка яваскрипта онлайн:
# 	http://www.javascriptlint.com/online_lint.php

# выбор из списка толком не работает:
# provincia: Islas Baleares
# [send_all_values:
#        1/12 {'tip': 'select', 'id': 'ctl00_main_OA_AF_A1_cbFR171', 'text_closest': u'Islas Baleares'} ['Por favor seleccione', 'Andaluc\xc3\xada', 'A
# rag\xc3\xb3n', 'Asturias', 'Canarias', 'Cantabria', 'Castilla - La Mancha', 'Castilla y Le\xc3\xb3n', 'Catalu\xc3\xb1a', 'Ceuta', 'Diputaci\xc3\xb3n F
# oral de \xc3\x81lava', 'Diputaci\xc3\xb3n Foral de Guip\xc3\xbazcoa', 'Diputaci\xc3\xb3n Foral de Navarra', 'Diputaci\xc3\xb3n Foral de Vizcaya', 'En
# el extranjero', 'Extremadura', 'Galicia', 'Illes Balears', 'La Rioja', 'Madrid', 'Melilla', 'Murcia', 'Valencia']


# поиск по вложениям:
# Match cases where Sign in is directly child of a or child of another element:

# //a[contains(@class,'btnX') and .//text()='Sign in']
# I mean

# <a class="btnX btnSelectedBG" href="#">Sign in</a>

# and

# <a class="btnX btnSelectedBG" href="#"><b>Sign in</b></a>


# finding an element in a sub-element

# When you start your XPath expression with //, it search from root of document ignoring your parent element. You should prepend expression with .

# element2 = driver.find_element_by_xpath("//div[@title='div2']")
# element2.find_element_by_xpath(".//p[@class='test']").text


# element2 = driver.find_element_by_cssselector("css=div[title='div2']")
# element2.find_element_by_cssselector("p[@class='test']").text

# поиск по тексту:
# 	[contains(text(), '" + text + "')] | //*[@value='" + text + "'])" it will search for given text not only inside element nodes, but also inside input elements whose text was set via 'value' attribute i.e. <button value="My Button" />

# xpath 2.0 has a lower-case function, so this should work: '//div[contains(lower-case(text()), "{0}")]'.format(text) – andrean Sep 7 '12 at 20:18

# multiple condition: //div[@class='bubble-title' and contains(text(), 'Cover')]
# partial match: //span[contains(text(), 'Assign Rate')]
# starts-with: //input[starts-with(@id,'reportcombo')
# value has spaces: //div[./div/div[normalize-space(.)='More Actions...']]
# sibling: //td[.='LoadType']/following-sibling::td[1]/select"
# more complex: //td[contains(normalize-space(@class), 'actualcell sajcell-row-lines saj-special x-grid-row-collapsed')]


# PhantomJS
# http://stackoverflow.com/questions/35666067/selenium-phantomjs-custom-headers-in-python
# 	from selenium import webdriver

# headers = {

# 	#'Accept':'*/*',
# 	'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
# 	#'Accept-Encoding':'gzip, deflate, sdch, br',
# 	'Accept-Language':'en-US,en;q=0.8',
# }
# 	headers = { 'Accept':'*/*',
# 	    'Accept-Encoding':'gzip, deflate, sdch',
# 	    'Accept-Language':'en-US,en;q=0.8',
# 	    'Cache-Control':'max-age=0',
# 	    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36'
# 	}

# 	for key, value in enumerate(headers):
# 	    webdriver.DesiredCapabilities.PHANTOMJS['phantomjs.page.customHeaders.{}'.format(key)] = value
# 	Then start work with your driver:

# 	service_args = [
# 	    '--proxy=127.0.0.1:9999',
# 	    '--proxy-type=socks5',
# 	]
# 	driver = webdriver.PhantomJS(service_args=service_args)


# phantomJs:
# 	как вычисляют:
# 		http://engineering.shapesecurity.com/2015/01/detecting-phantomjs-based-visitors.html

# Using PhantomJS? I will suggest to use Chrome headless instead. Yes, you can settup Chrome headless on Ubuntu. Thing run just like Chrome but it only does not have a view and less buggy like PhantomJS.


# новый селениум выеживается с фаерфоксом?
# Selenium using Python - Geckodriver executable needs to be in PATH
# The latest version in the selenium 2.x series is 2.53.6 (see e.g this answers, for an easier view of the versions).

# The 2.53.6 version page doesn't mention gecko at all. But since version 3.0.2 the documentation explicitly states you need to install the gecko driver.

# If after an upgrade (or install on a new system), your software that worked fine before (or on your old system) doesn't work anymore and you are in a hurry, pin the selenium version in your virtualenv by doing

# pip install selenium==2.53.6
# but of course the long term solution for development is to setup a new virtualenv with the latest version of selenium, install the gecko driver and test if everything still works as expected. But the major version bump might introduce other API changes that are not covered by your book, so you might want to stick with the older selenium, until you are confident enough that you can fix any discrepancies between the selenium2 and selenium3 API yourself.


#################################http://stackoverflow.com/questions/3277369/how-to-simulate-a-click-by-using-x-y-coordinates-in-javascript
# клик в точке
# 				t = 0
# 				if t:
# 					rectangle = self.S.get_element_rectangle(element)
# 					logger.debug('rectangle: %s' % rectangle)

# 					for i in range(1):

# 						t = 0
# 						if t:
# 							id_to_value.append(	{'tip':'click_js', 'element':element} )
# 							id_to_value.append(	{'sleep':1,} )
# 						else:
# 							js = "document.elementFromPoint([x], [y]).click();"#не сработало

# 							js = """
# 	function click(x, y)
# 	{

# 	    var ev = document.createEvent("MouseEvent");
# 	    ev.initMouseEvent(
# 		"dblclick",
# 		{
# 		'view': window,
# 		'bubbles': true,
# 		'cancelable': true,
# 		'screenX': x,
# 		'screenY': y
# 		}
# 	    );

# 	    var el = document.elementFromPoint(x, y);

# 	    el.dispatchEvent(ev);
# 	}

# 	click([x], [y]);
# 	"""

# 							js = """
# 	function click(x,y){
# 	    var ev = document.createEvent("MouseEvent");
# 	    var el = document.elementFromPoint(x,y);
# 	    ev.initMouseEvent(
# 		"click",
# 		true /* bubble */, true /* cancelable */,
# 		window, null,
# 		x, y, 0, 0, /* coordinates */
# 		false, false, false, false, /* modifier keys */
# 		0 /*left*/, null
# 	    );
# 	    el.dispatchEvent(ev);
# 	}

# 	click([x], [y]);
# 	"""
# 							js0 = """
# 	var event = $.Event('click');
# 	event.clientX = 20;
# 	event.clientY = 20;
# 	$('a.placeBet.abetslipBtn').trigger(event);
# 	"""


# 							x0, y0, x1, y1 = rectangle
# 							x = int((x0 + x1)/2)
# 							y = int((y0 + y1)/2)
# 							repl = {
# 								'[x]':x,
# 								'[y]':y,
# 							}
# 							js = no_probely(js, repl)
# 							id_to_value.append(	{'tip':'execute_js', 'js':js} )

# 							id_to_value.append(	{'sleep':10,} )


# 					t = 1
# 					t = 0
# 					if t:
# 						#https://groups.google.com/forum/#!topic/phantomjs/vFe9OWchLLc
# 						js = '''
# 		function getElementByXpath(path) {
# 		  return document.evaluate(path, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
# 		}

# 		function click(el){
# 		    var ev = document.createEvent("MouseEvent");
# 		    ev.initMouseEvent(
# 			"dblclick",
# 			true /* bubble */, true /* cancelable */,
# 			window, null,
# 			0, 0, 0, 0, /* coordinates */
# 			false, false, false, false, /* modifier keys */
# 			0 /*left*/, null
# 		    );
# 		    el.dispatchEvent(ev);
# 		waitforload=true;
# 		}


# 		var element = getElementByXpath('[xpath]');
# 		click(element);

# 		'''
# 						#js = "$('a.placeBet.abetslipBtn')[0].click()"


##element.setAttribute('style', 'border:10px solid blue;')

##var mouseEventObj = document.createEvent('MouseEvents');
##mouseEventObj.initMouseEvent('click', true, true, window, 0, 0, 0, 0, 0, false, false, false, false, 0, null );
##element.dispatchEvent(mouseEventObj);


# 						#logger.debug('js: %s' % js)
# 						repl = {
# 							'[xpath]':xpath,
# 						}
# 						js = no_probely(js, repl)
# 						id_to_value.append(	{'tip':'execute_js', 'js':js} )
# 						id_to_value.append(	{'sleep':3,} )


# if element:
# 	#t = 0
# 	#t = 1
# 	#if t:
# 	#	xpath_v = './/button'
# 	#	element_b = element.find_element_by_xpath(xpath_v)

# 	#кликаем на папу?
# 	t = 1
# 	t = 0
# 	if t:
# 		element_parent = element.find_element_by_xpath('..')


# комбинации:
# .RETURN

"""
triple click:
    https://stackoverflow.com/questions/44330194/triple-click-using-selenium
"""
