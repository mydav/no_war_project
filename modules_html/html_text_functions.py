#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from modules import *
from modules_html.html_functions import *

import lxml
import lxml.html as HTML_PARSER
from lxml import etree

logger = get_logger(__name__)


def kl(text, add_spaces=False):
    text = bytes_to_str(text)
    if add_spaces:
        text = text.replace("<", " <").replace(">", "> ")
    return no_probely(no_html(text)).strip()


def kl0(txt):
    return kl(do_lower(txt)).strip()


def get_cleared_parts_in_tags(start="<h1", finish="</h1>", txt=""):
    parts = []
    items = txt.split(start)[1:]
    for item in items:
        part = find_from_to_one(">", finish, item)
        # print(part)
        part = kl(part)
        if part == "":
            continue
        parts.append(part)
    return parts


def get_cleared_part_in_tags(start="<h1", finish="</h1>", txt=""):
    parts = get_cleared_parts_in_tags(start, finish, txt)
    if len(parts) > 0:
        return parts[0]
    else:
        return ""


def is_isXpath_visible(element):
    """Naive implementation of the element visibility check."""
    return "display: none;" not in element.attrib.get("style", "")


def isXpath_element(*args, **kwargs):
    elements = isXpath(*args, **kwargs)
    if not elements:
        return None
    return elements[0]


def delete_childs_from_lxml_element(element, xpath=""):
    if not xpath:
        return element

    for bad in element.xpath(xpath):
        # logger.debug(f"{bad=}")
        bad.getparent().remove(
            bad
        )  # here I grab the parent of the element to call the remove directly on it
        # element.remove(bad)  # here I grab the parent of the element to call the remove directly on it
    return element


def isXpath(
    content,
    xpath,
    otl=0,
    detailed=0,
    encoding="UTF-8",
    otstup=0,
    xpaths_to_delete=[],
    final_key=None,
):
    """
    на вход должны получать строку обычную, но для обработки переганяем ее в юникод
        https://habr.com/ru/post/128381/

    xpath
        https://stackoverflow.com/questions/47559666/selenium-difference-between-buttoncontainstext-s-and-buttont
        Return True if Xpath present else return False

        for future:
            from lxml.html import document_fromstring
            doc = document_fromstring('<a href="http://a.com" rel="bookmark">bla bla bla</a>')
            logger.debug(doc.xpath("//a")[0].get("href"))
            a.attrib['href']
            logger.(doc.text_content())

            http://lxml.de/lxmlhtml.html
            https://stackoverflow.com/questions/8692/how-to-use-xpath-in-python

    """
    fun = "isXpath"
    debug = True
    # encoding = 'utf8'
    # encoding = 'UTF-16'
    # encoding = 'UTF-8'

    MT = get_MT(name=fun, want_timer=0)
    MT.seq("start %s detailed=%s final_key=%s" % (fun, detailed, final_key))

    # content = unicode(content)

    otstup = otstup * "    "

    # logger.debug(type(content))
    elements = []
    if type(content) in [lxml.html.HtmlElement, lxml.html.FormElement]:
        doc = content
    else:
        MT.seq("decode content")

        want_decode = 0
        want_decode = 1
        if want_decode:
            content = decode_for_lxml(content, encoding)

        try:
            m = "%s %s %s %s %s" % (
                fun,
                type(content),
                type(xpath),
                xpath,
                content,
            )
        except Exception as er:
            m = "%s %s %s %s" % (fun, type(content), type(xpath), xpath)
        # print(m)
        # logger.debug(m)
        if otl:
            logger.debug(
                "%s[%s `%s`, page_size %s" % (otstup, fun, xpath, len(content))
            )

        doc = HTML_PARSER.fromstring(content)

    if not isinstance(xpath, unicode):
        MT.seq("decode xpath")
        xpath = decode_for_lxml(xpath, encoding)

    """
    проверка - это атрибут?
        /@href==атрибут
    """
    MT.seq("check is_attribute")
    is_attribute = False
    t = 0
    t = 1
    if t:
        # уже на атрибуты могу не проверять - там по типу проверка
        last_part = xpath.split("/")[-1]
        if last_part.startswith("@"):
            is_attribute = True
            final_key = None

    if otl:
        logger.debug("is_attribute=%s" % is_attribute)

    MT.seq("parse with xpath")
    # parsed = doc.xpath(xpath)
    try:
        parsed = doc.xpath(xpath)
    except Exception as er:
        m = f"ERROR {fun}: wrong {xpath=}"
        logger.error(m)
        wait_for_ok(m)

    t = 1
    t = 0
    if t:
        logger.debug("xpath=%s, parsed=%s" % (xpath, parsed))
        # wait_for_ok()

    if not parsed:
        if otl:
            logger.debug("%s no xpath %s" % (otstup, xpath))
    else:
        # logger.debug(type(doc.xpath(xpath)))
        # logger.debug('parsed:', type(parsed), parsed)
        # wait_for_ok()
        MT.seq("process %s elements" % len(parsed))
        num = 0
        for element in parsed:
            num += 1
            t = 1
            t = 0
            if t:
                logger.debug(
                    "%sis_isXpath_visible: %s for %s"
                    % (otstup, is_isXpath_visible(element), element)
                )
                # wait_for_ok()

            if xpaths_to_delete:
                MT.seq("xpaths_to_delete")
                for bad_xpath in xpaths_to_delete:
                    element = delete_childs_from_lxml_element(
                        element, bad_xpath
                    )

            t = 0
            t = 1
            if t and otl:
                try:
                    logger.debug(
                        "\n       %s/%s %s" % (num, len(parsed), type(element))
                    )

                    # the difference is in .text (single element) vs. .text_content() (recursive)

                    logger.debug("        text_c %s" % element.text_content())
                    logger.debug(
                        "        tostring: %s"
                        % etree.tostring(element, encoding=encoding)
                    )
                    logger.debug("        text %s" % element.text)
                    logger.debug("        tag %s" % element.tag)

                except Exception as er:
                    logger.error(f"        error_print_element ({er=}")

            if (0 and is_attribute) or type(
                element
            ) == lxml.etree._ElementStringResult:  # для атрибутов обычно type(element) == lxml.etree._ElementStringResult
                r = "%s" % element
                # logger.debug(r)

            elif detailed:
                # MT.seq('detailed')

                if final_key is None:
                    good_keys = [
                        "text",
                        "text_c",
                        "text_kl",
                        "tag",
                        "tostring",
                        "element",
                    ]
                else:
                    good_keys = [final_key]

                r = {}
                for key in good_keys:
                    if key == "text":
                        value = element.text
                    elif key == "text_c":
                        value = element.text_content()
                    elif key == "text_kl":
                        tostring = etree.tostring(element, encoding=encoding)
                        value = kl(
                            tostring, add_spaces=True
                        )  # <div class="qbs-NormalBetItem_Title ">Over<div class="qbs-NormalBetItem_Handicap ">2.5</div></div> - в реальности это с пробелом,
                        # logger.debug('tostring=%s value=%s' % (tostring, value))
                    elif key == "tag":
                        value = element.tag
                    elif key == "tostring":
                        tostring = etree.tostring(element, encoding=encoding)
                        value = tostring
                    elif key == "element":
                        value = element
                    else:
                        raise ValueError(f"unknown {key=}")

                    r[key] = value

                # processing keys
                keys = [
                    "text_kl",
                    "text_c",
                    "tostring",
                    "text",
                    "tag",
                ]

                for key in keys:
                    v = r.get(key)
                    if not v:
                        continue
                    tip = type(v)
                    tip_str = str(tip)
                    # wait_for_ok(tip_str)
                    if otl:
                        logger.debug(f"    {key}, {tip}, {v} {tip_str=}")

                    if (
                        tip == type("str")
                        or tip_str
                        == "<class 'lxml.etree._ElementStringResult'>"
                    ):
                        pass

                    elif tip_str == "<type 'NoneType'>":
                        v = ""

                    elif tip_str in [
                        "<class 'bytes'>",
                    ]:
                        v = bytes_to_str(text)

                    elif (tip == type("u")) or (
                        tip_str
                        in [
                            "<type 'lxml.etree._ElementUnicodeResult'>",
                            "<class 'lxml.etree._ElementUnicodeResult'>",
                        ]
                    ):
                        # logger.debug(v)
                        # v = see_to_norm(v)
                        v = v.encode(encoding, "ignore")
                        # v = text_to_charset(v, encoding)
                        # v = v.decode(encoding)
                        # uni(v)
                        # uni2(v)
                        # join_text_to_file(v, 'temp/%s.txt' % fun)
                    else:
                        m = f"unknown type {tip_str=} for {key=} {value=}"
                        logger.critical(m)
                        wait_for_ok(m)
                    r[key] = v

            else:
                r = element
            elements.append(r)

    if otl:
        logger.debug(
            "%s+%s elements final_key=%s]" % (otstup, len(elements), final_key)
        )

    if detailed and final_key is not None:
        elements = [_[final_key] for _ in elements]
    if otl:
        logger.debug(f"{elements=}")

    MT.flush_all_messages(min_procent=0)
    # logger.debug('done')
    # wait_for_ok('check timing')
    return elements


def found_atLeastOne_xpath(xpaths=[], p=""):
    found = 0
    for xpath in xpaths:
        t = isXpath(p, xpath)
        if t != []:
            found = 1
            break
    return found


def found_all_xpaths(xpaths=[], p=""):
    found = 1
    for xpath in xpaths:
        t = isXpath(p, xpath)
        if t == []:
            found = 0
            break
    return found


def decode_for_lxml(data, encoding="utf-8", otl=0):
    return data

    decoded = data.decode(encoding)

    if otl:
        logger.debug(
            "data with type %s (len %s) decoded to %s (len %s) (encoding %s)"
            % (type(data), len(data), type(decoded), len(decoded), encoding)
        )
    return decoded


def explore_lxml():
    otl = 1
    encoding = "UTF-8"

    data = """<html>
    <head>
    </head>
    <body>Привет мир</body>
    </html>"""

    data = decode_for_lxml(data)
    html = lxml.html.document_fromstring(data)
    logger.debug(f"{html=}")

    t = 1
    if t:
        doc = html
        xpath = "//body"
        xpath = '//body[text()="Привет мир"]'
        xpath = decode_for_lxml(xpath)

        parsed = doc.xpath(xpath)
        for element in parsed:
            t = 0
            t = 1
            if t and otl:
                # the difference is in .text (single element) vs. .text_content() (recursive)
                logger.debug(
                    f"""        
                type: {type(element)}
                text_c: {element.text_content()}
                tostring: {etree.tostring(element, encoding=encoding)}
                text: {element.text}
                tag: {element.tag}
"""
                )

    # doc = HTML_PARSER.fromstring(content)


def explore_xpaths(html="", xpaths=None):
    fun = "explore_xpaths"
    logger.debug("[%s :" % fun)
    if xpaths is None:
        xpaths = [
            "/html/head/meta/@content",
            "/html/head/meta/@*",
        ]
    root = HTML_PARSER.fromstring(html)
    for xpath in xpaths:
        elements = root.xpath(xpath)
        logger.debug(f"    {xpath=}, {elements=}")

    logger.debug(f"+{fun} done]")


if __name__ == "__main__":
    t = 1
    t = 0
    if t:
        """
        незалогинен:
            pt=N#o=15/8#f=102903166#fp=1744172130#so=#c=1#mt=2#id=102903166-1744172130Y#|TP=BS102903166-1744172130#||
        залогинен:
            pt=N#o=8/13#f=102900837#fp=1743935847#so=#c=1#mt=11#id=102900837-1743935847Y#|TP=BS102900837-1743935847#||
        """
        html = r"&ns=pt%3DN%23o%3D40%2F1%23f%3D102903152%23fp%3D1744170619%23so%3D%23c%3D1%23mt%3D2%23id%3D102903152-1744170619Y%23%7CTP%3DBS102903152-1744170619%23%7C%7C&betsource=FlashInPLay&bs=1&qb=1"
        html = r"&ns=pt%3DN%23o%3D8%2F13%23f%3D102900837%23fp%3D1743935847%23so%3D%23c%3D1%23mt%3D11%23id%3D102900837-1743935847Y%23%7CTP%3DBS102900837-1743935847%23%7C%7C&betsource=FlashInPLay&bs=1&qb=1"
        html = r"&ns=pt%3DN%23o%3D0%2F0%23f%3D102894014%23fp%3D1743341694%23so%3D%23c%3Dundefined%23sa%3D60a6b5fd-D8FC8D9%23mt%3D11%23%7Cat%3DY%23TP%3DBS102894014-1743341694%23olc%3D3%23%7C%7Cpt%3DN%23o%3D1%2F80%23f%3D102908146%23fp%3D1744669885%23so%3D%23c%3D1%23mt%3D11%23%7CTP%3DBS102908146-1744669885%23%7C%7C&betsource=FlashInPLay&bs=1&cr=1"

        # html = find_from_to_one('&ns=', '&betsource', html)
        r = urldecode(html)
        # r = unquote(html)
        logger.debug(f"{r=}")

        html0 = url_fix(r, safe="")
        logger.debug(f"1 {html=}")
        logger.debug(f"2 {html0=}")
        wait_for_ok()

    t = 1
    t = 0
    if t:
        explore_lxml()
        os._exit(0)

    t = 0
    t = 1
    if t:
        f = r"d:\kyxa\!code\!actual\google_addurl_selenium\log\addurl_selenium\panel.html"
        er = "An error has occurred. Please try again later."

        f = r"d:\kyxa\!code\!actual\google_addurl_selenium\data\!new_console\states\click_got_it.html"
        er = "Got it"

        xpath = '//*[text()="%s"]' % er

        f = r"d:\kyxa\!code\!actual\google_addurl_selenium\data\!new_console\states_console\domain_not_my.html"

        xpath = "//title"
        xpath = "//title[text()='У вас нет доступа к этому ресурсу']"
        # p = '<title>У вас нет доступа к этому ресурсу</title>'

        # next
        t = 1
        t = 0
        if t:
            title = "Hello title"
            title = "У вас нет доступа к этому ресурсу"
            xpath = "//title[text()='%s']" % title
            p = "<title>%s</title>" % title

        t = 1
        t = 0
        if t:
            f = r"d:\server\usr\local\python\Lib\site-packages\modules\data\isXpath_check\with_hidden_elements.html"
            p = text_from_file(f)

            # xpath = "//h1"

        t = 1
        if t:
            f = r"d:\kyxa\!code\!actual\google_addurl_selenium\data\!new_console\states_login\account_disabled.html"
            xpath = "//h1"
            xpaths = [
                "//h1[text()='Account disabled']",
                "//*[text()='Account disabled']",
                "//h1",
            ]

        t = 1
        if t:
            d_universal_bookmaker = r"s:\!kyxa\!code\!documentation\py4seo\advanced\08\dor_minimum\universal_bookmaker"
            f = (
                d_universal_bookmaker
                + r"\data\parimatch\typical_pages\coupon\put_stake_successfully.html"
            )
            xpath = '//div[@data-id="floating-betslip2-notification-title"][text()="Ставка принята"]'
            xpaths = [
                xpath,
            ]

        p = text_from_file(f)

        t = 1
        t = 0
        if t:
            explore_xpaths(
                p, xpaths=xpaths,
            )
            os._exit(0)

        otl = 1
        elements = isXpath(p, xpath, detailed=1, otl=otl)
        logger.debug(f"{elements=}")
        os._exit(0)

    t = 0
    t = 1
    if t:
        f = r"d:\kyxa\!code\!actual\google_addurl_selenium\data\!know_login_errors\browser.html"
        f = r"d:\kyxa\!code\!actual\google_addurl_selenium\data\!know_login_errors\final.html"
        txt = text_from_file(f)
        # lst = find_from_to_all('<h1', '<', txt)
        # lst = find_from_to_all_tag('<h1', '<', txt)
        lst = get_cleared_parts_in_tags("<h1", "</h1>", txt)

        print("h1: %s" % lst)
        show_list(lst)

        os._exit(0)
    t = 0
    t = 1
    if t:
        htmls = [
            "<h1>h1 full</h1>",
            "simple text",
        ]
        for html in htmls:
            logger.debug(kl(html))
        os._exit(0)
