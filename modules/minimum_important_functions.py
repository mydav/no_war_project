#!/usr/bin/python
# -*- coding: utf-8 -*-

# from modules.dict_functions import hitro_dict

try:
    from modules.dict_functions import hitro_dict, add_defaults, Bunch
except Exception as er:
    from modules.my_translit_ import hitro_dict, add_defaults, Bunch

try:
    from modules.file_functions import text_to_file, text_from_file
except Exception as er:
    from modules.my_translit_ import text_to_file, text_from_file

try:
    from modules.print_functions import show_dict, show_list, wait_for_ok
except Exception as er:
    from modules.my_translit_ import show_dict, show_list, wait_for_ok

from modules.find_functions import find_from_to_one
from modules.logging_functions import get_logger

### Не импортится в 2?
try:
    from modules.list_functions import clear_list
except Exception as er:
    from modules.list_functions_ import clear_list
