from modules import *


class OneRequest:
    def __init__(
        self,
        url: str = "",
        headers: OrderedDict = OrderedDict(),
        data: str = None,
    ):
        if not isinstance(headers, OrderedDict):
            m = f"headers of type {type(headers)} not OrderedDict"
            logger.critical(m)
            raise ValueError(m)

        if url.startswith("/"):
            if "Host" in headers:
                url = f'https://{headers["Host"]}{url}'
            else:
                logger.warning(f"{url=} without host (Host not in headers)")

        self.url = url
        self.headers = headers
        self.data = data

    @property
    def data_length(self):
        if self.data is None:
            data_length = None
        else:
            data_length = len(self.data)
        return data_length

    @property
    def details(self):
        return f"""<OneRequest: url=`{self.url}`
{len(self.headers)} headers:
{pretty_dict(self.headers)}

data size={self.data_length}, data=`{self.data}`
>
"""

    def almost_equals(self, other):
        """почти равные - когда хедеры в другом порядке просто"""
        error = ""

        if self.url != other.url:
            error = "different urls"
        elif self.data != other.data:
            error = "different data"
        elif dict(self.headers) != dict(other.headers):
            error = f"different headers {self.headers} != {other.headers}"
        if not error:
            return True
        else:
            logger.error(f"not almost equals, {error=}")
            return False

    def __eq__(self, other):
        error = ""
        if self.url != other.url:
            error = "different urls"
        elif self.headers != other.headers:
            error = f"different headers {self.headers} != {other.headers}"
        elif self.data != other.data:
            error = "different data"
        if not error:
            return True
        else:
            # logger.error(f"not equals, {error=}")
            return False

    def __repr__(self):
        return f"<OneRequest: url={self.url}, headers size={len(self.headers)}, data size={self.data_length}>"


if __name__ == "__main__":
    dct_1 = OrderedDict({"x": 1, "y": 2,})
    dct_2 = OrderedDict({"x": 1, "y": 2,})
    dct_1 = OrderedDict(
        {"User-Agent": "Demo User Agent", "Host": "google.com"}
    )
    dct_2 = OrderedDict(
        {"User-Agent": "Demo User Agent", "Host": "google.com"}
    )
    assert dct_1 == dct_2
    assert OrderedDict(
        [("User-Agent", "Demo User Agent"), ("Host", "google.com")]
    ) == OrderedDict(
        [("User-Agent", "Demo User Agent"), ("Host", "google.com")]
    )

    special = "compare_requests"

    if special == "compare_requests":
        # проверка - 1 и 2 одинаковые, 1 3 почти одинаковые, 1 4 разные
        headers_text_1 = """
            User-Agent: Demo User Agent
            Host: google.com
        """
        headers_text_2 = """
            User-Agent: Demo User Agent
            Host: google.com
        """
        headers_text_3 = """
            Host: google.com
            User-Agent: Demo User Agent
        """
        headers_text_4 = """
            Host: google2.com
            User-Agent: Demo User Agent
        """
        req_1 = OneRequest(
            url="https://google.com",
            headers=parse_all_headers_from_text(headers_text_1),
        )
        req_2 = OneRequest(
            url="https://google.com",
            headers=parse_all_headers_from_text(headers_text_2),
        )
        req_3 = OneRequest(
            url="https://google.com",
            headers=parse_all_headers_from_text(headers_text_3),
        )
        req_4 = OneRequest(
            url="https://google.com",
            headers=parse_all_headers_from_text(headers_text_4),
        )
        logger.debug(f"{req_1.details}")
        logger.debug(f"{req_2.details}")
        # assert req_1.headers == req_2.headers
        assert req_1 == req_2
        assert req_1 != req_3
        assert req_1.almost_equals(req_3)
        assert req_1 != req_4
        # eq_1_2 = req_1 == req_2
        # logger.debug(f"{eq_1_2=}")

    else:
        logger.critical(f"unknown {special=}")
