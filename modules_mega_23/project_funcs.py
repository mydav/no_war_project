#!/usr/bin/python
# -*- coding: utf-8 -*-
from modules import *


def check_success(task={}):
    d = {
        #'file_to_life':{},
        "subject": "check_success error",
        "cnt_tries": -1,
        "sleep": 60,
    }
    task = add_defaults(task, d)
    T = Bunch(task)
    if T.cnt_tries == -1:
        T.cnt_tries = 1000000

    for i in range(T.cnt_tries):
        Show_step("%s	step %d" % (T.subject, i + 1))

        message = []
        j = 0
        for file in T.file_to_life:
            j += 1
            max_life = T.file_to_life[file]
            life = file_life(file)
            minutes = life / 60

            logger.debug(
                "	%d/%d	%s, 	%s" % (j, len(T.file_to_life), file, life)
            )
            line = "%s	- %s minutes" % (file, minutes)
            logger.debug("		%s" % line)

            if life > max_life:
                logger.debug(line)
                message.append(line)
            else:
                logger.debug("good")

        message_txt = "\n".join(message)
        if message_txt != "":
            logger.error("errors: ")
            show_list(message)
            _ = {
                "subject": T.subject,
                "message": message_txt,
            }
            reaction(_)

        logger.debug("sleep  %d seconds" % T.sleep)
        time.sleep(T.sleep)


def p1_edit_sizes(sizes):
    if sizes.find("unique size") != -1:
        return sizes.replace("unique size", "")
    items = sizes.split(",")
    r = []
    for item in items:
        s = item.strip()
        if s.find("out of stock") != -1:
            continue
        r.append(s)
    r = ",".join(r)
    r = r.replace("years", "лет").replace("months", "месяцев")
    replaces = [
        ("chest", "Объем груди"),
        ("Chest", "Объем груди"),
        ("Boys", "Детский"),
        ("Boy", "Детский"),
        ("Tall", "Рост"),
        ("Size", "Размер"),
        ("Junior", "Подростковый"),
        ("Yrs", "Лет"),
        ("Available", "Доступен"),
        ("Years", "Лет"),
        ("Waist", "Талия"),
        ("Girls", "Детский"),
        ("yrs", "Лет"),
        ("Months", "Месяцев"),
        ("Junior", "Подростковый"),
    ]
    r = no_probely(r, replaces)
    return r


def get_str_to_cat(more=""):
    str_to_cat = []
    f = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "data", "categories.txt"
    )

    items = text_from_file(f).strip()
    if more != "":
        items = items + "\n" + more
    items = items.split("\n")
    for item in items:
        item = do_lower(item)
        x, y = item.split("	")
        x = x.strip()
        y = y.strip()
        words = []
        items = x.split(" ")
        for item in items:
            item = item.strip()
            if item == "":
                continue
            words.append(item)
        str_to_cat.append((words, y))
    return str_to_cat


def guess_category(title, str_to_cat):
    category = ""
    # 		temp = title.split(' ')
    # 		category = ' '.join(temp[-6:])
    title2 = do_lower(title)
    all_words = title2.split(" ")
    all_words = non_empty_strip_elements(all_words)

    for words, y in str_to_cat:
        found = True
        for w in words:
            if not w in all_words:
                found = False
                break
        if found:
            category = y
            break
    return category


class cached_list:
    """ Класс кешированный список"""

    def __init__(self, s):
        d = {
            "list": [],  # сам список начальный
            "in_final": "load_full",  #'wait',#что делать в конце - подождать или еще что?
            "name": "",  # имя куда храним
            "shuffle": 0,  # мешать или нет
            "unique": 1,  # уникализировать или нет
            "final_func": 0,  # что-то делать когда элементов 0? результат этой ф-ии - новые прокси наши
            "final_func_args": {},  # аргументы финальной ф-ии
            "save_list_after_get": 1,  # сохранять список после получения? Если в один поток, для скорости нелогично сохранять (например когда картинки рендомные выбираем или аудио)
            "otl": 0,  # отладка
        }
        s = add_defaults(s, d)
        # show_dict(s)
        T = Bunch(s)

        # wait_for_ok()
        # почему-то не работает
        for k in s:
            self.k = s[k]

        self.save_list_after_get = T.save_list_after_get

        if T.unique:
            T.list = unique_with_order(T.list)

        if T.shuffle:
            shuffle(T.list)

        self.name = T.name
        self.list = T.list

        self.shuffle = T.shuffle
        self.unique = T.unique
        self.in_final = T.in_final
        self.final_func = T.final_func
        self.final_func_args = T.final_func_args
        self.otl = T.otl

        self.last = "unknown"

        if s.has_key("d_log"):
            d_log = s["d_log"]
        else:
            d_log = os.path.join(
                os.path.dirname(os.path.abspath(sys.argv[0])),
                "temp",
                "cached_list",
                self.name,
            )

        self.f_cached = os.path.join(
            d_log, "cached_list"
        )  # тут лежит наш список сохраненный
        self.f_full = os.path.join(
            d_log, "full_list"
        )  # тут лежит наша полная версия
        self.f_used = os.path.join(
            d_log, "used"
        )  # тут то что мы использовали. Зачем его сохранять? нах
        self.list_cached = []

        self.save_list(self.list, self.f_full)

        # сохраняю полный лист на всякий
        ordered = sorted(self.list)
        h = to_hash(str(ordered))
        f = os.path.join(d_log, "full_%s" % h)
        if not os.path.isfile(f):
            self.save_list(ordered, f)

        # если битый файл
        if os.path.isfile(self.f_cached):
            v = self.load_list(self.f_cached)
            if v == False:
                rmfile(self.f_cached)
                self.if_empty()

        if os.path.isfile(self.f_cached):
            self.list_cached = self.load_list(self.f_cached)
            if len(self.list_cached) == 0:
                self.if_empty()
            # p = text_from_file(self.f_reuse)
            # proxies = [i.strip() for i in p.split('\n')]
            # shuffle(proxies)
            # self.reused = unique(proxies)
            # logger.debug('have %d proxies to reuse' % len(self.reused))
        else:
            self.if_empty()

        # self.get_all_proxies()

        logger.debug(
            "cached_list %s: have %s/%s cached elements"
            % (self.name, len(self.list_cached), len(self.list))
        )

        self.stata = {}

    def __len__(self):
        return len(self.list_cached)

    def if_empty(self):
        fun = "if_empty"
        logger.debug("[%s" % fun)
        if self.final_func != 0:
            t = 0
            if t:
                cmd = "%s()" % self.final_func
                logger.debug("eval %s" % cmd)
                eval(cmd)
            if self.final_func_args == {}:
                self.list = self.final_func()
            else:
                self.list = self.final_func(self.final_func_args)
            self.save_list(self.list, self.f_full)

        if self.in_final == "wait":
            wait_for_ok("empty cached list, do what you have to do")
        elif self.in_final == "load_full":
            logger.debug("load_full")
            self.list_cached = self.save_list(self.list, self.f_cached)
        else:
            wait_for_ok("unknown for if_empty")

    def load_list(self, f):
        # захружаем лист полностью
        fun = "load_list"
        bad = 0
        try:
            lst = obj_from_file(f)
            if type(lst) != type([]):
                bad = 1
            else:
                return lst[:]
        except Exception as er:
            logger.error("%s ERROR: corrupted %s" % (fun, f))
            bad = 1

        if bad:
            rmfile(f)
            self.if_empty()
            # wait_for_ok()
        return False

    def save_list(self, lst, f_to):
        # захружаем лист полностью
        fun = "save_list"
        if self.otl:
            logger.debug("[%s - %s elements to %s" % (fun, len(lst), f_to))
        obj_to_file(lst, f_to)
        return lst[:]

    def get(self):
        # получаем текущий елемент
        if len(self.list_cached) == 0:
            self.if_empty()

        if self.shuffle:
            shuffle(self.list_cached)

        v = self.list_cached.pop(0)
        self.last = v
        if self.save_list_after_get:
            self.save_list(self.list_cached, self.f_cached)
            # join_text_to_file(str(v), self.f_used)
        return v

    def insert0(self, element):
        # вставляем в первую позицию
        fun = "insert0"
        logger.debug("[%s %s" % (fun, element))
        self.list_cached.insert(0, element)
        self.save_list(self.list_cached, self.f_cached)


class class_info_saved:
    # сохраняю нужную инфу о событиях - например когда в матче вылезло 0.5
    # http://stackoverflow.com/questions/4014621/a-python-class-that-acts-like-dict

    def __init__(self, more={}):
        d = {
            "f": "data/f_events_info_saved.txt",  # в каком файле хранится словарь
            "tupo_int": 1,  # пытаться в целое переводить втупую?
            #'with_json':0,	#в йсон кодировать? Чтобы знать какого типа инфа
        }
        more = add_defaults(more, d)
        self.more = more

        self.setup("f", self.more["f"])
        self.info = {}
        self.load_from_history()
        self.last_name = ""

    def check_file_exists(self):
        if not os.path.isfile(self.f):
            logger.debug("IG ERROR - no file %s" % self.f)

    def setup(self, tip="f", f=""):
        """
			установка переменных
			f - файл
		"""
        if tip == "f":
            self.f = os.path.abspath(f)
            self.f_temp = os.path.abspath(f) + "___temp"

    def save_to_new_file(self, f_to="", remove_file=0):
        """
			сохраняем в новый файл (старый вытираем)
		"""
        if os.path.isfile(self.f):
            txt = text_from_file(self.f)
            text_to_file(txt, f_to)
            if remove_file:
                rmfile(self.f)

            logger.debug("IG resaved to %s" % f_to)

        self.setup("f", f_to)

    def debug(self, info=""):
        # вывод отладочной инфы
        if type(info) == type("str"):
            info = [info]
        info = list(map(str, info))
        info.insert(0, "	class_info_saved:")
        mess = "	".join(info)
        logger.debug("		%s" % mess)
        # lg.debug(mess)

    def get_name(self):
        v = self.more.get("name", "")
        return v

    def check_name(self, name=""):
        # проверяем - возможно мы дефолтное имя использовали
        default_name = self.get_name()
        if name == "":
            name = default_name
            # self.name = default_name
        return name

    def init(self, name=""):
        name = self.check_name(name)
        if name not in self.info:
            self.info[name] = {}

    def set_name(self, name=""):
        # дефолтное имя
        self.last_name = self.get_name()
        self.more["name"] = name

    # def remember_name(self, new_name = ''):
    # 	'''
    # 		запомни имя и установи новое
    # 	'''
    # 	self.set_name(new_name)

    def name_back(self):
        """
			возврат имени
		"""
        self.set_name(self.last_name)
        self.last_name = ""

    def key(self):
        return self.more.get("name", None)

    def get_curent_info(self):
        r = self.load_from_history()
        return r

    def has_key(self, key, name=""):
        name = self.check_name(name)
        self.init(name)

        # curent = self.get_curent_info
        return key in self.info[name]

    def get(self, key, name="", default=None):
        # получение значения по ключу
        name = self.check_name(name)
        self.init(name)
        if self.has_key(key, name):
            return self.info[name][key]
        else:
            return default

    def load_from_history(self):
        if not os.path.isfile(self.f):
            return self.info

        items = text_from_file(self.f).split("\n")
        for item in items:
            item = item.strip()
            if item == "":
                continue
            parts = item.split("    ")
            try:
                time, name, key, value = parts
            except Exception as er:
                logger.error("error %s %s" % (er, parts))
                continue

            if self.more["tupo_int"]:
                value_int = -1
                try:
                    value_int = int(value)
                except Exception as er:
                    pass
                if str(value_int) == value:
                    value = value_int

            self.init(name)
            self.info[name][key] = value

        return self.info

    # def update(self, key, value, name=''):
    # 	#если небыло значения - пишем
    # 	name = self.check_name(name)
    # 	self.init(name)

    # 	value_old = self.info[name].get(key, None)

    # 	logger.debug('value_old: %s' % value_old)

    # 	adding = [name, key, value]
    # 	mess_add = str(adding)

    # 	if value_old==None:
    # 		self.info[name][key] = value
    # 		add_to_full_log(adding, self.f)
    # 		self.debug('added ' + mess_add)

    # 	#если было и другое - перезаписываем
    # 	elif value not in [value_old, str(value_old)]:
    # 		self.delete(key, name)
    # 		add_to_full_log([name, key, value], self.f)
    # 		self.debug('added ' + mess_add)

    def __setitem__(self, key, item):
        self.add(key, item)

    def add(self, key, value="", name=""):
        # если небыло значения - пишем
        fun = "add"
        name = self.check_name(name)
        self.init(name)

        value_old = self.info[name].get(key, None)

        logger.debug(
            '[%s, add "%s", value_old: "%s"' % (fun, value, value_old)
        )

        adding = [name, key, value]
        mess_add = str(adding)

        if value_old is None:
            self.info[name][key] = value
            add_to_full_log(adding, self.f)
            self.debug("added " + mess_add)

        # если было и другое - перезаписываем
        elif value not in [value_old, str(value_old)]:
            self.delete(key, name)
            self.info[name][key] = value
            add_to_full_log([name, key, value], self.f)
            self.debug("added " + mess_add)

        # если было и то же самое - оставили
        else:
            mess = "not changed, value_old=%s, value=%s" % (value_old, value)
            self.debug(mess)
        logger.debug("+]")

    def add1(self, key, value, name=""):
        # добавляем только один раз, не перезаписывая. Например обозначаем так что рега сделана или еще что-то

        if not self.has_key(key, name):
            self.add(key, value, name)

    def plus_1(self, key, value=0, name=""):
        """
			счетчик увеличиваем на 1
		"""
        if not self.has_key(key, name):
            self.add(key, value, name)

        value = self.get(key, name)
        value2 = int(value) + 1
        self.add(key, value2, name)

    def add_to_root(self, key, value=""):
        """
			добавляем в корень, и возвращаемся к главному ключу
		"""
        self.set_name("")
        self.add(key, value=value)
        self.name_back()

    # def __delitem__(self, key):
    # 	del self.__dict__[key]

    def delete(self, key, name=""):
        self.check_file_exists()

        self.debug("delete key=%s, name=%s" % (key, name))
        name = self.check_name(name)
        self.init(name)
        if key in self.info[name]:
            del self.info[name][key]

            # пересохраняем файл с логом:
            # скопировали в темповский
            text_to_file(text_from_file(self.f), self.f_temp)

            # в темповском удалили все строчки name-key
            new_lines = []
            items = text_from_file(self.f_temp).split("\n")
            for item in items:
                item = item.strip()
                if item == "":
                    continue
                parts = item.split("    ")
                try:
                    time0, name0, key0, value0 = parts
                except Exception as er:
                    logger.debug("cnt_parts: %s" % len(parts))
                    logger.error("ERROR DELETE: %s" % er)
                    continue
                if name == name0 and key == key0:
                    self.debug(
                        '	key=%s, name=%s, killing line "%s" from %s'
                        % (key, name, item, self.f_temp)
                    )
                else:
                    new_lines.append(item)

            # переименовали темповский на настоящий
            text_to_file("\n".join(new_lines), self.f)
            rmfile(self.f_temp)

    def __repr__(self):
        return "IG from file %s %s" % (self.f, self.info)


def get_global_info(task={}):
    # сюда я сохраняю все важные переменные. Например инфу о то было ли подтверждение по почте для бета, айдишник бета и т.д.
    d = {"f_global_info": "temp/global_info.txt"}
    # task = add_defaults(task, get_global_settings())
    task = add_defaults(task, d)

    _ = {
        "f": task["f_global_info"],
    }
    I = class_info_saved(_)
    return I


if __name__ == "__main__":

    t = 0
    t = 1
    if t:
        _ = {"f": "temp/test_saved_info.txt"}
        I = class_info_saved(_)
        logger.debug(f"{I=}")
        # info = I.load_from_history()
        info = I.info
        logger.debug(f"{info=}")
        show_dict(info)
        wait_for_ok()

        I.add(key="started", value="2016", name="event_2")
        # I.add(key='finished', value='2017', name='event_2')

        I.delete(key="finished", name="event_2")

        name = "event_2"
        I.set_name(name)
        key = "started2"
        if not I.has_key(key):
            I.add(key, value="now")

        # I.add(key='started', value='2016', name='event_2')

        logger.debug("f{I.info=}")
        key = "started"
        key = "nooo"
        logger.debug("value for %s = %s" % (key, I.get(key)))

        k = "counter"
        for i in range(5):
            logger.debug("	i %s, counter %s" % (i, I.get(k)))
            I.plus_1(k)

        os._exit(0)

    pass
