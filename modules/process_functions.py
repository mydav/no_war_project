import os


def os_system_f(f_bat=""):
    cmd_f_bat = '"%s"' % f_bat
    return os.system(cmd_f_bat)
