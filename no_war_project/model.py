from no_war_project.settings import *

from modules import *
from no_war_project.urls_normalizer import *

logger = get_logger(__name__)


class Task:
    name = "task"
    tip = "unknown_task"
    priority = 10

    def __init__(self, *args, **kwargs):
        self.hash_human = None
        self.hash = None

    def mark_done(self, info=None, f_to=None):
        """
        отметим что задачу выполнили
        """
        t_finished = get_human_time()
        res = {
            "t_finished": t_finished,
            "info": info,
        }
        if not f_to:
            f_to = self.get_file_with_done_file()
        text_to_file(f"{res}", f_to)
        logger.debug(f"+mark_done to {f_to}")

    def get_time_after_successReport(self):
        """сколько прошло время после репорта"""
        f_report = self.get_file_with_reportTime()
        life = file_life(f_report)
        return life

    def mark_reported(self, message=""):
        """отмечаю время когда репорт сделал"""
        f_report = self.get_file_with_reportTime()
        text_to_file(message, f_report)

    @property
    def is_done(self):
        f = self.get_file_with_done_file()
        status = False
        if file_exists(f):
            status = True
        # logger.debug(f"is_done={status} for {f=}")
        return status

    @property
    def min_details(self):
        return f"<task:{self.name}>"

    @property
    def special_details(self):
        return ""

    @property
    def details(self):
        details = (
            f"{self.min_details} with tip {self.tip}, priority {self.priority}"
        )
        if self.special_details:
            details = f"{details}\nspecial: {self.special_details}"
        return details

    def get_file_with_reportTime(self):
        """тут файл, в который время успеха"""
        f = get_f_here(f"temp/!times/report_{self.tip}.txt")
        # logger.debug(f"{f=}")
        return f

    def get_file_with_done_file(self):
        """тут файл, в который отчет поступает"""
        f = get_f_here(f"temp/!finished_tasks/{self.tip}__{self.hash}.txt")
        # logger.debug(f"{f=}")
        return f

    def get_hash(self):
        if getattr(self, "hash", None):
            pass
        else:
            h = to_hash(self.hash_human)
            self.hash = h
        return self.hash

    def get_hash_info(self):
        return [self.url, str(self.bad_videos)]

    def __eq__(self, other):
        return self.hash == other.hash

    def __hash__(self):
        return hash(self.hash)

    def __repr__(self):
        return self.min_details


class Dislike(Task):
    name = "dislike"
    tip = "dislike"
    priority = 20

    def __init__(
        self,
        url="",
        bad_videos="",
        zhaloba="",
        alternative_zhaloba: str = "",
        **kwargs,
    ):
        Task.__init__(self, **kwargs)

        self.url = url

        if isinstance(bad_videos, list):
            pass

        elif not bad_videos or bad_videos is None:
            bad_videos = []

        elif isinstance(bad_videos, str):
            bad_videos = clear_list(
                bad_videos.replace(" ", "\n")
                .replace(",", "\n")
                .replace("|", "\n")
            )
        bad_videos.sort()
        self.bad_videos = bad_videos

        if not zhaloba:
            zhaloba = alternative_zhaloba

        if isinstance(zhaloba, str):
            zhaloba = clear_list(zhaloba.replace("|", "\n"))
        zhaloba.sort()
        self.zhaloba = zhaloba

        hash_info = self.get_hash_info()
        hash_human = " + ".join(hash_info)
        self.hash_human = hash_human
        self.hash = self.get_hash()

    @property
    def min_details(self):
        return f"<{self.name}: hash={self.hash_human}>"


class YoutubeChanelDislike(Task):
    name = "YoutubeChanelDislike"
    tip = "YoutubeChanelDislike"
    priority = 20

    def __init__(
        self,
        url="",
        bad_videos="",
        zhaloba="",
        alternative_zhaloba: str = "",
        **kwargs,
    ):
        Task.__init__(self, **kwargs)

        if "/watch?" not in url:
            if not url.endswith("/about"):
                url = f"{url}/about"

        self.url = url

        if isinstance(bad_videos, list):
            pass

        elif not bad_videos or bad_videos is None:
            bad_videos = []

        elif isinstance(bad_videos, str):
            bad_videos = clear_list(
                bad_videos.replace(" ", "\n")
                .replace(",", "\n")
                .replace("|", "\n")
            )
        bad_videos.sort()
        self.bad_videos = bad_videos

        if not zhaloba:
            zhaloba = alternative_zhaloba

        if isinstance(zhaloba, str):
            zhaloba = clear_list(zhaloba.replace("|", "\n"))
        zhaloba.sort()
        self.zhaloba = zhaloba

        hash_info = [
            self.url,
            str(self.bad_videos),
            # str(self.zhaloba),
        ]
        hash_human = " + ".join(hash_info)
        self.hash_human = hash_human
        self.hash = self.get_hash()

    @property
    def min_details(self):
        return f"<{self.name}: hash={self.hash_human}"

    @property
    def special_details(self):
        return f"zhaloba: {self.zhaloba}"


class InstagramDislike(Dislike):
    name = "InstagramDislike"
    tip = "InstagramDislike"
    priority = 20

    def __init__(
        self, url="", zhaloba="", alternative_zhaloba: str = "", **kwargs
    ):

        real_url = guess_instagram_url(url)
        if not real_url:
            m = f"{url=} not of tip={self.tip}"
            logger.critical(m)
            os._exit(0)

        _ = {
            "url": real_url,
            "zhaloba": zhaloba,
            "alternative_zhaloba": alternative_zhaloba,
        }
        Dislike.__init__(self, **_)

    def get_hash_info(self):
        return [self.url]


class TelegramDislike(Dislike):
    name = "TelegramDislike"
    tip = "TelegramDislike"
    priority = 20

    def __init__(
        self, url="", zhaloba="", alternative_zhaloba: str = "", **kwargs
    ):

        real_url = guess_telegram_url(url)
        if not real_url:
            m = f"{url=} not of tip={self.tip}"
            logger.critical(m)
            os._exit(0)

        if not zhaloba:
            zhaloba = alternative_zhaloba

        if isinstance(zhaloba, str):
            zhaloba = clear_list(zhaloba.replace("|", "\n"))
        zhaloba.sort()
        self.zhaloba = zhaloba

        _ = {
            "url": real_url,
            "zhaloba": zhaloba,
            "alternative_zhaloba": alternative_zhaloba,
        }
        Dislike.__init__(self, **_)

    def get_hash_info(self):
        return [self.url]


if __name__ == "__main__":
    special = "YoutubeChanelDislike"
    special = "InstagramDislike"
    special = "TelegramDislike"

    if special == "YoutubeChanelDislike":

        kwargs = {
            # "debug": True,
            "url": "https://www.youtube.com/watch?v=x0mEXifo8gU",
            "url": "https://www.youtube.com/channel/UCxPUxaXn8sVLABf7HxxMabQ",
            "bad_videos": "r29k_T_o9To",
            "zhaloba": "War propaganda in Ukraine | war proganda | пропаганда войны в Украине | пропагандируют напасть на Украину",
        }
        task = YoutubeChanelDislike(**kwargs)
        logger.info(f"{task=}")
        logger.debug(f"{task.is_done=}")
        time_after_success_report = task.get_time_after_successReport()
        # task.mark_reported()
        logger.debug(f"{time_after_success_report=}")
        os._exit(0)

        task.mark_done({"info": "скосили всех!"})
        logger.debug(f"{task.is_done=}")

        tasks = [task, task]
        logger.debug(f"{len(tasks)} {tasks=}")

        print(hash(task))

        tasks = unique(tasks)
        logger.debug(f"unique {len(tasks)} {tasks=}")

    elif special == "InstagramDislike":

        kwargs = {
            # "debug": True,
            "url": "nah",
            "url": "https://www.instagram.com/craterimpact/?utm_medium=copy_link",
            "zhaloba": "War propaganda in Ukraine | war proganda | пропаганда войны в Украине | пропагандируют напасть на Украину",
        }
        task = InstagramDislike(**kwargs)
        logger.info(f"{task=}")

    elif special == "TelegramDislike":

        kwargs = {
            # "debug": True,
            "url": "https://t.me/stoprussiachannel",
            "zhaloba": "War propaganda in Ukraine | war proganda | пропаганда войны в Украине | пропагандируют напасть на Украину",
        }
        task = TelegramDislike(**kwargs)
        logger.info(f"{task=}")

    else:
        logger.critical(f"unknown {special=}")
