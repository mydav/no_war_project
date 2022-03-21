#!/usr/bin/python
# -*- coding: utf-8 -*-

from modules.minimum_important_functions import *
from copy import copy as copy_copy

import itertools
from typing import List, Iterable

logger = get_logger(__name__)


def get_all_combinations(lst: List, sizes: Iterable[int] = None):
    """получаем все возможные комбинации"""
    if sizes is None:
        sizes = [2]

    all_combos = []
    for size in sizes:
        combos = list(itertools.combinations(lst, size))
        all_combos = all_combos + combos
    return all_combos


def get_all_combinations_lst1_lst2(lst1=[], lst2=[]):
    t = 0
    if t:
        result = list(itertools.product(*[lst1, lst2]))
        return result

    l1 = lst1[:]
    l2 = lst2[:]

    t = 0
    if t:
        to_add = len(lst2) - len(lst1)
        for i in range(to_add):
            l1.append(None)

    t = 1
    if t:
        # result = itertools.product(*[l1, l2])
        # result = [[[x,y] for x in l1] for y in l2]
        result = list(
            list(zip(r, p))
            for (r, p) in zip(itertools.repeat(l1), itertools.permutations(l2))
        )
        # show_list(result)
        # result = map(list, result)
        # wait_for_ok()
    return result

    c = list(itertools.product(l1, l2))
    logger.info(c)
    wait_for_ok()

    t = 0
    if t:
        ret = []
        for i, e in enumerate(a):
            for j, f in enumerate(b):
                l = [e + f]
                new_l = rec(a[i + 1 :], b[:j] + b[j + 1 :], ll)
                if not new_l:
                    ret.append(l)
                for k in new_l:
                    l_k = l + k
                    ret.append(l_k)
                    if len(l_k) == size:
                        ll.append(l_k)
    return ret


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
    logger.debug("Solution_permutator...")
    s = Solution_permutator()
    r = s.permute(iterable)
    logger.debug("+%d" % len(r))
    return r


def my_permutations_gluk(iterable, r=None):
    # permutations('ABCD', 2) --> AB AC AD BA BC BD CA CB CD DA DB DC
    # permutations(range(3)) --> 012 021 102 120 201 210
    pool = tuple(iterable)
    n = len(pool)
    r = n if r is None else r
    if r > n:
        return
    indices = range(n)
    cycles = range(n, n - r, -1)
    yield tuple(pool[i] for i in indices[:r])
    while n:
        for i in reversed(range(r)):
            cycles[i] -= 1
            if cycles[i] == 0:
                indices[i:] = indices[i + 1 :] + indices[i : i + 1]
                cycles[i] = n - i
            else:
                j = cycles[i]
                indices[i], indices[-j] = indices[-j], indices[i]
                yield tuple(pool[i] for i in indices[:r])
                break
        else:
            return


def get_all_combinations_lst1_lst2_new(lst1=[], lst2=[]):
    # беру все комбинации, и ищу с минимальной суммой
    # https://stackoverflow.com/questions/12935194/combinations-between-two-lists?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
    # Suppose len(list1) >= len(list2)

    fun = "get_all_combinations_lst1_lst2_new"
    logger.debug("[%s" % fun)
    l1 = lst1[:]
    l2 = lst2[:]

    to_add = len(lst2) - len(lst1)
    for i in range(to_add):
        l1.append(None)

    to_add = len(lst1) - len(lst2)
    for i in range(to_add):
        l2.append(None)

    # combos = [zip(x,l2) for x in itertools.permutations(l1,len(l2))]
    perms = list(my_permutations(l1, len(l2)))
    logger.debug("  %s permuations" % (len(perms)))
    # sleep_(.001)    #может поможет задержка https://stackoverflow.com/questions/47023141/sending-data-bytesio-buffer-through-a-pipe-works-but-causes-a-fatal-python-exc?noredirect=1&lq=1&utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
    combos = []
    for x in perms:
        # v = zip(x, l2)
        combo = []
        for i in range(len(l2)):
            combo.append([x[i], l2[i]])
        combos.append(combo)

    logger.debug("combos_real")

    combos_real = []
    for combo in combos:
        # combo = list(combo)

        combo_real = []
        for _ in combo:
            if None in _:
                continue
            combo_real.append(_)
        combos_real.append(combo_real)
    logger.debug("+%s combos_real]" % len(combos_real))
    return combos_real


def get_perestanovki(words, otladka=False):
    """генерим все возможные подстановки из [[1, 11, 3], [2, 22, 222], [3, 33, 333]]"""
    generated = []
    for podst in words:
        new_podst = []
        if generated == []:
            for p in podst:
                t = []
                t.append(p)
                new_podst.append(t)
        else:
            if otladka:
                logger.debug("generated: %s" % generated)
            for g in generated:
                for p in podst:
                    t = copy_copy(g)
                    if otladka:
                        logger.debug("t=%s" % t)
                    if otladka:
                        logger.debug("    %s" % p)
                    t.append(p)
                    new_podst.append(t)
        if otladka:
            logger.debug("done step: %s" % new_podst)
        generated = new_podst

    return generated


def get_perestanovki_from_dct(dct):
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

    keys = list(dct.keys())
    lists = []
    for k in keys:
        v = dct[k]
        lists.append(v)

    permutations = get_perestanovki(lists)
    logger.debug(f"{len(permutations)} {permutations=}")
    rez = []
    for permutation in permutations:
        _ = {}
        for num, k in enumerate(permutation):
            _[keys[num]] = k

        rez.append(_)
    return rez


if __name__ == "__main__":
    special = "get_all_combinations"
    special = "get_perestanovki"
    special = "get_perestanovki_from_dct"
    special = "get_all_combinations_lst1_lst2"

    if special == "get_all_combinations_lst1_lst2":
        lst1 = [1, 2]
        lst2 = ["x", "y", "z"]
        generated = get_all_combinations_lst1_lst2(lst1, lst2)
        logger.info(f"have {len(generated)} {generated=}")

    elif special == "get_all_combinations":
        ids = [1, 2, 3]
        generated = get_all_combinations(ids, [2, 3])
        logger.info(f"have {len(generated)} {generated=}")

    elif special == "get_perestanovki":
        words = [[1, 2], ["a", "b", "c"], ["x", "y"]]
        generated = get_perestanovki(words)

        logger.info(f"have {len(generated)} {generated=}")

    elif special == "get_perestanovki_from_dct":
        dct = {
            "x": [1, 2],
            "y": ["a", "b", "c"],
            "z": ["x", "y"],
        }
        generated = get_perestanovki_from_dct(dct)

        logger.info(f"have {len(generated)} {generated=}")

    else:
        logger.critical(f"unknown {special=}")
