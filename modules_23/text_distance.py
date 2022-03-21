#!/usr/bin/python
# -*- coding: utf-8 -*-

from modules_23.minimum_important_functions import *

from modules_mega_23.kombinatorika import get_all_combinations_lst1_lst2_new
import difflib

logger = get_logger(__name__)


def levenshtein(s, t):
    m, n = len(s), len(t)
    D = [range(n + 1)] + [[x + 1] + [None] * n for x in range(m)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s[i - 1] == t[j - 1]:
                D[i][j] = D[i - 1][j - 1]
            else:
                before_insert = D[i][j - 1]
                before_delete = D[i - 1][j]
                before_change = D[i - 1][j - 1]
                D[i][j] = min(before_insert, before_delete, before_change) + 1
        # поиск предписания проходом от конца к началу
    prescription = []  # собственно, предписание
    prescription_s = []  # соответствие предписания и символов строки s
    prescription_t = []  # соответствие предписания и символов строки t
    i, j = m, n
    while i and j:
        insert = D[i][j - 1]
        delete = D[i - 1][j]
        match_or_replace = D[i - 1][j - 1]
        best_choice = min(insert, delete, match_or_replace)
        if best_choice == match_or_replace:
            if s[i - 1] == t[j - 1]:  # match
                prescription.append("M")
            else:  # replace
                prescription.append("R")
            prescription_s.append(s[i - 1])
            prescription_t.append(t[j - 1])
            i -= 1
            j -= 1
        elif best_choice == insert:
            prescription.append("I")
            prescription_s.append("-")
            prescription_t.append(t[j - 1])
            j -= 1
        elif best_choice == delete:
            prescription.append("D")
            prescription_s.append(s[i - 1])
            prescription_t.append("-")
            i -= 1
    # поиск шел в обратном направлении, reverse вернет прямой порядок
    prescription.reverse()
    prescription_s.reverse()
    prescription_t.reverse()

    return D[m][n]


def levenshtein3(a, b, normed=0):
    t = difflib.SequenceMatcher(None, a, b).ratio()
    if t == 0.0:
        t = 0.001

    v = 1 / (t) - 1

    if normed:
        # min_word_len = max(    1,     max([len(a), len(b)])    )
        min_word_len = max(1, min([len(a), len(b)]))
        v = v / min_word_len

    return v


def levenshtein2(a, b):
    n, m = len(a), len(b)
    if n > m:
        a, b = b, a
        n, m = m, n
    current_row = range(n + 1)
    for i in range(1, m + 1):
        previous_row, current_row = current_row, [i] + [0] * n
        for j in range(1, n + 1):
            add, delete, change = (
                previous_row[j] + 1,
                current_row[j - 1] + 1,
                previous_row[j - 1],
            )
            if a[j - 1] != b[i - 1]:
                change += 1
            current_row[j] = min(add, delete, change)

    return current_row[n]


def select_closest_phrase(phrase, phrases, otl=0, one_element=1, normed=1):
    # ищем ближайшую фразу
    lst = []
    for t in phrases:
        l = levenshtein3(phrase, t, normed=normed)
        lst.append([l, t])

        # if normed:
        #    #logger.debug('min_word_len %s %s, distance_norm %.3f'% (r1, min_word_len, distance_norm))
        #    lst.append(    [distance_norm, t]    )
        # else:
        #    lst.append(    [l, t]    )

    lst.sort()
    if otl:
        try:
            show_list(lst)
        except Exception as er:
            logger.error("error %s" % er)
    if one_element:
        return lst[0][1]
    else:
        return lst


def select_closest_for_list(lst1=[], lst2=[], normed=1, otl=0):
    """
        ищем ближайшее для списка
    """
    fun = "select_closest_for_list"
    # otl = 1
    # otl = 0

    if otl:
        logger.debug("[%s %s*%s" % (fun, len(lst1), len(lst2)))
        logger.debug("    lst1 %s" % lst1)
        logger.debug("    lst2 %s" % lst2)

    t = 1
    if t:
        # wait_for_ok()
        closest = {}
        min_combo_sum = 1000000000000000
        combo_best = []

        # считаю расстояния между всема элементами
        distances = {}
        # normed = 1
        for x in lst1:
            distances[x] = {}
            for y in lst2:
                dist = levenshtein3(x, y, normed=normed)
                distances[x][y] = dist

        if otl:
            logger.debug("distances:")
            show_dict(distances)

        # combinations = [zip(x,lst2) for x in itertools.permutations(lst1,len(lst2))]
        if otl:
            logger.debug("get_all_combinations_lst1_lst2")
        # combinations = get_all_combinations_lst1_lst2(lst1, lst2)
        combinations = get_all_combinations_lst1_lst2_new(lst1, lst2)

        if otl:
            logger.debug("+")

        # combinations = [zip(x,lst2) for x in itertools.permutations(lst1,min(len(lst1), len(lst2)))]
        if otl:
            logger.debug("have %s combinations " % len(combinations))
            # show_list(combinations)
            # wait_for_ok()

        i = 0
        for combo in combinations:
            i += 1

            t = 0
            if t and otl:
                logger.debug("    %s/%s %s" % (i, len(combinations), combo))
            combo_distances = []
            for x, y in combo:
                dist = distances[x][y]
                combo_distances.append(dist)
            combo_sum = sum(combo_distances)

            best = 0
            mess_best = ""
            if combo_sum < min_combo_sum:
                best = 1
                mess_best = "BEST!"

                combo_best = combo[:]
                min_combo_sum = combo_sum

            t = 0
            if t and otl:
                logger.debug(
                    "    combo_sum %s %s %s"
                    % (mess_best, combo_sum, combo_distances)
                )

        for x, y in combo_best:
            info = {
                "element": y,
                "distance": distances[x][y],
            }
            closest[x] = info

        # wait_for_ok()

    else:
        name_to_distances = {}
        for e1 in lst1:
            distances = select_closest_phrase(e1, lst2, one_element=0)

            t = 0
            if t:
                min_word_len = max(1, min([len(r1), len(e1)]))
                distance_norm = d1 / min_word_len
                logger.debug(
                    "min_word_len %s %s, distance_norm %.3f"
                    % (r1, min_word_len, distance_norm)
                )

            # if otl:
            #    logger.debug('element %s' % e1)
            #    logger.debug('distances')
            #    show_list(distances)

            name_to_distances[e1] = distances  # все посчитали

            # element papa
            # distances
            #    0       [0.0, "papa"]
            #    1       [0.333333333333, "pape"]
            #    2       [2.5, "dva"]
            #    3       [2.5, "raz"]
            #    4       [3.0, "mame"]
            #    5       [999.0, "hello  123"]
            #    6       [999.0, "hello 123"]
            #    7       [999.0, "hello llll23"]
            #    8       [999.0, "hello123"]
            #    9       [999.0, "lllello123"]
            #    10      [999.0, "n"]

            # wait_for_ok()

        if otl:
            logger.debug("name_to_distances")
            show_dict(name_to_distances)

        # теперь будем ити от элемента, для которого есть наилучший сосед
        resorted = []
        for e1 in lst1:
            items = name_to_distances[e1]
            if len(items) == 0:
                continue

            d1, r1 = items[0]
            resorted.append([d1, e1])

        resorted.sort()
        e1_sorted = [_[1] for _ in resorted]

        t = 1
        t = 0
        if t or otl:
            logger.debug("resorted")
            show_list(resorted)

            logger.debug("e1_sorted: %s" % e1_sorted)

        # для каждого элемента ищем ближайший
        selected = []  # что уже выбрал?
        closest = {}
        i = 0
        for e1 in e1_sorted:
            i += 1
            if otl:
                logger.debug("\n %s/%s work with %s" % (i, len(e1_sorted), e1))

            distances1 = name_to_distances[e1]
            # ищем - есть ли для элемента e2 какой-то элемент который еще ближе?
            for d1, r1 in distances1:
                if r1 in selected:
                    continue

                # для всех элементов которые остались ищу еще другие
                is_best = 1
                for e2 in e1_sorted:
                    if e2 in selected or e2 == r1:
                        continue

                    distances2 = name_to_distances[e2]
                    for d2, r2 in distances:
                        if r2 in selected:
                            continue

                        # if r1!=r2:
                        if r1 == r2:
                            continue

                        if d2 < d1:
                            is_best = 0
                            logger.debug(
                                '    for e1 "%s" r1 "%s" with distances %s is not the best because r2 "%s" with distance %s is closer'
                                % (e1, r1, d1, r2, d2)
                            )
                            break

                    if not is_best:
                        break

                if is_best:
                    selected.append(r1)

                    distance_norm = d1
                    # min_word_len = max(    1,     min([len(r1), len(e1)])    )
                    # distance_norm = d1/min_word_len
                    # logger.debug('min_word_len %s %s, distance_norm %.3f'% (r1, min_word_len, distance_norm))
                    info = {
                        "element": r1,
                        "distance": d1,
                        #'distance_norm':distance_norm,
                    }
                    closest[e1] = info
                    break

    if otl:
        logger.debug("closest")
        show_dict(closest, "    ")
    return closest
