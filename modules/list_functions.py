from modules_23.list_functions import *
from modules.text_functions import to_hash
from operator import itemgetter
from functools import cmp_to_key
from random import shuffle
from collections import Counter
import time
import re
from modules.logging_functions import get_logger

logger = get_logger(__name__)


def multiply_list(myList):
    # Multiply elements one by one
    result = 1
    for x in myList:
        result = result * x
    return result


def flat(_list):
    """ [(1,2), (3,4)] -> [1, 2, 3, 4]
    [[1, 2], 3]) -> [1, 2, 3]
    """
    debug = True
    debug = False

    if debug:
        print(f"start with {_list}")
    lst = []
    for item in _list:
        if isinstance(item, str):
            value = [item]
        else:
            try:
                value = list(item)
            except Exception as er:
                value = [item]
        lst.append(value)
        if debug:
            print(type(item), item, value)

    if debug:
        print(f"final list: {lst}")
        print(f"final sum: {sum(lst, [])}")
    return sum(lst, [])

    return sum([list(item) for item in _list], [])


def unique(lst0=[]):
    return list(set(lst0))


def unique_with_order(lst0=[]):
    lst_hash = set()
    lst = []
    for item in lst0:
        if item not in lst_hash:
            lst_hash.add(item)
            lst.append(item)
    return lst


def leave_unique_from_list_for_hashfunc(
    lst: list, key: str = None, hash_func: callable = None
):
    """

    :param lst:
    :param key:
    :param hash_func:
    :return:
    """
    filtered = []
    hashes = set()
    for _ in lst:
        if key:
            value = _[key]
        else:
            value = _
        if hash_func:
            value = hash_func(value)
        if value in hashes:
            continue

        hashes.add(value)
        filtered.append(_)
    return filtered


def unique_with_order_hashed(lst0=[]):
    lst_hash = set()
    lst = []
    for item in lst0:
        h = to_hash(item)
        if h not in lst_hash:
            lst_hash.add(h)
            lst.append(item)
    return lst


def clear_list(lst: list, bad_starts="") -> list:
    if isinstance(lst, str):
        lst = lst.split("\n")

    items = [_.strip() for _ in lst if _.strip()]
    if bad_starts:
        # items = [_ for _ in items if not _[0] in bad_starts]
        good = []
        for _ in items:
            is_bad = False
            for bad in bad_starts:
                if _.startswith(bad):
                    is_bad = True
                    break
            if not is_bad:
                good.append(_)
        items = good[:]

    return items


def sort_nicely(l):
    """ Sort the given list in the way that humans expect.
	"""
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split("([0-9]+)", key)]
    l.sort(key=alphanum_key)


def split_chunk(l, n):
    """Yield successive n-sized chunks from l."""
    n = int(n)
    for i in range(0, len(l), n):
        yield l[i : i + n]


def split_list(l, n):
    """Yield successive n-sized chunks from l."""
    chunks = split_chunk(l, n)
    return [list(_) for _ in chunks]


def list_minus_list(list1, list2, progress_bar=5):
    """из списка1 отнимаем список2
    2015.07 - усложнил, чтобы работать с гигантскими списками"""
    fun = "list_minus_list"

    want_progress = 0
    if len(list1) > 1000 * 10:
        want_progress = 1

    if want_progress:
        print(f"[{fun}:")

    f_ = to_hash  # hash func

    hashes2 = set([f_(_) for _ in list2])

    rez = []
    for i, _ in enumerate(list1):
        if want_progress and i % 1000 == 0:
            print(len(list1) - i, end="")
        h = f_(_)
        if h in hashes2:
            continue
        rez.append(_)

    if want_progress:
        print("have %d items after %s" % (len(rez), fun))
    return rez


def shuffle_and_sort_list_by_priority(lst, columns=["-priority"]):
    new_list = lst[:]
    # пустые отбросили
    if not new_list:
        return new_list

    shuffle(new_list)
    # logger.debug(f"{new_list=}")

    # если не словарь - подготовим словарь
    item = new_list[0]
    if isinstance(item, dict):
        new_list = sort_list_with_dicts(new_list, columns=columns)
    else:
        hash_to_element = {}
        dicts = []
        for element in new_list:
            h = to_hash(str(element))
            _ = {
                "hash": h,
            }
            for c in columns:
                if c[0] == "-":
                    c = c[1:]
                _[c] = getattr(element, c, "")
            # logger.debug(f"created {_} from {element}")
            hash_to_element[h] = element
            dicts.append(_)
        dicts = sort_list_with_dicts(dicts, columns=columns)
        new_list = [hash_to_element[_["hash"]] for _ in dicts]

    return new_list


def sort_list_with_dicts(items, columns=[]):
    """
        idea: https://stackoverflow.com/questions/1143671/python-sorting-list-of-dictionaries-by-multiple-keys
        a = sort_list_with_dicts(b, ['-Total_Points', 'TOT_PTS_Misc'])

        for Python 3:
            https://stackoverflow.com/questions/2531952/how-to-use-a-custom-comparison-function-in-python-3


    """
    type_dct = type({})
    # columns0 = [col[1:] for col in columns]
    columns0 = columns[:]
    columns0 = []
    for c in columns:
        if c[0] == "-":
            c = c[1:]
        columns0.append(c)
    # show_list(columns0)
    # wait_for_ok()

    items2 = []
    for item in items:
        # if type(item) != type_dct:
        #     continue

        for col in columns0:
            if col not in item:
                item[col] = ""
        items2.append(item)

    from operator import itemgetter

    comparers = [
        (
            (itemgetter(col[1:].strip()), -1)
            if col.startswith("-")
            else (itemgetter(col.strip()), 1)
        )
        for col in columns
    ]

    def comparer(left, right):
        for fn, mult in comparers:
            result = cmp(fn(left), fn(right))
            if result:
                return mult * result
        else:
            return 0

    # return sorted(items2, cmp=comparer)
    return sorted(items2, key=cmp_to_key(comparer))


def cmp(x, y):
    """
    Replacement for built-in function cmp that was removed in Python 3

    Compare the two objects x and y and return an integer according to
    the outcome. The return value is negative if x < y, zero if x == y
    and strictly positive if x > y.

    https://portingguide.readthedocs.io/en/latest/comparisons.html#the-cmp-function
    """

    return (x > y) - (x < y)


def sort_list_with_dicts_2(items, columns):
    """
    Idea: https://stackoverflow.com/questions/1143671/how-to-sort-objects-by-multiple-keys-in-python
    """
    comparers = [
        (
            (itemgetter(col[1:].strip()), -1)
            if col.startswith("-")
            else (itemgetter(col.strip()), 1)
        )
        for col in columns
    ]

    def comparer(left, right):
        comparer_iter = (
            cmp(fn(left), fn(right)) * mult for fn, mult in comparers
        )
        return next((result for result in comparer_iter if result), 0)

    return sorted(items, key=cmp_to_key(comparer))


def leave_unique_items_for_key(bets=[], key="", default_value=None, reason=""):
    """
    Вылазят неуникальные ставки от разных людей, а иногда и в том же человеке (например перезапустил и он опять ту же ставку сделал)
    Проверяю - если за 5 минут до того была такая ставка значит пропускаю
    """
    fun = "leave_unique_bets_for_key"
    t_start = time.time()
    filtered = []
    hashes = set()
    for _ in bets:
        # hash = _.get(key, to_hash(_))
        hash = _.get(key, None)
        if hash in hashes:
            continue

        hashes.add(hash)
        filtered.append(_)
    duration = time.time() - t_start
    logger.debug(
        f"[{fun} {reason=} {key=} {len(bets)} items... unique {len(filtered)}/{len(bets)} bets in {duration:.2f} seconds]",
    )
    return filtered


def get_counter_for_key_in_list(items: list, name="", default_value=""):
    keys = [_.get(name, default_value) for _ in items]
    return dict(Counter(keys))


def get_unique_elements_for_key(bets, name, default_value="", debug=False):
    items = list(
        set(
            get_elements_for_key(
                bets, name, default_value=default_value, debug=debug
            )
        )
    )
    if debug:
        print(f"{len(items)} {name} , {items=}")
    return items


def get_elements_for_key(bets, name, default_value="", debug=False):
    items = [_.get(name, default_value) for _ in bets]
    if debug:
        print(f"{len(items)} {name} , {items=}")
    return items


def is_sublist(child: list, parent: list):
    r = set(child).issubset(set(parent))
    # print(f"is_sublist={r} for {child=} and {parent=}")
    return r


def sort_list_like_other_list(lst1, lst2, reverse=False, sort_first_list=True):
    """
        сортировать один список как другой (lst2 уже сортированный)
    """
    lst_base = lst1[:]
    if sort_first_list:
        lst_base.sort()

    to_sort = []
    elements_not_in_lst2 = []
    for num_item, item in enumerate(lst_base, 1):
        try:
            num = lst2.index(item)
        except Exception as er:  # может и не быть в списке2 нужных элементов
            num = len(lst_base) + num_item
            pass
            # continue
        to_sort.append([num, item])
    to_sort.sort()
    # print(to_sort)

    if reverse:
        to_sort.reverse()

    names = [_[-1] for _ in to_sort]
    return names


class infinite_list:
    """
        бесконечный список хочу
    """

    def __init__(self, lst, want_shuffle=0):
        self.want_shuffle = want_shuffle
        self.list = lst[:]
        self.current_element = None

        self.current_list = []  # тут собираем текущие элементы
        self.setup_current_list()
        self.cnt_get = 0

    def get(self):
        self.cnt_get += 1
        if len(self.current_list) == 0:
            self.setup_current_list()
        self.current_element = self.current_list.pop(0)
        return self.current_element

    def get_sublist(self, size=10):
        lst = []
        for i in range(size):
            element = self.get()
            lst.append(element)
        return lst

    def setup_current_list(self):
        self.current_list = self.list[:]
        if self.want_shuffle:
            shuffle(self.current_list)

    def __repr__(self):
        m = f"infinite_list: size {len(self.list)}, got {self.cnt_get} times"
        return m


def splist(lst=[]):
    # print("lst %s =%s" % (type(lst), lst))
    if lst:
        return "%s" % ", ".join(lst)
    else:
        return ""


# def plist(lst=[]):
#     return "[%s]" % splist(lst)


def slitj_list_listov(list_listov, want_nepustie_only=1, unique=0):
    """получаем [ [],[],[],[] ] и возвращаем один большой [] из значений в маленьких"""
    rezult = []
    for kusok in list_listov:
        if type(kusok) != list:
            kusok = [kusok]
        if len(kusok) > 0:
            for i in kusok:
                if unique and i in rezult:
                    continue
                rezult.append(i)

    # 	print type(rezult), rezult

    if want_nepustie_only == 1:
        non_empty = []
        for i in rezult:
            if i != "":
                non_empty.append(i)
        return non_empty
    else:
        return rezult


def list_peretyn(list1, list2):
    """показывает перетын двух списков"""
    s1 = set(list1)
    s2 = set(list2)
    return list(s1 & s2)


def check_value_in_white_black_list(value=None, white_list=[], black_list=[]):
    """
    если белый список - должно быть в белом
    если черный - НЕ должно быть в черном
    иначе - входит
    """
    if value is None:
        return True
    good = True
    if white_list and value not in white_list:
        good = False
    if good:
        if black_list and value in black_list:
            good = False
    return good


if __name__ == "__main__":
    special = "old"
    special = "flat"
    special = "sort_list_like_other_list"
    special = "leave_unique_from_list_for_hashfunc"
    special = "shuffle_and_sort_list_by_priority"

    if not special:
        logger.error(f"empty special")

    elif special == "shuffle_and_sort_list_by_priority":
        from modules.dict_functions import Bunch

        lst = [
            {"priority": 1, "value": 1,},
            {"priority": 10, "value": "MAIN",},
            {"priority": 1, "value": 2,},
            {"priority": 1, "value": 3,},
            {"priority": 1, "value": 4,},
        ]
        lst = [Bunch(_) for _ in lst]
        step = 0
        while True:
            step += 1
            new_list = shuffle_and_sort_list_by_priority(
                lst, columns=["-priority"]
            )
            logger.debug(f"{new_list=}")
            if isinstance(new_list[0], dict):
                logger.info(f"{step} {[_['value'] for _ in new_list]}")
            else:
                logger.info(
                    f"{step} {[getattr(_, 'value') for _ in new_list]}"
                )
            os._exit(0)

    elif special == "leave_unique_from_list_for_hashfunc":

        def hash_func(txt):
            return txt[1]

        el1 = {"x": 1, "test": "f1"}
        el2 = {"x": 2, "test": "f2"}
        key = "test"

        t = 1
        if t:
            el1 = "f1"
            el2 = "f2"
            key = None

        lst = [el1, el2]

        r = leave_unique_from_list_for_hashfunc(
            lst, key=key, hash_func=hash_func
        )
        print(r)

    elif special == "sort_list_like_other_list":
        lst1 = [238, 1, 5, 4]
        lst2 = [238, 1, 2]
        lst3 = sort_list_like_other_list(lst1, lst2)
        print(lst3)

    elif special == "flat":
        # print(flat([[1, 2], [3, 4]]))
        print(flat([[1, 2], [3]]))
        print(flat([[1, 2], 3]))
        print(flat(["ab", 1, 2, [3, 4]]))
        # wait_for_ok()

    if special == "old":
        print(list_minus_list([1, 3, 2, 2, 5], [1, 2, 3]))

        lst = [
            {"title": "title 1", "value": 3,},
            {"title": "title 2", "value": 1,},
            {"title": "title 3", "value": 1.5,},
        ]
        new_list = sort_list_with_dicts(lst, ["-value"])
        # new_list = sort_list_with_dicts_2(lst, ["-value"])
        print(new_list)
