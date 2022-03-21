import sys
from modules.logging_functions import *

logger = get_logger(__name__)

if sys.version_info[0] >= 3:
    unicode = str


def find_from_to_one_in_tag(start, text="", stop="<"):
    """
	в таком:
		class="sip-MarketGroupButton_Text ">Fulltime Result</div>
	ищем по
		start = 'class="sip-MarketGroupButton_Text'
	"""
    t = find_from_to_one(start, stop, text)
    # print(t)
    found = find_from_to_one(">", "nahposhuk", t).strip()
    return found


def find_from_to_one(from_text, to_text, text, coding="utf-8", not_found=""):
    """получаем шаблон из от, до. Возвращаем одно найденное значение
    если from_text 'nahposhuk', то исчем с самого начала. """
    # logger.debug(str([type(text), type(from_text)]))
    num_from = text.find(from_text)
    if from_text == "nahposhuk":
        num_from = 0
        i_want = text
    else:
        if num_from == -1:
            return not_found
        else:
            i_want = text[num_from + len(from_text) :]

    if to_text == "nahposhuk":
        return i_want

    num_to = i_want.find(to_text)
    if num_to == -1:
        return not_found

    i_want = i_want[:num_to]
    return i_want


def untag(from_text, tag="a"):
    return find_from_to_one(f"<{tag}>", f"</{tag}>", from_text)


def found_atLeastOne(phrases=[], p="", debug=False):
    for phrase in phrases:
        if phrase in p:
            return True
        else:
            if debug:
                logger.debug("no phrase %s in page" % phrase)
    return False


def found_all(phrases=[], p=""):
    for phrase in phrases:
        if phrase not in p:
            return False
    return True


if __name__ == "__main__":
    text = "hello world and"
    text = b"hello world and"
    text_ot = "o"
    text_do = "and"
    t = find_from_to_one(text_ot, text_do, text)
