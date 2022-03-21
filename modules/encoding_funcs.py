import urllib.parse

from modules_23.encode_decode import *
from modules.logging_functions import get_logger

logger = get_logger(__name__)


def deep_encode(obj, encoding="utf-8"):
    """
    возвращает просто текст в encoding

    Python 3 renamed the unicode type to str, the old str type has been replaced by bytes.
    """
    # if isinstance(obj, unicode):
    # print(type(obj))
    # print(f"deep_encode {type('')=} {type(obj)=} {obj=} ")
    if type(obj) == type(""):
        return obj
        # return obj.encode(encoding)

    elif isinstance(obj, (bytes, bytearray)):
        return obj.decode(encoding)

    elif isinstance(obj, dict):
        return {
            deep_encode(key, encoding): deep_encode(value, encoding)
            for key, value in obj.items()
        }
    elif isinstance(obj, list):
        return [deep_encode(item, encoding) for item in obj]
    else:
        return obj


def escape_text_like_sqlite(text, encoding_from="utf-8", encoding_to="latin1"):
    """sqlite сохраняет текст вот так вот странно"""
    _ = urllib.parse.quote(text)
    encoded = text_from_enc_to_enc(
        _, encoding_from=encoding_from, encoding_to=encoding_to
    )
    # print(f"{encoded=} {_=}")
    return encoded


def text_from_enc_to_enc(text, encoding_from="latin1", encoding_to="utf-8"):
    debug = True
    debug = False
    text = text.encode(encoding_from)  # ==bytes

    if debug:
        print(f"    1: {text=}")
    # print(type(text), text)
    text = text.decode(encoding_to)  # ==str
    if debug:
        print(f"    2: {text=}", text)
    return text


def convert_js_to_html(js: str, encoding: str = "utf-8") -> str:
    """Convert js code to html"""
    return unescape_text(text=js, encoding=encoding)


def unescape_text(text: str, encoding: str = "utf-8") -> str:
    """////xd0////xd1 -> //xd0//xd1"""
    html = text

    html = html.encode(encoding)
    html = html.decode("unicode-escape")
    return html


def bytes_to_str(text, encoding="utf-8", attr="ignore"):
    """Converts a binary to Unicode string by removing all non Unicode char
    text: binary string to work on
    encoding: output encoding *utf-8"""
    if not is_bytes(text):
        return text

    return text.decode(encoding, attr)


def is_bytes(data):
    """проверяем что текст - байт"""
    if str(type(data)).find("bytes") != -1:
        return True
    return False


if __name__ == "__main__":
    import os

    special = "convert_js_to_html"
    special = "deep_encode"
    special = "bytes_to_str"

    if special == "bytes_to_str":
        data = b"bytes data"
        text = bytes_to_str(data)
        logger.debug("%s %s" % (type(text), text))

    elif special == "deep_encode":
        str1 = b"test"
        str2 = "test"
        print(f"{str1=} {type(str1)} {str2=} {type(str2)=} {str1 == str2}")

        obj = {
            b"fork_id": b"3091ba909c9fd9d8ac",
            "income": 0.25,
            "unicode": 1,
        }
        obj2 = deep_encode(obj)
        print(f"{obj2=}")

    elif special == "convert_js_to_html":
        line = "\xd0\x9d\xd0\xb8\xd0\xb6\xd0\xb5 \xd0\xbf\xd1\x80\xd0\xb8\xd0\xb2\xd0\xb5\xd0\xb4\xd0\xb5\xd0\xbd"
        line = "\\xd0\\xa2"
        print(line, f"{line=}")
        line = convert_js_to_html(line)
        line = line.replace("\\\\\\", "\\")
        print(line, f"{line=}")
        line = line.replace(r"\\\\", r"\\")
        print(line, f"{line=}")

        text = text_from_enc_to_enc(line)
        print(type(text), text)
        os._exit(0)
        print("-" * 20)

        encoding_from = "utf-8"
        encoding_from = "ascii"
        encoding_from = "utf8"
        encoding_from = "UTF-8"
        encoding_from = "latin1"
        encoding_to = "utf-8"

        # encoding_from = "latin1"
        # print(type(line), line)
        # line = b(line)
        # line = bytes(line, encoding_from)
        line = line.encode(encoding_from)
        print(type(line), line)

        # line = eval(f'b"{line}"')
        # print(line.decode("utf-8"))
        print(line.decode(encoding_to))
        os._exit(0)
    else:
        print(f"ERROR: unknown {special=}")
