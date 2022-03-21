# -*- coding: utf-8 -*-

try:
    import sgmllib
    from sgmllib import SGMLParser
except Exception as er:
    print(f"can no import SGMLParser")

# from html_functions import *

from html.entities import entitydefs as html_entitydefs

# from modules import to_hash, get_logger
from my_requests.url_helpers import *

logger = get_logger(__name__)


class BaseHTMLProcessor(SGMLParser):
    def reset(self):
        # extend (called by SGMLParser.__init__)
        self.pieces = []
        SGMLParser.reset(self)

    def unknown_starttag(self, tag, attrs):
        # called for each start tag
        # attrs is a list of (attr, value) tuples
        # e.g. for <pre class="screen">, tag="pre", attrs=[("class", "screen")]
        # Ideally we would like to reconstruct original tag and attributes, but
        # we may end up quoting attribute values that weren't quoted in the source
        # document, or we may change the type of quotes around the attribute value
        # (single to double quotes).
        # Note that improperly embedded non-HTML code (like client-side Javascript)
        # may be parsed incorrectly by the ancestor, causing runtime script errors.
        # All non-HTML code must be enclosed in HTML comment tags (<!-- code -->)
        # to ensure that it will pass through this parser unaltered (in handle_comment).
        strattrs = "".join([' %s="%s"' % (key, value) for key, value in attrs])
        self.pieces.append("<%(tag)s%(strattrs)s>" % locals())

    def unknown_endtag(self, tag):
        # called for each end tag, e.g. for </pre>, tag will be "pre"
        # Reconstruct the original end tag.
        self.pieces.append("</%(tag)s>" % locals())

    def handle_charref(self, ref):
        # called for each character reference, e.g. for "&#160;", ref will be "160"
        # Reconstruct the original character reference.
        self.pieces.append(" ")

    # 		self.pieces.append("&#%(ref)s;" % locals())

    def handle_entityref(self, ref):
        self.pieces.append(" ")
        return
        # called for each entity reference, e.g. for "&copy;", ref will be "copy"
        # Reconstruct the original entity reference.
        self.pieces.append("&%(ref)s" % locals())
        # standard HTML entities are closed with a semicolon; other entities are not
        if html_entitydefs.has_key(ref):
            self.pieces.append(";")

    def handle_data(self, text):
        # called for each block of plain text, i.e. outside of any tag and
        # not containing any character or entity references
        # Store the original text verbatim.
        self.pieces.append(text)

    def handle_comment(self, text):
        # called for each HTML comment, e.g. <!-- insert Javascript code here -->
        # Reconstruct the original comment.
        # It is especially important that the source document enclose client-side
        # code (like Javascript) within comments so it can pass through this
        # processor undisturbed; see comments in unknown_starttag for details.
        self.pieces.append("<!--%(text)s-->" % locals())

    def handle_pi(self, text):
        # called for each processing instruction, e.g. <?instruction>
        # Reconstruct original processing instruction.
        self.pieces.append("<?%(text)s>" % locals())

    def handle_decl(self, text):
        # called for the DOCTYPE, if present, e.g.
        # <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
        # 	 "http://www.w3.org/TR/html4/loose.dtd">
        # Reconstruct original DOCTYPE
        self.pieces.append("<!%(text)s>" % locals())

    def output(self):
        """Return processed HTML as a single string"""
        return "".join(self.pieces)


class NoHtmlParser(sgmllib.SGMLParser):
    """убирает любое хтмл-форматирование и хтмл-символы заменяет на пробелы"""

    entitydefs = html_entitydefs  # replace entitydefs from sgmllib

    def __init__(self):
        sgmllib.SGMLParser.__init__(self)
        self.result = ""
        self.endTagList = []

    def handle_data(self, data):
        if data:
            self.result = self.result + data

    def handle_charref(self, name):
        self.result = self.result + " "  # "%s&#%s;" % (self.result, name)

    def handle_entityref(self, name):
        if self.entitydefs.has_key(name):
            x = ";"
        else:
            # this breaks unstandard entities that end with ';'
            x = ""
        self.result = self.result + " "  # "%s&%s%s" % (self.result, name, x)

    def unknown_starttag(self, tag, attrs):
        pass

    def unknown_endtag(self, tag):
        pass


class ReplaceBadTagsParser(sgmllib.SGMLParser):
    """абзацный парсер - заменяет разные вредные теги типа br', 'LI', 'li', 'DT', 'DD' и т.д. на нужные нам теги"""

    zameny = {
        "p": ["br", "li", "dt", "dd", "div", "quote"],
        "h2": ["h1", "h2", "h3"],
        "strong": ["strong", "em", "h4", "h5", "h6"],
    }
    zamenjajem = {}
    abzacnije = []
    tag_abzac = []

    entitydefs = html_entitydefs  # replace entitydefs from sgmllib

    def __init__(self):
        sgmllib.SGMLParser.__init__(self)
        self.result = ""
        self.endTagList = []

        for good_tag in self.zameny.keys():
            bad_tags = self.zameny[good_tag]
            for bad_tag in bad_tags:
                self.abzacnije.append(bad_tag)
                self.zamenjajem[bad_tag] = good_tag

    def handle_data(self, data):
        if data:
            self.result = self.result + data

    def handle_charref(self, name):
        self.result = "%s&#%s;" % (self.result, name)

    def handle_entityref(self, name):
        if self.entitydefs.has_key(name):
            x = ";"
        else:
            # this breaks unstandard entities that end with ';'
            x = ""
        self.result = "%s&%s%s" % (self.result, name, x)

    def unknown_starttag(self, tag, attrs):
        """ Delete all tags except for legal ones """
        if tag in self.abzacnije:
            self.result = self.result + "<" + self.zamenjajem[tag]
            for k, v in attrs:
                if k[0:2].lower() != "on" and v[0:10].lower() != "javascript":
                    self.result = '%s %s="%s"' % (self.result, k, v)
            endTag = "</%s>" % tag
            self.endTagList.insert(0, endTag)
            self.result = self.result + ">"
        else:
            self.result = self.result + "<" + tag
            for k, v in attrs:
                if k[0:2].lower() != "on" and v[0:10].lower() != "javascript":
                    self.result = '%s %s="%s"' % (self.result, k, v)
            endTag = "</%s>" % tag
            self.endTagList.insert(0, endTag)
            self.result = self.result + ">"

    def unknown_endtag(self, tag):
        if tag in self.abzacnije:
            self.result = "%s</%s>" % (self.result, self.zamenjajem[tag])
            remTag = "</%s>" % tag
            self.endTagList.remove(remTag)
        else:
            self.result = "%s</%s>" % (self.result, tag)
            remTag = "</%s>" % tag
            try:
                self.endTagList.remove(remTag)
            except Exception as er:
                # 				logger.debug(f"{tag} NOT FOUND IN {self.endTagList}")
                pass


class LeaveTagsIWantNew(sgmllib.SGMLParser):
    """убираем лишние теги и другое попсовое форматирование из текста"""

    bad_urls = ()
    bad_imgs = ()

    entitydefs = html_entitydefs  # replace entitydefs from sgmllib

    def __init__(self, valid_tags, valid_attrs):
        sgmllib.SGMLParser.__init__(self)
        self.result = ""
        self.endTagList = []
        self.bad = []
        self.valid_tags = valid_tags
        self.valid_attrs = valid_attrs

    def handle_data(self, data):
        if data:
            self.result = self.result + data

    def handle_charref(self, name):
        self.result = "%s&#%s;" % (self.result, name)

    def handle_entityref(self, name):
        if self.entitydefs.has_key(name):
            x = ";"
        else:
            # this breaks unstandard entities that end with ';'
            x = ""
        self.result = "%s&%s%s" % (self.result, name, x)

    def unknown_starttag(self, tag, attrs):
        """ Delete all tags except for legal ones """
        if tag in self.valid_tags:
            # 			if tag == 'a':
            # 				attributes = [' ']
            # 				is_bad_url = True
            ##				ОТКЛЮЧИЛ НАХЕР ВСЕ ССЫЛКИ ЧТОБЫ НЕ МЕШАЛИ
            ##				for k, v in attrs:
            ##					if k=='href':
            ##						if v in self.bad_urls: #если в плохих - ставим ссылку на себя
            ##							attributes.append('%s=""' % (k))
            ##							is_bad_url = True
            ##						else:
            ##							attributes.append('%s="%s"' % (k, v))
            ##							attributes.append('rel="nofollow"')
            ##					elif k=='target':
            ##						pass
            ##				attributes.append('target="_blank"')
            # 				endTag = '</%s>' %  tag

            # 				if not is_bad_url:
            # 					self.result = self.result + '<' + tag + ' '.join(attributes)
            # 					self.endTagList.insert(0,endTag)
            # 					self.result = self.result + '>'
            # 				else:
            # 					self.bad.insert(0, endTag)

            # 			if tag == 'img':
            # 				attributes = [' ']
            # 				is_bad_image = False
            # 				tppabs = ''
            # 				src = ''
            # 				for k, v in attrs:
            ##					logger.debug(f"{k}, {v}")
            # 					if k == 'src':
            # 						src = v
            # 						if v in self.bad_imgs: #если в плохих - делаем пустым
            # 							is_bad_image = True
            # 					elif k == 'tppabs':
            # 						tppabs = v
            #
            ##				а в tppabs телепорт сам вставляет абсолютные пути - вот их то мне и нужно
            # 				attributes.append('src="%s"' % src)
            #
            # 				endTag = '</%s>' % tag
            # 				if not is_bad_image:
            # 					self.result = self.result + '<' + tag + ' '.join(attributes)
            # 					self.endTagList.insert(0,endTag)
            # 					self.result = self.result + '>'
            # 				else:
            # 					self.bad.insert(0, endTag)

            if False:
                pass
            else:
                # 				logger.debug(f"{attrs=}")
                self.result = self.result + "<" + tag
                for k, v in attrs:
                    # 					logger.debug(f"{k}, {v}")
                    if (
                        k[0:2].lower() != "on"
                        and v[0:10].lower() != "javascript"
                        and k in self.valid_attrs
                    ):
                        self.result = '%s %s="%s"' % (self.result, k, v)
                endTag = "</%s>" % tag
                self.endTagList.insert(0, endTag)
                self.result = self.result + ">"

    def unknown_endtag(self, tag):
        remTag = "</%s>" % tag
        if tag in self.valid_tags:
            if remTag in self.bad:
                self.bad.remove(remTag)
            else:
                self.result = "%s</%s>" % (self.result, tag)
                if remTag in self.endTagList:
                    self.endTagList.remove(remTag)

    def cleanup(self):
        """ Append missing closing tags """
        for j in range(len(self.endTagList)):
            self.result = self.result + self.endTagList[j]


class LeaveTagsIWant(sgmllib.SGMLParser):
    """убираем лишние теги и другое попсовое форматирование из текста"""

    # These are the HTML tags that we will leave intact
    # 	valid_tags = ('h1', 'h2', 'h3', 'h4', 'b', 'strong', 'i', 'em', 'br', 'p', 'table', 'tr', 'td', 'ht', 'img', )#
    # 	valid_tags = ('h1', 'h2', 'h3', 'h4', 'b', 'strong', 'i', 'em', 'br', 'p')#'img',
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
        "a",
        "img",
    )  #'img',
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
    bad_urls = ()
    bad_imgs = ()

    from html.entities import entitydefs  # replace entitydefs from sgmllib

    def __init__(self):
        sgmllib.SGMLParser.__init__(self)
        self.result = ""
        self.endTagList = []
        self.bad = []

    def handle_data(self, data):
        if data:
            self.result = self.result + data

    def handle_charref(self, name):
        self.result = "%s&#%s;" % (self.result, name)

    def handle_entityref(self, name):
        if self.entitydefs.has_key(name):
            x = ";"
        else:
            # this breaks unstandard entities that end with ';'
            x = ""
        self.result = "%s&%s%s" % (self.result, name, x)

    def unknown_starttag(self, tag, attrs):
        """ Delete all tags except for legal ones """
        if tag in self.valid_tags:
            if tag == "a":
                attributes = [" "]
                is_bad_url = True
                # 				ОТКЛЮЧИЛ НАХЕР ВСЕ ССЫЛКИ ЧТОБЫ НЕ МЕШАЛИ
                # 				for k, v in attrs:
                # 					if k=='href':
                # 						if v in self.bad_urls: #если в плохих - ставим ссылку на себя
                # 							attributes.append('%s=""' % (k))
                # 							is_bad_url = True
                # 						else:
                # 							attributes.append('%s="%s"' % (k, v))
                # 							attributes.append('rel="nofollow"')
                # 					elif k=='target':
                # 						pass
                # 				attributes.append('target="_blank"')
                endTag = "</%s>" % tag

                if not is_bad_url:
                    self.result = (
                        self.result + "<" + tag + " ".join(attributes)
                    )
                    self.endTagList.insert(0, endTag)
                    self.result = self.result + ">"
                else:
                    self.bad.insert(0, endTag)

            elif tag == "img":
                attributes = [" "]
                is_bad_image = False
                tppabs = ""
                src = ""
                for k, v in attrs:
                    # 					logger.debug(f"{k}, {v}")
                    if k == "src":
                        src = v
                        if v in self.bad_imgs:  # если в плохих - делаем пустым
                            is_bad_image = True
                    elif k == "tppabs":
                        tppabs = v

                # 				а в tppabs телепорт сам вставляет абсолютные пути - вот их то мне и нужно
                attributes.append('src="%s"' % src)

                endTag = "</%s>" % tag
                if not is_bad_image:
                    self.result = (
                        self.result + "<" + tag + " ".join(attributes)
                    )
                    self.endTagList.insert(0, endTag)
                    self.result = self.result + ">"
                else:
                    self.bad.insert(0, endTag)

            else:
                self.result = self.result + "<" + tag
                for k, v in attrs:
                    if (
                        k[0:2].lower() != "on"
                        and v[0:10].lower() != "javascript"
                        and k in self.valid_attrs
                    ):
                        self.result = '%s %s="%s"' % (self.result, k, v)
                endTag = "</%s>" % tag
                self.endTagList.insert(0, endTag)
                self.result = self.result + ">"

    def unknown_endtag(self, tag):
        remTag = "</%s>" % tag
        if tag in self.valid_tags:
            if remTag in self.bad:
                self.bad.remove(remTag)
            else:
                self.result = "%s</%s>" % (self.result, tag)
                if remTag in self.endTagList:
                    self.endTagList.remove(remTag)

    def cleanup(self):
        """ Append missing closing tags """
        for j in range(len(self.endTagList)):
            self.result = self.result + self.endTagList[j]


class ValidTagsParser(sgmllib.SGMLParser):
    """убираем лишние теги и другое попсовое форматирование из текста"""

    # These are the HTML tags that we will leave intact
    valid_tags = (
        "h1",
        "h2",
        "b",
        "strong",
        "a",
        "i",
        "br",
        "p",
        "img",
        "item",
        "vopros_otvet",
        "page_url",
        "page_title",
        "page",
        "url",
        "abs_url",
        "page_content",
        "isto4nik",
        "page_description",
        "kategorija",
        "main_kategorija",
        "from_site",
        "how_to_link",
        "ITEMS",
    )  #'table', 'tr', 'td',
    valid_attrs = (
        "cellspacing",
        "cellpadding",
        "width",
        "src",
        "href",
        "COUNT",
    )
    bad_urls = "http://www.stomatolog.md"
    bad_imgs = (
        "http://www.stomatolog.md/im/pod_medafarm.jpg",
        "http://www.stomatolog.md/pics/article/body_314_1.jpg",
    )

    from html.entities import entitydefs  # replace entitydefs from sgmllib

    def __init__(self):
        sgmllib.SGMLParser.__init__(self)
        self.result = ""
        self.endTagList = []
        self.bad = []

    def handle_data(self, data):
        if data:
            self.result = self.result + data

    def handle_charref(self, name):
        self.result = "%s&#%s;" % (self.result, name)

    def handle_entityref(self, name):
        if self.entitydefs.has_key(name):
            x = ";"
        else:
            # this breaks unstandard entities that end with ';'
            x = ""
        self.result = "%s&%s%s" % (self.result, name, x)

    def unknown_starttag(self, tag, attrs):
        """ Delete all tags except for legal ones """
        if tag in self.valid_tags:
            if tag == "a":
                attributes = [" "]
                is_bad_url = True
                # 				ОТКЛЮЧИЛ НАХЕР ВСЕ ССЫЛКИ ЧТОБЫ НЕ МЕШАЛИ
                # 				for k, v in attrs:
                # 					if k=='href':
                # 						if v in self.bad_urls: #если в плохих - ставим ссылку на себя
                # 							attributes.append('%s=""' % (k))
                # 							is_bad_url = True
                # 						else:
                # 							attributes.append('%s="%s"' % (k, v))
                # 							attributes.append('rel="nofollow"')
                # 					elif k=='target':
                # 						pass
                # 				attributes.append('target="_blank"')
                endTag = "</%s>" % tag

                if not is_bad_url:
                    self.result = (
                        self.result + "<" + tag + " ".join(attributes)
                    )
                    self.endTagList.insert(0, endTag)
                    self.result = self.result + ">"
                else:
                    self.bad.insert(0, endTag)

            elif tag == "img":
                attributes = [" "]
                is_bad_image = False
                tppabs = ""
                for k, v in attrs:
                    if k == "src":
                        if v in self.bad_imgs:  # если в плохих - делаем пустым
                            is_bad_image = True
                    elif k == "tppabs":
                        tppabs = v

                # 				а в tppabs телепорт сам вставляет абсолютные пути - вот их то мне и нужно
                attributes.append('src="%s"' % tppabs)

                endTag = "</%s>" % tag
                if not is_bad_image:
                    self.result = (
                        self.result + "<" + tag + " ".join(attributes)
                    )
                    self.endTagList.insert(0, endTag)
                    self.result = self.result + ">"
                else:
                    self.bad.insert(0, endTag)

            else:
                self.result = self.result + "<" + tag
                for k, v in attrs:
                    if (
                        k[0:2].lower() != "on"
                        and v[0:10].lower() != "javascript"
                        and k in self.valid_attrs
                    ):
                        self.result = '%s %s="%s"' % (self.result, k, v)
                endTag = "</%s>" % tag
                self.endTagList.insert(0, endTag)
                self.result = self.result + ">"

    def unknown_endtag(self, tag):
        remTag = "</%s>" % tag
        if tag in self.valid_tags:
            if remTag in self.bad:
                self.bad.remove(remTag)
            else:
                self.result = "%s</%s>" % (self.result, tag)
                if remTag in self.endTagList:
                    self.endTagList.remove(remTag)

    def cleanup(self):
        """ Append missing closing tags """
        for j in range(len(self.endTagList)):
            self.result = self.result + self.endTagList[j]


class ValidTagsParser_temp(sgmllib.SGMLParser):
    """убираем лишние теги и другое попсовое форматирование из текста"""

    # These are the HTML tags that we will leave intact
    valid_tags = (
        "h1",
        "h2",
        "b",
        "strong",
        "a",
        "i",
        "br",
        "p",
        "img",
        "item",
        "vopros_otvet",
        "page_url",
        "page_title",
        "page",
        "url",
        "abs_url",
        "page_content",
        "isto4nik",
        "page_description",
        "kategorija",
        "main_kategorija",
        "from_site",
        "how_to_link",
        "ITEMS",
    )  #'table', 'tr', 'td',
    valid_attrs = (
        "cellspacing",
        "cellpadding",
        "width",
        "src",
        "href",
        "COUNT",
    )
    bad_urls = "http://www.stomatolog.md"
    bad_imgs = (
        "http://www.stomatolog.md/im/pod_medafarm.jpg",
        "http://www.stomatolog.md/pics/article/body_314_1.jpg",
    )

    from html.entities import entitydefs  # replace entitydefs from sgmllib

    def __init__(self, base_url):
        sgmllib.SGMLParser.__init__(self)
        self.result = ""
        self.endTagList = []
        self.bad = []
        self.base_url = base_url

    def handle_data(self, data):
        if data:
            self.result = self.result + data

    def handle_charref(self, name):
        self.result = "%s&#%s;" % (self.result, name)

    def handle_entityref(self, name):
        if self.entitydefs.has_key(name):
            x = ";"
        else:
            # this breaks unstandard entities that end with ';'
            x = ""
        self.result = "%s&%s%s" % (self.result, name, x)

    def unknown_starttag(self, tag, attrs):
        """ Delete all tags except for legal ones """
        if tag in self.valid_tags:
            if tag == "a":
                attributes = [" "]
                is_bad_url = True
                # 				ОТКЛЮЧИЛ НАХЕР ВСЕ ССЫЛКИ ЧТОБЫ НЕ МЕШАЛИ
                # 				for k, v in attrs:
                # 					if k=='href':
                # 						if v in self.bad_urls: #если в плохих - ставим ссылку на себя
                # 							attributes.append('%s=""' % (k))
                # 							is_bad_url = True
                # 						else:
                # 							attributes.append('%s="%s"' % (k, v))
                # 							attributes.append('rel="nofollow"')
                # 					elif k=='target':
                # 						pass
                # 				attributes.append('target="_blank"')
                endTag = "</%s>" % tag

                if not is_bad_url:
                    self.result = (
                        self.result + "<" + tag + " ".join(attributes)
                    )
                    self.endTagList.insert(0, endTag)
                    self.result = self.result + ">"
                else:
                    self.bad.insert(0, endTag)

            elif tag == "img":
                attributes = [" "]
                is_bad_image = False
                tppabs = ""
                for k, v in attrs:
                    if k == "src":
                        if v in self.bad_imgs:  # если в плохих - делаем пустым
                            is_bad_image = True
                        tppabs = url_abs(self.base_url, v).encode(
                            "utf8"
                        )  #'xxx'

                    elif k == "tppabs":
                        tppabs = v

                attributes.append('src="%s"' % tppabs)
                endTag = "</%s>" % tag
                if not is_bad_image:
                    self.result = (
                        self.result + "<" + tag + " ".join(attributes)
                    )
                    self.endTagList.insert(0, endTag)
                    self.result = self.result + ">"
                else:
                    self.bad.insert(0, endTag)

            else:
                self.result = self.result + "<" + tag
                for k, v in attrs:
                    if (
                        k[0:2].lower() != "on"
                        and v[0:10].lower() != "javascript"
                        and k in self.valid_attrs
                    ):
                        self.result = '%s %s="%s"' % (self.result, k, v)
                endTag = "</%s>" % tag
                self.endTagList.insert(0, endTag)
                self.result = self.result + ">"

    def unknown_endtag(self, tag):
        remTag = "</%s>" % tag
        if tag in self.valid_tags:
            if remTag in self.bad:
                self.bad.remove(remTag)
            else:
                self.result = "%s</%s>" % (self.result, tag)
                if remTag in self.endTagList:
                    self.endTagList.remove(remTag)

    def cleanup(self):
        """ Append missing closing tags """
        for j in range(len(self.endTagList)):
            self.result = self.result + self.endTagList[j]


class FindSrcParser(sgmllib.SGMLParser):
    """нужно просто из картинок убрать tppabs"""

    from html.entities import entitydefs  # replace entitydefs from sgmllib

    def __init__(self):
        sgmllib.SGMLParser.__init__(self)
        self.result = ""
        self.img_urls = []
        self.endTagList = []

    def handle_data(self, data):
        if data:
            self.result = self.result + data

    def handle_charref(self, name):
        self.result = "%s&#%s;" % (self.result, name)

    def handle_entityref(self, name):
        if self.entitydefs.has_key(name):
            x = ";"
        else:
            # this breaks unstandard entities that end with ';'
            x = ""
        self.result = "%s&%s%s" % (self.result, name, x)

    def unknown_starttag(self, tag, attrs):
        """ Delete all tags except for legal ones """
        self.result = self.result + "<" + tag
        for k, v in attrs:
            if k == "src" and tag == "img":
                self.img_urls.append(v)
            elif k[0:2].lower() != "on" and v[0:10].lower() != "javascript":
                self.result = '%s %s="%s"' % (self.result, k, v)
        endTag = "</%s>" % tag
        self.endTagList.insert(0, endTag)
        self.result = self.result + ">"

    def unknown_endtag(self, tag):
        self.result = "%s</%s>" % (self.result, tag)
        remTag = "</%s>" % tag
        try:
            self.endTagList.remove(remTag)
        except Exception as er:
            # 			logger.debug(f"{tag} NOT FOUND IN {self.endTagList}")
            pass


class FindImagesParser(sgmllib.SGMLParser):
    """нужно просто из картинок убрать tppabs"""

    entitydefs = html_entitydefs  # replace entitydefs from sgmllib

    def __init__(self):
        sgmllib.SGMLParser.__init__(self)
        self.result = ""
        self.img_urls = []
        self.endTagList = []

    def handle_data(self, data):
        if data:
            self.result = self.result + data

    def handle_charref(self, name):
        self.result = "%s&#%s;" % (self.result, name)

    def handle_entityref(self, name):
        if self.entitydefs.has_key(name):
            x = ";"
        else:
            # this breaks unstandard entities that end with ';'
            x = ""
        self.result = "%s&%s%s" % (self.result, name, x)

    def unknown_starttag(self, tag, attrs):
        """ Delete all tags except for legal ones """
        self.result = self.result + "<" + tag
        for k, v in attrs:
            if k == "src" and tag == "img":
                self.img_urls.append(v)
            elif k[0:2].lower() != "on" and v[0:10].lower() != "javascript":
                self.result = '%s %s="%s"' % (self.result, k, v)
        endTag = "</%s>" % tag
        self.endTagList.insert(0, endTag)
        self.result = self.result + ">"

    def unknown_endtag(self, tag):
        self.result = "%s</%s>" % (self.result, tag)
        remTag = "</%s>" % tag
        try:
            self.endTagList.remove(remTag)
        except Exception as er:
            # 			logger.debug(f"{tag} NOT FOUND IN {self.endTagList}")
            pass


class ReplaceImagesParser(sgmllib.SGMLParser):
    """заменяю глобальные картинки на мои скачанные"""

    entitydefs = html_entitydefs  # replace entitydefs from sgmllib

    def __init__(self):
        from zlib import crc32

        sgmllib.SGMLParser.__init__(self)
        self.result = ""
        self.endTagList = []

    def handle_data(self, data):
        if data:
            self.result = self.result + data

    def handle_charref(self, name):
        self.result = "%s&#%s;" % (self.result, name)

    def handle_entityref(self, name):
        if self.entitydefs.has_key(name):
            x = ";"
        else:
            # this breaks unstandard entities that end with ';'
            x = ""
        self.result = "%s&%s%s" % (self.result, name, x)

    def unknown_starttag(self, tag, attrs):
        """ Delete all tags except for legal ones """
        self.result = self.result + "<" + tag
        for k, v in attrs:
            if k == "src" and tag == "img":
                self.result = '%s %s="image.php?image=%s"' % (
                    self.result,
                    k,
                    self.get_local_url(v),
                )
            elif k[0:2].lower() != "on" and v[0:10].lower() != "javascript":
                self.result = '%s %s="%s"' % (self.result, k, v)
        endTag = "</%s>" % tag
        self.endTagList.insert(0, endTag)
        self.result = self.result + ">"

    def unknown_endtag(self, tag):
        self.result = "%s</%s>" % (self.result, tag)
        remTag = "</%s>" % tag
        try:
            self.endTagList.remove(remTag)
        except Exception as er:
            # 			logger.debug(f"{tag} NOT FOUND IN {self.endTagList}")
            pass

    def get_local_url(self, url):
        """ф-я получает глобальный урл (обычно картинки), и заменяет его на мой локальный по этому алгоритму"""
        return to_hash(url)


def url_relative(url):
    # 	получаем абсолютный путь, и делаем его относительным
    items = url.split("/")
    parts = items[3:]
    url2 = "/" + "/".join(parts)
    return url2


if __name__ == "__main__":
    # python -u /usr/lib/python2.7/dist-packages/modules/html_parsers.py

    t = 0
    t = 1
    if t:
        tasks = [
            [
                "https://goldenfront.ru/articles/view/millionery-blokadnogo-leningrada",
                "/media/article_images/image001_434.jpg",
                "https://goldenfront.ru/media/article_images/image001_434.jpg",
            ],
            [
                "http://forum.finance.ua/topic60851.html",
                "./images/smilies/icon_biggrin.gif",
                "http://forum.finance.ua/images/smilies/icon_biggrin.gif",
            ],
            [
                "http://thepr0.narod.ru/?id=rswa",
                "files/rswa/rswa001.png",
                "http://thepr0.narod.ru/files/rswa/rswa001.png",
            ],
            [
                "http://thepr0.narod.ru/1/2/?id=rswa",
                "../files/rswa/rswa001.png",
                "http://thepr0.narod.ru/1/files/rswa/rswa001.png",
            ],
            [
                "http://thepr0.narod.ru/1/2/?id=rswa",
                "//d2dmszldu8of4z.cloudfront.net/wiziqcss/css/skin01/images/info-icon-gray.jpg",
                "http://d2dmszldu8of4z.cloudfront.net/wiziqcss/css/skin01/images/info-icon-gray.jpg",
            ],
            [
                "https://thepr0.narod.ru/1/2/?id=rswa",
                "//d2dmszldu8of4z.cloudfront.net/wiziqcss/css/skin01/images/info-icon-gray.jpg",
                "https://d2dmszldu8of4z.cloudfront.net/wiziqcss/css/skin01/images/info-icon-gray.jpg",
            ],
        ]

        cnt_bad = 0
        for task in tasks:
            logger.debug(f"{task=}")
            url_ot, im, must_be = task
            t = 1
            t = 0
            if t:
                logger.info(url_good(url_ot, min=False, no_www=True))
                os._exit(0)
                wait_for_ok()

            rez = url_abs(url_ot, im)
            if rez != must_be:
                cnt_bad += 1
                logger.debug(f"rezult {rez}")
                Show_step("bad!")

        logger.debug("-" * 100)

        if cnt_bad == 0:
            logger.debug("URAAA, ALL IS GOOD")
        else:
            wait_for_ok("have errors")

        os._exit(0)

        u = url_abs(
            "http://www.free-css.com/assets/files/free-css-templates/preview/page1/aquatic/",
            "style.css",
        )
        u = url_abs(
            "http://www.i-kreditnaya-istoriya.ru/templates/ca_cloudbase2_j25/css/template.css",
            "../../../images/kreditnaja-istorija.png",
        )
        logger.debug(u)
