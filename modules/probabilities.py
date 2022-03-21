# -*- coding: utf-8 -*-

import random

try:
    from html_functions import to_hash
except Exception as er:
    from modules.text_functions import to_hash


def choose1d(P, g=random.Random()):
    """P - список из вероятностей, в сумме должно быть 1"""
    U = g.random()
    #    random.seed(1)
    #    print '    ', U
    sumP = 0.0
    for j in range(len(P)):
        sumP += P[j]
        if U < sumP:
            break
    return j


def probability_list_value(lst=[]):
    """probability_list = [
    [dct1, 25],
    [dct2, 15],
    ]
        surebet = probability_list_value(probability_list)

    :param lst:
    :return:
    """
    probability_dict = {}
    hash_to_item = {}
    for item, probability in lst:
        h = to_hash(item)
        hash_to_item[h] = item
        probability_dict[h] = probability
    # print(probability_dict)
    found_hash = probability_dict_value(probability_dict)
    return hash_to_item[found_hash]


def probability_dict_value(dct0):
    """получаем словарь с вероятностями (ключи - символы, значения вероятности, сумма вероятностей==1), и возвращаем случайный символ исходя из этих вероятностей"""
    dct = probabilyze_dict(dct0)

    values = list(dct.keys())
    probabilities = list(dct.values())
    # print(f"{values=} {probabilities=}")
    next = choose1d(probabilities)  # 0..3

    return values[next]


def probabilyze_dict(dct):
    """получаем словарь, ключи - символы, значения - цифровые значения. Возвращаем словарь с вероятностями (вероятности-по этим значениям)"""
    keys = list(dct.keys())
    values = list(dct.values())
    new_values = probabilyze_lst(values)
    new_dct = {}
    for i in range(len(keys)):
        new_dct[keys[i]] = new_values[i]
    #    print keys, values
    return new_dct


def probabilyze_lst(lst):
    """пробабилизируем список - получаем список значений, и делаем все пропорционально так чтобы сумма его была 1"""
    suma = float(sum(lst))
    if not suma:  # для вероятности 0
        suma = 0.01
    koef = 1 / suma
    new_lst = [koef * i for i in lst]
    return new_lst


def select_position_like_human(cnt_elements=10, possible_positions={}):
    """
        выбираем позицию как человек
    """
    fun = "select_position_like_human"
    cnt_fixed_positions = 3  # я зависксировал 3 позиции

    if possible_positions == {}:
        possible_positions = {
            1: 40,  # вероятность клика по первой ссылке в выдаче 40%
            2: 30,
            3: 20,
            "other": 10,
        }

    max_position = cnt_elements
    max_other = cnt_elements - cnt_fixed_positions

    position = probability_dict_value(possible_positions)
    # position = 'other'
    if position == "other":
        if max_other > 0:
            # берем рандомный из тех что остались(0-max_other)
            position = (
                cnt_fixed_positions + 1 + random.choice(range(max_other))
            )

        else:
            position = max_position

    print(
        "[%s selected position %s/%s using probabilities %s]"
        % (fun, position, cnt_elements, possible_positions)
    )

    position = min(max_position, position)
    return position


if __name__ == "__main__":
    special = "probability_list_value"
    if special == "probability_list_value":
        lst = [
            [{"num": 1,}, 10],
            [{"num": 2,}, 5],
        ]
        #    получить значение исходя из вероятностного словаря
        checking = {}
        for i in range(1000):
            val = probability_list_value(lst)
            val_str = str(val)
            # print(val)
            #        val = choose1d(lst)
            if val_str not in checking:
                checking[val_str] = 0
            checking[val_str] += 1

        print(checking)
        os._exit(0)
    t = 1
    t = 0
    if t:
        items = range(100)
        for cnt in items:
            position = select_position_like_human(cnt)
            print("cnt %s, position %s" % (cnt, position))
        os._exit(0)

    #    P = [0.7, 0.1, 0.1, 0.1]
    #    dict_verojatnostej = {'a':0.7, 'b':0.1, 'c':0.1, 'd':01}
    #
    #    count_rezults = {}
    ##
    #    for i in range(10000):
    ##        next = choose1d(P)  #    просто выдаем случайное значение исходя из вероятностей
    #        next = probability_dict_value(dict_verojatnostej)#    случайное значение из словаря
    #
    ##        print next
    #        if not count_rezults.has_key(next):
    #            count_rezults[next] = 0
    #        count_rezults[next]+=1
    #
    #    print count_rezults

    #    как уменьшать списки и словари
    lst = [0.50, 8, 1.01, 0, 20]
    lst = probabilyze_lst(lst)
    #    print lst

    dct = {"a": 0.50, "b": 8, "c": 1.01, "d": 0, "e": 20}
    dct = probabilyze_dict(dct)

    tlds_stat = {
        "ucoz.ru": 47,
        "at.ua": 46,
        "3dn.ru": 14,
        "ucoz.ua": 9,
        "my1.ru": 7,
        "do.am": 4,
        "moy.su": 6,
        "clan.su": 17,
        "ucoz.com": 10,
        "ucoz.net": 3,
    }
    dct = probabilyze_dict(tlds_stat)

    #    получить значение исходя из вероятностного словаря
    checking = {}
    for i in range(1000):
        val = probability_dict_value(dct)
        print(val)
        #        val = choose1d(lst)
        if not val in checking:
            checking[val] = 0
        checking[val] += 1

    print(checking)
