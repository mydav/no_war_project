from modules import *
from itertools import combinations, product
from typing import List


def get_perestanovki_from_dct(dct, sizes=[2], return_mode="list"):
    #    #получаем словарь x:[1, 2], y:[a,b], и с него - список всех возможных перестановок в виде словаря
    #    var_descr = [
    #        'full',
    #        'title',
    #        'reviews',
    #        ]

    #    #вариант ссылки
    #    var_link = [
    #        'amazon',
    #        'amzn',
    #        ]

    #    var_cnt_links = [
    #        '0',
    #        '1',
    #        'start_end',    #сначала и в конце
    #    ]

    #    dct_variants = {
    #        'var_descr':var_descr,
    #        'var_link':var_link,
    #        'var_cnt_links':var_cnt_links,
    #    }

    #    результат:
    # 0       {'var_descr': 'full', 'var_cnt_links': '0', 'var_link': 'amazon'}
    # 1       {'var_descr': 'full', 'var_cnt_links': '0', 'var_link': 'amzn'}
    # 2       {'var_descr': 'full', 'var_cnt_links': '1', 'var_link': 'amazon'}
    # 3       {'var_descr': 'full', 'var_cnt_links': '1', 'var_link': 'amzn'}
    # 4       {'var_descr': 'full', 'var_cnt_links': 'start_end', 'var_link': 'amazon'}
    # ...
    fun = "get_perestanovki_from_dct"

    debug = True
    debug = False
    if debug:
        show_dict(dct)

    all_keys = dct.keys()
    rez = []

    for size in sizes:
        keys = get_combinations(all_keys, size)
        if debug:
            print(f"{size=} {keys=}")

        tips = []
        list_for_size = []

        for num, key_combos in enumerate(keys, 1):
            tips_combos = []
            for key in key_combos:
                v = dct[key]
                tips_combos.append(v)
            tips.append(tips_combos)

            if debug:
                print(f"    {num}/{len(keys)} {tips_combos=}")
                # wait_for_ok()

            lst_combos = get_perestanovki(tips_combos)
            list_for_size.append(lst_combos)
            if debug:
                print(f"        {lst_combos=}")

        list_for_size = flat(list_for_size)
        rez.append(list_for_size)
        if debug:
            print(f"{list_for_size=}")

        t = 0
        if t:
            for l in lst:
                _ = {}
                for i, k in enumerate(l):
                    _[keys[i]] = k

                rez.append(_)
    rez = flat(rez)
    if return_mode == "list":
        return rez
    else:
        wait_for_ok(f"ERROR {fun} - unknown {return_mode=}")


def get_perestanovki(list_of_lists: List[List]) -> List[List]:
    """
    words = [[1, 2], ["a", "b"]]
    generated = get_perestanovki(words)
        0	[1, 'a']
        1	[1, 'b']
        2	[2, 'a']
        3	[2, 'b']
    """
    rez = list(product(*(tuple(list_of_lists))))
    rez = [list(_) for _ in rez]
    return rez


def get_combinations(lst: list = None, size=2):
    """
    lst = [1, 2, 3, 4, 5]
    get_combinations(lst, 2)
        [[1, 2], [1, 3], [1, 4], [1, 5], [2, 3], [2, 4], [2, 5], [3, 4], [3, 5], [4, 5]]
    """
    lst = [list(i) for i in combinations(lst, size)]
    return lst


if __name__ == "__main__":
    special = "get_perestanovki_from_dct"

    if special == "get_perestanovki_from_dct":
        sizes = [1, 2, 3]
        _ = {
            "lst1": [1, 2],
            "lst2": ["a", "b"],
            "lst3": ["Y", "Z"],
        }
        r = get_perestanovki_from_dct(_, sizes=sizes)
        print(r)

    else:
        lst = [1, 2, 3, 4, 5]
        sizes = [1, 2, 3]
        for size in sizes:
            print(size, get_combinations(lst, size))

        words = [[1, 2], ["a", "b", "c"], ["x", "y"]]
        words = [[1, 2], ["a", "b"]]
        generated = get_perestanovki(words)
        show_list(generated)
        # print(generated)
