#!/usr/bin/python
# -*- coding: utf-8 -*-

try:
    from modules.file_functions import text_from_file
except Exception as er:
    from modules.file_save_open import text_from_file
from modules.logging_functions import *

## !!!СИНХРОНИЗИРУЙ PY2-PY3 sync_py2_py3

logger = get_logger(__name__)


def get_module_text_from_file(f=r"s:\!kyxa\!code\learn_debugging\area_2.py"):
    fun = "get_module_text_from_file"
    text = text_from_file(f)
    text = text.split("\nif __name__ == ")[0].strip()
    logger.debug("%s from f=%s len(text)=%s" % (fun, f, len(text)))
    return text


def reload_module_from_file_NOT_WORKING(
    f=r"s:\!kyxa\!code\learn_debugging\area_2.py",
):
    """не работает - не глобальное по факту"""
    fun = "reload_module_from_file"
    text = text_from_file(f)
    text = text.split("\nif __name__ == ")[0].strip()
    return text
    # exec(text)
    # logger.warning(f"{fun} done from {f=} with {len(text)=}")


if __name__ == "__main__":
    f = r"s:\!kyxa\!code\learn_debugging\area_2.py"
    get_module_text_from_file(f)
