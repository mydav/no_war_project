from lxml import html as lxml_html
from lxml import etree as lxml_etree
from itertools import chain
from lxml.html.clean import clean_html, Cleaner
from modules.file_functions import text_to_file
from modules.text_functions import find_from_to_one
from typing import List
from modules.urls import unquote
import logging
import re
from bs4 import BeautifulSoup
from html import unescape as html_unescape
from modules.text_functions import no_probely


logger = logging.getLogger(__name__)


def xpath_to_attribute(
    xpath: str,
    attribute: str,
    dom_tree: lxml_html.HtmlElement,
    return_type: str = "list",
):
    return xpath_to_attributes(xpath, attribute, dom_tree, return_type="first")


def xpath_to_attributes(
    xpath: str,
    attribute: str,
    dom_tree: lxml_html.HtmlElement,
    return_type: str = "list",
):
    elements = xpath_to_elements(xpath, dom_tree, return_type="list")
    # print(f"{len(elements)} elements: {elements=}")
    attributes = []
    for element in elements:
        attr = element.get(attribute)
        # print(element, attr)
        if attr:
            attributes.append(attr)

    if return_type == "list":
        return attributes

    elif return_type == "first":
        if len(attributes):
            return attributes[0]
        else:
            return None
    else:
        raise Exception(f"unknown {return_type=}")


def xpath_to_element(xpath: str, dom_tree: lxml_html.HtmlElement):
    return xpath_to_elements(
        xpath=xpath, dom_tree=dom_tree, return_type="first"
    )


def xpath_to_elements(
    xpath: str, dom_tree: lxml_html.HtmlElement, return_type: str = "list"
):
    elements = dom_tree.xpath(xpath)

    if return_type == "list":
        return elements
    elif return_type == "first":
        if len(elements):
            return elements[0]
        else:
            return None
    else:
        raise Exception(f"unknown {return_type=}")


def xpath_to_textContent(
    xpath: str, dom_tree: lxml_html.HtmlElement, return_type: str = "list"
):
    return xpath_to_textContents(
        xpath=xpath, dom_tree=dom_tree, return_type="first"
    )


def xpath_to_textContents(
    xpath: str,
    dom_tree: lxml_html.HtmlElement,
    return_type: str = "list",
    adding: str = "text_content",
):
    fun = "xpath_to_textContents"
    items = []
    elements = dom_tree.xpath(xpath)
    for elem in elements:
        if adding == "string_content":
            try:
                value = elem.string_content()
            except Exception as er:
                print(f"     ERROR {fun}: {er=}")
                continue
        elif adding == "text_content" or 1:
            value = elem.text_content()

        items.append(value)
        # if return_type == "first":
        #     break

    if return_type == "list":
        return items
    elif return_type == "first":
        if len(items):
            return items[0]
        else:
            return ""
    else:
        raise Exception(f"unknown {return_type=}")


def xpath_to_parentElement(xpath: str, dom_tree: lxml_html.HtmlElement):
    element = xpath_to_element(xpath, dom_tree)
    if element is None:
        return None

    parent = element.getparent()

    t = 1
    t = 0
    if t:
        print(parent)
        print(element_to_string(parent))

    return parent


def xpath_to_childrenHtml(xpath: str, dom_tree: lxml_html.HtmlElement):
    elements = dom_tree.xpath(xpath)
    if not elements:
        return ""
    elem = elements[0]
    answer = lxml_etree.tostring(
        elem, pretty_print=True
    )  # , encoding='unicode'

    node = lxml_etree.fromstring(answer)
    children = stringify_children(node)
    return children


def stringify_children(node, encoding="unicode"):
    res = "".join(
        chunk
        for chunk in chain(
            (node.text,),
            chain(
                *(
                    (
                        lxml_etree.tostring(
                            child, with_tail=False, encoding=encoding
                        ),
                        child.tail,
                    )
                    for child in node.getchildren()
                )
            ),
            (node.tail,),
        )
        if chunk
    )
    res = res.strip()
    return res


def stringify_children2(node, encoding: str = "utf-8"):
    """Given a LXML tag, return contents as a string

       html = "<p><strong>Sample sentence</strong> with tags.</p>"
       node = lxml.html.fragment_fromstring(html)
       extract_html_content(node)
       "<strong>Sample sentence</strong> with tags."
    """
    if node is None or (len(node) == 0 and not getattr(node, "text", None)):
        return ""
    node.attrib.clear()
    opening_tag = len(node.tag) + 2
    closing_tag = -(len(node.tag) + 3)
    res = lxml_html.tostring(node)[opening_tag:closing_tag]
    res = res.decode(encoding)
    return res


def string_to_element(html):
    if html.strip() == "":
        root = lxml_html.fromstring("<empty></empty>")
    else:
        root = lxml_html.fromstring(html)
    return root


def element_to_string(element, encoding="unicode", pretty_print=True):
    """
        If you tostring lxml dom is HTML, you can use

        etree.tostring(html_dom, method='html')
        to prevent self-closing tag like <a />
    """
    if element is None:
        return ""

    method = "html"
    method = "xml"
    html = lxml_etree.tostring(
        element, encoding=encoding, pretty_print=pretty_print, method=method
    )

    if method == "xml":
        html = xml_to_correct_html(html)
    return html


def pretty_html(html: str = "") -> str:
    if html.strip() == "":
        return ""

    document_root = lxml_html.fromstring(html)
    pretty = element_to_string(
        document_root, encoding="unicode", pretty_print=True
    )
    # pretty = strip_similar_startFinish_tags(pretty)
    return pretty


def fix_broken_html(html: str = "", encoding="unicode") -> str:
    tree = lxml_html.fromstring(html)
    fixed = lxml_etree.tostring(tree, pretty_print=True, encoding=encoding)
    return fixed


def my_clean_html(html: str = "", safe_attrs=["href", "src", "class"]) -> str:
    if html.strip() == "":
        return html

    # html = fix_broken_html(html)

    # cleaned = clean_html(html)    # не хватает управления

    cleaner = Cleaner(safe_attrs=safe_attrs)
    try:
        cleaned = cleaner.clean_html(html)
    except Exception as er:
        cleaned = ""

    cleaned = pretty_html(cleaned)

    cleaned = change_google_links_to_site_links(cleaned)

    cleaned = leave_only_allowed_classes(cleaned)

    return cleaned


def leave_only_allowed_classes(html: str, allowed: list = None) -> str:
    """
    С гугля парсю, и оставляю только некоторые классы которые сам прописал

    """
    if allowed is None:
        allowed = ["Ss2Faf", "w8qArf", "kno-vrt-t", "WTbp9e", "thumb"]

    debug = True
    debug = False
    new_items = []

    delim = 'class="'
    items = html.split(delim)
    new_items.append(items[0])
    for num, item in enumerate(items[1:], 1):
        if debug:
            print(f"{num}/{len(items)} {item=}")
        classes = find_from_to_one("nahposhuk", '"', item)
        after = find_from_to_one('"', "nahposhuk", item)
        if debug:
            print(f"{classes=}")
            print(f"{after=}")

        old_classes = classes.split(" ")
        new_classes = [_ for _ in old_classes if _ in allowed]

        classes_str = " ".join(new_classes)
        new_items.append(f'{classes_str}"{after}')

    # print(new_items)
    new_html = delim.join(new_items)
    new_html = new_html.replace(' class=""', "")
    return new_html


def change_google_links_to_site_links(html: str = "") -> str:
    """
     <span><a href="/search?lr=lang_en&amp;hl=en&amp;q=crow+length&amp;stick=H4sIAAAAAAAAAOPgE-LVT9c3NExKNjNJzy1L0tLKTrbST8rMz8lPr9TPL0pPzMsszo1PzkksLs5My0xOLMnMz7PKSc1LL8lYxMqdXJRfrgDhAQA_CGXjSwAAAA&amp;sa=X&amp;ved=2ahUKEwiV07TA873qAhXdxzgGHfVWAHAQ6BMoADACegQIDBAC">
    
    """
    debug = False

    new_items = []

    delim = 'href="'
    items = html.split(delim)
    new_items.append(items[0])
    for num, item in enumerate(items[1:], 1):
        if debug:
            print(f"{num}/{len(items)} {item=}")
        url = find_from_to_one("nahposhuk", '"', item)
        after = find_from_to_one('"', "nahposhuk", item)
        if debug:
            print(f"{url=}")
            print(f"{after=}")
        new_url = url
        if url.startswith("/search?"):
            q = find_from_to_one("&amp;q=", "&amp;", url)
            q_phrase = unquote(q)
            # new_url = f"/{q}/"
            new_url = f"[[key_to_url {q_phrase}]]"
            if debug:
                print(f"{q_phrase=} {new_url=}")
        new_items.append(f'{new_url}"{after}')
    # print(new_items)
    new_html = delim.join(new_items)
    return new_html


def strip_similar_startFinish_tags(html: str) -> str:
    """To to use Cleaner, lxml.html without returning div tag.

    https://stackoverflow.com/questions/21420922/how-to-use-cleaner-lxml-html-without-returning-div-tag
    """
    html = html.strip()
    # print(f"{html=}")
    tags_to_strip = ["p", "div"]
    step = 0
    while True:
        step += 1
        if not tags_to_strip:
            break
        tag = tags_to_strip.pop()

        html = html.strip()
        start = f"<{tag}>"
        finish = f"</{tag}>"
        found_finish = html[-len(finish) :]
        # print(
        #     f"{step=} check {tag=} {start=} {html.startswith(start)} {found_finish=}, {finish=}"
        # )
        if html.startswith(start) and found_finish == finish:
            html = html[len(start) : -len(finish)]
            # tags_to_strip.append(tag)

    return html


def element_to_file(
    element: lxml_html.HtmlElement, f_to: str = "temp/images.html"
) -> None:
    text = lxml_etree.tostring(element)
    text_to_file(text, f_to)


def remove_texts_with_xpaths(html, xpaths: List[str]):
    tree = lxml_html.fromstring(html)
    tree = remove_elements_with_xpaths(tree, xpaths)
    new_html = element_to_string(tree)
    return new_html


def remove_texts_with_xpath(html, xpath):
    return remove_texts_with_xpaths(html, [xpath])


def remove_elements_with_xpaths(root, xpaths: List[str]):
    for xpath in xpaths:
        root = remove_elements_with_xpath(root, xpath)
    return root


def remove_elements_with_xpath(root, xpath: str = './/h2[text()="Hello"]'):
    step = 0
    while True:
        step += 1
        element = xpath_to_element(xpath, root)
        # print(f"{step=}, {element=}")

        if element is None:
            break

        element.getparent().remove(element)
    return root


def change_googleTravel_links_to_site_links(html=""):
    """
    Меняю на нормальный ключ ссылку гугля или любую другую ссылку
            <div class="Z1hOCe">
              <div class="zloOqf PZPZlf">
                <span class="w8qArf"><a class="fl" href="/common+raven+scientific+name/">Scientific name</a>: </span>
                <span class="LrzXr kno-fv">Corvus corax</span>
              </div>
            </div>
    """
    fun = "change_googleTravel_links_to_site_links"
    debug = True
    debug = False

    root = string_to_element(html)

    xpath = ".//a"
    xpath = '//div[@class="kno-vrt-t"]/a'
    nodes = root.xpath(xpath)

    replaces = {}
    for num, node in enumerate(nodes, 1):  # root is the ElementTree object
        href = node.get("href")
        if (
            href
            and href.startswith("/")
            and not href.startswith("//")
            and not "key_to_url" in href
        ):
            if debug:
                print("   ", node, href, node.text_content())

            new_node_id = f"__ReplaceHref_id_{num}__"
            node.set("href", new_node_id)

            key = node.text_content().strip()
            new_url = f"[[key_to_url {key}]]"
            replaces[new_node_id] = new_url

    html = element_to_string(root)
    # print(html)

    if debug:
        print(f"{fun}: {replaces=}")

    for old, new in replaces.items():
        if old not in html:
            logger.error(f"{fun}: no {old=}")

        html = html.replace(old, new)

    return html


def delete_empty_tags(html: str = "", tags=None) -> str:
    """
    удаляем:
    1:
        <div/>

    2:
        <div>
            </div>

    """
    debug = True
    debug = False

    if tags is None:
        tags = ["div", "span"]

    tags_txt = "|".join(tags)

    deleting = [
        f"(?is)<\s*({tags_txt})\s*/>",  # <div />
    ]
    for tag in tags:
        exp = f"(?is)<\s*{tag}\s*>\s*</{tag}>"  # <div> </div>
        deleting.append(exp)

    step = 0
    while deleting:
        step += 1
        html0 = html
        exp = deleting.pop()
        exp_replace = r""

        if debug:
            print(f"{step=} {exp=}")
            parts = re.findall(exp, html)
            pprint(parts)

        html = re.sub(exp, exp_replace, html)

        if html0 != html:
            deleting.append(exp)

    return html


def minimize_self_closing_tags(html: str = "") -> str:
    """
     Удаляем закрывающий таг там, где нужно для html
        < base href='probel' /> ->
            < base href='probel' >
        <hr/>
    """

    debug = True
    debug = False

    tags = get_self_closing_tags("|")
    exp = f"(?is)<\s*({tags})([^>]*)/\s*>"
    exp_replace = r"<\1\2>"

    if debug:
        print(f"{exp=}")
        parts = re.findall(exp, html)
        pprint(parts)

    html = re.sub(exp, exp_replace, html)
    return html


def change_keyToUrl_to_text(html: str = "") -> str:
    """
        # Заменяем урлы на просто текст: <a href="[[key_to_url{from=also_ask} Что лучше пальто из шерсти или кашемира?]]">Что Лучше Пальто Из Шерсти Или Кашемира?</a> -> <b>Что Лучше Пальто Из Шерсти Или Кашемира?</b>
    """
    debug = True
    debug = False

    exp = f'(?is)<a href="\[\[key_to_url.*?">(.*?)<\/a>'
    exp_replace = r"<\1\2>"
    exp_replace = r"<b>\1</b>"

    if debug:
        print(f"{exp=}")
        parts = re.findall(exp, html)
        print(f" have {len(parts)} parts")
        pprint(parts)

    html = re.sub(exp, exp_replace, html)
    return html


def xml_to_correct_html(html: str = "") -> str:
    """.tostring(method=html) коцаент атрибуты  - все ескейпит

    Поэтому я делаю method=xml, а потом опять привожу к html

    """
    html = delete_empty_tags(html)
    html = expand_self_closing_tags(html)
    html = minimize_self_closing_tags(html)
    return html


def expand_self_closing_tags(html: str = "") -> str:
    """.tostring(method=html) коцаент атрибуты  - все ескейпит

    Поэтому я делаю method=xml, а потом опять привожу к html

    """
    debug = True
    debug = False

    tags = get_self_closing_tags("|")
    exp = f"(?is)<(?!{tags})([a-z|A-Z|_|\-|:|0-9]+)([^>]*)/>"
    exp_replace = r"<\1\2></\1>"
    parts = re.findall(exp, html)
    if debug:
        print(f"{exp=}")
        pprint(parts)
    html = re.sub(exp, exp_replace, html)

    return html


def get_self_closing_tags(delim=None):
    tags = "area|base|br|col|command|embed|hr|img|input|keygen|link|meta|param|source|track|wbr".split(
        "|"
    )
    if delim:
        tags = delim.join(tags)
    return tags


def remove_html_tags_beautifulsoup(html):
    features = "lxml"
    soup = BeautifulSoup(html, features=features)
    text = soup.get_text()
    return text


def remove_html_tags_nltk(html):
    """
    Copied from NLTK package.
    Remove HTML markup from the given string.

    :param html: the HTML string to be cleaned
    :type html: str
    :rtype: str
    """

    """
    Что нужно сделать отдельным предложением:
        Например <li> логически значит что это и есть отдельное предложение
    """
    replaces = {
        "</li>": "</li>\n",
        "</div>": "</div>\n",
    }
    html = no_probely(html, replaces, ignore_case=True, limit=1)

    # First we remove inline JavaScript/CSS:
    cleaned = re.sub(r"(?is)<(script|style).*?>.*?(</\1>)", "", html.strip())
    # Then we remove html comments. This has to be done before removing regular
    # tags since comments can contain '>' characters.
    cleaned = re.sub(r"(?s)<!--(.*?)-->[\n]?", "", cleaned)
    # Next we can remove the remaining tags:
    cleaned = re.sub(r"(?s)<.*?>", " ", cleaned)
    # Finally, we deal with whitespace
    cleaned = re.sub(r"&nbsp;", " ", cleaned)
    cleaned = re.sub(r"  ", " ", cleaned)
    cleaned = re.sub(r"  ", " ", cleaned)
    cleaned = cleaned.strip()
    # на этом nltk останавливался - но я делаю лучше

    # замена разных html сущностей текстом
    cleaned = unescape_html_entities(cleaned)

    # удаляем у каждой строчки ее мусор
    delim = "\n"
    cleaned = delim.join(clear_list(cleaned.split(delim)))

    # после правки куча кода приводим в норм. форму
    replaces = [
        ["  ", " "],
    ]
    cleaned = no_probely(cleaned, replaces)
    return cleaned


def remove_html_tags_re(html):
    """
    Новая версия - оказалось что в remove_html_tags_nltk тоже все через регекспы, но при этом удаляются скрипты и т.д.

    Старая версия:
        Через ре криво - будут и скрипты, и т.д.

        Еще копнуть:
            https://stackoverflow.com/questions/328356/extracting-text-from-html-file-using-python/24618186#24618186

        Есть в
            https://stackoverflow.com/questions/37018475/python-remove-all-html-tags-from-string/37019031
    """
    return remove_html_tags_nltk(html)

    p = re.compile(r"<.*?>")
    return p.sub("", html).strip()


def unescape_html_entities(html: str) -> str:
    """
    https://stackoverflow.com/questions/2087370/decode-html-entities-in-python-string
    """
    return html_unescape(html)


if __name__ == "__main__":
    from modules import *
    from pprint import pprint

    special = "leave_only_allowed_classes"
    special = "change_googleTravel_links_to_site_links"
    special = "expand_self_closing_tags"
    special = "unescape_html_entities"
    special = "remove_html_tags_nltk"
    special = "change_keyToUrl_to_text"
    special = "remove_texts_with_xpath"
    special = "xpath_to_attributes"
    special = "test"

    if special == "xpath_to_attributes":
        html = """
            <meta name="description" content="Интерактивные игрушки в интернет-магазине ROZETKA. Тел: 0(800)303-344. Интерактивные игрушки для детей, лучшие цены, доставка, гарантия!">
        """
        root = string_to_element(html)
        xpath = '//meta[@name="description"]'
        description = xpath_to_attribute(xpath, "content", root)
        print(f"{description=}")

    if special == "test":
        html = """
        <h3 class="V2Zq0e">
            <span class="mfMhoc">People also search for</span>
        </h3>
        """

        html = """
        <h3 class="V2Zq0e">
            People also search for
        </h3>
        """

        t = 1
        if t:
            f = r"s:\!kyxa\!code\!documentation\py4seo\advanced\08\dor_minimum\intentuss\data\typical_pages\google_page.html"
            html = text_from_file(f)

        name = "People also search for"
        xpath = f"//div[text()='{name}'] | //h3[text()='{name}'] | //h2[text()='{name}'] | //h3/span[text()='{name}'] "
        xpath = f"//div[text()='{name}'] | //h3[text()='{name}'] | //h2[text()='{name}'] "
        xpath = f"//h3/*[text()[contains(.,'{name}')]]"
        xpath = f"//h3/span[text()='{name}']"

        xpath = f'//h3[contains(string(), "{name}")]'  # !!!
        """
        string() function returns string-value of the first node:

            A node-set is converted to a string by returning the string-value of the node in the node-set that is first in document order. If the node-set is empty, an empty string is returned.
        """

        xpath = f'//h3[contains(text(), "{name}")]'  # no
        xpath = f'//h3[contains(., "{name}")]'  # !!!
        xpath = f"//h3[text()='{name}']"
        xpath = f"//h3[normalize-space()='{name}']"  # yes!
        xpath = f"//h1 | //h3"  # yes!

        print(xpath)
        root = string_to_element(html)
        data_tree = xpath_to_element(xpath, root)
        print("data_tree:", data_tree)
        values = xpath_to_textContents(xpath, root, adding="text_content")
        print(f"{values=}")

    if special == "remove_texts_with_xpath":
        os._exit(0)

    if special == "change_keyToUrl_to_text":
        # Заменяем урлы на просто текст: <a href="[[key_to_url{from=also_ask} Что лучше пальто из шерсти или кашемира?]]">Что Лучше Пальто Из Шерсти Или Кашемира?</a>
        text = """
        <a href="http://google">hello</a>
        <br>
        <a href="[[key_to_url{from=also_ask} Что лучше пальто из шерсти или кашемира?]]">Что Лучше Пальто Из Шерсти Или Кашемира?</a>
        """
        new_text = change_keyToUrl_to_text(text)
        print(new_text)
        os._exit(0)

    if special == "unescape_html_entities":
        text = """ &#91;1&#93; .
        Мышление &#160;— психический процесс моделирования 
        <p>&pound;682m</p>
        """
        r = unescape_html_entities(text)
        print(r)

    if special == "remove_html_tags_nltk":
        from modules.file_functions import *

        f = r"s:\!kyxa\!code\!documentation\py4seo\advanced\08\dor_minimum\nlp\data\pages\min_page.html"
        f = r"S:/!kyxa/!code/!documentation/py4seo/advanced/08/dor_minimum/temp/external_pages/6fdba2ed5eb938243ba9fa44ceb49915/1a300118665cceca71b8545e8a4d09ed.html"
        funcs = [
            # remove_html_tags_beautifulsoup,
            remove_html_tags_nltk,
            # remove_html_tags_re,
        ]
        html = text_from_file(f)
        for func in funcs:
            f_to = f"temp/remove_html_tags/text__{func.__name__}.txt"
            text = func(html)
            text_to_file(text, f_to)

            t = 1
            t = 0
            if t:
                print("text:")
                print(text)

    if special == "expand_self_closing_tags":

        html = """
        <html>
        <head>
        < base href="probel" />
        <base href="oppa" />
        <base href="normal">
        <meta charset="utf-8"/>
        <meta charset ="utf-8"/>

        </head>
        <body>
        
        <div>
         <div> </div>
        </div>
        
        < hr />
        <br/>
        <BR />
        <hR/>
        <div class="style1"></div>
        <div  Class="style2"/>
        <DIV Class="style2"/>
        <div></div>
        <div/>
        <a href="[[key_to_url привет]]">Привет?</a>
        <a href="[[key_to_url hello]]">Hello?</a>
        
  <div>
    
  </div>
        """
        # new_html = minimize_self_closing_tags(html)
        # new_html = delete_unnecessary_self_closing_tags(html)
        # new_html = expand_self_closing_tags(html)
        new_html = xml_to_correct_html(html)

        print(new_html)

    if special == "change_googleTravel_links_to_site_links":
        html = """
        <div class="kno-vrt-t">
        <a href="/travel/things-to-do/see-all?g2lb=2502548,4258168,4260007,4270442,4274032,4305595,4306835,4317915,4322822,4328159,4358982,4364504,4366684,4367954,4371334,4381263,4386665,4393965,4395590,4398672,4400364,4401769,4402097,4403882,4270859,4284970,4291517,4316256&amp;hl=en&amp;gl=es&amp;un=1&amp;otf=1&amp;dest_mid=/m/0j5g9&amp;dest_state_type=sattd&amp;dest_src=tsvr&amp;sa=X&amp;ved=2ahUKEwiBu8-szMPqAhV2xMQBHS2XC20QMSgAMCd6BAgEEAE">
            <div><img src="data:image/jpeg;base64,/9j/4AAQ?q1zMPqAhV2xMQ"></div>
            <div>Caernarfon Castle</div>
        </a></div>
        
        <a href="[[key_to_url привет]]">Привет?</a>
        
        """

        t = 0
        t = 1
        if t:
            html = """
            <html><body>
            <div class="style1"></div>
            <div></div>
            <div/>
            <a href="[[key_to_url привет]]">Привет?</a>
            <a href="[[key_to_url hello]]">Hello?</a>

            """

            root = string_to_element(html)

            t = 1
            if t:
                new_html = lxml_etree.tounicode(root)
                print('{"-" * 100} tounicode', new_html)

            t = 1
            if t:
                new_html = str(root)
                print('{"-" * 100} str', new_html)

            t = 0
            t = 1
            if t:
                new_html = lxml_etree.tostring(
                    root,
                    encoding="unicode",
                    pretty_print=True,
                    # method="html"
                    # method="xml",
                )

            # new_html = change_googleTravel_links_to_site_links(html)

        print("-" * 100, new_html)

    if special == "leave_only_allowed_classes":
        html = """
                    <div class="Z1hOCe">
                      <div class="zloOqf PZPZlf">
                        <span class="w8qArf"><a class="fl" href="/common+raven+scientific+name/">Scientific name</a>: </span>
                        <span class="LrzXr kno-fv">Corvus corax</span>
                      </div>
                    </div>
        """
        new_html = leave_only_allowed_classes(html)

    t = 0
    if t:
        html = """
        <span > <a
        href="/search?lr=lang_en&amp;hl=en&amp;q=crow+length&amp;stick=H4sIAAAAAAAAAOPgE-">anchor</a>
        <h2><div>Hello 1!</div></h2>
        <h2 id="remove">Hello 2!</h2>
        <div>Final!</div>
        huh
        """
        new_html = change_google_links_to_site_links(html)
        print(f"{new_html=}")

        xpath = '//h2[text()="Hello"]'
        xpath = '//h2[@id="remove"]'
        xpath = '//h2[contains(., "Hello")]'
        new_html = remove_texts_with_xpath(new_html, xpath)
        print(f"{new_html=}")

    t = 0
    if t:
        from lxml import etree, html

        document_root = html.fromstring(
            """<html><body><h1>hello world</h1></body></html>"""
        )
        print(
            lxml_etree.tostring(
                document_root, encoding="unicode", pretty_print=True
            )
        )

        special = "stringify_children"
        special = "convert_js_to_html"
        special = "clean_html"

        if special == "clean_html":
            html = """
    <html>
     <head>
       <script type="text/javascript" src="evil-site"></script>
       <link rel="alternate" type="text/rss" src="evil-rss">
       <style>
         body {background-image: url(javascript:do_evil)};
         div {color: expression(evil)};
       </style>
     </head>
     <body onload="evil_function()">
        <!-- I am interpreted for EVIL! -->
       <a href="javascript:evil_function()">a link</a>
       <a href="#" onclick="evil_function()">another link</a>
       <p onclick="evil_function()">a paragraph</p>
       <div style="display: none">secret EVIL!</div>
       <object> of EVIL! </object>
       <iframe src="evil-site"></iframe>
       <form action="evil-site">
         Password: <input type="password" name="password">
       </form>
       <blink>annoying EVIL!</blink>
       <a href="evil-site">spam spam SPAM!</a>
       <image src="evil!">
     </body>
    </html>"""

            html = """
            <div>one</div>
            <div>
            <ul class="i8Z77e">\n    
            <li class="TrT0Xe">The Introduction Parts of the Essay. The introduction is usually the base of the essay. ... </li>\n    <li class="TrT0Xe">The First Body Paragraph. ... </li>
            </ul>
            """
            print(my_clean_html(html))

        if special == "convert_js_to_html":
            js = """
            {window.jsl.dh('_0Y7wXsi5IPLB7gLfwo2QCA76','\x3cdiv class\x3d\x22mod\x22 data-md\x3d\x2283\x22\x3e\x3c!--m--\x3e\x3cdiv class\x3d\x22di3YZe\x22\x3e\x3cdiv class\x3d\x22co8aDb gsrt\x22 aria-level\x3d\x223\x22 role\x3d\x22heading\x22\x3e\x3cb\x3eHow to Write an Essay in 5 Easy Steps\x3c/b\x3e\x3c/div\x3e\x3cdiv class\x3d\x22RqBzHd\x22\x3e\x3col class\x3d\x22X5LH0c\x22\x3e\x3cli class\x3d\x22TrT0Xe\x22\x3ePick a topic. If possible, choose something that interests you.\x3c/li\x3e\x3cli class\x3d\x22TrT0Xe\x22\x3eBrainstorm. Write down any idea that comes to your head about things you\x26#39;d like to include, including key points, examples, and illustrations.\x3c/li\x3e\x3cli class\x3d\x22TrT0Xe\x22\x3eOrganize. Pick out a thesis, or main point you are trying to prove. ... \x3c/li\x3e\x3cli class\x3d\x22TrT0Xe\x22\x3eWrite. ... \x3c/li\x3e\x3cli class\x3d\x22TrT0Xe\x22\x3eRevise.\x3c/li\x3e\x3c/ol\x3e\x3c/div\x3e\x3c/div\x3e\x3c!--n--\x3e\x3c/div\x3e\x3cdiv class\x3d\x22g\x22\x3e\x3c!--m--\x3e\x3cdiv class\x3d\x22rc\x22 data-hveid\x3d\x22CAwQJg\x22 data-ved\x3d\x222ahUKEwiI5vL5oZXqAhXyoFsKHV9hA4IQFSgBMA16BAgMECY\x22\x3e\x3cdiv class\x3d\x22r\x22\x3e\x3ca href\x3d\x22https://uniontestprep.com/blog/how-to-write-an-essay-in-5-easy-steps\x22 ping\x3d\x22/url?sa\x3dt\x26amp;source\x3dweb\x26amp;rct\x3dj\x26amp;url\x3dhttps://uniontestprep.com/blog/how-to-write-an-essay-in-5-easy-steps\x26amp;ved\x3d2ahUKEwiI5vL5oZXqAhXyoFsKHV9hA4IQFjANegQIDBAn\x22\x3e\x3cbr\x3e\x3ch3 class\x3d\x22LC20lb DKV0Md\x22\x3eHow to Write an Essay in 5 Easy Steps - Union Test Prep\x3c/h3\x3e\x3cdiv class\x3d\x22TbwUpd NJjxre\x22\x3e\x3ccite class\x3d\x22iUh30 bc tjvcx\x22\x3euniontestprep.com\x3cspan class\x3d\x22eipWBe\x22\x3e \x26rsaquo; blog \x26rsaquo; how-to-write-an-essay-in-5-ea...\x3c/span\x3e\x3c/cite\x3e\x3c/div\x3e\x3c/a\x3e\x3cdiv class\x3d\x22B6fmyf\x22\x3e\x3cdiv class\x3d\x22TbwUpd\x22\x3e\x3ccite class\x3d\x22iUh30 bc tjvcx\x22\x3euniontestprep.com\x3cspan class\x3d\x22eipWBe\x22\x3e \x26rsaquo; blog \x26rsaquo; how-to-write-an-essay-in-5-ea...\x3c/span\x3e\x3c/cite\x3e\x3c/div\x3e\x3cdiv class\x3d\x22eFM0qc\x22\x3e\x3c/div\x3e\x3c/div\x3e\x3c/div\x3e\x3cdiv class\x3d\x22s\x22\x3e\x3cdiv\x3e\x3cspan class\x3d\x22st\x22\x3e\x3c/span\x3e\x3c/div\x3e\x3c/div\x3e\x3c/div\x3e\x3c!--n--\x3e\x3c/div\x3e\x3cdiv class\x3d\x22iOBnre match-mod-horizontal-padding\x22\x3e\u0418\u0441\u043a\u0430\u0442\u044c: \x3ca href\x3d\x22/search?hl\x3dru\x26amp;q\x3dHow+do+you+write+easy%3F\x26amp;sa\x3dX\x26amp;ved\x3d2ahUKEwiI5vL5oZXqAhXyoFsKHV9hA4IQzmd6BAgMECs\x22\x3eHow do you write easy?\x3c/a\x3e\x3c/div\x3e');}
            """
            html = convert_js_to_html(js)
            print(html)

        if special == "stringify_children":
            html = """<body>
               <div class="rwrl rwrl_pri rwrl_padref">To write a five paragraph essay, start with an <strong>introductory paragraph</strong> that includes a hook to capture your audience&#8217;s attention, and a thesis that explains the main point you&#8217;re trying to make. Then, use the next 3 paragraphs to explain 3 separate points that support your thesis.</div>
               </body>"""
            # node = lxml_html.fragment_fromstring(html)
            node2 = lxml_html.fragment_fromstring(html)
            node = lxml_html.fromstring(html)
            print(f"{type(node)}, {node=}", node.text_content())
            print(f"{type(node2)}, {node2=}", node2.text_content())

            print("stringify_children ", stringify_children(node))
            print("stringify_children2", stringify_children2(node))

            print("node:", node.text_content())

            answer = xpath_to_childrenHtml(
                '//div[@class="rwrl rwrl_pri rwrl_padref"]', node
            )
            print(f"{answer=}")
