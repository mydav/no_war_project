from modules.my_types import *
from modules.os_functions import *


from random import choice, shuffle
import logging
import json

# wait_for_ok()

import os, sys

# import xlsxwriter
import io
from urllib.request import urlopen

# import webbrowser

from hashlib import md5
from copy import deepcopy

import shutil

import random

#!без этого не получается использовать подмодули с этой папки в modules_mega
t = 0
t = 1
if t:
    d_current = os.path.join(os.path.dirname(os.path.realpath(__file__)))
    sys.path += [d_current]
    # sys.path.insert(0, d_current)
    # print(f'        add to path "{d_current}" (file {__file__})')

from modules.print_functions import *
from modules.print_colored import *
from modules.list_functions import *
from modules.dict_functions import *
from modules.list_functions import *
from modules.file_functions import *
from modules.text_functions import *
from modules.test_helpers import *
from modules.funcs_audio import *

from modules.type_functions import *
from modules.api_functions import *
from modules.time_functions import *
from modules_23.numbers_functions import *

from modules.probabilities import *
from modules.logging_functions import *
from modules.my_audio import *
from modules.class_functions import *
from modules.module_functions import *

from modules.inspection_functions import *
from modules.functional_programming import *

from modules_23.print_tabulate import *
from modules.logging_functions import *
from modules.process_functions import *

# подключаю внешние штуки
from modules_23.my_forms import *
from modules_23.my_math import *

# from modules_23.settings_readers import *
from modules_23.my_log_functions import *
from modules_23.potoki import *
from modules_23.mozgo_funcs import *

from modules.random_data import *
from modules_23.random_functions import *

from modules.downloaders import *

"""
from type_functions import *
from random_functions import *

from text_functions import *
from settings_parsers import *
from translit_functions import *

from dict_functions import *
from file_functions import *
from time_functions import *
from project_functions import *

from explore_function import *

"""
############################file functions
# special logging settings?
t = 0
t = 1
if t:
    # log = logging.getLogger(__name__)
    LOGLEVEL = "INFO"
    LOGLEVEL = "DEBUG"  # logging.DEBUG
    LOGLEVEL_CONSOLE = "INFO"
    LOGLEVEL_FILE = "DEBUG"
    LOGLEVEL_CONSOLE = LOGLEVEL

    LOGFORMAT = "%(levelname)s:%(message)s"
    LOGFORMAT = None
    LOGFORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    log = logging.getLogger(__name__)
    log.setLevel(os.environ.get("LOGLEVEL", LOGLEVEL))
    # logging.basicConfig(level=os.environ.get("LOGLEVEL", LOGLEVEL))#, format=LOGFORMAT

    #           create console handler with a higher log level
    console_log = logging.StreamHandler()
    console_log.setLevel(LOGLEVEL_CONSOLE)

    if LOGFORMAT is not None:
        formatter = logging.Formatter(LOGFORMAT)
        console_log.setFormatter(formatter)

    #           create file handler which logs even debug messages
    t = 0
    if t:
        f_log = "temp/log.log"
        mkdir(f_log)
        file_log = logging.FileHandler(f_log)
        file_log.setLevel(LOGLEVEL_CONSOLE)

        if LOGFORMAT is not None:
            formatter = logging.Formatter(LOGFORMAT)
            file_log.setFormatter(formatter)

        #           adding handlers
        log.addHandler(console_log)
        log.addHandler(file_log)

# print("imported modules.base_functions")
