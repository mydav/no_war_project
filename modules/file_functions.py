import os
import stat
import time
import pathlib
import logging
from modules.list_functions import flat, clear_list
import pickle
from modules_23.file_functions import *
from modules.list_functions import list_peretyn

# logger = logging.getLogger(__name__)
logger = get_logger(__name__)


def copy_file(f_from, f_to, debug=False):
    r = copy_file_shutil(f_from, f_to)
    if debug:
        logger.debug(f"{r=} for copy_file {f_from} to {f_to}")

    return r
    # if file_exists(f_from):
    #     return text_to_file(text_from_file(f_from, "rb"), f_to, "wb")
    # else:
    #     logger.error("ERROR_copy_file: no file %s" % f_from)
    # return False


def move_file(f_from, f_to):
    # print 'move %s to %s' % (f_from, f_to)
    status = copy_file(f_from, f_to)
    if status == False:
        return False
    os.remove(f_from)
    return status


def save_text_html(text, name=""):
    save_text(text, name=name, rash="html")


def save_text(text, name="", rash="txt"):
    f_to = f"temp/{name}.{rash}"
    text_to_file(text, f_to)


def list_from_file(f_name=""):
    if not file_exists(f_name):
        return []

    lst = clear_list(text_from_file(f_name))
    return lst


def obj_from_file(f_name, sposob="pickle", encoding="utf-8"):
    """достает обьект питоновский из файла
    encoding = "latin1"
    encoding = "bytes"
    """
    fun = "obj_from_file"

    if sposob == "marshal":
        f = open(f_name, "rb")
        try:
            return marshal.load(f)
        except Exception as er:
            logger.error(f"ERROR {fun}: {sposob} {er}")
            f.close()
            return marshal.load(f)

    elif sposob == "pickle":
        f = open(f_name, "rb")
        try:
            return pickle.load(f, encoding=encoding)
        except Exception as er:
            logger.error(f"ERROR {fun}: {sposob} {er}")
            f.close()
            # return marshal.load(f)
            return "error obj_from_file"

    elif sposob == "json":
        html = text_from_file(f_name)
        obj = k_load_json(html)
        return obj


def obj_to_file(obj, f_name, polube=0, sposob="pickle"):
    """заганяет обьект питоновский в файл"""
    fun = "obj_to_file"
    if os.path.dirname(f_name) != "":
        mkdir(f_name)

    try:
        if polube:
            print("polube...", end="")
            obj0 = edit_dict_before_serialize(obj)
        else:
            obj0 = obj

        if sposob == "marshal":
            f = open(f_name, "wb")
            marshal.dump(obj, f)
            f.close()

        elif sposob == "json":
            json = k_to_json(obj)
            text_to_file(json, f_name)

        elif sposob == "pickle":
            f = open(f_name, "wb")
            pickle.dump(obj, f)
            f.close()

    except Exception as er:
        print(f"{fun} - error with {f_name}")
        print(er)
        rmfile(f_name)

    if file_exists(f_name):
        return 1
    return 0


def obj_from_file_p(f):
    """pickle"""
    return obj_from_file(f, sposob="pickle")


def obj_to_file_p(obj, f_name, polube=0):
    """pickle"""
    return obj_to_file(obj, f_name, polube=polube, sposob="pickle")


def text_from_file(f, *args, **kwargs):
    if not isinstance(f, list):
        f = [f]
    return text_from_files(f, *args, **kwargs)


def text_from_files(files: list, mode="r", enc="utf8", errors="ignore"):
    found_file = None
    for f in files:
        if file_exists(f):
            found_file = f
            break
    if found_file is None:
        logger.error(f"no file in {files=}")
        return None

    return text_from_file_one(found_file, mode=mode, enc=enc, errors=errors)


def text_from_file_one(f_name="", mode="r", enc="utf8", errors="ignore"):
    if not os.path.isfile(f_name):
        logger.error(f"no file {f_name}")
        return None

    with open(f_name, mode, encoding=enc, errors=errors) as f:
        body = f.read()
    return body


def text_to_utf8_for_saving(text, charset="utf-8"):
    if isinstance(text, str):
        text = text.encode(charset)
    return text


def text_to_file(text, f_name="", mode="wb", charset="utf-8"):
    fun = "text_to_file"
    if f_name is None:
        return

    mkdir(f_name)

    text = text_to_utf8_for_saving(text, charset)

    try:
        with open(f_name, mode) as file:
            file.write(text)
    except Exception as er:
        logger.error(f"error {fun} {er=}")


def mkdir(f_name=""):
    """making directory recursively"""
    d_name = os.path.dirname(f_name)
    if not d_name:
        return True
    return make_dir_for_dir(d_name)


def make_dir_for_dir(d_name):
    """реально создаю папку"""
    if not dir_exists(d_name):
        pathlib.Path(d_name).mkdir(parents=True, exist_ok=True)

        if dir_exists(d_name):
            logger.debug(f'mkdir success: created "{d_name}"')
        else:
            logger.error(f'mkdir error: directory "{d_name}" not created')
    else:
        pass
        # logger.debug(f'dir already exists "{d_name}"')


make_dir_for_file = mkdir  # синонимы


def file_exists(f=""):
    if not f:
        return False
    return os.path.isfile(f)


def dir_exists(f=""):
    return os.path.isdir(f)


def rmfile(f):
    if file_exists(f):
        try:
            os.remove(f)
        except Exception as er:
            logger.error(f'error rmfile "{f}", er == {er}')
            pass


def get_all_file_names(
    dir_names=[],
    bad_dirs=[],
    bad_names=[],
    otl=0,
    searching="files",
    debug=False,
):
    """ф-я получает название директории, и выводит список всех файлов в ней"""

    if not isinstance(dir_names, list):
        dir_names = [dir_names]

    if debug:
        logger.debug(f"get_all_file_names from {dir_names}")

    files = []
    for dir_name in dir_names:
        dir_name = normalize_file_name(dir_name)
        # logger.debug(f"{dir_name=}")
        files_and_folders = get_all_file_and_dir_names(dir_name)

        if bad_names:
            files_and_folders_good = []
            for f in files_and_folders:
                bad = False
                for bad_name in bad_names:
                    if bad_name in f:
                        bad = True
                        break
                if bad:
                    continue
                files_and_folders_good.append(f)
            if debug:
                logger.debug(
                    f"{len(files_and_folders_good)}/{len(files_and_folders)} good names for {bad_names=}"
                )
            files_and_folders = files_and_folders_good

        if debug:
            logger.debug(
                f"{len(files_and_folders)} files-folders in {dir_name=}, {files_and_folders=}"
            )

        if bad_dirs:
            good_dirs = []

            # dirs = list(filter(os.path.isdir, files_and_folders))
            dirs = files_and_folders[:]

            for d in dirs:
                parts = d.split("\\")
                # pretty(parts)
                # wait_for_ok(f'{d} is good?')

                # if d in bad_dirs:
                peretyn = list_peretyn(parts, bad_dirs)
                if peretyn:
                    if otl:
                        m = f'    bad directory "{peretyn}" in "{d}"'
                        print(m)
                        # wait_for_ok()
                    continue
                else:
                    good_dirs.append(d)

            if otl:
                if dirs != good_dirs:
                    logger.debug(f'good dirs in "{dirs}": {good_dirs}')
                    # wait_for_ok()

            ##сначала добавляем файлы, потом папки только те, что подходят
            # for _ in filter(os.path.isfile, files_and_folders):
            #    good_dirs.append(_)

            files_and_folders[:] = good_dirs[:]

            # wait_for_ok()
        # wait_for_ok()
        if searching == "dirs":
            files.append(filter(os.path.isdir, files_and_folders))

        elif searching == "files":
            if debug:
                logger.debug(f"search files in {files_and_folders}")
            files.append(filter(os.path.isfile, files_and_folders))

    files = flat(files)
    files = list(set(files))
    files.sort()
    files = [os.path.abspath(f) for f in files]

    return files


def normalize_file_name(dir_name=""):
    return os.path.abspath(dir_name)


def get_dirNames_level_0(path):
    return [
        _.replace(path, "")
        for _ in get_files_and_dirs_level_0(path, add_path=False)
    ]


def get_dirs_level_0(path):
    """
        получить только папки
    """
    elements = get_files_and_dirs_level_0(path)
    files = []
    for f in elements:
        if os.path.isdir(f):
            files.append(f)
    return files


def get_files_level_0(path):
    """
        получить только файлы
    """
    elements = get_files_and_dirs_level_0(path)
    files = []
    for f in elements:
        if os.path.isfile(f):
            files.append(f)
    return files


def get_files_and_dirs_level_0(path, add_path: bool = True):
    """
        получить файлы и папки с нулевого уровня
    """
    # https://stackoverflow.com/questions/14176166/list-only-files-in-a-directory
    files = []

    if not os.path.isdir(path):
        return files

    for file in os.listdir(path):
        if add_path:
            f = os.path.join(path, file)
        else:
            f = file
        files.append(f)

    return files


def get_all_file_and_dir_names(dir_name, debug=False):
    if debug:
        logger.debug(f"get_all_file_and_dir_names {dir_name}")
    files_all = []
    for root, subdirs, files in os.walk(dir_name):
        if debug:
            logger.debug(f"{root=}")
            logger.debug(f"{subdirs=}")
            logger.debug(f"{files=}")
        for file in os.listdir(root):
            filePath = os.path.join(root, file)
            files_all.append(filePath)

        if debug:
            logger.debug(f"{files_all=}")
        # wait_for_ok()
    return files_all


def file_date_creation(f, mode="human"):
    """время жизни файла"""

    if not file_exists(f) and not os.path.isdir(f):
        return -1

    try:
        file_stats = os.stat(f)
        # print(file_stats)
        #     r = {'f_lm': time.strftime("%m/%d/%Y %I:%M:%S %p",time.localtime(file_stats[stat.ST_MTIME])),   'f_la': time.strftime("%m/%d/%Y %I:%M:%S %p",time.localtime(file_stats[stat.ST_ATIME])),   'f_ct': time.strftime("%m/%d/%Y %I:%M:%S %p",time.localtime(file_stats[stat.ST_CTIME]))}
        #     logger.debug('r=%s' % r)
        time_created = file_stats[stat.ST_MTIME]
        # life = int(time.time()) - time_created
        # mlsec = repr(time_created).split(".")[1][:3]
        if mode == "human":
            life = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(time_created),
            )
            # life = time.strftime(
            #     "%Y-%m-%d %I:%M:%S %p", time.localtime(time_created)
            # )
        else:
            life = time_created
    except Exception as er:
        if mode == "human":
            life = ""
        else:
            life = -1
    return life


def file_life(f, time_created=None):
    """время жизни файла"""

    if not file_exists(f) and not os.path.isdir(f):
        return -1
    if time_created in [-1]:
        return -1

    # print(os.stat(f))

    try:
        if time_created is None:
            time_created = file_date_creation(f, mode="seconds")
        life = int(time.time()) - time_created
    except Exception as er:
        return -1
    return life


def join_text_to_file(text, f_name, delimiter="\n"):
    """добавляет текст к файлу через делиметр"""
    fun = "join_text_to_file"
    if file_exists(f_name):
        t = delimiter + text
    else:
        t = text
    mode = "ab"
    text_to_file(t, f_name, mode)


def add_to_full_log(logs=[], f="full_log.txt", seconds=""):
    # if f=='critical':
    #    f = get_f_log_critical()
    # elif f in ['all', '+']:
    #    f = [get_f_log_critical(), get_f_log()]

    # type_str = type('str')
    # type_un = type(u'str')
    if type(f) != type([1]):
        f = [f]

    if type(logs) != type([1]):
        logs = [logs]

    logs = map(str, logs)

    # if len(logs)>1:
    ##if logs[0]=='acc_log':
    #    f3 = get_f_log_acc(logs[1])
    #    f.append(f3)

    if seconds == "":
        seconds = time.time()
    t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(seconds))
    mess = "%s    %s" % (t, "    ".join(logs))

    for f_one in f:
        join_text_to_file(mess, f_one)


def get_file_name(f):
    return os.path.basename(f)


def json_serialize(obj, filename, use_jsonpickle=True):
    f = open(filename, "w")
    if use_jsonpickle:
        import jsonpickle

        json_obj = jsonpickle.encode(obj)
        f.write(json_obj)
    else:
        simplejson.dump(obj, f)
    f.close()


def json_load_file(filename, use_jsonpickle=True):
    f = open(filename)
    if use_jsonpickle:
        import jsonpickle

        json_str = f.read()
        obj = jsonpickle.decode(json_str)
    else:
        obj = simplejson.load(f)
    return obj


def get_file_size(f):
    """размер файла"""

    if not file_exists(f) and not os.path.isdir(f):
        return -1

    # logger.debug(os.stat(f))

    try:
        size = os.stat(f).st_size
    except Exception as er:
        logger.error("error %s" % er)
        return -1
    return size


def allow_pickling():
    """
    решает ошибку
        pickle.PicklingError: Can't pickle <type 'instancemethod'>: it's not found as __builtin__.instancemethod
        
    https://stackoverflow.com/questions/25156768/cant-pickle-type-instancemethod-using-pythons-multiprocessing-pool-apply-a
    

    :return: 
    """
    logger.debug("allow_pickling")
    import copy_reg
    import types

    def _pickle_method(m):
        if m.im_self is None:
            return getattr, (m.im_class, m.im_func.func_name)
        else:
            return getattr, (m.im_self, m.im_func.func_name)

    copy_reg.pickle(types.MethodType, _pickle_method)


if __name__ == "__main__":
    special = "copy_file"
    t = 1
    if t:
        f = r"s:\!kyxa\!code\!documentation\py4seo\advanced\08\dor_minimum\modules\api_functions.py"
        f_to = r"s:\!chaos\to_obfuscate\modules\api_functions.py"
        copied = copy_file(f, f_to)
        logger.debug(f"{copied=}")
    os._exit(0)
    t = 1
    if t:
        f = os.path.abspath("temp/1.txt")
        f2 = os.path.abspath("temp/2.txt")
        files = [f, f2]
        for _ in range(3):
            add_to_full_log("hello", files)
        logger.info(f"check in {f}")
        print(f)
        os._exit(0)

    t = 1
    if t:
        d = r"s:\!data\!forted\!monitore_surebets"
        dirs = get_dirs_level_0(d)
        print(dirs)
        os._exit(0)
    t = 1
    if t:

        class Foo:
            def __init__(self, hello):
                self.hello = hello

        # make a Foo obj
        obj = Foo("hello world")
        print(obj)
        f_to = "temp/serialized.json"

        t = 1
        if t:
            json_serialize(obj, f_to)

            loaded = json_load_file(f_to)
            print(loaded)
            os._exit(0)

        else:
            obj_str = jsonpickle.encode(obj)
            restored_obj = jsonpickle.decode(obj_str)
            list_objects = [restored_obj]
            # We now get a list with a dictionary, rather than
            # a list containing a Foo object
            print("list_objects: ", list_objects)
        os._exit(0)

    from pprint import pprint

    # text_to_file("test", "temp/test.txt")

    special = "get_all_file_names"
    special = "file_life"
    special = "list_from_file"
    special = "join_text_to_file"

    if special == "join_text_to_file":
        f = "temp/join_text_to_file.txt"
        for i in range(1000):
            print(f"{i}")
            message = f"шаг {i}"
            join_text_to_file(message, f)
        os._exit(0)

    if special == "file_life":
        f = r"s:\!kyxa\!code\!documentation\py4seo\advanced\08\dor_minimum\modules\file_functions.py"
        print(file_life(f))
        print(file_date_creation(f))

    if special == "get_all_file_names":
        d = r"s:\!chaos\!keywords\liallt.club"
        files = get_all_file_names(d)
        print(files)

    if special == "list_from_file":
        f = r"s:\!chaos\!keywords\net_001\domains.txt"
        lst = list_from_file(f)
        pprint(lst)
