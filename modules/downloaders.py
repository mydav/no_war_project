# from modules import *
import time
import requests
import gzip

from modules.logging_functions import get_logger

logger = get_logger(__name__)


def requests_u(
    u, data=None, headers={}, timeout=1, debug=False, print_final_info=True
):
    """
     response = fun(u,
                      # json=data,
                      data=json_string,
                      headers=headers,
                      timeout=timeout,
                      )
print('response=', response)


    :param u:
    :param data:
    :param headers:
    :param timeout:
    :return:
    """

    kwargs = {
        "headers": headers,
        "timeout": timeout,
    }
    method = "get"
    if data is None:
        fun = requests.get
    else:
        method = "post"
        fun = requests.post
        kwargs["data"] = data

    if print_final_info:
        print("     => %s %s " % (method, u), end="")

    if debug:
        print("data=%s" % data)
    if debug:
        print("kwargs:")
        show_dict(kwargs)

    t_start = time.time()

    response = fun(u, **kwargs)

    seconds = time.time() - t_start
    status_code = response.status_code

    if debug:
        print_response_info(response)
    if print_final_info:
        print(
            " <= done %s %s in %.2f seconds, status code: %s"
            % (method, u, seconds, status_code)
        )

    return response


def get_response_text(response, default=None):
    """даже когда ответ в неправильном формате (например гзип, а неправильный хедер - получаем ответ)"""
    if response is None:
        return default
    html = response.text
    if html.startswith(
        "\x1f"
    ):  # в бетке иногда тупо текст вылазил - а потому что кодировка неправильная (типа хтмл, а в реальности гзип)
        html = ungzip_bytes(response.content)
        logger.warning(f"response was gzip with wrong type, {html=}")
    return html


def ungzip_bytes(data="", enc="utf-8", debug=False):
    bites = data
    # if not isinstance(bites, bytes):
    #     bites = bites.encode(enc, 'ignore') # bytes
    if debug:
        logger.debug(f"{type(bites)} {bites=}")

    answer = gzip.decompress(bites)
    return answer.decode()


if __name__ == "__main__":
    special = "get_useragent"
    special = "parse_headers_from_text"
    special = "requests_u"
    special = "ungzip_bytes"

    if special == "ungzip_bytes":
        f = r"s:\!kyxa\!code\!documentation\py4seo\advanced\08\dor_minimum\bet365_one_api\temp\response_content.pickled"
        t = 1
        if t:
            data = obj_from_file(f)
            logger.debug(f"{type(data)} {data=}")

        f = r"s:\!kyxa\!code\!documentation\py4seo\advanced\08\dor_minimum\bet365_one_api\temp\response.pickled"
        f = r"s:\!kyxa\!code\!documentation\py4seo\advanced\08\dor_minimum\bet365_one_api\temp\response_content.pickled"
        data = obj_from_file(f)
        logger.debug(f"{type(data)} {data=}")
        answer = ungzip_bytes(data)
        logger.info(f"{answer=}")
        os._exit(0)

    elif special == "requests_u":
        u = "nah"
        u = "https://google.com"
        # requests_u(u)
        try:
            requests_u("http://localhost:8081/save_info/", data="nah")
        except Exception as er:
            print(f"{er=}")

    else:
        logger.critical(f"unknown {special=}")
