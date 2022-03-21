# -*- coding: utf-8 -*-
from no_war_project.settings import *

from typing import List
from modules.excel_functions import *
from modules.mozgo_funcs import execute_func_while_not_found
from no_war_project.model import *
from no_war_project.tasks_downloader import *
from no_war_project.tasks_decryptor import HiderUnziper
from no_war_project.urls_normalizer import *


logger = get_logger(__name__)


class UniversalTasksReader:
    name = "UniversalTasksReader"

    def __init__(self, **kwargs):
        debug = kwargs.pop("debug", False)
        d = kwargs.pop("d", False)
        logger.debug(f"UniversalTasksReader {d=}")

        settings = kwargs.pop("settings", None)
        if settings is None:
            settings = get_default_settings(d_root=d)

        work_with = kwargs.pop(
            "work_with", settings.get("work_with", ["youtube", "instagram"])
        )
        work_with = clear_list(work_with)

        self.debug = debug

        self.settings = settings
        self.work_with = work_with

        self.tasks = []
        self.t_last_read = 0  # когда последний раз создавал хедеры

    def seconds_since_last_read(self):
        """сколько прошло времени с последнего успешного создания пирхтов"""
        seconds_since_last_created_headers = time.time() - self.t_last_read
        return seconds_since_last_created_headers

    # def select_task(self, tasks=None):
    #     if not tasks:
    #         tasks = self.tasks

    def get_tasks(self, func=None, func_filter=None, **kwargs):
        if not func:
            func = self.get_tasks_one_ideal
        if func_filter == "leave_only_unfinished_tasks":
            func_filter = leave_only_unfinished_tasks
        kwargs["func_filter"] = func_filter

        tasks = execute_func_while_not_found(func, **kwargs)
        # tasks = leave_only_unfinished_tasks(tasks)
        return tasks

    def get_tasks_one_ideal(self, *args, **kwargs):
        """обрабатываем задачи
        делаем уникальными
        """
        fun = "get_tasks_one_ideal"
        try:
            tasks = self.get_tasks_one(*args, **kwargs)
        except Exception as er:
            logger.debug(f"{er=}")
            logger.error(f"ERROR {fun}")
            tasks = []

        unique_tasks = unique(tasks)

        f = getattr(self, "f", None)
        where = ""
        if f:
            where = f" in {f=}"

        logger.debug0(
            f"         unique {len(unique_tasks)}/{len(tasks)} tasks {where}"
        )
        return unique_tasks

    def get_tasks_one(self):
        """
        """
        raise ValueError(f"get_tasks not implemented")

    def urls_to_tasks(self, urls=[], debug=None):
        if debug is None:
            debug = self.debug

        data = []
        alternative_zhaloba = self.settings["message_dislike_youtube_chanel"]
        for url in urls:
            chanel_url_youtube = guess_youtube_chanel_url(url)
            channel_url_instagram = guess_instagram_url(url)
            channel_url_telegram = guess_telegram_url(url)
            task = None
            if chanel_url_youtube:
                if "youtube" in self.work_with:
                    _ = {
                        "url": chanel_url_youtube,
                        "alternative_zhaloba": alternative_zhaloba,
                    }
                    task = YoutubeChanelDislike(**_)

            elif channel_url_instagram:
                if "instagram" in self.work_with:
                    _ = {
                        "url": channel_url_instagram,
                    }
                    task = InstagramDislike(**_)

            elif channel_url_telegram:
                if "telegram" in self.work_with:
                    _ = {
                        "url": channel_url_telegram,
                        "alternative_zhaloba": alternative_zhaloba,
                    }
                    task = TelegramDislike(**_)

            else:
                if debug:
                    logger.debug(f"          unknown task type for {url=}")

            if task:
                data.append(task)

        return data

    def __repr__(self):
        return f"<{self.name} work_with {self.work_with}>"


class TextTasksReader(UniversalTasksReader):
    name = "TextTasksReader"

    def __init__(self, f="", **kwargs):
        UniversalTasksReader.__init__(self, **kwargs)
        self.f = f

    def get_tasks_one(self):
        urls = read_urls_from_text_file(self.f)
        data = self.urls_to_tasks(urls)
        return data

    def __repr__(self):
        return f"<{self.name}: from f={self.f}>"


class MusorExcelTasksReader(UniversalTasksReader):
    """любая екселька, в любом поле всё возможноJ"""

    name = "MusorExcelTasksReader"

    def __init__(self, f="", **kwargs):
        UniversalTasksReader.__init__(self, **kwargs)
        self.f = f

    def get_tasks_one(self):
        raw_data = read_xlsx(f=self.f, spec_task="all_rows")
        data = []
        for num, item in enumerate(raw_data, 1):
            # logger.debug(f"{num}/{len(raw_data)} {item=}")
            item_as_text = " ".join(map(str, item))
            data.append(item_as_text)
        txt = "\n".join(data)
        # logger.debug(f'{txt=}')
        # nah
        urls = find_all_urls_in_text(txt)
        data = self.urls_to_tasks(urls)

        return data

    def __repr__(self):
        return f"<{self.name}: from f={self.f}>"


class PrettyExcelTasksReader(UniversalTasksReader):
    """красивая екселька, подготовленная"""

    name = "PrettyExcelTasksReader"

    def __init__(self, f="", **kwargs):
        UniversalTasksReader.__init__(self, **kwargs)
        self.f = f

    def get_tasks_one(self, debug=None):
        if debug is None:
            debug = self.debug
        raw_data = read_tasks_from_prepared_excel(self.f)
        alternative_zhaloba = self.settings["message_dislike_youtube_chanel"]
        data = []
        for item in raw_data:
            task = None
            # logger.debug(f"{item=}")
            url = item.get("chanel_url")
            zhaloba = item["zhaloba"]
            chanel_url_youtube = guess_youtube_chanel_url(url)
            channel_url_instagram = guess_instagram_url(url)
            channel_url_telegram = guess_telegram_url(url)
            if chanel_url_youtube:
                if "youtube" in self.work_with:
                    _ = {
                        "url": chanel_url_youtube,
                        "bad_videos": item["bad_videos"],
                        "zhaloba": zhaloba,
                        "alternative_zhaloba": alternative_zhaloba,
                    }
                    task = YoutubeChanelDislike(**_)

            elif channel_url_instagram:
                if "instagram" in self.work_with:
                    _ = {
                        "url": channel_url_instagram,
                    }
                    task = InstagramDislike(**_)

            elif channel_url_telegram:
                if "telegram" in self.work_with:
                    _ = {
                        "url": channel_url_telegram,
                        "zhaloba": zhaloba,
                        "alternative_zhaloba": alternative_zhaloba,
                    }
                    task = TelegramDislike(**_)

            else:
                if debug:
                    logger.debug(f"          unknown task type for {item=}")

            if task:
                data.append(task)
        return data

    def __repr__(self):
        return f"<{self.name}: from f={self.f}>"


class AllTasksReader(UniversalTasksReader):
    """читаю задачи:
        извне + проверяю
        свои секретные
    """

    name = "AllTasksReader"

    def __init__(self, pwd=None, **kwargs):
        UniversalTasksReader.__init__(self, **kwargs)

        d = kwargs.pop("d", get_f_here())
        d_downloaded = kwargs.pop("d_downloaded", f"{d}/temp/tasks")
        logger.debug(f"AllTasksReader {d=} {d_downloaded=}")
        self.d = d
        self.d_downloaded = d_downloaded

        # добавляю секретную папку - с нее все ссылки засчитываются
        self.super_directory = f"{self.d}/!TASKS_SLAVA_UKRAINI!"

        # задержки
        delays_between_reports = kwargs.pop("delays_between_reports", {})
        d_delays_between_reports = {
            "YoutubeChanelDislike": "5m-10m",
            "InstagramDislike": "5m-10m",
            "TelegramDislike": "5m-10m",
        }  # каждому типу - своя задержка
        delays_between_reports = add_defaults(
            delays_between_reports, d_delays_between_reports
        )

        # добавляю секретную папку - с нее все ссылки качаются
        _ = {
            "d": d_downloaded,
        }

        downloader = HtmlTasksDownloader(**_)
        self.downloader = downloader

        hider = HiderUnziper(d=f"{self.d_downloaded}", pwd=pwd)
        self.hider = hider

        self.delays_between_reports = delays_between_reports
        # logger.debug(f"{self.delays_between_reports=}")
        # logger.debug(f"{self.work_with=}")
        # os._exit(0)

    def get_tasks_one(self):
        files_with_tasks = []

        # сначала качаем все файлы
        logger.debug0(f"monitoring live tasks")
        r_downloaded = self.downloader.get_tasks()
        logger.debug(f"{r_downloaded=}")

        # теперь их разархивируем и собираем только те файлы, которые подходят
        hider = self.hider
        r = hider.decrypt_dir()
        logger.debug0(f"decrypted directory {r=}")

        r = hider.unzip_dir()
        logger.debug0(f"unzip directory {r=}")

        identical_directories = hider.return_identical_directories()
        logger.debug0(f"{identical_directories=}")

        super_directory = self.super_directory
        logger.debug(f"{super_directory=}")
        identical_directories.append(super_directory)

        for d in identical_directories:
            files = get_all_file_names(d)
            for f in files:
                files_with_tasks.append(f)

        logger.debug0(
            f"selected {len(files_with_tasks)} files from tasks, {files_with_tasks=}"
        )

        tasks = read_all_tasks_from_files(d=self.d, files=files_with_tasks)

        want_add_fixed_urls = False
        want_add_fixed_urls = True
        if want_add_fixed_urls:
            urls_text = """
            https://t.me/zvpered
            """
            urls = find_all_urls_in_text(urls_text)
            fixed_tasks = self.urls_to_tasks(urls)
            for num, _ in enumerate(fixed_tasks, 1):
                # _.priority = 100
                if num in [1]:
                    _.priority = 100
                else:
                    _.priority = 99

            logger.debug0(f"add {len(fixed_tasks)} fixed tasks")
            logger.debug(f"{fixed_tasks=}")

            tasks = tasks + fixed_tasks
            # os._exit(0)

        r_tasks_unfinished = leave_only_unfinished_tasks(
            tasks,
            work_with=self.work_with,
            delays=self.delays_between_reports,
            mode_return="detailed",
        )
        tasks_unfinished = r_tasks_unfinished["tasks"]
        reasons = r_tasks_unfinished["reasons"]

        logger.debug3(
            f"found {len(tasks_unfinished)}/{len(tasks)} unfinished tasks, skip {reasons=}"
        )
        if (
            len(tasks_unfinished) == 0
            and len(tasks) > 0
            and "delayed" not in reasons
        ):
            logger.info(
                f"Ура, все задачи выполнены! Но не выключайте программу, ждем новых задач."
            )
        return tasks_unfinished

    def __repr__(self):
        return f"<{self.name}: downloader={self.downloader} hider={self.hider} {self.work_with=}>"


def read_tasks_from_prepared_excel(f: str = None):
    if f is None:
        f = r"ЗАВДАННЯ.xlsx"

    kwargs = {
        "f": f,
    }
    raw_data = read_xlsx(**kwargs)
    data = []
    for ua_acc in raw_data:
        item = {}
        for k, v in ua_acc.items():
            if k == "канал":
                k = "chanel_url"
            elif k == "на які відео скаржитися":
                k = "bad_videos"
            elif k == "скарга":
                k = "zhaloba"

            item[k] = v
        data.append(item)
    return data


def read_urls_from_text_file(f: str = None):
    if f is None:
        f = r"!ЗАВДАННЯ\youtube.txt"

    data = []
    kwargs = {
        "f": f,
    }
    if not file_exists(f):
        logger.warning(f"no file {f} with tasks")
        return data

    urls = find_all_urls_in_text(text_from_file(f))
    return urls


def find_all_urls_in_text(txt=""):
    expression = "/(?:(?:https?|ftp|file):\/\/|www\.|ftp\.)(?:\([-A-Z0-9+&@#\/%=~_|$?!:,.]*\)|[-A-Z0-9+&@#\/%=~_|$?!:,.])*(?:\([-A-Z0-9+&@#\/%=~_|$?!:,.]*\)|[A-Z0-9+&@#\/%=~_|$])/igm"
    expression = "(http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])"
    expression = "(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-&?=%.\+]+"
    return re.findall(expression, txt)


def find_dubli(tasks):
    for i in range(0, len(tasks)):
        el1 = tasks[i]
        for j in range(i + 1, len(tasks)):
            el2 = tasks[j]
            if el1 == el2:
                logger.info(f"{i} * {j}: {el1} == {el2}")


def guess_type_of_taskFile(f):
    """угадываем тип файла с задачами"""
    tip = None
    rash = f.split(".")[-1].lower()
    f_name = os.path.basename(f)

    if f_name.startswith("~$") and rash in ["xlsx"]:
        tip = "skip_temp_excel_file"

    elif rash in ["txt"]:
        tip = "TextTasksReader"

    elif rash in ["xlsx"]:
        # узнаем - это pretty задача или фигня
        columns = read_xlsx(f=f, spec_task="return_keys")
        if (
            "канал" in columns
            and "на які відео скаржитися" in columns
            and "скарга" in columns
        ):
            tip = "PrettyExcelTasksReader"
        else:
            tip = "MusorExcelTasksReader"
    else:
        logger.warning(f"unknown tip for file {f}")

    return tip


def leave_only_unfinished_tasks(
    tasks, work_with=None, delays={}, mode_return="list"
):
    # logger.debug(f"{work_with=}")
    # os._exit(0)
    reasons = {
        "finished": 0,
        "bad_task_type": 0,
        "delayed": 0,
    }
    unfinished_tasks = []
    for task in tasks:
        if task.is_done:
            reasons["finished"] += 1
            continue

        is_good = False
        if work_with:
            is_good = False
            # logger.debgu(f"{task=} {work_with=}")
            for name in work_with:
                if name == "youtube" and task.tip == "YoutubeChanelDislike":
                    is_good = True
                    break
                elif name == "instagram" and task.tip == "InstagramDislike":
                    is_good = True
                    break
                elif name == "telegram" and task.tip == "TelegramDislike":
                    is_good = True
                    break

                else:
                    pass
                    # logger.error(
                    #     f"bad_tip for {name=} with {task.tip=} {work_with=}"
                    # )

        if not is_good:
            reasons["bad_task_type"] += 1
            continue

        unfinished_tasks.append(task)

    if delays:
        logger.debug0("check delays")
        real_delays = {}
        for tip, delay in delays.items():
            real_delay = get_random_value_in_range(delay)
            logger.debug(f"   {tip=} {real_delay=} for {delay=}")
            real_delays[tip] = real_delay
        logger.debug(f"{real_delays=}")

        tip_to_life = {}
        actual_tasks = []
        for task in unfinished_tasks:
            tip = task.tip
            if tip not in tip_to_life:
                life = task.get_time_after_successReport()
                tip_to_life[tip] = life
            life = tip_to_life[tip]
            delay = real_delays[tip]
            # logger.debug(f"{tip=} {life=} {delay=}")

            if life != -1 and life < delay:
                logger.debug(f"skip / {life=}<{delay} delay")
                reasons["delayed"] += 1
                continue
            actual_tasks.append(task)
        logger.debug(
            f"{len(actual_tasks)}/{len(unfinished_tasks)} are actual (passed enough time)"
        )
        unfinished_tasks = actual_tasks[:]

    reasons = {
        k: v for k, v in reasons.items() if v
    }  # удаляю нулевые элементы :)

    logger.debug0(
        f"found {len(unfinished_tasks)}/{len(tasks)} tasks, skip reasons: {reasons}"
    )
    if mode_return == "list":
        return unfinished_tasks
    else:
        _ = {
            "tasks": unfinished_tasks,
            "reasons": reasons,
        }
        return _


def read_all_tasks_from_files(d="", d_root="", good_names=[], files=None):
    """получаю все задачи из файлов"""
    fun = "read_all_tasks_from_files"
    if not d_root:
        d_root = d
    logger.debug0(f"[{fun} {d=} {d_root=}")
    settings = get_default_settings(d_root=d)
    all_tasks = []
    if not files:
        files = get_all_file_names(d)
    for num_f, f in enumerate(files, 1):
        logger.debug(f"read file {num_f}/{len(files)} {f}")
        if good_names:
            found_name = False
            f_name = os.path.basename(f)
            for name in good_names:
                if name in f_name:
                    found_name = True
                    break
            if not found_name:
                logger.debug(f"{f_name=} not in {good_names=}, so skip")
                continue

        tip = guess_type_of_taskFile(f)
        logger.debug(f"{tip=}")

        if not tip:
            logger.debug(f" unknown type of {f}")
            continue
        elif tip.startswith("skip"):
            logger.debug(f" skip file")
            continue

        if tip == "TextTasksReader":
            klas = TextTasksReader
            kwargs = {
                "f": f,
            }
        elif tip == "PrettyExcelTasksReader":
            klas = PrettyExcelTasksReader
            kwargs = {
                "f": f,
            }
        elif tip == "MusorExcelTasksReader":
            klas = MusorExcelTasksReader
            kwargs = {
                "f": f,
            }
        else:
            logger.critical(f"unknown {tip=}")
            os._exit(0)

        kwargs["settings"] = settings

        tasks_reader = klas(**kwargs)
        tasks = tasks_reader.get_tasks(max_step=1)
        logger.debug(f"found {len(tasks)} tasks in {f=}")
        all_tasks.append(tasks)

    # show_list(all_tasks)
    all_tasks = slitj_list_listov(all_tasks, want_nepustie_only=0)
    all_tasks_unique = unique(all_tasks)
    logger.debug0(
        f"found {len(all_tasks_unique)}/{len(all_tasks)} from {len(files)} files in {d}"
    )
    return all_tasks_unique


if __name__ == "__main__":
    special = "read_tasks_from_prepared_excel"
    special = "read_urls_from_text_file"

    special = "read_all_tasks_from_files"
    special = "someTasksReader"

    if special == "read_urls_from_text_file":
        data = read_urls_from_text_file()
        logger.debug(f"{len(data)} items:")
        show_list(data)

    elif special == "read_tasks_from_prepared_excel":
        r = read_tasks_from_prepared_excel()
        logger.debug(f"{r=}")

    elif special == "someTasksReader":
        special = "TextTasksReader"
        special = "MusorExcelTasksReader"
        special = "PrettyExcelTasksReader"
        special = "AllTasksReader"

        if special == "TextTasksReader":
            f = r"s:\!kyxa\!code\no_war\data\!ЗАВДАННЯ - СЛАВА УКРАЇНІ\youtube.txt"
            klas = TextTasksReader
            kwargs = {
                "f": f,
            }

        elif special == "PrettyExcelTasksReader":
            f = r"s:\!kyxa\!code\no_war\data\!ЗАВДАННЯ - СЛАВА УКРАЇНІ\pretty_ЗАВДАННЯ.xlsx"
            klas = PrettyExcelTasksReader
            kwargs = {
                "f": f,
            }
        elif special == "MusorExcelTasksReader":
            f = r"s:\!kyxa\!code\no_war\data\!ЗАВДАННЯ - СЛАВА УКРАЇНІ\musor.xlsx"
            klas = MusorExcelTasksReader
            kwargs = {
                "f": f,
            }
        elif special == "AllTasksReader":
            d = r"s:\!kyxa\!code\no_war"
            klas = AllTasksReader
            kwargs = {
                "d": d,
            }
        else:
            logger.critical(f"unknown {special=}")
            die()

        work_with = "youtube\ninstagram"
        work_with = ["instagram"]
        work_with = ["youtube"]
        kwargs["work_with"] = work_with

        tasks_reader = klas(**kwargs)
        logger.info(f"{tasks_reader=}")
        # nah

        special = "get_tasks"
        func = tasks_reader.get_tasks
        func = tasks_reader.get_tasks_one
        func = tasks_reader.get_tasks_one_ideal

        if special == "get_tasks":
            tasks = func()
            logger.info(f"{len(tasks)} {tasks=}")
            show_list(tasks)

            # tasks[0].mark_done()
        logger.info(f"details: {tasks[0].details}")
        logger.debug(f"have {len(tasks)}, unique {len(unique(tasks))}")
        find_dubli(tasks)

    elif special == "read_all_tasks_from_files":
        d = r"s:\!kyxa\!code\no_war\!ЗАВДАННЯ"
        good_names = ["pretty"]
        good_names = ["musor", "pretty"]
        tasks = read_all_tasks_from_files(d=d, good_names=good_names)

        logger.info(f"{len(tasks)} tasks:")
        show_list(tasks)
        logger.info(f"details: {tasks[0].details}")
        logger.debug(f"have {len(tasks)}, unique {len(unique(tasks))}")
        find_dubli(tasks)

        searching_urls = ["UCz63ar5uANqYTKJIwnUQucw"]
        for task in tasks:
            found = False
            for s in searching_urls:
                # logger.debug(f'{s=} {task.hash_human=}')
                if s in task.hash_human:
                    logger.info(f"found {s} in {task}")
                    found = True
                    break

    else:
        logger.critical(f"no {accounts=}")
