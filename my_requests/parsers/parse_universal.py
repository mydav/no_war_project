from modules import *
from my_requests.parsers.model import *
from my_requests.parsers.headers_helpers import *
from my_requests.requests_helper import *

logger = get_logger(__name__)


class RequestReplay:
    def __init__(self, session=None):
        self.session = None
        self.init_session(session)

    def init_session(self, session=None):
        if not session:
            session = requests.Session()
        self.session = session

    def multiple_replay(self, replaying=None, **kwargs):
        pass

    def replay(self, replaying=None, **kwargs):
        fun = "replay"
        logger.debug(f"[{fun}:")
        session = self.session
        res = request_with_requests_html(
            session, replaying=replaying, **kwargs
        )
        return res


class RequestPrepare:
    def prepare_request(self, *args, **kwargs) -> OneRequest:
        # headers = OrderedDict({"User-Agent": "Demo User Agent"})
        headers_text = """
        Host: api.ipify.org
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Accept-Language: en-GB,en;q=0.5
Accept-Encoding: gzip, deflate, br
Connection: keep-alive
Upgrade-Insecure-Requests: 1
        """
        headers = parse_all_headers_from_text(headers_text)
        demo = OneRequest(
            url="https://api.ipify.org/?format=json", headers=headers, data=""
        )
        logger.debug(f"demo request: {demo.details}")
        return demo
        raise ValueError(f"not implemented, demo result: {demo}")


class RequestReplayer(RequestPrepare, RequestReplay):
    name = "RequestReplayer"

    def __repr__(self):
        return f"<{self.name}>"


if __name__ == "__main__":
    replayer = RequestReplayer()
    logger.debug(f"{replayer=}")

    special = "prepare_request"

    if special == "prepare_request":
        req = replayer.prepare_request("some text")
        logger.info(f"request = {req}")
        replayed = replayer.replay(req)
        logger.info(f"{replayed=}")

    else:
        logger.critical(f"unknown {special=}")
