from modules.base_functions import *


class RandomizerSettingsParser:
    """
        парсим настройки
    """

    def __init__(
        self, otl=0,
    ):
        """
        """
        self.otl = otl

    def parse(
        self, text="", order="shuffle", delimiter="|", join=" ", cnt=1,
    ):
        """
            парсинг одного блока
        """
        fun = "parse"
        d = {
            "order": order,
            "delimiter": delimiter,
            "join": join,
            "cnt": cnt,
            "after": [],
            #'join': 'new_line',
            #'delimiter': '|',
            #'join': '|',
            #'cnt': 1,
        }

        block_settings = deepcopy(d)

        name_to_parse_function = {
            "order": self.parse_settings_order,
            "cnt": self.parse_settings_cnt,
            "delimiter": self.parse_settings_delimiter_join,
            "join": self.parse_settings_delimiter_join,
            "after": self.parse_settings_after,
        }

        parts = text.split(":")
        for part in parts:
            part = part.lstrip()

            if part == "":
                continue

            name = find_from_to_one("nahposhuk", " ", part)
            value = find_from_to_one(" ", "nahposhuk", part)

            name = name.strip()
            if self.otl:
                print(f'       name "{name}", value "{value}"')

            parse_function = name_to_parse_function.get(name, None)

            if parse_function is None:
                wait_for_ok(
                    f'{fun} ERROR: not exists parsing function for name "{name}" with value "{value}"'
                )

            else:
                if self.otl:
                    print(
                        f'                parsing value "{value}"...', end=""
                    )
                value = parse_function(value)
                if self.otl:
                    print(f'        +parsed "{value}"')
                block_settings[name] = value

        for name in ["delimiter", "join"]:
            v = block_settings[name]
            replaced = self.replace_special_symbols(v)
            block_settings[name] = replaced

        return block_settings

    def parse_settings_order(self, text="", default=""):
        """
        """
        permited_list = ["shuffle", "normal"]
        return self.should_be_in_list(text, permited_list)

    def parse_settings_after(self, text=""):
        """
        как полученный текст нужно обработать после?
        """
        delim1 = "    "  # 4 пробела
        delim2 = " "  # 1 пробел

        delims = [delim1]
        delims = [delim1, delim2]
        for delim in delims:
            pos = text.find(delim)
            # print(f'    delim  `{delim}`, pos `{pos}`, text `{text}`')
            if pos != -1:
                break

        parsed = clear_list(text.split(delim))

        # parsed = no_probely(parsed, replaces)  #не работает
        # print(f'1{parsed}2')
        # wait_for_ok(f'after, parsed {parsed} (delim `{delim}`')
        return parsed

    def parse_settings_delimiter_join(self, text=""):
        """
        delimiter and join - and parsing spec symbols
        """
        parsed = text

        # parsed = no_probely(parsed, replaces)  #не работает
        # print(f'1{parsed}2')
        return parsed

    def parse_settings_cnt(self, text=""):
        """
        """
        parsed = prepare_random_range(text)
        return parsed

    def should_be_in_list(self, value="", permited_list=[]):
        """
            значение должно быть среди списка
        """
        fun = "should_be_in_list"
        found = None
        if value not in permited_list:
            wait_for_ok(
                f'ERROR - fun "{fun}", value "{value}" not in "{permited_list}"'
            )
        else:
            found = value

        return found

    def replace_special_symbols(self, parsed=""):

        replaces = [
            ["new_line", "\n"],
        ]
        for bad, good in replaces:
            parsed = parsed.replace(bad, good)
        return parsed


if __name__ == "__main__":

    t = 1
    if t:
        otl = 0
        otl = 1

        settings_parser = RandomizerSettingsParser(otl=otl)

        text_settings = "order shuffle:cnt 100"
        # text_settings = 'order shuffle:cnt >0'
        text_settings = ""
        # text_settings = 'order shuffle: cnt >0: delimiter * : join new_line'
        text_settings = "order shuffle: cnt >0: delimiter * : join new_line: after add<, >    "
        r = settings_parser.parse(text_settings)

    print(f"r: {r}")
    os._exit(0)
