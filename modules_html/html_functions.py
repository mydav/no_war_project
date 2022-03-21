# -*- coding: utf-8 -*-

from modules import *
from modules_html.html_parsers import *

# import re, os
# from modules import *
# from BeautifulSoup import *
# from html_parsers import *
# #from text_functions import no_probely
# from modules.text_functions import *
# from modules.find_functions import *
# from modules.dict_functions import *
# from mofile_save_open import *
# from zlib import crc32
# import md5
# import hashlib

# from my_translit_ import *

logger = get_logger(__name__)


def no_html(s):
    """убиваем все HTML таги из строки, хтмл-сущности заменяем на пробелы"""
    # 	s = pravitj_tagi(s)
    parser = NoHtmlParser()
    try:
        parser.feed(s)
        r = parser.result
        parser.close()
    except Exception as er:
        logger.error(f"ERROR IN no_html FUNCTION {er=}")
        r = ""

    return r


def tag_search_edit(task):
    """вставляем нужный код сверху-снизу\впереди-после любого хтмл-елемента
	f_to = 'temp/done.txt'
	html = text_from_file('temp/task.txt')
	task = {
		'html':html,
		'path':'@class="eTitle"',
		'path':'@class="eMessage"',
		#'position':'top-before',
		'position':'bottom-before',
		#'position':'bottom-after',
		'inserting':'[INSERTED]',
		}
	res = tag_search_edit(task)
	text_to_file(res, f_to)"""

    html = task.get("html")
    path = task.get("path")
    positions = task.get("position").split("-")
    inserting = task.get("inserting")

    doc = lxml.html.document_fromstring(html)
    xp = ".//*[%s]" % path  # xp = './/*[@class="eTitle"]'
    # logger.debug(f"{xp=}")
    found = False
    for item in doc.xpath(xp)[:1]:
        # logger.debug(f"{r=} {item=}")
        found = tostring(item)
        # logger.debug(f"{found=}")
        if positions[0] == "top":
            if positions[1] == "before":
                replaced = inserting + found
            elif positions[1] == "after":
                pos = found.find(">")
                replaced = found[:pos] + inserting + found[pos:]
        elif positions[0] == "bottom":
            if positions[1] == "before":
                items = found.split("<")
                replaced = "<".join(items[:-1]) + inserting + "<" + items[-1]
            elif positions[1] == "after":
                replaced = found + inserting

        logger.debug(f"{replaced=}")

        html = html.replace(found, replaced)
    if found == False:
        wait_for_ok("CHECK, not found %s" % path)
    return html


def find_images(s):
    """возвращает все картинки (в tppabs значения)"""
    parser = FindImagesParser()
    parser.feed(s)
    parser.close()
    return parser.img_urls


def find_srcs(s):
    """возвращает все картинки (в tppabs значения)"""
    parser = FindSrcParser()
    parser.feed(s)
    parser.close()
    return parser.img_urls


def replace_bad_tags(s):
    """ заменяет разные вредные теги типа br', 'LI', 'li', 'DT', 'DD' и т.д. на нужные нам теги"""
    # 	parser = ReplaceBadTagsParser()
    # 	parser.feed(s)
    # 	parser.close()
    # 	return parser.result
    first = find_from_to_one("nahposhuk", "<page_content>", s)
    second = find_from_to_one("<page_content>", "</page_content>", s)
    third = find_from_to_one("</page_content>", "nahposhuk", s)
    parser = ReplaceBadTagsParser()
    parser.feed(second)
    parser.close()
    return (
        first
        + "\n<page_content>\n"
        + parser.result
        + "\n</page_content>\n"
        + third
    )


def replace_tags_2(text, tags={}):
    for tag in tags:
        tag_to = tags[tag]
        t0 = tag.lower()
        t1 = tag.upper()
        # 		logger.debug(f"{t0=}, {tag_to=}")
        text = text.replace("<%s" % (t0), "<%s" % tag_to).replace(
            "</%s>" % (t0), "</%s>" % tag_to
        )
    return text


def Leave_Tags_I_Want(s, valid_tags="", valid_attrs=""):
    """ заменяет разные вредные теги типа br', 'LI', 'li', 'DT', 'DD' и т.д. на нужные нам теги"""
    # 	logger.debug(f'opa1')
    s = s.replace("<br/>", "<br>")
    if valid_tags == "":
        valid_tags = (
            "h1",
            "h2",
            "h3",
            "h4",
            "b",
            "strong",
            "i",
            "em",
            "br",
            "p",
            "table",
            "tr",
            "td",
            "br",
            "span",
            "ul",
            "li",
        )  #'img',
    if valid_attrs == "":
        valid_attrs = (
            "cellspacing",
            "cellpadding",
            "width",
            "title",
            "name",
            "alt",
            "width",
            "height",
            "style",
        )
    parser = LeaveTagsIWantNew(valid_tags, valid_attrs)
    parser.feed(s)
    parser.close()
    return parser.result


def valid_tags(s):
    """ заменяет разные вредные теги типа br', 'LI', 'li', 'DT', 'DD' и т.д. на нужные нам теги"""
    # 	parser = ValidTagsParser()
    # 	parser.feed(s)
    # 	parser.close()
    # 	return parser.result

    first = find_from_to_one("nahposhuk", "<page_content>", s)
    second = find_from_to_one("<page_content>", "</page_content>", s)
    third = find_from_to_one("</page_content>", "nahposhuk", s)
    parser = ValidTagsParser()
    parser.feed(second)
    parser.close()
    return (
        first
        + "\n<page_content>\n"
        + parser.result
        + "\n</page_content>\n"
        + third
    )


def replace_images(s):
    """получает текст, в котором урлы абсолютные.
	эти урлы заменяем на мои урлы - картинки, которые я качал (как заменять-алгоритм я помню)"""
    # 	parser = ReplaceImagesParser()
    # 	parser.feed(s)
    # 	parser.close()
    # 	return parser.result

    first = find_from_to_one("nahposhuk", "<page_content>", s)
    second = find_from_to_one("<page_content>", "</page_content>", s)
    third = find_from_to_one("</page_content>", "nahposhuk", s)
    parser = ReplaceImagesParser()
    parser.feed(second)
    parser.close()
    return (
        first
        + "\n<page_content>\n"
        + parser.result
        + "\n</page_content>\n"
        + third
    )


def pravitj_tagi(s, from_encoding="cp1251"):
    """правит таги в тексте при помощи бьютифулсупа
	довольно быстро работает даже с большими файлами"""
    from BeautifulSoup import BeautifulSoup

    soup0 = BeautifulSoup(s, fromEncoding=from_encoding)
    s = soup0.prettify()
    # 	s = unicode(s, 'utf-8').encode('cp1251')
    return s


def only_words_(text, russian=False):
    """в уникоде - оставляем в тексте только слова"""
    if russian:
        rus = unicode("йцукенгшщзхъэждлорпавыфячсмитьбю", "cp1251")
        tokens = re.compile(r"\b[%s]+\b" % rus, re.UNICODE | re.I)
    else:
        tokens = re.compile(r"[\w']+", re.UNICODE)

    assert isinstance(text, unicode), "Text must be unicode"
    text = text.lower()  # делаем маленькими
    words = tokens.findall(text)
    return words


def html_normalize(text):
    """ф-я нормализации текста
	убирает все хтмл-форматирование и точки-запятые, и делает маленьким текст"""

    # 	убираем хтмл-таги + заменям спец-хтмл символы на пробел
    text = no_html(text)

    # 	оставляем в тексте только слова + делаем текст маленьким
    text = " ".join(only_words(text))

    return text


def get_local_url(url, sposob="md5"):
    """ф-я получает глобальный урл (обычно картинки), и заменяет его на мой локальный по этому алгоритму"""
    if sposob == "md5":
        return to_hash(url)
    elif sposob == "crc32":
        return str(abs(crc32(url))) + "_" + os.path.basename(url)
    else:
        logger.error("HAX - NE ZNAJU KAK DEKODIROVATJ. NEIZVESTNIJ SPOSOB.")


def to_hash_file(fname):
    """получить файл и посчитать его хеш - работает на файлах любых размеров
	https://stackoverflow.com/questions/3431825/generating-an-md5-checksum-of-a-file
	"""
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def to_hash_file_with_memory_error(f=""):
    """
		вываливается на больших файлах
		получить файл и посчитать его хеш
		https://stackoverflow.com/questions/3431825/generating-an-md5-checksum-of-a-file
	"""

    def file_as_bytes(file):
        with file:
            return file.read()

    return hashlib.md5(file_as_bytes(open(f, "rb"))).hexdigest()


def scrap(
    text,
    settings={
        "find_in": None,
        "split_with": None,
        "split_from_to": (1, -1),
        "find_what": None,
        "modify": None,
    },
):
    """получаем текст.
	и из него вытягиваем "чистую" информацию - все статьи, которые нам подходят, в один хтмл-файл. Т.е. скрапим.

	настройки говорят где искать (find_in) и что искать (find_what)
#	settings = {'find_in':('<table border="0" width="100%" cellspacing="0" cellpadding="5">', '<table border="0" width="100%" cellspacing="0" cellpadding="5">'), 'split_with':'</tr>', 'find_what':('tm=">', '</a>')}
	"""

    rezult = []

    start, end = settings["find_in"]
    grjazj = find_from_to_one(start, end, text)

    items = []
    if settings["split_with"] != None:
        items = grjazj.split(settings["split_with"])
        ot, do = settings["split_from_to"]
        if do == 0:
            if ot == 0:
                items = items[:]
            else:
                items = items[ot:]
        elif ot == 0:
            items = items[:do]

        else:
            items = items[ot:do]
    else:
        items.append(grjazj)

    # 	сначала действительно скраплю
    for item in items:
        small = {}
        for want in settings["find_what"]:
            start, end, tag = want
            small[tag] = find_from_to_one(start, end, item).strip()
        rezult.append(small)

    # 	а теперь модифицирую и возвращаю

    return modify_rezult(rezult, settings["modify"])


def get_a(page):
    soup = BeautifulSoup(page)
    links = soup("a")
    # 	logger.debug(f"{links=}")
    rez = []
    for link in links:
        # 		logger.debug(f"{link.attrs=}")
        if link.has_key("href"):
            # 			logger.debug(f"{link=}")
            # 			ankor = link.string#.encode('cp1251')
            ankor = find_from_to_one(">", "nahposhuk", str(link))
            ankor = ankor[:-4]
            href = link["href"].encode("cp1251", "ignore")
            rez.append([href, ankor])
    return rez


def do_abs_urls(html, url_ot, more={}):
    """сделать абсолютные урлы к ссылкам и к картинкам"""
    # 	images = find_images(html)
    # 	for im in images:
    # 		u_abs = url_abs(url_ot, im)
    ##		logger.debug(f"{im=}, {u_abs=}")
    global s
    # 	logger.debug(f"{s=}")
    # 	logger.debug(f"{html=}")
    local_images = more.get("local_images", False)
    domen = more.get("domen", "")

    viraz = r"""(<img\s+.*?src\s*=\s*(['"](.*?)['"]).*?>)"""
    # 	r = re.findall(viraz, html, re.I|re.DOTALL)
    # 	logger.debug(f"{r=}")
    # 	wait_for_ok()
    found = re.compile(viraz, re.I | re.DOTALL)
    html = found.sub(ucoz_edit_images, html)

    # 	размерчики для видео меняю
    html = (
        html.replace("<object>", '<object height="295" width="480">')
        .replace(
            "<embed ",
            '<embed height="295" width="480" allowfullscreen="true" allowscriptaccess="always" ',
        )
        .replace("</object>", "</object><br>")
    )
    return html


def prepare_absolute_a(text, more):
    # global task
    global more2
    more2 = more
    viraz = r"""(<a\s+.*?href\s*=(\s*['"](.*?)['"]).*?(?:>(.*?)</a|/)>)"""
    # 	r = re.findall(viraz, text, re.I|re.DOTALL)
    # 	show_list(r)
    # 	wait_for_ok()
    found = re.compile(viraz, re.I | re.DOTALL)
    text = found.sub(edit_absolute_a, text)

    return text


def edit_absolute_a(match):
    global more2
    # logger.debug(f"{more2=}")

    full = match.group(0)
    # logger.debug(f"{match=}")

    found_lapki_url = match.group(2)
    found_url = match.group(3)

    # logger.debug(f"{found_url=}")

    abs_url = url_abs(more2["u_from"], found_url)
    # logger.debug(f"{abs_url=}")

    r = full.replace(found_lapki_url, '"%s"' % abs_url)
    # logger.debug(f"{r=}")
    # wait_for_ok('check link')
    return r


def prepare_links(text):
    viraz = r"""(<a\s+.*?href\s*=(\s*['"](.*?)['"]).*?(?:>(.*?)</a|/)>)"""
    # 	r = re.findall(viraz, text, re.I|re.DOTALL)
    # 	show_list(r)
    # 	wait_for_ok()
    found = re.compile(viraz, re.I | re.DOTALL)
    text = found.sub(edit_one_link, text)

    return text


def edit_one_link(match):

    full = match.group(0)

    found_url = match.group(2)
    phrase = match.group(4)

    prepared = norm_phrase(kl(phrase))
    # 	logger.debug(f"{full=}")
    # 	logger.debug(f"{found_url=}")
    # 	uni(phrase)

    if (
        len(prepared) <= 3 or len(prepared) >= 50
    ):  # маленькие ссылочки (обычно в сносках они) вообще выбрасываю. И огромные тоже.
        return phrase

    r = full.replace(found_url, '"#%s"' % prepared)
    return r


def links_to_txt(text):
    viraz = r"""(<a\s+.*?href\s*=(\s*['"](.*?)['"]).*?(?:>(.*?)</a|/)>)"""
    # 	r = re.findall(viraz, text, re.I|re.DOTALL)
    # 	show_list(r)
    # 	wait_for_ok()
    found = re.compile(viraz, re.I | re.DOTALL)
    text = found.sub(one_link_to_txt, text)

    return text


def one_link_to_txt(match):

    full = match.group(0)

    found_url = match.group(2)
    phrase = match.group(4)
    return phrase


def get_h1(text, ot="<h1", do="<"):
    """
	получаем h1
	"""
    h1 = "|".join(find_from_to_all_tag(ot, do, text))
    h1 = h1.strip()
    return h1


def scrap_css_style_by_class_name(name="IbfkTd", text=""):
    ot = ".%s{" % name
    logger.debug(f"{ot=}")
    return find_from_to_one(ot, "}", text)


if __name__ == "__main__":
    special = "no_html"
    if special == "no_html":
        html = f"""<h1>title</h1><body>hello!</body>"""
        text = no_html(html)
        logger.info(f"{text=}")

    os._exit(0)

    t = 0
    t = 1
    if t:
        name = "IbfkTd"  # видимый
        name = "cTsG4"  # невидимый

        f = r"d:\kyxa\!code\!actual\google_addurl_selenium\data\!new_console\states_console\indexing_requested#2.html"
        text = text_from_file(f)
        logger.debug(scrap_css_style_by_class_name(name, text))
        os._exit(0)

    t = 1
    t = 0
    if t:
        f = r"d:\server\home\paint\www\uploads\e5c563d6695aaedbe239df26cf59265b.djvu"
        f = r"g:\!даше\!books - старые по развитию\Журнал Горизоны техники для детей\1963\GTD-1963-07.djvu"
        logger.debug(to_hash_file(f))
        logger.debug(to_hash_file_with_memory_error(f))
        os._exit(0)

    t = 0
    if t:
        # 	replace_images('123')
        page = """<a href="href">name1</a>
		<a href="http://google.com">name2</a><a href="http://depositfiles.com/files/xtl6oqz58" target="_blank">Скачать с <b>Depositfiles.com</b></a>
		"""
        rez = get_a(page)
        logger.debug(f"{rez=}")
