from modules.base_functions import *

from text_generator.LazyCartesianProduct import LazyCartesianProduct
import itertools


class Solution_permutator(object):
    # https://codereview.stackexchange.com/questions/178164/generate-all-permutations-of-a-list-in-python?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
    def permute(self, nums):
        res = []
        self._permuteHelper(nums, 0, res)
        return res

    def _permuteHelper(self, nums, start, results):  # helper method
        if start >= len(nums):
            results.append(nums[:])
        else:
            for i in range(start, len(nums)):
                nums[i], nums[start] = nums[start], nums[i]
                self._permuteHelper(nums, start + 1, results)
                nums[start], nums[i] = nums[i], nums[start]


def my_permutations(iterable, r=None):
    print("Solution_permutator...", end="")
    s = Solution_permutator()
    r = s.permute(iterable)
    print("+%d" % len(r))
    return r


def get_permutations(lst, length=None):
    # https://docs.python.org/3/library/itertools.html#itertools.permutations
    # permutations('ABCD', 2) --> AB AC AD BA BC BD CA CB CD DA DB DC
    # permutations(range(3)) --> 012 021 102 120 201 210

    return list(itertools.permutations(lst, r=length))


class TextRewriter:
    """
        учусь переписывать тексты
    """

    def __init__(
        self, otl=0, start="{", finish="}", delimiter="|",
    ):
        """
        """

        self.otl = otl
        self.start = start
        self.finish = finish
        self.delimiter = delimiter

    def get_random_text_variation(
        self, text="",
    ):
        """
            получаем случайную вариацию текста
            идея: как только встречаем неоднозначность - ее разгадываем. Все.
        """

        final_blocks = []

        blocks = text.split(self.start)
        final_blocks.append(blocks.pop(0))

        step = 0
        while True:
            step += 1

            m = f"step {step}"
            if self.otl:
                print(m)

            if len(blocks) == 0:
                break

            block = blocks.pop(0)
            # wait_for_ok(block)

            (
                block_settings,
                list_in_block,
                text_after,
            ) = self.parse_main_block_parts(block)

            # break
            if self.otl:
                m = f"step {step} done, todo {len(blocks)} blocks"
                wait_for_ok(m)

    def parse_main_block_parts(self, block=""):
        settings_text, list_text, text_after = self.get_texts_for_main_parts(
            block
        )
        block_settings = self.parse_settings_in_block(settings_text)
        list_in_block = self.parse_list_in_block(list_text)
        return block_settings, list_in_block, text_after

    def get_texts_for_main_parts(self, block):
        fun = "get_texts_for_main_parts"

        parts = block.split(self.finish)
        # print(parts)
        if len(parts) != 2:
            wait_for_ok(f"{fun} error, cnt parts {len(parts)} != 2 in {parts}")

        settings_text = ""
        list_text = parts[0]
        text_after = parts[1]

        if block[0] in ["#"]:
            settings_text, list_text = parts[0][1:].split("#")

        if self.otl:
            print(
                f'{fun}: settings_text "{settings_text}", list_text "{list_text}", text_after "{text_after}"'
            )
            # wait_for_ok()

        return settings_text, list_text, text_after

    def parse_settings_in_block(self, txt=""):
        """
            получаем настройки блока
        """
        settings_parser = RandomizerSettingsParser()
        block_settings = settings_parser.parse(txt)
        return block_settings
        d = {
            "order": "shuffle",
            "split": "new_line",
            "join": "new_line",
            "cnt": 1,
        }

        block_settings = deepcopy(d)

        name_to_parse_function = {
            "order": self.parse_settings_order,
            "split": self.parse_settings_dumb,
            "join": self.parse_settings_dumb,
            "cnt": self.parse_settings_cnt,
        }

        parts = txt.split(":")
        for part in parts:
            name = find_from_to_one("nahposhuk", " ", part)
            value = find_from_to_one(" ", "nahposhuk", part)

            name = name.strip()
            if self.otl:
                print(f'       name "{name}", value "{value}"')

            parse_function = name_to_parse_function.get(name, None)

            if parse_function is None:
                wait_for_ok()

            # else:

            # if name in name_to_parse_function:
            #   value =

            # if name in ['order']:
            #    value = self.parse_settings_order(value)
            #    available_values = ['shuffle']
            #    if value not in available_values:
            #        wait_for_ok(f'ERROR - name "{name}", value "{value}" not in "{available_values}"')

        if self.otl:
            pass
            # wait_for_ok()

        return block_settings

    def parse_list_in_block(self, txt=""):
        """
            получаем настройки блока
        """
        lst = []
        items = txt.split(self.delimiter)
        return items


if __name__ == "__main__":

    t = 0
    t = 1
    if t:
        f = r"c:\!code\kyartist\venv\Lib\site-packages\modules\data\combinatorics\demo1.md"

        text = text_from_file(f)

        otl = 1
        rewriter = TextRewriter(otl=otl,)

        t = 0
        if t:
            r = rewriter.get_random_text_variation(text=text,)

        t = 1
        if t:
            text_settings = "order shuffle:cnt >0"
            text_settings = "order shuffle: cnt >0: split * : join *"
            text_settings = "order shuffle:cnt 100"
            # text_settings = ''
            r = rewriter.parse_settings_in_block(text_settings)

        print(f"r: {r}")
        os._exit(0)

    t = 1
    if t:
        lst = [1, 2, 3]
        lst = [1, 1]
        lst = [1, 2]
        length = 2
        # print(my_permutations(lst))
        print(get_permutations(lst, length=length))
        os._exit(0)
