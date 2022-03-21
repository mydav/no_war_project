# pyarmor options: no-spp-mode
# -*- coding: utf-8 -*-

import os, sys

from modules.base_functions import *
from random import shuffle
from text_generator.settings_parser import *

import itertools

from modules_mega_23.tester_functions import my_tester

logger = get_logger(__name__)


class TextRandomizer:
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

    def evaluate_variations_quantity(self, text="", cnt_tries=100):
        fun = "evaluate_variations_quantity"

        logger.debug(f"[{fun}", end=" ")
        special = "count_variations"
        # cnt_tries = 1000

        cnt_variations = []
        for i in range(cnt_tries):
            if i % 20 == 0:
                logger.debug(cnt_tries - i, end=" ")

            r = self.get_random_text_variation(text=text, special=special)
            cnt_variations.append(r)

        rounded_cnt_variations = int(
            1.0 * sum(cnt_variations) / len(cnt_variations)
        )
        logger.debug(
            f"\nevaluated: after {cnt_tries} tries I know that I can generate about {rounded_cnt_variations} variations]"
        )
        return rounded_cnt_variations

    def get_random_text_variation(
        self,
        text="",
        special="get_random_variation",
        # special='count_variations',
    ):
        """
            получаем случайную вариацию текста
            идея: как только встречаем неоднозначность - ее разгадываем. Все.
        """
        t_start = time.time()

        text = text.split("<obrezaluss>")[0]

        is_correct_template = self.check_template_correctness(text)
        if not is_correct_template:
            detailed_error = self.find_top_block(
                text, start=self.start, finish=self.finish
            )
            wait_for_ok(f"ERROR: template is not correct!")
            os._exit(0)

        count_all_possible_variations = []

        step = 0
        while True:
            step += 1

            # на каждом шаге ищем начало блока, и если оно есть - ищем его конец (считаем открытые и закрытые блоки, количество открытых-закрытых должно совпасть

            if self.otl:
                logger.debug1(f"step {step}, text `{text}`")
                # wait_for_ok(m)

            if text.find(self.start) == -1:
                if self.otl:
                    logger.debug(f"start `{self.start}` not found, break")
                break

            # demo: `a {1|2|3} b`
            text_before_block = find_from_to_one(
                "nahposhuk", self.start, text
            )  # `a `
            block_and_text_after_block = self.start + find_from_to_one(
                self.start, "nahposhuk", text
            )  # `{1|2|3} b`

            # в тексте после ищем где он закрывается, но не просто так, а корректно, с учетом вложенности
            block = self.find_top_block(
                block_and_text_after_block,
                start=self.start,
                finish=self.finish,
            )  # `1|2|3`

            text_after_block = find_from_to_one(
                block + self.finish, "nahposhuk", text
            )  # ` b`

            if self.otl:
                logger.debug(f"{text_before_block=}")

                logger.debug(f"{block_and_text_after_block=}")

                logger.debug(f"block in block_and_text_after_block: {block=}")

            block_settings, list_in_block = self.parse_main_block_parts(block)
            count_all_possible_variations.append(len(list_in_block))
            # wait_for_ok('parsed?')

            if self.otl:
                logger.debug(f"{block_settings=}")
                logger.debug(f"{list_in_block=}")

            #   чтобы визуально проверить как там что, можно выставить не 1 а 10 например :)
            for i in range(1):
                generated_text = self.generate_text_from_list(
                    list_in_block, block_settings
                )

            generated_text = self.edit_text_with_special_functions(
                generated_text, block_settings["after"]
            )

            # wait_for_ok(f'generated_text {generated_text}')
            text = text_before_block + generated_text + text_after_block

            # break
            if self.otl:
                m = f"new text: \n`{text}`"
                logger.debug(m)

                m = f"step {step} done"
                logger.debug(m)
                # wait_for_ok()

        count_variations = multiply_list(count_all_possible_variations)
        duration = time.time() - t_start

        if self.otl:
            logger.debug(
                f"{count_variations} all possible combinations from {count_all_possible_variations} in {duration:.3f} seconds"
            )

        if special == "count_variations":
            return count_variations

        elif special == "get_random_variation":
            return text

        else:
            wait_for_ok(f"ERROR: unknown special {special}")

    def check_template_correctness(
        self, text="", start=None, finish=None,
    ):
        """
            проверяем - корректный шаблон?
        """
        start = self.get_default_value("start", start)
        finish = self.get_default_value("finish", finish)

        cnt_starts = text.count(start)
        cnt_finishes = text.count(finish)

        status = 1
        if cnt_starts != cnt_finishes:
            logger.debug(
                f"NOT CORRECT TEMPLATE, cnt_starts of {start} {cnt_starts} != {cnt_finishes} cnt_finishes of {finish}"
            )
            status = 0

        return status

    def parse_main_block_parts(self, block=""):
        settings_text, list_text = self.get_texts_for_main_parts(block)
        block_settings = self.parse_settings_in_block(settings_text)
        list_in_block = self.parse_list_from_block(list_text, block_settings)
        return block_settings, list_in_block

    def get_texts_for_main_parts(self, block):
        fun = "get_texts_for_main_parts"

        settings_text = ""
        list_text = block

        if block[0] in ["#"]:
            settings_text = find_from_to_one("nahposhuk", "#", block[1:])
            list_text = find_from_to_one("#", "nahposhuk", block[1:])

        if self.otl:
            logger.debug(
                f'{fun}: settings_text "{settings_text}", list_text "{list_text}"'
            )
            # wait_for_ok()

        return settings_text, list_text

    def parse_settings_in_block(self, text=""):
        """
            получаем настройки блока
        """
        settings_parser = RandomizerSettingsParser()
        block_settings = settings_parser.parse(
            text=text, delimiter=self.delimiter,
        )
        return block_settings

    def parse_list_from_block(self, text="", block_settings={}):
        """
            получаем настройки блока
        """
        # pretty(block_settings)
        items = self.split_top_list(
            text,
            delimiter=block_settings["delimiter"],
            start=self.start,
            finish=self.finish,
        )

        if self.otl:
            logger.debug(f"[parse_list_from_block items: {items}]")
        # wait_for_ok()
        items = [_ for _ in items if self.list_item_is_good(_)]
        return items

    def list_item_is_good(self, item=""):
        if item.strip() == "":
            return 0
        return 1

    def generate_text_from_list(self, lst=[], block_settings={}):
        """
            у нас уже есть список и настройки, нужно с него сгенерить норм. текст
        """
        S = Bunch(block_settings)

        #       order
        generated = lst[:]

        #       getting random size
        range_from_settings = S.cnt
        real_range = get_random_value_in_range(
            range_from_settings, special="range"
        )
        ot, do = real_range
        ot = min(ot, len(generated))
        do = min(do, len(generated))

        random_size = get_random_value_in_range(f"{ot}-{do}")

        generated = self.select_random_list_values(
            generated, size=random_size, order=S.order
        )

        # joininig
        generated = block_settings["join"].join(generated)

        if self.otl:
            m = f"generated: {generated} \n             from settings: random_size == {random_size}, ot-do == {ot}-{do} (range_from_settings {range_from_settings}, real_range {real_range})"
            logger.debug(m)
            # wait_pretty(m)

        return generated

    def select_random_list_values(
        self, items=[], size=3, order="shuffle",
    ):
        """
            выбираем из списка нужное количество рандомных значений (если надо - шафлим, если нет - в том же порядке но рандомные
        """

        indexes = list(range(len(items)))
        shuffle(indexes)
        indexes = indexes[:size]

        if order == "shuffle":
            pass

        elif order == "normal":
            indexes.sort()

        else:
            wait_for_ok(f'unknown order "{order}"')

        lst = [items[i] for i in indexes]
        return lst

    def find_top_block(
        self, text="", start=None, finish=None,
    ):
        """
            ищем верхний корректный блок
        """
        otl = 1
        otl = 0

        start = self.get_default_value("start", start)
        finish = self.get_default_value("finish", finish)

        pos_search_from = 0
        step = 0
        while True:
            step += 1
            pos_start = text.find(start) + len(start)
            pos_finish = text.find(finish, pos_search_from)

            text_before = text[pos_start:pos_finish]
            text_after = text[pos_finish + len(finish) :]

            cnt_starts = text_before.count(start)
            cnt_finishes = text_before.count(finish)

            if otl and self.otl:
                logger.debug(
                    f"    step {step}: pos_finish {pos_finish}, pos_search_from {pos_search_from}, cnt_starts {cnt_starts}, cnt_finishes {cnt_finishes}, text_before: `{text_before}`, text_after `{text_after}`"
                )

            if pos_finish == -1:
                # wait_for_ok(f'{pos_finish}, {cnt_starts}, {cnt_finishes}')
                if cnt_starts == 0 and cnt_finishes == 0:
                    text_before = ""

                else:
                    cnt_not_closed = 1 + cnt_starts - cnt_finishes
                    if cnt_not_closed > 0:
                        logger.debug(
                            f"ERROR_TEMPLATE - NOT CLOSED {cnt_not_closed} tags `{finish}`"
                        )
                        return False

                    else:
                        wait_for_ok("ERROR WITH TEMPLATE: ")

            # == cnt_finishes:
            #        break
            #    else:
            #        wait_for_ok(f'not found {finish} after position {pos_search_from}, text_after "{text_after}"')

            if cnt_starts == cnt_finishes:
                # wait_for_ok(text_after)
                # проверяем - корректный блок тот что остался после найденного?
                if self.check_template_correctness(text_after):
                    break

                else:
                    logger.debug(
                        f"ERROR_TEMPLATE - closed but not opened this part `{text_after[:100]}...`"
                    )
                    # wait_for_ok()
                    return False

                # wait_for_ok(f'found "{text_before}"')

            else:
                pos_search_from = pos_finish + 1
                # wait_for_ok('continue search')
                continue

        if otl and self.otl:
            logger.debug(f"found top block: {text_before}")
            # wait_for_ok()
        return text_before

    def split_top_list(
        self, text="", delimiter=None, start=None, finish=None,
    ):
        """
            разбиваем список только по верхнему уровню
            {{#order shuffle#a111|a112}|a12|a13|a14|a15}|a2|a3

            разбиваем по |

            получаем список из
                {{#order shuffle#a111|a112}|a12|a13|a14|a15}
                a2
                a3
        """
        start = self.get_default_value("start", start)
        finish = self.get_default_value("finish", finish)
        delimiter = self.get_default_value("delimiter", delimiter)

        otl = 0
        otl = 1

        top_delimiters = []
        pos_search_from = 0
        step = 0
        while True:
            step += 1
            pos_delimiter = text.find(delimiter, pos_search_from)

            if pos_delimiter == -1:
                break

            text_before = text[:pos_delimiter]
            text_after = text[pos_delimiter + 1 :]

            cnt_starts = text_before.count(start)
            cnt_finishes = text_before.count(finish)

            if otl and self.otl:
                logger.debug(
                    f'    step {step}: pos_delimiter {pos_delimiter}, pos_search_from {pos_search_from}, cnt_starts {cnt_starts}, cnt_finishes {cnt_finishes}, text_before: "{text_before}", text_after "{text_after}"'
                )

            if cnt_starts == cnt_finishes:
                top_delimiters.append(pos_delimiter)
                m = f"found top_delimiter {pos_delimiter}"
            else:
                m = f"not top_delimiter"

            if otl and self.otl:
                logger.debug(m)
                # wait_for_ok()

            pos_search_from = pos_delimiter + 1
            # wait_for_ok(f'step {step} done, continue search')
            continue

        offset = len(delimiter)
        if otl and self.otl:
            logger.debug(
                f"found {len(top_delimiters)} top delimiters: {top_delimiters}, offset {offset}"
            )

        top_list = []
        if len(top_delimiters) == 0:
            top_list = [text]

        else:
            # знаю главные разделители - остально разбить
            for num in range(len(top_delimiters)):
                # первый элемент
                if num == 0:
                    pos_ot = 0
                    pos_do = top_delimiters[num]

                else:
                    pos_ot = top_delimiters[num - 1] + offset
                    pos_do = top_delimiters[num]

                top_item = text[pos_ot:pos_do]
                if otl and self.otl:
                    logger.debug(f"num {num}, top_item {top_item}")

                top_list.append(top_item)

            if 1:
                pos_ot = top_delimiters[num] + offset
                pos_do = len(text)
                top_item = text[pos_ot:pos_do]
                top_list.append(top_item)

        if otl and self.otl:
            logger.debug("top_list:")
            pretty(top_list)

        # wait_for_ok()
        return top_list

    def get_default_value(self, name="start", value=None):
        if value == None:
            if name == "start":
                value = self.start
            elif name == "finish":
                value = self.finish
            elif name == "delimiter":
                value = self.delimiter
            else:
                wait_for_ok(f"ERROR: unknown name {name}")
        return value

    def edit_text_with_special_functions(
        self, text="", funcs=[],
    ):
        for func in funcs:
            if func == "":
                continue

            elif func == "strip":
                text = text.strip()

            elif func == "upper":
                text = text.upper()

            elif func == "capitalize":
                text = text.capitalize()

            elif func == "title":
                text = text.title()

            elif func[:4] in ["add<"]:
                if text != "":
                    adding = find_from_to_one("<", ">", func)
                    text = adding + text

            else:
                wait_for_ok(f"ERROR: unknown function {func}")

        return text


if __name__ == "__main__":

    t = 0
    t = 1
    if t:
        f = r"s:\!data\!offers\solcredito\description.md"
        f = r"data\combinatorics\demo1.md"

        text = text_from_file(f)

        otl = 0
        otl = 1

        start = "{"
        finish = "}"
        delimiter = "|"

        t = 1
        if t:
            templates = clear_list(
                r"""
            # Пропаганда (убийств%войны% продолжения войны% продолжения военных действий%продолжения войны) (на Украине%в Украине)
            # Пропаганда (%истребления%убийства%) (украинского народа%украинцев%украинской нации%украинских людей%жителей Украины)
            # ((11%12)%(21%22%(31%32))) (01%02)
            # (1%(21%(31%32%33))) (01%02)
            (Распостранение%Публикация) (фейков%фейковых новостей%неправдивой информации%не правдивой информации%лживых фактов%лживой информации%фейковой информации%лжи%неправды%вранья) (о войне на Украине%о войне в Украине%о событиях на Украине%о событиях в Украине%о военных действиях на Украине%о военных действиях в Украине)
            """,
                bad_starts=["#"],
            )
            text = templates[0]
            start = "("
            finish = ")"
            delimiter = "%"

        t = 1
        t = 0
        if t:
            start = "{{"
            finish = "}}"
            delimiter = "|||"

        # ру-разметка
        t = 1
        t = 0
        if t:
            start = "(("
            finish = "))"
            delimiter = "%%"

        rewriter = TextRandomizer(
            otl=otl, start=start, finish=finish, delimiter=delimiter,
        )

        t = 0
        t = 1
        if t:
            r = rewriter.get_random_text_variation(text=text)

        t = 1
        t = 0
        if t:
            r = rewriter.evaluate_variations_quantity(text=text)

        t = 1
        t = 0
        if t:
            text = "selecting word {{a111|a112}|a12|a13|a14|a15}|a2|a3} successfully :)"
            text = "{{{oppa}}"
            r = rewriter.check_template_correctness(text)

        t = 1
        t = 0
        if t:
            text = "selecting word {{a111}|a112}|a12|a13|a14|a15}|a2|a3} successfully :)"  # error - рано закрыли
            text = "selecting word {{a111} successfully :)"  # error - лишний открыли
            # r = rewriter.find_top_block(text)

            tasks = [
                ["{a1|a2|a3} finish", "a1|a2|a3",],
                ["selecting word successfully :)", "",],
                [
                    "{selecting word {{a111|a112}|a12|a13|a14|a15}|a2|a3} successfully :)",
                    "selecting word {{a111|a112}|a12|a13|a14|a15}|a2|a3",
                ],
                ["demo with error 1: {{a}, not closed", False,],
                ["demo with error 2: {a}}, not opened", False,],
            ]

            r = my_tester(tasks, rewriter.find_top_block)

        t = 1
        t = 0
        if t:
            text = "{{#order shuffle#a111|a112}|a12|a13|a14|a15}|a2|a3"
            text = "a21%%a22%%a23"
            text = "a21|||a22|||a23"
            r = rewriter.split_top_list(text)

        t = 1
        t = 0
        if t:
            text = " hello world"
            funcs = ["strip", "upper", "lower"]
            r = rewriter.edit_text_with_special_functions(text, funcs=funcs)

        t = 1
        t = 0
        if t:
            items = "0 1 2 3 4 5 6 7 8 9".split(" ")
            # wait_for_ok(items)
            size = 3
            order = "normal"
            order = "shuffle"
            r = rewriter.select_random_list_values(
                items, size=size, order=order
            )

        logger.debug(f"r: {r}")
        os._exit(0)

    t = 1
    if t:
        lst = [1, 2, 3]
        lst = [1, 1]
        lst = [1, 2]
        length = 2
        # logger.debug(my_permutations(lst))
        logger.debug(get_permutations(lst, length=length))
        os._exit(0)
