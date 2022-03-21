from my_requests.parsers.parse_universal import *

logger = get_logger(__name__)


class ComposerReplayer(RequestReplayer):
    name = f"ComposerReplayer"

    def __init__(self, **kwargs):
        RequestReplayer.__init__(self, **kwargs)

    def prepare_request(self, text: str, debug: bool = False) -> OneRequest:
        fun = "prepare_request"

        delim_request_response = "HTTP/1.1"
        if text.count(delim_request_response) == 2:
            parts = text.split(delim_request_response)
            text = delim_request_response.join(parts[:-1])

        text = text.strip()
        lines = [_.strip() for _ in text.split("\n")]

        first_line = lines[0]
        items = first_line.split(" ")
        if len(items) == 1:  # просто урл
            pass
        elif items[0] in [
            "POST",
            "GET",
        ]:  # POST https://www.bet365.com/BetsWebAPI/placebet?betGuid=11858eee-aac9-43f0-b957-33b15a690759 HTTP/1.1
            if debug:
                logger.debug(f"{len(items)} items {items=}")
            if len(items) == 3:
                new_first_line = " ".join(items[1:-1]) + "\n"
            else:
                new_first_line = " ".join(items[1:]) + "\n"
            # text = text.replace(old_first_line, new_first_line) + '\n'
            lines[0] = new_first_line

        else:
            m = f"type {items[0]} not in [GET, POST]"
            raise ValueError(m)

        text = "\n".join(lines)
        logger.debug(f"{text=}")

        parts = text.split("\n\n")

        if len(parts) == 1:  # первая ссылка, дальше сразу хедеры
            parts = text.split("\n")
            new_parts = []
            new_parts.append(parts[0])
            new_parts.append("\n".join(parts[1:]))
            post_data = None
            parts = new_parts[:]

        if len(parts) == 2:
            post_data = None

        elif len(parts) == 3:
            post_data = parts[2].strip()

        else:
            logger.error(f"ERROR {fun} - lengths not in 2, 3")
            wait_for_ok()

        url = parts[0].strip()

        headers_text = parts[1].strip()  #
        headers = parse_all_headers_from_text(headers_text)

        res = OneRequest(url=url, headers=headers, data=post_data)
        return res

    def prepare_response(self, text: str, debug: bool = False):
        text = text.strip()
        lines = [_.strip() for _ in text.split("\n")]

        first_line = lines[0]
        first_items = first_line.split(" ")
        if first_items[0] in [
            "HTTP/1.1",
        ]:  # POST https://www.bet365.com/BetsWebAPI/placebet?betGuid=11858eee-aac9-43f0-b957-33b15a690759 HTTP/1.1
            if debug:
                logger.debug(f"{len(first_items)} first_items {first_items=}")
            if len(first_items) == 3:
                new_first_line = " ".join(first_items[1:-1]) + "\n"
            else:
                new_first_line = " ".join(first_items[1:]) + "\n"
            # text = text.replace(old_first_line, new_first_line) + '\n'
            lines[0] = new_first_line

        else:
            m = f"type {first_items[0]} not in [HTTP/1.1]"
            raise ValueError(m)

        text = "\n".join(lines)

        parts = text.split("\n\n")

        if len(parts) != 3:
            logger.error(f"ERROR {fun} - WRONG text != LEN3")
            wait_for_ok()
        url = parts[0].strip()

        headers_text = parts[1].strip()  #
        headers = parse_all_headers_from_text(headers_text)

        post_data = None
        if len(parts) == 3:
            post_data = parts[2].strip()

        res = OneRequest(url=url, headers=headers, data=post_data)
        return res


if __name__ == "__main__":
    replayer = ComposerReplayer()
    logger.info(f"{replayer=}")

    special = "prepare_response"
    special = "prepare_request"

    if special == "prepare_request":
        f = r"s:\!kyxa\!code\!documentation\py4seo\advanced\08\dor_minimum\bet365_one_api\data\composer_demo_request.txt"
        f = r"s:\!kyxa\!code\!documentation\py4seo\advanced\08\dor_minimum\bet365_one_api\data\spain_login\request_step_1.txt"
        f = r"s:\!kyxa\!code\!documentation\py4seo\advanced\08\dor_minimum\bet365_one_api\data\spain_login\login_request.txt"
        f = r"s:\!kyxa\!code\!ddos\rbc.ru\data\register.txt"

        text = text_from_file(f)
        replaying = replayer.prepare_request(text)
        # replaying.headers["Content-Length"] = 1
        logger.info(f"final {replaying=}")
        logger.info(f"details: {replaying.details}")

        replayed = replayer.replay(replaying)
        logger.info(f"{replayed=}")

    elif special == "prepare_response":
        f = r"s:\!kyxa\!code\!documentation\py4seo\advanced\08\dor_minimum\bet365_one_api\data\composer_demo_response.txt"
        text = text_from_file(f)
        r = replayer.prepare_response(text)
        # r.headers["Content-Length"] = 1
        logger.info(f"final {r=}")
        logger.info(f"details: {r.details}")

    else:
        logger.critical(f"unknown {special=}")
