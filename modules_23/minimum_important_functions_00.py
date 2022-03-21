import sys


def get_python_version():
    return sys.version_info[0]


PY2 = get_python_version() == 2
PY3 = get_python_version() == 3

if PY3:
    text_type = str

else:
    text_type = unicode
