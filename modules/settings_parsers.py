from modules.text_functions import *
from modules.type_functions import *


def prepare_text_for_settings_parsers(text0=""):
    obrezka = "<obrezaluss>"  # все что после этого - игнорим

    # text = text.strip()
    # lines = text.split('\n')
    text = text0.replace("\r", "\n")

    if text.find(obrezka) != -1:
        text = find_from_to_one("nahposhuk", obrezka, text)

    text = "\n" + text + "\n"
    return text


def get_settings_from_my_ini_without_sections(text, delim="="):
    """
    не беру секции, просто влоб вытягиваю все x=y
    """
    otl = 1
    otl = 0
    result = {}

    text = prepare_text_for_settings_parsers(text)
    items = text.split("\n")[1:]
    for item in items:
        item = item.strip()
        parts = item.split(delim)
        if otl:
            print(parts)

        # только имена переменных
        if len(parts) == 1 or parts[0].find(" ") != -1:
            continue

        k = parts[0]
        v = delim.join(parts[1:])
        if k in result:
            continue

        v = change_variable_type_to_most_suitable(v)
        result[k] = v

        if otl:
            print(f"            parsed key `{k}`, value `{v}`")

    return result


def get_settings_from_my_ini(text, delim="=", spec="dict"):
    """
        <ini section1>
                demo_1=1
                demo2='1'
                demo3=привет мир1
                demo4=adfasdf1
        </ini>
    """
    ot = "<ini "
    do = "</ini>"

    result = {}

    #   сначала секции выпарсиваем
    while True:
        ini_text = find_from_to_one(ot, do, text)
        if ini_text == "":
            break

        section_name = find_from_to_one("nahposhuk", ">", ini_text)
        section = get_settings_from_my_ini_without_sections(
            ini_text, delim=delim
        )
        # wait_pretty(section)

        result[section_name] = section

        ini_block = ot + ini_text + do
        text = text.replace(ini_block, "")

    #   осталось что-то не в секциях?
    ini_upper_level = get_settings_from_my_ini_without_sections(text)
    # wait_pretty(ini_upper_level)

    for k, v in ini_upper_level.items():
        if not k in result:
            result[k] = v

    # wait_pretty(result)
    if spec == "dict":
        return result

    elif spec == "text":
        return text

    elif spec == "dict+text":
        return result, text

    elif spec == "text":
        return text

    else:
        wait_for_ok(f"unknown spec {spec}")


def get_settings_from_my_txt(text, more_keys=[], with_ini=1):
    """получаем текст вида <x>значение<y> и берет автоматом все значения"""
    otl = 1
    otl = 0
    result = {}

    text = prepare_text_for_settings_parsers(text)

    if with_ini:
        dict_from_ini, text = get_settings_from_my_ini(text, spec="dict+text")
        for k in dict_from_ini:
            if not k in result:
                result[k] = dict_from_ini[k]

        if otl:
            pretty(result)
            wait_for_ok(f"result")

    items = text.split("\n<")[1:]
    # items = text.split('\r<')[1:]
    if otl:
        print("%s items" % len(items))
        show_list(items)

    keys_found = []
    for item in items:
        k = find_from_to_one("nahposhuk", ">", item)
        if otl:
            print("        key", k)
        k_start = "\n<%s>" % k

        # k_start = '<%s>' % k
        #        k_end = '</%s>\n' % k
        k_end = "</%s>" % k
        if text.find(k_end) != -1:
            #            print     '    ', k
            keys_found.append(k)

    # keys_found = unique(keys_found + more_keys)
    keys_found = keys_found + more_keys  # уменьшаю зависимости
    for k in keys_found:
        k_start = f"<{k}>"
        k_end = f"</{k}>"
        v = find_from_to_one(k_start, k_end, text)

        v = change_variable_type_to_most_suitable(v)
        result[k] = v

    # дополнительно выпарсиваю ини-файлы
    return result


def parse_args_from_text(txt: str, parts_delim="&", name_delim="="):
    vars = {}
    items = txt.split(parts_delim)
    for item in items:
        name = find_from_to_one("nahposhuk", name_delim, item)
        if not name:
            continue
        value = find_from_to_one(name_delim, "nahposhuk", item)
        vars[name] = value
    return vars


def get_settings_from_text(text, delim="="):
    text = text.strip()
    lines = text.split("\n")
    # print(lines)
    rezult = {}
    section = ""
    for line in lines:
        if line.strip() == "":
            continue
        # print line
        #        line = line.replace('=', ':')
        # секции могу организовывать
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1].strip()
            rezult[section] = {}
            continue

        k = find_from_to_one("nahposhuk", delim, line).strip()
        v = find_from_to_one(delim, "nahposhuk", line).strip()

        if section == "":
            searching_in = rezult
        else:
            searching_in = rezult[section]

        if k in searching_in:
            continue

        searching_in[k] = v
    return rezult


if __name__ == "__main__":
    from modules import *

    t = 1
    if t:
        f_settings = r"s:\!kyxa\!code\!documentation\py4seo\advanced\08\dor_minimum\forted\settings.txt"
        text = text_from_file(f_settings)
        fun = get_settings_from_my_ini_without_sections
        fun = get_settings_from_text
        sett = fun(text)
        print(f"sett from file {f_settings}: {sett}")
        os._exit(0)

    t = 0
    t = 1
    if t:
        f = r"c:\!code\kyartist\venv\Lib\site-packages\doorway_creator\settings_doorwayCreator.txt"
        f = r"c:\!code\kyartist\settings_youtube_stas.txt"
        f = r"c:\!code\kyartist\venv\Lib\site-packages\modules\data\settings_parsers\settings1.txt"

        from modules.file_functions import text_from_file

        text = text_from_file(f)
        r = get_settings_from_my_txt(text)
        # r = get_settings_from_my_ini(text)
        print("RESULT:")
        print(r)
        pretty(r)

        v = r["section1"]["demo_1"]
        print(type(v), v)
        os._exit(0)
