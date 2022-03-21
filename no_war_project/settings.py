# -*- coding: utf-8 -*-

from modules.dict_functions import add_defaults
from modules.list_functions import clear_list
from modules.excel_functions import *
from modules.file_functions import text_from_file, file_exists
from modules.settings_parsers import *
from modules.file_functions import get_all_file_names
from no_war_project.report_templates import get_default_report_templates

from text_generator.text_randomizer import TextRandomizer

logger = get_logger(__name__)


def get_default_settings(sett={}, f=None, d_root=None):
    d_defaults = {
        "lang": "ru",
        "work_with": ["youtube", "instagram"],
        "delay_youtube": "5m-10m",
        "delay_instagram": "5m-10m",
        "delay_telegram": "5m-10m",
    }
    logger.debug(f"get_default_settings {f=} {d_root=}")
    settings_from_file = get_settings_from_file(f=f, d_root=d_root)
    logger.debug(f"{settings_from_file=}")
    sett = add_defaults(sett, settings_from_file)
    sett = add_defaults(sett, d_defaults)

    # считываю настройки
    delays_between_reports = {
        "YoutubeChanelDislike": sett["delay_youtube"],
        "InstagramDislike": sett["delay_instagram"],
        "TelegramDislike": sett["delay_telegram"],
    }
    sett["delays_between_reports"] = delays_between_reports
    keys_to_delete = ["delay_youtube", "delay_instagram", "delay_telegram"]
    for k in keys_to_delete:
        if k in sett:
            del sett[k]
    return sett


def get_settings_from_file(f=None, d_root=None):
    logger.debug(f"get_settings_from_file {f=} {d_root=}")
    if not f:
        f_name = "налаштування.txt"
        f = get_f_here(f_name, d_root=d_root)
        logger.debug(f"will get default settings from {f=}")

    if not file_exists(f):
        m = f"file with settings `{f}` not exists"
        logger.critical(m)
        os._exit(0)

    key_report_template = "message_dislike_youtube_chanel"
    sett = get_settings_from_my_txt(text_from_file(f))
    if key_report_template not in sett:
        sett[key_report_template] = get_default_report_templates()
    list_keys = [
        key_report_template,
        # 'work_with',
    ]
    for k in list_keys:
        v = sett[k]
        v = clear_list(v.split("\n"))
        v.sort()
        sett[k] = v

    return sett


def get_f_here(name="", d_root=None):
    if not d_root:
        if getattr(sys, "frozen", False):
            # cx_freeze windows:
            d_root = os.path.dirname(sys.executable)
            # multiprocessing.freeze_support()
        else:
            # logger.debug(f"{__file__=}")
            # logger.debug(f"{__name__=}")
            d_root = os.path.dirname(os.path.realpath(__file__))
            # d_root = os.path.dirname(os.path.realpath(__name__))
    return os.path.abspath(f"{d_root}/{name}")


def get_text_rewriter():

    otl = 0
    start = "("
    finish = ")"
    delimiter = "%"

    klas = TextRandomizer
    # klas = MinTextRandomizer

    rewriter = klas(otl=otl, start=start, finish=finish, delimiter=delimiter,)
    return rewriter


def MinTextRandomizer():
    def __init__(self, *args, **kwrags):
        pass

    def get_random_text_variation(self, tpl, *args, **kwargs):
        return tpl


def convert_reportTemplates_from_txt_to_py(want_check_templates=True):
    """чтобы инфу никто не вытянул - нужно шаблоны в .py перенести"""
    if want_check_templates:
        rewriter = get_text_rewriter()

    d_with_templates = get_f_here("data/!report_templates")
    f_tpl = get_f_here("data/tpl_templates.py")
    f_to = get_f_here("report_templates.py")

    files = get_all_file_names(d_with_templates)
    logger.debug(f"found {len(files)} files in {d_with_templates=}")

    all_templates = []
    for f in files:
        txt = text_from_file(f)
        templates = clear_list(txt)
        if want_check_templates:
            for tpl in templates:
                if tpl.startswith("---") or tpl.startswith(
                    "#"
                ):  # skip comments
                    continue

                is_correct = rewriter.check_template_correctness(tpl)
                if is_correct:
                    all_templates.append(tpl)
                else:
                    logger.warning(f"not correct {tpl=}")
    logger.debug(f"found {len(all_templates)} correct templates")
    templates = "\n".join(all_templates)

    tpl = text_from_file(f_tpl)
    tpl = tpl.replace("[txt_with_templates]", templates)
    text_to_file(tpl, f_to)
    logger.debug0(f"saved {len(all_templates)} templates to {f_to=}")


if __name__ == "__main__":
    special = "read_accounts_from_excel"
    special = "get_settings_from_file"
    special = "get_default_settings"
    special = "convert_reportTemplates_from_txt_to_py"

    if special == "convert_reportTemplates_from_txt_to_py":
        converted = convert_reportTemplates_from_txt_to_py()
        logger.info(f"{converted=}")

    elif special == "get_default_settings":
        kwargs = {
            "lang": "en",
        }
        f = r"s:\!kyxa\!code\no_war\налаштування.txt"
        settings = get_default_settings(kwargs, f=f)
        logger.debug(f"{settings=}")

    elif special == "get_settings_from_file":
        settings = get_settings_from_file()
        logger.debug(f"{settings=}")

    elif special == "read_accounts_from_excel":
        r = read_accounts_from_excel()
        logger.debug(f"{r=}")
    else:
        logger.critical(f"no {accounts=}")
