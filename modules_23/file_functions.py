import shutil
import os

from modules.logging_functions import get_logger

logger = get_logger(__name__)


def remove_files(files_list):
    for f in files_list:
        os.remove(f)


def create_dir(dir_name):
    """получает имя папки и если она не существует, то создает ее"""
    fun = "create_dir"
    if dir_name == "":
        return
    if not os.path.isdir(dir_name):
        try:
            os.makedirs(dir_name)
        except Exception as er:
            logger.error("error %s" % er)


def copy_dir(src, dst):
    try:
        shutil.copytree(src, dst)
    except Exception as er:  # python >2.5
        shutil.copy(src, dst)
    else:
        pass


def copy_file_with_attributes(f_from, f_to):
    return copy_file_shutil(f_from, f_to, want_copy_all_attributes=1)


def copy_file_shutil(f_from, f_to, want_copy_all_attributes=1):
    """
    дату НЕ копирует
    """
    fun = "copy_file_shutil"
    d = os.path.dirname(f_to)
    create_dir(d)
    try:
        if want_copy_all_attributes:
            shutil.copy2(f_from, f_to)
        else:
            shutil.copy(f_from, f_to)
        status = 1
    except Exception as er:
        mess = "    error %s - from %s to %s" % (fun, f_from, f_to)
        logger.error(mess)
        status = 0
    return status
