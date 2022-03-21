#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
from modules_23.minimum_important_functions import *
from modules_23.encode_decode import obj_to_utf8
from modules.logging_functions import get_logger


logger = get_logger(__name__)


class My_timer:
    def __init__(self, task={}):
        d = {
            "want_display": 1,
            "want_slito": 0,
            "status": "on",
            "print_on_ini": 0,
            "print_pristavka": "",  # приставка перед выводом
            "is_hidden": 0,
            "seq_is_step": 0,  # seq step или нет?
            "tpl": """[pristavka]    [message] [seconds]""",
        }
        task = add_defaults(task, d)
        T = Bunch(task)
        self.T = T

        self.want_display = task["want_display"]
        self.status = task["status"]
        self.print_on_ini = task["print_on_ini"]
        self.want_slito = task["want_slito"]

        # self.print_pristavka = task['print_pristavka']
        self.add_timer_print_pristavka(task["print_pristavka"])

        self.seq_is_step = task["seq_is_step"]
        self.all_messages = []

        self.clear()

        self.print_pristavki = []

    def add_sub_pristavka(self, pristavka=""):
        """
            если я хочу временно использовать приставку, а потом вернуть ее через comeback_sub_pristavka
        """
        pristavka0 = self.print_pristavka
        self.print_pristavki.append(pristavka0)

        self.add_timer_print_pristavka(pristavka)

    def comeback_sub_pristavka(self, pristavka=""):
        fun = "comeback_sub_pristavka"
        if len(self.print_pristavki) == 0:
            logger.error("%s error, no more pristavok" % fun)
            pristavka = ""
        else:
            pristavka = self.print_pristavki.pop()

        self.add_timer_print_pristavka(pristavka)

    def add_timer_print_pristavka(self, pristavka=""):
        # real_pristavka = '\n' + 'TIMER    ' + pristavka
        real_pristavka = pristavka
        self.print_pristavka = real_pristavka

    def pr(self, mess="", coma=0):
        # wait_for_ok()
        if len(mess) > 1:
            if coma:
                logger.debug(mess)
            else:
                logger.debug(mess)

    def message(self, proshlo=0.1, descr="", before="", act="print"):
        """
            если оканчивается на " ," - в строчку печатаем
        """
        fun = "message"

        coma = 0
        t = 0
        if t:
            # mess = '    %sfrom %s:    proshlo %.3f seconds' % (self.print_pristavka, descr, proshlo)
            if descr[-2:] == " ,":
                descr = descr[:-2]
                coma = 1

        repl = {
            "[pristavka]": self.print_pristavka,
            "[message]": descr,
            "[before]": before,
            "[seconds]": "%.3f seconds" % proshlo,
        }
        # mess = no_probely(self.T.tpl, repl)
        mess = self.T.tpl
        for k in repl:
            mess = mess.replace(k, str(repl[k]))
        _ = {
            #'message':descr,
            "message": mess,
            "before": before,
            "seconds": proshlo,
        }
        self.all_messages.append(_)

        # wait_for_ok(1)
        if act == "print":
            if not self.T.is_hidden:
                self.pr(mess, coma=coma)
            # wait_for_ok(fun)
            # wait_for_ok(2)
            return mess
        else:
            return act

    def step(self, want_display=1, mess=""):
        # wait_for_ok('in step?')

        if not want_display:
            return

        t_now = time.time()
        proshlo = t_now - self.last_time
        self.last_time = t_now
        # self.message(proshlo, '        %s        /previous "%s"' % (mess, self.last_step_name) )

        # wait_for_ok(1)
        printed = self.message(proshlo, descr=mess, before=self.last_step_name)
        # wait_for_ok(2)
        # self.pr('%s%s    /previous "%s" %.3f seconds' % (self.print_pristavka, mess, self.last_step_name, proshlo) )
        # self.last_step_name = mess
        self.last_step_name = printed

    def ini(self, name, polube=0, want_print="default", seconds=""):
        fun = "ini"
        if polube or not self.info.has_key(name):
            self.info[name] = {
                "lst": [],
                "last_access": time.time(),
            }
        if name not in self.names:
            self.names.append(name)

        if want_print == "default":
            want_print = self.print_on_ini

        if want_print:
            if seconds != "":
                seconds = "%.3f" % seconds
            r = "%s%s %s" % (self.print_pristavka, name, seconds)
            r = r.strip()
            print(r)

        t = 1
        t = 0
        if t:
            show_dict(self.info)
            wait_for_ok(fun)

    def seq(self, name="name", want_display="default", sluzhebno=0):
        fun = "seq"

        if self.status == "propusk":
            return

        if want_display == "default":
            want_display = self.want_display

        # want_display = self.check_want_display()
        # logger.debug(str(['    %s want_display %s' % (fun, want_display), self.want_display, self.seq_is_step, name)]))

        if want_display and self.seq_is_step:
            self.step(want_display, name)
            return

        if self.status == "off":
            return

        t_now = time.time()
        last_name = self.last_name

        seconds_for_last = ""
        if last_name != name and last_name != 0:
            seconds_for_last = t_now - self.info[last_name]["last_access"]
            self.info[last_name]["lst"].append(seconds_for_last)

        if sluzhebno:
            return

        self.ini(name, seconds=seconds_for_last)

        # logger.debug(str([fun, name, last_name, self.info.get(last_name)]))
        self.last_name = name
        self.info[name]["last_access"] = t_now

        t = 0
        if t:
            if want_display and last_name != 0:
                name = last_name
                all_seconds = sum(self.info[name]["lst"])
                self.message(all_seconds, name)
                self.ini(name, polube=1, want_print=0)

    def sluzhebno_add(self):
        self.seq(self.last_name, want_display=0, sluzhebno=1)

    def flush_all_messages(self, min_procent=1, cnt_skip_last=0):
        # выводим все сообщения которые были
        fun = "flush_all_messages"

        try:
            self.seq("flush_all_messages")
        except Exception as er:
            logger.error("error %s" % er)
            pass

        all_messages = self.all_messages[
            0 : len(self.all_messages) - cnt_skip_last
        ]

        # logger.debug('% %s' % (fun, all_messages))
        # wait_for_ok()

        seconds_sum = [_["seconds"] for _ in all_messages]
        seconds_sum = sum(seconds_sum)
        i = 0
        messages = []

        messages_slito = []
        messages_slito_details = {}

        cum_seconds = 0
        for b in all_messages:
            i += 1

            t = 0
            if t:
                logger.debug("\n" * 2 + "%s/%s" % (i, len(all_messages)))
                show_dict(b)

            seconds = b["seconds"]
            if seconds_sum not in [0, 0.0]:
                procent = int(100 * float(seconds) / seconds_sum)
            else:
                procent = 0

            # нули сбивают, их вообще не вывожу. Так вижу что сколько времени взяло
            procent_txt = procent
            if procent == 0:
                procent_txt = ""

            cum_seconds += seconds

            event = b["before"].strip()
            now = b["message"].strip()

            # log = ['%2d/%d %.2f' % (i, len(all_messages), cum_seconds), '%.2f=%2d%%' % (seconds, procent), '%.2f'%seconds, procent_txt, event, 'now %s' % now]
            procent_info = procent
            if procent_info == 0:
                procent_info = ""
            log = [
                "%2d/%d %.2f" % (i, len(all_messages), cum_seconds),
                "%.2f=%2d%%" % (seconds, procent),
                "%.2f" % seconds,
                procent_info,
                event,
            ]

            log = map(str, log)
            message = "    ".join(log)

            if procent >= min_procent:
                messages.append(message)

            if not event in messages_slito:
                messages_slito.append(event)
                messages_slito_details[event] = {
                    "seconds_all": [seconds],
                }

            else:
                messages_slito_details[event]["seconds_all"].append(seconds)

            # logger.debug(message)
            # wait_for_ok('message %s' % i)
        # show_list(all_messages)
        # wait_for_ok()
        # хочу события с одинаковыми именами слить
        t = 1
        if t and self.want_slito:
            messages.append("\n" * 3)
            messages.append("SLITO")

            i = 0
            for event in messages_slito:
                i += 1
                details = messages_slito_details[event]

                cnt_events = len(details["seconds_all"])
                seconds = sum(details["seconds_all"])
                srednee = float(seconds) / cnt_events

                if seconds_sum not in [0, 0.0]:
                    procent = int(100 * float(seconds) / seconds_sum)
                else:
                    procent = 0
                # нули сбивают, их вообще не вывожу. Так вижу что сколько времени взяло
                procent_txt = procent
                if procent == 0:
                    procent_txt = ""

                # log = ['%2d/%d %.2f' % (i, len(all_messages), cum_seconds), '%.2f=%2d%%' % (seconds, procent), '%.2f'%seconds, procent, event, 'now %s' % now]

                mess_sred = "cnt %2d, sred %.2f" % (cnt_events, srednee)
                if cnt_events == 1:
                    mess_sred = "        "

                log = [
                    "%2d/%d %.2f" % (i, len(messages_slito), cum_seconds),
                    "%.2f=%2d%%" % (seconds, procent),
                    "%.2f" % seconds,
                    procent_txt,
                    mess_sred,
                    event,
                ]

                log = map(str, log)
                message = "    ".join(log)
                if procent >= min_procent:
                    messages.append(message)

        message = "min_procent %s, vsego secund: %.3f" % (
            min_procent,
            seconds_sum,
        )
        messages.append(message)

        print("%s all_messages:" % fun)
        show_list(messages)
        # logger.debug('messages %s' % messages)
        # wait_for_ok()
        _ = {
            "messages": messages,
            "seconds": seconds_sum,
        }
        return _

    def flush(self, clear=0, act="print"):
        # хочу вывести всю стату за весь период
        fun = "flush"
        otl = 0
        otl = 1
        # self.sluzhebno_add()
        if otl:
            show_dict(self.info)

        # wait_for_ok('todo %s' % fun)
        all_rez = []
        for name in self.names:
            all_seconds = sum(self.info[name]["lst"])
            steps = len(self.info[name]["lst"])

            srednee = -1
            if steps != 0:
                srednee = float(all_seconds) / steps

            descr = (
                "name: %s (srednee: %.3f seconds in %s steps)    all_seconds: "
                % (name, srednee, steps)
            )
            # if act=='print':
            #    self.message(all_seconds, descr)
            # else:
            r = self.message(all_seconds, descr, act=act)
            all_rez.append(descr)

        # wait_for_ok()
        if clear:
            self.clear()

        return all_rez

    def clear(self):
        """
            очистить всю инфу
        """
        self.last_time = time.time()
        self.last_time_seq = time.time()
        self.last_name = 0
        self.last_step_name = ""

        self.info = {}
        self.names = []  # список имен

        self.all_messages = []
        # self.__init__()

    def seq0(self, descr="description", want_display=1):
        if not want_display:
            return

        if descr == 0:
            self.last_time_seq = time.time()
            return 0

        t_now = time.time()
        proshlo = t_now - self.last_time_seq
        self.last_time_seq = t_now
        self.message(proshlo, descr)


def My_timer_step(task={}):
    """
        запуск таймера
    """
    d = {
        "print_on_ini": 1,
        "print_pristavka": "\n" + "TIMER    ",
        "seq_is_step": 1,
        "want_display": 1,
        "is_hidden": 0,
    }
    task = add_defaults(task, d)
    MT = My_timer(task)
    MT.seq("My_timer_step STARTED")
    # wait_for_ok()
    return MT


def get_MT(name="", want_timer=1):
    """
        "want_timer": 0 - тогда ничег не выведем
    """
    # debug = True
    _ = {
        "print": 0,
        "seq_is_step": 1,
        "want_display": 1,
        "name": name,
        "want_timer": want_timer,
    }
    MT = log_action(_)
    return MT


class log_action:
    """
        класс для логирования действий
    """

    def __init__(self, task={}):
        d = self.get_default()
        # wait_for_ok(task)

        task["timer_settings"] = add_defaults(
            task.get("timer_settings", {}), d["timer_settings"]
        )

        task = add_defaults(task, d)

        # show_dict(task)
        # wait_for_ok()

        T = Bunch(task)

        self.T = T
        self.name = T.name
        self.task = task
        self.otl = task["print"]
        self.want_display = task["want_display"]

        self.zero()

        self.init_timer()

        t = 1
        t = 0
        if t:

            logger.debug("after init: %s %s" % (self.T.want_timer, self.MT))
            wait_for_ok()

    def get_default(self):
        d_timer_settings = {
            "print_on_ini": 0,
            "want_display": 1,
            "is_hidden": 1,
            "tpl": """[pristavka]    [message]""",
        }
        d = {
            "print": 1,  # выводить при add?
            "deep": 100,  # глубина детализации (потом для вывода используется)
            "max_tabs": 4,
            "want_timer": 1,
            "timer_settings": d_timer_settings,
            "want_display": 1,
            "name": "",
        }

        return d

    def init_timer(self):
        if not hasattr(self.T, "want_timer"):
            d = self.get_default()
            self.T.want_timer = d["want_timer"]

        if self.T.want_timer == 0:
            MT = 0

        elif self.T.want_timer == 1:
            MT = My_timer_step(self.T.timer_settings)

        else:
            MT = T.want_timer

        self.MT = MT
        # wait_for_ok("MT?")

    def flush_all_messages(self, min_procent=1, cnt_skip_last=0):
        if not hasattr(self, "MT"):
            self.init_timer()

        r = 0
        if self.MT != 0:
            r = self.MT.flush_all_messages(
                min_procent=min_procent, cnt_skip_last=cnt_skip_last
            )
        return r

    def clear(self):
        self.zero()

        if not hasattr(self, "MT"):
            self.init_timer()

        if self.MT != 0:
            self.MT.clear()

    def seq(self, info=""):
        """
            добавление в таймер
        """
        if not hasattr(self, "MT"):
            self.init_timer()

        func = str
        func = any_to_txt

        if self.MT != 0:
            m = func(info)
            # logger.debug('seq %s' % m)
            self.MT.seq(m)

            if self.want_display:
                logger.debug("%s %s" % (self.name, m))

        t = 1
        t = 0
        if t:
            logger.debug("%s %s" % (self.MT, self.T.want_timer))
            logger.debug("all_messages %s" % self.MT.all_messages)
            self.flush_all_messages()
            wait_for_ok("flush_all_messages")

    def zero(self):
        """обнуляем результат"""
        self.lines = []

    def add(self, message0="", deep=0, description="", pos=-1):

        # message = str(message)

        # wait_for_ok('otl: %s' % otl)
        # message = to_utf8_string(message)

        # не поборол словарь. И ладно.

        # if type(message)==type('str'):
        #    message = message.decode('utf8', 'ignore')
        #    message = message.encode('cp1251', 'ignore')
        # else:
        #    message = str(message)

        # if type(message)==type({}):
        #    {k:v.encode('utf-8') if isinstance(v, basestring) else v for k,v in d.items()}

        #    #message = str(message)
        #    #logger.debug('%s %s'% (type(mess), mess2))
        # else:
        #    message = str(message)

        # message = str(message)
        # message = text_to_charset(message, 'cp1251', 'utf8')
        # message = text_to_charset(message, 'utf8', 'cp1251')

        # message = message.replace('\\t', '    ').replace('\\', '')

        message = obj_to_utf8(message0)

        t = 1
        t = 0
        if t:
            logger.debug("add: %s" % type(message0))
            uni2(message)
            logger.debug("<" * 5)
            # wait_for_ok()
        line_log = [message, deep, description]

        if pos == -1:
            self.lines.append(line_log)
        else:
            self.lines.insert(pos, line_log)

        if self.otl:
            displayed = self.display_line(line_log)
            if displayed:
                uni2("%s%s %s" % ("\n" * 2, "LOG:", displayed))

        self.seq(line_log)

        # show_list(self.lines)

        # details = self.show_like_list()
        # show_list(details)
        # wait_for_ok()

    def show_like_list(self):
        """
            выводим списком, глубинные детали не показываем
        """
        details = []
        for line in self.lines:
            displayed = self.display_line(line)
            if displayed:
                details.append(displayed)

        return details

    def show_like_txt(self, delim="\n"):
        """
            выводим текстом
        """
        details = self.show_like_list()
        r = delim.join(details)

        return r

    def print_txt(self):
        details_txt = self.show_like_txt()
        uni2(details_txt)

    def display_line(self, line):
        message, deep, description = line
        if deep > self.T.deep:
            return 0

        # отступаем (максимум 3 табы)
        tabs = min(deep, self.T.max_tabs) * "    "
        # logger.debug('tabs: %s' % tabs)
        # wait_for_ok(tabs)

        if description != "":
            description = description + "    "

        line = "%s%s%s" % (tabs, description, message)
        return line


def any_to_txt(val):
    t = 1
    t = 0
    if t:
        return str(val)

    _ = {
        "print": 0,
        "want_timer": 0,
    }
    L = log_action(_)
    L.add(val)
    r = L.show_like_txt()
    return r


def dict_to_txt(dct={}):
    """
        словарь в текстовый читаемый вид
    """
    r = any_to_txt(dct)
    return r


if __name__ == "__main__":
    from modules import *

    # тест таймера
    t = 0
    t = 1
    if t:
        # show_list([1, 2, 3])
        # wait_for_ok()

        # MT = My_timer()

        t = 0
        if t:
            _ = {
                "print_on_ini": 0,
                "want_display": 0,
                "is_hidden": 1,
            }
            MT = My_timer_step(_)

        _ = {
            "deep": 1000,  # sett['emulate_log_details'],
            "print": 1,
            "want_timer": 1,
        }

        _ = {
            "print": 0,
        }
        L = log_action(_)

        MT = L

        # logger.debug('%s' % MT.MT)
        # wait_for_ok('MT?')
        # MT = L.MT

        flush_after = "after_all_cycles"
        flush_after = "after_every_cycle"

        pristavka_sub = "TIMER-SUBFUNCTION"

        step = 0
        max_steps = 2
        max_steps = 2
        max_steps = 10

        want_display = 1

        while True:
            MT.clear()
            step += 1
            if step > max_steps:
                break

            # t = 0
            # t = 1
            # if t:
            #    if step%3==1:
            #        want_display = 1
            #    else:
            #        want_display = 0
            # else:
            #    want_display = 0

            # if step%3==0:
            #    MT.flush(clear=1)

            logger.debug("\n" * 2 + str(step))
            MT.add("add0")
            sleep_(0.15)

            # MT.seq('step1', want_display=want_display)
            MT.seq("seq1")
            sleep_(0.2)

            MT.seq("seq2")
            sleep_(0.1)

            # L.MT.add_timer_print_pristavka(pristavka_sub)
            L.MT.add_sub_pristavka(pristavka_sub)
            # logger.debug('%s' % L.MT.print_pristavka)

            MT.seq("seq2.1")
            sleep_(0.1)

            MT.seq("seq2.2")
            sleep_(0.1)

            MT.seq("finish")
            L.MT.comeback_sub_pristavka()

            if flush_after == "after_every_cycle":
                lst = MT.flush_all_messages(min_procent=0)
                MT.clear()
                # lst = MT.flush(clear=1)
                logger.debug("lst: %s" % lst)

                lst0 = MT.flush_all_messages(min_procent=0)
                logger.debug("lst0: %s" % lst0)
                wait_for_ok()

        if flush_after == "after_all_cycles":
            lst = MT.flush_all_messages()
            MT.clear()
            # lst = MT.flush(clear=1)
            logger.debug("lst: %s" % lst)

            wait_for_ok()

        # MT.flush()

        os._exit(0)
