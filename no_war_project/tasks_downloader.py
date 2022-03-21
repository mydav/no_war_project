from no_war_project.settings import *
from typing import List
from modules.excel_functions import *
from my_requests.requests_helper import *
from no_war_project.model import *


logger = get_logger(__name__)


class UniversalTasksDownloader:
    name = "UniversalTasksDownloader"

    def __init__(self, d=None, **kwargs):
        debug = kwargs.pop("debug", False)
        self.debug = debug
        if not d:
            d = get_f_here("temp/tasks")
        self.d = d

    def get_tasks(self, func=None, **kwargs):
        if not func:
            func = self.get_tasks_one
        # return get_tasks(func, **kwargs)
        return func(**kwargs)

    def get_tasks_one(self):
        """
        """
        raise ValueError(f"get_tasks not implemented")

    def get_f(self, name, rash="clever"):
        if rash == "clever":
            if not "." in name:
                name = f"{name}.html"
        return f"{self.d}/{name}"

    def __repr__(self):
        return f"<{self.name}>"


class HtmlTasksDownloader(UniversalTasksDownloader):
    name = "HtmlTasksDownloader"

    def __init__(self, url=None, **kwargs):
        if not url:
            url = "https://nowarpropaganda.blogspot.com/2022/03/no-war.html"
            url = "https://nowarpropaganda.blogspot.com/"
        self.url = url

        headers_text = """
            User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0
            Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
            Accept-Language: en-GB,en;q=0.5
            Accept-Encoding: gzip, deflate, br
            Connection: keep-alive
            Upgrade-Insecure-Requests: 1
            """
        self.headers = parse_headers_from_text(headers_text)
        self.session = requests.Session()

        _ = {
            "d": kwargs.pop("d", None),
        }
        UniversalTasksDownloader.__init__(self, **_)

    def get_tasks_one(self, **kwargs):
        return self.download_tasks()

    def download_tasks(self):
        fun = "download_tasks"
        logger.debug(f"[{fun}")
        urls = self.download_tasks_urls()
        logger.debug(f"found {len(urls)}")
        for num, url in enumerate(urls, 1):
            logger.debug(f"download {num}/{len(urls)} {url=}")
            res = self.download_bin_file(url)
            logger.debug(f"   +downloaded {res=}")

    def download_bin_file(self, url, f_to=None):
        """если был скачанный - не будем качать"""
        h = to_hash(url)
        if f_to is None:
            f_to = self.get_f("raw_tasks/[hash].jpg")
        f_to = f_to.replace("[hash]", h)
        logger.debug(f"{f_to=}")

        info = ""
        error = ""
        while True:
            if file_exists(f_to):
                info = "already_downloaded"
                break

            try:
                response = self.session.get(url, headers=self.headers)
                kod = response.status_code
                if kod == 200:
                    content = response.content
                    # h = to_hash(content)
                    text_to_file(content, f_to)
                    # with open(f_to, 'wb') as f:
                    #     f.write(content)
                    info = "downloaded"
                else:
                    logger.warning(f"{kod=}, can not download {url=}")
                    error = f"kod_{kod}"
            except Exception as er:
                logger.error(f"can not download {url}, {er=}")
                error = f"exception"

            break

        res = {}
        if error:
            res["error"] = error
            info = error

        res["info"] = info

        return res

    def download_tasks_urls(self):
        logger.debug("download tasks list")
        f_temp = self.get_f("page_with_tasks")
        etag = get_etag(self.session, self.url)
        logger.debug(f"{etag=}")

        f_cache = self.get_f(
            f"cache/page_with_tasks_{to_hash(self.url)}_{to_hash(etag)}.html"
        )
        if file_exists(f_cache):
            logger.debug(f"already exists {f_cache=}")
            html = text_from_file(f_cache)

        else:
            _ = {
                "session": self.session,
                "url": self.url,
                "headers": self.headers,
            }
            r = request_with_requests_html(**_)
            response = r["response"]
            logger.debug(f"{r=}")
            html = get_response_text(response)
            text_to_file(html, f_temp)
            if etag:
                text_to_file(html, f_cache)
            logger.debug(f"saved to {f_temp}")
        return self.parse_urls_to_data(html)

    def parse_urls_to_data(self, text=""):
        delim_1 = "img alt='Image'"
        delim_1 = 'a href="'
        urls = []
        items = text.split(delim_1)
        for item in items:
            # url = find_from_to_one(" src='", "'", item)
            url = find_from_to_one("nahposhuk", '"', item)
            if "blogger.googleusercontent.com" not in url:
                continue
            urls.append(url)
        urls = unique_with_order(urls)
        return urls

    def __repr__(self):
        return f"<{self.name} from url {self.url}, d={self.d}>"


if __name__ == "__main__":
    special = "HtmlTasksDownloader"

    if special == "HtmlTasksDownloader":
        downloader = HtmlTasksDownloader()
        logger.info(f"{downloader=}")

        special = "download_tasks"
        special = "download_tasks_urls"

        if special == "download_tasks":
            res = downloader.download_tasks()
            logger.debug(f"downloaded {res=}")

        elif special == "download_tasks_urls":
            special = "download_tasks_urls"
            special = "download_tasks"
            step = 0
            t_start = time.time()
            while True:
                step += 1
                t_start_one = time.time()

                if special == "download_tasks_urls":
                    func = downloader.download_tasks_urls
                elif special == "download_tasks":
                    func = downloader.download_tasks

                result = func()
                duration_one = time.time() - t_start_one

                if special == "download_tasks_urls":
                    if not result:
                        m = "no urls"
                        logger.critical(m)
                        inform_critical(m)
                    logger.debug(
                        f"{step=}, {duration_one:.2f} duration {get_human_duration(time.time() - t_start)}, {len(result)} {result=}"
                    )
                else:
                    logger.debug(
                        f"{step=}, {duration_one:.2f} duration {get_human_duration(time.time() - t_start)} {result=}"
                    )

                sleep_(1)
                # sleep_(10*6)

        else:
            logger.critical(f"no {accounts=}")

    else:
        logger.critical(f"no {accounts=}")
