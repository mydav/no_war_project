import xlrd
from modules.text_functions import find_from_to_one, my_symbols
from modules.file_functions import text_to_file
from modules.list_functions import list_minus_list
from modules.logging_functions import *

logger = get_logger(__name__)


def xlsx_to_list(task={}):
    return read_xlsx(**task)


def read_xlsx(
    f=r"d:\kyxa\!code\!actual\djvu_convert\!info.xlsx",
    keys_int=[],  # ['Год', 'Первая страница', 'Года', 'Балов'],
    default_bad="",
    sheet=0,
    sheet_name=None,
    spec_task="",  # return_keys - возвратить ключи, если пусто просто работаем
    to_float: bool = False,  # переводим в флоат если можем?
    to_int: bool = False,  # переводим в целое если можем?
    result_type="dicts_list",  # тип результата. словарь или список
    main_dict_key=None,
    max_rows=1000000,  # макс. количество строчек
):
    """Получает такой ексель, и его в список обьектов
    lists    actions_before    InEarlyPosition
    list_pairs_high    f$all_folded    R
    list_pairs_high    f$all_called    R
    """

    fun = "read_xlsx_list"
    debug = False

    if debug:
        print(f"[{fun}", end="")

    # rb = xlrd.open_workbook(f,formatting_info=True)
    rb = xlrd.open_workbook(f)
    if sheet_name is not None:
        sheet = rb.sheet_by_name(sheet_name)
    else:
        sheet = rb.sheet_by_index(sheet)

    keys = []
    row = sheet.row_values(0)
    for c_el in row:
        keys.append(c_el)

    if spec_task == "return_keys":
        return keys
    elif spec_task == "all_rows":
        num_rows = sheet.nrows - 1
        num_cells = sheet.ncols - 1
        curr_row = -1
        data = []
        while curr_row < num_rows:
            curr_row += 1
            # row = sheet.row(curr_row)
            row_values = []
            curr_cell = -1
            while curr_cell < num_cells:
                curr_cell += 1
                # Cell Types: 0=Empty, 1=Text, 2=Number, 3=Date, 4=Boolean, 5=Error, 6=Blank
                cell_type = sheet.cell_type(curr_row, curr_cell)
                cell_value = sheet.cell_value(curr_row, curr_cell)
                row_values.append(cell_value)
            data.append(row_values)
        return data

    # show_list(keys)
    # wait_for_ok()

    type_int = type(10)
    type_float = type(0.1)
    type_str = type("str")

    all_rows = []
    for rownum in range(sheet.nrows)[1:]:
        # print len(all_rows), max_rows

        if len(all_rows) >= max_rows:
            break

        if result_type in ["dicts_list", "dict"]:
            row_result = {}
        elif result_type == "lists_list":
            row_result = []
        else:
            raise Exception(f"unknown {result_type=}")

        row = sheet.row_values(rownum)

        # print(row_result, row)

        i = 0
        for c_el in row:
            # print(c_el)
            k = keys[i]
            # if k=='Год':
            #    print c_el

            # c_el = unicode(c_el)
            # v = c_el.encode(charset)
            v = str(c_el)

            # print(f"    {k=}, {v=}")
            # print type(c_el)
            if k in keys_int:
                if v.find(".") != -1:
                    v = find_from_to_one("nahposhuk", ".", v)
                try:
                    v = int(v)
                except Exception as er:
                    v = default_bad
                # print v

            if type(v) == type_str:
                # print type(v), v, v.find('.')
                if to_int and v.find(".") == -1:
                    # print 'to int'
                    if to_int:
                        v0 = -111111111111111111111111111
                        v0 = my_symbols(v, "-.1234567890")
                        try:
                            v0 = int(v0)
                        except Exception as er:
                            pass
                        # print v0
                        if str(v0) == v:
                            v = v0

                elif to_float:
                    v0 = my_symbols(v, "-.1234567890")
                    try:
                        v0 = float(v0)
                    except Exception as er:
                        # print er
                        pass
                    if str(v0) == v:
                        v = v0

            # wait_for_ok()
            i += 1

            if result_type in ["dicts_list", "dict"]:
                row_result[k] = v
            elif result_type in ["lists_list"]:
                row_result.append(v)
            else:
                raise Exception(f"unknown {result_type=}")

        all_rows.append(row_result)

    if result_type == "dict":
        if main_dict_key is None:
            main_dict_key = keys[0]
        one_dict = {}
        for dct in all_rows:
            one_dict[dct[main_dict_key]] = dct
        all_rows = one_dict

    if debug:
        print(f"+{len(all_rows)} rows]")
    return all_rows


def read_csv(
    f: str,
    encoding="utf-8",
    result_type="dicts_list",
    keys_int=[],  # ['Год', 'Первая страница', 'Года', 'Балов'],
    to_float: bool = False,  # переводим в флоат если можем?
    to_int: bool = False,  # переводим в целое если можем?
    fields: list = None,
    default_bad="",
    main_dict_key=None,
    max_rows=1000000,  # макс. количество строчек
):
    import csv

    debug = False

    type_int = type(10)
    type_float = type(0.1)
    type_str = type("str")

    all_rows = []
    with open(f, "r", encoding=encoding) as file:
        reader = csv.reader(file, delimiter=";")  # Reader object

        if fields is None:
            fields = []
            fields = next(reader)
        else:
            next(reader)

        keys = fields[:]
        for row in reader:
            # all_rows.append(row)

            if len(all_rows) >= max_rows:
                break

            if result_type in ["dicts_list", "dict"]:
                row_result = {}
            elif result_type == "lists_list":
                row_result = []
            else:
                raise Exception(f"unknown {result_type=}")

            # print(row_result, row)

            i = 0
            for c_el in row:
                k = keys[i]
                v = str(c_el)

                if k in keys_int:
                    if v.find(".") != -1:
                        v = find_from_to_one("nahposhuk", ".", v)
                    try:
                        v = int(v)
                    except Exception as er:
                        v = default_bad
                    # print v

                if type(v) == type_str:
                    # print type(v), v, v.find('.')
                    if to_int and v.find(".") == -1:
                        # print 'to int'
                        if to_int:
                            v0 = -111111111111111111111111111
                            v0 = my_symbols(v, "-.1234567890")
                            try:
                                v0 = int(v0)
                            except Exception as er:
                                pass
                            # print v0
                            if str(v0) == v:
                                v = v0

                    elif to_float:
                        v0 = my_symbols(v, "-.1234567890")
                        try:
                            v0 = float(v0)
                        except Exception as er:
                            # print er
                            pass
                        if str(v0) == v:
                            v = v0

                # wait_for_ok()
                i += 1

                if result_type in ["dicts_list", "dict"]:
                    row_result[k] = v
                elif result_type in ["lists_list"]:
                    row_result.append(v)
                else:
                    raise Exception(f"unknown {result_type=}")

            all_rows.append(row_result)

        if result_type == "dict":
            if main_dict_key is None:
                main_dict_key = keys[0]
            one_dict = {}
            for dct in all_rows:
                one_dict[dct[main_dict_key]] = dct
            all_rows = one_dict

        if debug:
            print(f"+{len(all_rows)} all_rows]")
        return all_rows

        print(f"You have {reader.line_num} all_rows")  # Number of all_rows

        print(f"{len(fields)}: {fields=} ")  # Field names
        # id            title        timing   genre    rating
        for row in all_rows[:6]:
            for col in row:
                print(col)


def save_clever_to_csv(
    polja,
    dela,
    f_rez,
    linko=[],
    encoding="utf-8",
    polja_start=[],
    round_float=1,
    round_float_format="%.3f",
):
    # если поля пустые - собираю все возможные поля
    """
        round_float - округляем до 2 знаков после запятой
    """

    # from xlwt import *
    from xlwt import Workbook, Font, XFStyle

    polja = get_polja_from_list(polja, dela)

    # show_list(polja)
    # wait_for_ok()

    polja = resort_polja(polja, polja_start)

    t = 1
    t = 0
    if t:
        show_list(polja)

    import csv

    with open(f_rez, mode="w", encoding=encoding) as csv_file:
        fieldnames = polja[:]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()

        for row in dela:
            writer.writerow(row)
            # writer.writerow(
            #     {
            #         "emp_name": "Erica Meyers",
            #         "dept": "IT",
            #         "birth_month": "March",
            #     }
            # )
    print(f"saved {len(dela)} items to {f_rez}")


def resort_polja(polja=[], polja_start=[]):
    if polja_start not in ["", []]:
        new_polja = []
        for pole in polja_start:
            if pole in polja:
                new_polja.append(pole)

        for pole in polja:
            if pole not in new_polja:
                new_polja.append(pole)

        polja = new_polja[:]
    return polja


def get_polja_from_list(polja, dela=[]):
    if polja in ["", []]:
        polja_all = set()
        for user in dela:
            polja = user.keys()
            for p in polja:
                polja_all.add(p)

        polja_all = list(polja_all)
        polja_all.sort()

        polja = polja_all[:]
    return polja


def save_clever_to_xls(
    polja,
    dela,
    f_rez,
    linko=[],
    encoding="utf-8",
    polja_start=[],
    polja_propusk=[],
    round_float=1,
    round_float_format="%.3f",
):
    # если поля пустые - собираю все возможные поля
    """
        round_float - округляем до 2 знаков после запятой
    """
    fun = "save_clever_to_xls"
    logger.debug(f"[{fun} {len(dela)} item")

    # from xlwt import *
    from xlwt import Workbook, Font, XFStyle, Formula

    polja = get_polja_from_list(polja, dela)

    # show_list(polja)
    # wait_for_ok()

    polja = resort_polja(polja, polja_start)
    polja = list_minus_list(polja, polja_propusk)

    t = 1
    t = 0
    if t:
        show_list(polja)
        wait_for_ok()

    wbk = Workbook(encoding=encoding)
    sheet = wbk.add_sheet("sheet 1", cell_overwrite_ok=True)
    #    sheet.write(0,0,'oppa')

    font0 = Font()
    font0.name = "Times New Roman"
    font0.bold = True
    font0.height = 20 * 12

    style0 = XFStyle()
    #    style0.borders = borders
    style0.font = font0

    for j in range(0, len(polja)):
        key = polja[j]
        sheet.write(0, j, key, style0)
        sheet.col(j).width = 0x0D00 + 1000

    type_float = type(1.0)
    type_int = type(123)
    type_str = type("str")
    n = "HYPERLINK"
    i = 0
    for delo in dela:
        i += 1

        #        print i,
        for j in range(0, len(polja)):
            key = polja[j]
            #            if not delo.has_key(key):
            #                print('no pole |%s|' % key)
            v = delo.get(key, "")
            try:
                v = v.replace("\r", " ")
            except Exception as er:
                pass

            # возможно это число можно в флоат закинуть - если точка там есть
            if round_float and v != "" and type(v) == type_str:
                if my_symbols(v, "-.1234567890") == v:
                    try:
                        v = float(v)
                    except Exception as er:
                        pass

            if key in linko and v != "":
                parts = v.split("|")
                if len(parts) == 2:
                    x, y = parts
                else:
                    x = v
                    y = v
                v = Formula(n + '("%s";"%s")' % (x, y))

            if (
                key not in linko
                and type(v) != type_float
                and type(v) != type_int
            ):
                try:
                    v = str(v)
                except Exception as er:
                    print("-", end="")

            else:
                pass
                if type(v) == type_float and round_float:
                    v0 = round_float_format % v
                    v = float(v0)
                #    pass

            # не умеет писать
            if type(v) == type_str and len(v) > 32767:  # 32000:
                v = v[:32767]
                # v = "xls_error_Too_long"
                pass

            sheet.write(i, j, v)
    text_to_file("", f_rez)
    wbk.save(f_rez)


if __name__ == "__main__":
    import os

    special = "settings"
    special = "keywords"
    special = "read_csv"
    special = "save_clever_to_xls"
    special = "read_xlsx"

    if special == "read_xlsx":
        f = r"s:\!kyxa\!code\!documentation\py4seo\advanced\08\dor_minimum\modules\temp\created_xls.xls"
        result_type = "dict"
        result_type = "dicts_list"
        lst = read_xlsx(f=f, result_type=result_type)
        print(lst)

    if special == "save_clever_to_xls":
        dela = [
            {"title": "hello", "num": 25,},
            {"title": "world", "num": 26.6,},
        ]
        f_rez = "temp/created_xls.xlsx"
        polja = []
        save_clever_to_xls(polja=polja, dela=dela, f_rez=f_rez)

        print(f"created {f_rez}")
        os._exit(0)

    if special == "read_csv":
        f = r"s:\!kyxa\!code\!documentation\py4seo\advanced\08\dor_minimum\data\example_of_files_with_keys\bukvarix\как гардероб.csv"
        f = r"s:\!chaos\!keywords\универсальное - как\как одежда.csv"
        max_rows = 1
        max_rows = 1000
        max_rows = 1000000

        fields = [
            "key",
            "words",
            "symbols",
            "chastotnostj",
            "chastotnostj_exact",
        ]
        keys_int = [
            "words",
            "symbols",
            "chastotnostj",
            "chastotnostj_exact",
        ]
        data = read_csv(f, fields=fields, max_rows=max_rows, keys_int=keys_int)
        print(f"{len(data)} example:{data[0]}")

    if special == "settings":
        f = r"s:\!kyxa\!code\!documentation\py4seo\advanced\08\dor_minimum\data\settings.xlsx"
        result_type = "dict"
        lst = read_xlsx(f=f, result_type=result_type)
        print(lst)

    if special == "keywords":
        f = r"s:\!chaos\!keywords\liallt.club\Keyword Tool Export - funlearningforkids com.xlsx"
        result_type = "dicts_list"
        lst = read_xlsx(f=f, result_type=result_type)
        print(lst)
