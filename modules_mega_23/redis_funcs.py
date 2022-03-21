#!/usr/bin/python
# -*- coding: utf-8 -*-

from typing import Literal
from redis import Redis
import pickle
from modules import (
    obj_from_json,
    obj_to_json,
    text_to_file,
    find_from_to_one,
    try_execute_function,
)
import time

from modules.logging_functions import *
from pirxt_server.model import *

logger = get_logger(__name__)


def get_session_headers_from_session_server(session_server):
    r_session = session_server.load(wait_while_exists=True)
    logger.debug("session=%s" % r_session)
    session = r_session["session"]
    mark = find_from_to_one("X-Net-Sync-Term:", "=", session)
    logger.debug("use session_server %s" % (mark))
    return session


class KyxaRedis:
    klass_name = "KyxaRedis"

    def __init__(
        self,
        host="173.249.2.50",  # contabo3
        # port = 6379 defolt redis port
        port=6371,
        password="LJ9dsdflsdfhY675d",
        main_key="oddscorp",
        db=0,
        processing_mode: Literal["json", "pickle"] = "json",
    ):
        _kwargs = {
            "host": host,
            "port": port,
            "password": password,
            "db": db,
        }
        rdb = Redis(**_kwargs)
        self.rdb = rdb
        if processing_mode == "json":
            func_process_data_before_saving = obj_to_json
            func_process_data_after_loading = obj_from_json

        elif processing_mode == "pickle":
            func_process_data_before_saving = pickle.dumps
            func_process_data_after_loading = pickle.loads

        else:
            logger.critical(f"unknown {processing_mode=}")
            os._exit(0)

        self.processing_mode = processing_mode
        self.func_process_data_before_saving = func_process_data_before_saving
        self.func_process_data_after_loading = func_process_data_after_loading

        self.main_key = main_key
        logger.debug(f"__init__ finished, rdb={self}")
        self.cnt_delets = 0  # количество удаленных

    def delete_key(self, key=None):
        # for key in r.scan_iter("prefix:*"):
        #     r.delete(key)
        fun = "delete_key"
        t_start = time.time()
        if not key:
            key = self.main_key
        deleted = self.rdb.delete(key)
        duration = time.time() - t_start
        logger.debug(f"    +{fun} for {key=} in {duration:.3f} seconds")
        self.cnt_delets += 1
        return deleted

    def exists(self, key=None):
        """
        длинна списка
        """
        fun = "exists"
        if not key:
            key = self.main_key

        func = self.rdb.exists
        args = (key,)
        task = {
            "func": func,
            "args": args,
        }
        exists = try_execute_redis_function(task)
        return exists

    def len(self, *args, **kwargs):
        return self.llen(*args, **kwargs)

    def llen(self, key=None):
        """
        длинна списка
        """
        fun = "llen"
        t_start = time.time()
        if not key:
            key = self.main_key

        # value = self.rdb.llen(key)
        task = {
            "func": self.rdb.llen,
            "args": (key,),
        }
        value = try_execute_redis_function(task)

        duration = time.time() - t_start
        logger.debug(
            " +length of list in %s=%s in %.3f seconds"
            % (key, value, duration)
        )
        return value

    def pop_last_element(self, *args, **kwargs):
        """получить последний элемент списка"""
        return self.brpop(*args, **kwargs)

    def brpop(self, key=None, want_dict=True):
        """
        последний элемент выдает
        https://redis.io/commands/brpop

        :param key:
        :return:
        """
        fun = "brpop"
        t_start = time.time()
        if not key:
            key = self.main_key

        # logger.debug(type("value"))
        logger.debug("start getting...")

        # _, value = self.rdb.brpop(
        #     [key], timeout=0
        # )  # b'test_list', b'{"from": 2}')

        task = {
            "func": self.rdb.brpop,
            "args": ([key],),
            "kwargs": {"timeout": 0},
        }
        _, value = try_execute_redis_function(task)

        if want_dict:
            value = self.prepare_data_after_loading(value)

        duration = time.time() - t_start
        logger.debug(" +%s in %.3f seconds" % (fun, duration))
        return value

    def add_list(self, items=[], key=None):
        """добавляем список
        [{}, {}, {}]
        """
        fun = "add_list"
        t_start = time.time()
        if not key:
            key = self.main_key
        if not items:
            logger.debug(f"{fun} - nothing to add")
            return 0

        # logger.debug(type("value"))
        prepared = [self.prepare_data_before_saving(value) for value in items]
        # logger.debug(f"{prepared=}")
        task = {
            "func": self.rdb.rpush,
            "args": (key, *prepared),
        }
        # logger.debug(f"{task=}")
        cnt_total = try_execute_redis_function(task)
        # cnt_total = task["func"](*task["args"])

        duration = time.time() - t_start
        logger.debug(
            f" +{fun} {len(prepared)} elements (total {cnt_total}) in {duration:.3f} seconds"
        )
        return cnt_total

    def save_dict(self, dct: dict, key=None, debug: bool = False):
        """сохраняем инфу-словарь
        это называется redis_hash
            https://pythontic.com/database/redis/hash%20-%20add%20and%20remove%20elements
        """
        fun = "save"
        t_start = time.time()
        if not key:
            key = self.main_key

        # logger.debug(type("dct"))
        # saving = self.prepare_data_before_saving(dct)
        saving = dct

        task = {
            "func": self.rdb.hset,
            "args": (key,),
            "kwargs": {"mapping": saving,},
        }
        saved = try_execute_redis_function(task)
        if debug:
            logger.debug(f"{saved=}")
        error = get_api_error(saved, key="break_error")
        if error:
            logger.error(f"{error=}")

        if (
            1
            and error
            and (
                "WRONGTYPE Operation against a key holding the wrong kind of value"
                in error
            )
        ):  # значит раньше сохранял инфу не словарем а по другому
            logger.warning(f"deleting {key=} and retry ({error=}")
            deleted = self.delete_key(key=key)
            logger.debug(f" +{deleted=}")

            saved = try_execute_redis_function(task)
            logger.debug(f"second try, {saved=}")

        duration = time.time() - t_start
        logger.debug(f" +{fun} in {duration:.3f} seconds")
        return saved

    def load_dict(
        self, key=None, wait_while_exists=False, seconds_wait: float = 0.5,
    ):
        """
        загружаю именно как словарь - редис умеет это делать
        ограничение: всегда будет только строки, нет возможности другие типы бросать
        """
        fun = "load_dict"
        if not key:
            key = self.main_key
        t_start = time.time()

        step = 0
        while True:
            duration = time.time() - t_start

            # value = self.rdb.get(key)
            task = {
                "func": self.rdb.hgetall,
                "args": (key,),
            }
            value = try_execute_redis_function(task)
            if wait_while_exists and value is None:
                logger.debug(
                    f"  {key=} not exists {duration:.0f} seconds, wait {seconds_wait}"
                )
                time.sleep(seconds_wait)
                continue
            break

        value = decode_redis(value)

        duration = time.time() - t_start
        logger.debug(f" +{fun} in {duration:.3f} seconds")
        return value

    def load_dict_key(
        self,
        key=None,
        subkey="child",
        wait_while_exists=False,
        seconds_wait: float = 0.5,
    ):
        """
        загружаю именно как словарь - редис умеет это делать
        """
        fun = "load_dict_key"
        if not key:
            key = self.main_key
        t_start = time.time()

        step = 0
        while True:
            duration = time.time() - t_start

            # value = self.rdb.get(key)
            task = {
                "func": self.rdb.hget,
                "args": (key, subkey),
            }
            value = try_execute_redis_function(task)
            if wait_while_exists and value is None:
                logger.debug(
                    f"  {key=} not exists {duration:.0f} seconds, wait {seconds_wait}"
                )
                time.sleep(seconds_wait)
                continue
            break

        logger.debug(f"{value=}")
        value = decode_redis(value)

        duration = time.time() - t_start
        logger.debug(f" +{fun} in {duration:.3f} seconds")
        return value

    def save(self, value, key=None):
        """сохраняем инфу"""
        fun = "save"
        t_start = time.time()
        if not key:
            key = self.main_key

        # logger.debug(type("value"))
        saving = self.prepare_data_before_saving(value)

        saved = self.rdb.set(key, saving)
        duration = time.time() - t_start
        logger.debug(f" +{fun} in {duration:.3f} seconds")
        return saved

    def load_list(self, start=0, stop=-1, key=None, want_dict=True):
        """подгрузить список"""
        fun = "load_list"
        if not key:
            key = self.main_key
        t_start = time.time()
        items = self.rdb.lrange(key, start, stop)  # = ['text1', 'text2', ]

        if want_dict:
            items = [self.prepare_data_after_loading(_) for _ in items]

        duration = time.time() - t_start
        logger.debug(" +%s in %.3f seconds" % (fun, duration))
        return items

    def load_key(self, key=None, subkey="child", **kwargs):
        """
        загружаю именно как словарь - редис умеет это делать
        """
        fun = "load_key"
        if not key:
            key = self.main_key
        loaded = self.load(key=key, **kwargs)
        if loaded and isinstance(loaded, dict):
            value = loaded.get(subkey)
        else:
            value = None
        return value

    def load(
        self,
        key=None,
        want_dict=True,
        wait_while_exists=False,
        seconds_wait: float = 0.5,
        debug: bool = False,
    ):
        fun = "load"
        if not key:
            key = self.main_key
        if debug:
            logger.debug(f"{fun} {key=}")
        t_start = time.time()

        step = 0
        while True:
            duration = time.time() - t_start

            # value = self.rdb.get(key)
            task = {
                "func": self.rdb.get,
                "args": (key,),
            }
            value = try_execute_redis_function(task)
            if wait_while_exists and value is None:
                logger.debug(
                    f"  {key=} not exists {duration:.0f} seconds, wait {seconds_wait}"
                )
                time.sleep(seconds_wait)
                continue
            break

        if want_dict:
            value = self.prepare_data_after_loading(value)

        duration = time.time() - t_start
        logger.debug(f" +{fun} in {duration:.3f} seconds")
        return value

    def prepare_data_before_saving(self, value):
        """
        подготовка инфы перед сохранением
        :param value:
        :return:
        """
        if type(value) != type(""):
            value = self.func_process_data_before_saving(value)
        return value

    def prepare_data_after_loading(self, value):
        """подготовка инфы после получения"""
        if value is not None:
            value = self.func_process_data_after_loading(value)
        return value

    def __repr__(self):
        return f"<{self.klass_name}={self.rdb}, main_key={self.main_key}>"


class RedisPirxtServer(KyxaRedis, UniversalPirxtServer):
    klass_name = "RedisPirxtServer"

    def __init__(self, *args, **kwargs):
        KyxaRedis.__init__(self, *args, **kwargs)

        UniversalPirxtServer.__init__(self)

        # self.main_key="pirxts:unlimited:headers" # нельзя!!!

    def delete_pirxt_headers(self):
        self.delete_key()
        self.prepared_pirxt_headers = None

    def get_pirxt_headers(self):
        """
        главная ф-я - получить готовый pirxt
        :return:
        """
        fun = "get_pirxt_headers"
        t_start = time.time()
        logger.debug2("get_pirxt_headers")

        # key = "pirxt_list"
        item = self.pop_last_element()
        logger.debug(f"{item=}")

        headers = item["headers"]

        pirxt_headers = headers["pirxt_headers"]
        pirxt_b = find_from_to_one("-b: ", "\n", pirxt_headers).strip()

        duration = time.time() - t_start
        logger.debug(
            f""" +{fun} in {duration:.3f} seconds, {pirxt_b=} created {item["t_created_human"]}"""
        )
        # return headers
        return item


def make_pirxts_unique(
    my_redis,
    main_key="pirxts:unlimited:headers",
    f_cache="temp/prepared_headers.obj",
):
    """
    хочу пересохранить только уникальные хедеры - фильтррую всё
    """
    fun = "make_pirxts_unique"
    logger.debug2(fun)

    load_from = "redis"
    load_from = "cache"

    my_redis.main_key = main_key
    logger.info("my_redis=%s" % my_redis)
    logger.debug("len=%s" % my_redis.len())

    if load_from == "redis":
        logger.debug("loading from readis...")
        start = 0
        stop = -1
        # stop = 9
        prepared_headers = my_redis.load_list(start=start, stop=stop)

        logger.debug(
            "saving %s items to %s" % (len(prepared_headers), f_cache)
        )
        obj_to_file(prepared_headers, f_cache)
    else:
        logger.debug("loading from cache...")
        prepared_headers = obj_from_file(f_cache)

    logger.debug("filtering...")
    hashes = set()
    cnt_dubli = 0
    uniques = []
    for item in prepared_headers:
        # show_dict(item["headers"])
        pirxt_headers = item["headers"]["pirxt_headers"]
        h = to_hash(pirxt_headers)
        if h in hashes:
            cnt_dubli += 1
            continue

        uniques.append(item)
        hashes.add(h)
        # wait_for_ok()

    logger.debug(
        "have %s dubli, unique %s/%s dubli"
        % (cnt_dubli, len(uniques), len(prepared_headers))
    )

    logger.debug("saving back to redis...")
    my_redis.delete_key()
    my_redis.add_list(uniques)
    logger.debug("saved successfully")
    logger.debug("+%s" % fun)


def try_execute_redis_function(*args, **kwargs):
    _ = {
        "max_duration": 60 * 3,
        "message": "redis not working",
        "errors_to_break": [
            "WRONGTYPE Operation against a key holding the wrong kind of value",
        ],
    }
    kwargs.update(_)
    return try_execute_function(*args, **kwargs)


def decode_redis(src, encoding="utf-8"):
    if isinstance(src, list):
        rv = list()
        for key in src:
            rv.append(decode_redis(key, encoding=encoding))
        return rv
    elif isinstance(src, dict):
        rv = dict()
        for key in src:
            rv[key.decode(encoding=encoding)] = decode_redis(
                src[key], encoding=encoding
            )
        return rv
    elif isinstance(src, bytes):
        return src.decode(encoding=encoding)
    else:
        raise Exception("type not handled: " + type(src))


def get_redis_pirxt_server(main_key="pirxt_list", **kwargs) -> KyxaRedis:
    host = "173.249.2.50"  # contabo
    port = 6379
    port = 6371
    password = "wrong_password"
    password = "LJ9dsdflsdfhY675d"

    if main_key in ["unlimited_pirxts"]:
        main_key = "pirxts:unlimited:headers"

    if not main_key:
        raise ValueError(f"empty {main_key=}")

    _kwargs = {
        "host": host,
        "port": port,
        "password": password,
        "db": 0,
        "main_key": main_key,
    }
    _kwargs.update(kwargs)
    my_redis = RedisPirxtServer(**_kwargs)
    logger.info(f"{my_redis=}")
    return my_redis


if __name__ == "__main__":

    from modules import *

    special = "KyxaRedis"
    special = "want_delete_all_keys"

    if special == "KyxaRedis":
        main_key = "user_01"

        _kwargs = {
            "main_key": main_key,
            "processing_mode": "pickle",
        }
        my_redis = KyxaRedis(**_kwargs)

        func_save = my_redis.save_dict
        func_load = my_redis.load_dict
        func_load_key = my_redis.load_dict_key

        t = 1
        if t:
            func_save = my_redis.save
            func_load = my_redis.load
            func_load_key = my_redis.load_key

        logger.info(f"{my_redis=}")

        t = 1
        if t:
            data = {
                "t_add_human": get_human_time(),
                "cookies": random_suffix(),
                "pstk": random_suffix(),
                "int": 10,
                "float": 22.5,
                "ts": datetime.datetime.utcnow(),
            }
            data0 = {
                "users": 10,
                "timestamp": datetime.datetime.utcnow().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            }

            t = 0
            if t:
                my_redis.save("some text")

            t = 0
            if t:
                deleted = my_redis.delete_key()
                logger.debug(f"{deleted=}")

            saved = func_save(data)
            logger.debug(f"{saved=} of {data=}")

        data = func_load()
        logger.debug(f"loaded: {data=}")

        # можно ли получить инфу по подключу
        subkey = "ts"
        key = f"{main_key}"
        data = func_load_key(key=key, subkey=subkey)
        logger.debug(f"{data=} for {key=}, {subkey=}")

        data = func_load(key="not_exists")
        logger.debug(f"loaded not_existed: {data=}")

    elif special == "want_delete_all_keys":

        t = 0
        if t:
            files = [
                r"s:\python2.7\Lib\site-packages\universal_bookmaker\api_bet365\temp\auto_pirxt2.txt",
                r"s:\python2.7\Lib\site-packages\universal_bookmaker\api_bet365\temp\auto_pirxt.txt",
            ]
            for f in files:
                h = to_hash(text_from_file(f))
                print("h=%s for f=%s" % (h, f))
            os._exit(0)

        host = "173.249.2.50"  # contabo
        port = 6379
        port = 6371
        password = "wrong_password"
        password = "LJ9dsdflsdfhY675d"

        _kwargs = {
            "host": host,
            "port": port,
            "password": password,
            "db": 0,
        }

        # без моей либы - просто тест редиса
        t = 0
        if t:
            rdb = Redis(**_kwargs)
            logger.info("default Redis rdb=%s" % rdb)
            setuped = rdb.set("test", time.time())

        klas = KyxaRedis
        klas = RedisPirxtServer

        my_redis = klas(**_kwargs)

        want_delete_all_keys = False
        want_delete_all_keys = True
        if want_delete_all_keys:
            my_redis.main_key = "pirxts:unlimited:headers"

            t = 0
            if t:
                tip = my_redis.rdb.type(my_redis.main_key)
                logger.debug(
                    "my_redis=%s, main_key=%s, type=%s, cnt_elements=s"
                    % (my_redis, my_redis.main_key, tip)
                )
            t = 0
            if t:
                value = my_redis.load()
                logger.debug("value=%s" % value)

            wait_for_ok(
                "delete all keys? Run `service redis-server restart` before deleting."
            )
            """
            Redis is loading the dataset in memory
            """
            deleted = my_redis.delete_key()
            logger.info(f"{deleted=}")
            os._exit(0)

            wait_for_ok("deleted, insert empty?")

            my_redis.add_list([{}])
            # last = my_redis.pop_last_element()
            logger.info(f"deleted, exit")
            os._exit(0)

        logger.info(
            list(
                map(
                    str,
                    [
                        my_redis,
                        my_redis.klass_name,
                        my_redis.t_last_created_headers,
                        # my_redis.seconds_since_last_creation(),
                    ],
                )
            )
        )
        # wait_for_ok()

        t = 0
        if t:
            data = {
                "x": 1.25,
                "y": "yyy",
            }
            saved = my_redis.save(data)
            logger.debug("saved=%s" % saved)
            os._exit(0)

        special = "save"
        special = "make_pirxts_unique"
        special = "exists"
        special = "test_list"

        t_start_main = time.time()

        if special == "make_pirxts_unique":
            r = make_pirxts_unique(my_redis)
            logger.info("r=%s" % r)

        elif special == "exists":
            r = my_redis.exists("key_not_exists")
            logger.info("r=%s" % r)

        elif special == "test_list":
            key = "pirxts:Waldasa90:headers"
            key = "pirxt_list"
            key = "test_list"

            special = "brpop"
            special = "add_list"

            t = 1
            if t:
                lst = my_redis.load_list(key=key)
                show_list(lst)
                logger.info("success loaded")
                os._exit(0)
            t = 0
            if t:
                my_redis.delete_key(key)
                wait_for_ok("deleted key")

            if special == "brpop":
                for i in range(1):
                    logger.debug("had %s elements" % (my_redis.len(key)))
                    f_headers = r"s:\python2.7\Lib\site-packages\universal_bookmaker\api_bet365\temp\auto_pirxt.txt"

                    t = 0
                    if t:
                        value = my_redis.pop_last_element(key=key)
                        logger.debug("value=%s" % value)

                        t = 1
                        if t:
                            headers = value["headers"]
                            text_to_file(headers, f_headers)
                    else:
                        headers = my_redis.get_pirxt_headers()
                        text_to_file(headers, f_headers)

                # my_redis.delete_key(key)

            elif special == "add_list":
                for i in range(3):
                    lst = [{"from": i} for _ in range(50)]
                    # lst = ["test" for _ in range(5)]
                    added = my_redis.add_list(lst, key=key)
                    logger.debug("added=%s" % added)
            else:
                logger.error("unknown special=%s" % special)

        elif special == "save":
            want_save = False
            want_save = True
            key = "oddscorp"

            for i in range(10):
                t_start = time.time()
                # setuped = rdb.set(key, t_start)

                if want_save:
                    data = {
                        "t_start": t_start,
                    }
                    # data = "1"
                    setuped = my_redis.save(data)
                else:
                    setuped = None

                duration_set = time.time() - t_start

                t_start = time.time()
                value = my_redis.load()
                duration = time.time() - t_start
                logger.debug(
                    "set in %.3f, got in %.3f seconds, key=%s, value=%s setuped=%s"
                    % (duration_set, duration, key, value, setuped)
                )

                # time.sleep(1)

        else:
            logger.error("unknown special=%s" % special)

        duration_main = time.time() - t_start_main
        logger.debug("duration_main=%.3f" % duration_main)

    else:
        logger.critical(f"{special=}")
