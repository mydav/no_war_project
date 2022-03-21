# -*- coding: utf-8 -*-

from modules_23.url_helpers import *


def get_regru_possible_zones():
    all_possible_zones = text_from_file(r"all_regru_zones.txt").split("\n")
    all_possible_zones = set(all_possible_zones)
    return all_possible_zones


def check_sites_existing(sites):
    """проверяем откликаются ли наши сайты
	возвращаем плохие"""
    need_rukami_perazagruzitj = []
    for i in sites:
        logger.debug("\t %s" % i)
        conn = httplib.HTTPConnection(i)
        conn.request("GET", "/")
        r1 = conn.getresponse()
        conn.close()
        if r1.status == 200:
            logger.debug("+")
        else:
            logger.error("- %s" % r1.status)
            need_rukami_perazagruzitj.append(i)
    return need_rukami_perazagruzitj


def check_site_existing(url):
    """проверяем откликаются ли сайт. Если нет - даем его ошибку"""
    page = ""
    conn = httplib.HTTPConnection(url)
    try:
        conn.request("GET", "/")
    except Exception as er:
        logger.error("error %s" % er)
        return "", str(er)

    r1 = conn.getresponse()
    if r1.status == 200:
        message = "+"
        page = r1.read()
    else:
        message = r1.status
    conn.close()
    return (page, str(message))


def is_domen_free(domen, otladka=False):
    """ф-я проверки домена на свободность
	аналог check_sites_existing"""
    socket.setdefaulttimeout(10)
    if otladka:
        uni("проверяю домен %s" % domen)
    while True:
        try:
            conn = httplib.HTTPConnection(domen)
            conn.request("GET", "/")
            r1 = conn.getresponse()
            if r1.status == 404:
                rezult = True
            else:
                rezult = False
            break
        except:
            pass
    return rezult


def remove_sessions_from_page(page, parts="PHPSESSID phpsessid sid"):
    if isinstance(parts, str):
        bads = parts.split(" ")
    else:
        bads = parts
    zamena = "PHPSESSID"
    for b in bads:
        page = page.replace(b, zamena)
    # 	return page
    removing = ["&%s=" % zamena, "?%s=" % zamena]
    for r in removing:
        items = page.split(r)
        parts = [items[0]]
        for item in items[1:]:
            more = item[32:]
            parts.append(more)
        page = "".join(parts)
    return page


def prokladka_url(
    url,
    prokladki="""http://skirda.net/css/prokladka.php
http://beethe.ru/upload/prokladka.php
http://chaise-lounge.org/templates/prokladka.php""".split(
        "\n"
    ),
):

    # 	prokladki = #http://demoshop.phonomania.ru/images/prokladka.php
    # http://kosigazon.ru/images/prokladka.php
    # http://cirld.pp.ru/wp-content/prokladka.php
    # http://agarly.ru/wp-content/prokladka.php
    # http://posir.ru/wp-content/prokladka.php
    # http://tehnomob.com/css2/prokladka.php

    prokladka = choice(prokladki)
    if prokladka != "":
        u = "%s?%s" % (prokladka, url)
    else:
        u = url
    return u


def cnt_ya(p):
    p = text_to_charset(p, "cp1251", "utf8")
    if (
        p.find(
            """<title>
&nbsp;&mdash;
Яндекс:
ничего не найдено
</title>"""
        )
        != -1
        or p.find(
            """Яндекс:
ничего не найдено
"""
        )
        != -1
        or p.find("&mdash; Яндекс: ничего не найдено") != -1
        or p.find('title = " — Яндекс: ничего не найдено"') != -1
    ):
        return 0
    p = do_lower(p).replace("&nbsp;", " ")

    # 	cnt = find_from_to_one('нашлось ', 'ответ', p)
    # 	if cnt=='':
    # 		cnt = find_from_to_one('нашлось ', 'страниц', p)
    # 	if cnt=='':
    # 		cnt = find_from_to_one('нашлась ', 'страниц', p)
    # 	if cnt=='':
    # 		cnt = find_from_to_one('нашёлся', 'ответ', p)
    # 	if cnt=='':
    # 		cnt = find_from_to_one('нашёлся ', 'страниц', p)

    cnt = find_from_to_one("наш", "ответ", p)
    if cnt == "":
        cnt = find_from_to_one("наш", "страниц", p)
    cnt = find_from_to_one(" ", "nahposhuk", cnt)

    # 	uni( cnt +',')
    cnt = (
        cnt.replace("тыс.", "000")
        .replace("млн", "000000")
        .replace("&nbsp;", " ")
        .replace(" ", "")
        .replace(" ", "")
    )
    if cnt == "":
        return -5
        wait_for_ok(p)

    try:
        cnt = int(cnt)
    except Exception as er:
        return -5
    return cnt


def cnt_ya_xml(p):

    # ~ wait_for_ok()
    # ~ cnt = find_from_to_one('наш', 'ответ', p)
    # ~ if cnt=='':
    # ~ cnt = find_from_to_one('наш', 'страниц', p)
    # ~ cnt = find_from_to_one(' ', 'nahposhuk', cnt)

    # ~ #	uni( cnt +',')
    # ~ cnt = cnt.replace('тыс.', '000').replace('млн', '000000').replace('&nbsp;', ' ').replace(' ', '').replace(' ', '')

    # ~ cnt = find_from_to_one('<doccount>', '</doccount>', p)
    cnt = find_from_to_one('<found priority="phrase">', "</found>", p)
    if cnt == "":
        cnt = find_from_to_one("наш", "страниц", p)
    try:
        cnt = int(cnt)
    except Exception as er:
        return -1
    return cnt


def cnt_mailru(p):
    p = text_to_charset(p, "cp1251", "utf8")
    if (
        p.find(
            """<title>
&nbsp;&mdash;
Яндекс:
ничего не найдено
</title>"""
        )
        != -1
        or p.find(
            """Яндекс:
ничего не найдено
"""
        )
        != -1
        or p.find("&mdash; Яндекс: ничего не найдено") != -1
    ):
        return 0
    p = do_lower(p).replace("&nbsp;", " ")

    # 	cnt = find_from_to_one('нашлось ', 'ответ', p)
    # 	if cnt=='':
    # 		cnt = find_from_to_one('нашлось ', 'страниц', p)
    # 	if cnt=='':
    # 		cnt = find_from_to_one('нашлась ', 'страниц', p)
    # 	if cnt=='':
    # 		cnt = find_from_to_one('нашёлся', 'ответ', p)
    # 	if cnt=='':
    # 		cnt = find_from_to_one('нашёлся ', 'страниц', p)

    cnt = find_from_to_one("foundCount: ", ",", p)

    if cnt == "":
        cnt = find_from_to_one("наш", "страниц", p)
    cnt = find_from_to_one(" ", "nahposhuk", cnt)

    # 	uni( cnt +',')
    cnt = (
        cnt.replace("тыс.", "000")
        .replace("млн", "000000")
        .replace("&nbsp;", " ")
        .replace(" ", "")
        .replace(" ", "")
    )
    if cnt == "":
        return -1

    try:
        cnt = int(cnt)
    except Exception as er:
        return -1
    return cnt


def cnt_g(p):
    # 	cnt = find_from_to_one('&amp;swrnum=', '"', p)
    # 	if cnt=='':
    # 		if p.find("""Не найдено ни одного документа, соответствующего запросу""")!=-1:
    # 			return 0
    # 		p = text_to_charset(p, 'cp1251', 'utf8')
    # 		if p.find("""Не найдено ни одного документа, соответствующего запросу""")!=-1:
    # 			return 0
    # 		else:
    # 			wait_for_ok('unknown cnt_g, check')
    #
    # 	return int(cnt)

    p = text_to_charset(p, "cp1251", "utf8")

    if (
        p.find("<li>Убедитесь, что все слова написаны без ошибок") != -1
        or p.find("<li>Make sure that all words are spelled correctly.</li>")
        != -1
    ):
        return 0

    cnt = find_from_to_one("из приблизительно <b>", "<", p)
    if cnt == "":
        cnt = find_from_to_one("из <b>", "<", p)

    if cnt == "":
        cnt = find_from_to_one("Результатов: примерно ", "<", p)

    if cnt == "":
        cnt = find_from_to_one("Результатов: ", "<", p)

    if cnt == "":
        cnt = find_from_to_one("Результатов: примерно ", "<", p)

    cnt = cnt.replace("&nbsp;", "").replace("&#160;", "")
    if cnt == "":
        return -1
    try:
        cnt = int(cnt)
    except Exception as er:
        return -5

    return cnt


def get_domen_cena(domen):
    rash = find_from_to_one(".", "nahposhuk", domen)
    if rash in ["org.ru", "net.ru", "pp.ru", "com.ru"]:
        c = 12
    elif rash in ["ru"]:
        c = 3
    elif rash in ["com", "info", "net", "org", "us"]:
        c = 10
    elif rash in ["kiev.ua", "com.ua", "dp.ua"]:
        c = 10
    else:
        logger.error("[unknown cena for %s]" % domen)
        c = -1
        wait_for_ok()
    return c


def get_hreno_urls():
    """если в урле встречается такая хрень, значит урл 95% плохой - такие просто игнорим"""
    return """/tags/
/tag/
/search/
?tag
&tag
/category/
?q=
&q=
&nick=
tagid=
=tag
/tegs/
?alltag
alltag=
/teg/
&teg=
torrent
/alltag/
warez
prn=
profile/
profile=
arhnew
feed""".split(
        "\n"
    )


# archiv


def get_abuzniki():
    """список абузных доменов #donor"""
    domens0 = """legalbasis.ru
rabotaihobby.ru
komfortnyj-dom.info
iha.com
shelton.su
pcb-admin.ru
llentab.ua
dostavka05.ru
good-mebel.com
remontelektro.ru
na-slyx.ru
cabeltov.ru
marketing-revolution.ru
pchelenok.com
avtotehnologii.ru
climl.ru
vse-v-ogorod.ru
obl-ceram.ru
cservice.ru
stroytorg74.ru
tattoo.moy.su
vaspol.ru
salon-helga.ru
whatscookingamerica.net
famous-smoke.com
liskilife.ru
vadim-galkin.ru
kiddy-for.ru
evayoga.livejournal.com
investsuccess.org
iceberg.ru
mika-design.ru
autoeurope.ru
inoption.info
nepoznannoe.su
mauirealestate.net
inlavka.ru
autoeurope.ru
criativediamonds.com
life-child.com
domruss.ru
7u8.ru
samsebewebmaster.ru
sardtravel.ru
roomforromance.com
xn--62-mlcaoysjdt.xn--p1ai
ydoma.info
recons.ru
catfishes.ru
my-pitomec.ru
stroyinform.net
my-pitomec.ru
nsnbr-doctor.net
tdmetallukraine.com
tako-tako.ru
megamozg.kz
xn--80aatkd3aop.xn--p1ai
umnyestroiteli.ru
gn24.net
mencey.ru
medremark.ru
ice-nut.ru
magya-online.ru
masternpol.ru
salon-edelweiss.ru
livelikeyouarerich.com
remont-kvartir.zakaz-rabot.ru
remontmoskow.ru
caution-very-hot.com
domkopchenie.ru
coolbusinessideas.info
mypozvonok.ru
partner-org.blogspot.com
starhab.ru
512volt.ru
monolith.in.ua
french-selection.co.uk
startsmile.ru
superzapravka.ru
boqdanov.ru
makeit-up.ru
stardance.kiev.ua
akumulator.by
zhivem-legko.ru
pro-artroz.ru
velikan.info
512volt.ru
sadovod-moskva.ru
baragoziki.ru
profpanel.ru
365cars.ru
kak-nauchitsia.ru
alboo.ru
okna-i-balkony.com.ua
metizplant.ru
rlocman.ru
imbeton.ru
motopapa.ru
cleanter.by
linspb.ru
rutracker.org
zov.maxi.by
rambitteh.ru
ultradizz.ru
youtube.com
vsedlyavasdamy.ru
alibaba.com
differed.ru
prazdnik-na-bis.com
postroika.biz
rybalca.com
16mb.com
budumamoi.ru
cipotya.ru
chaechka.ru
all2lady.ru
enpf.ru
leskarelii.com.ua
freshremont.com
psychologyofchildren.wordpress.com
innovacia.com.ua
dom-dacha-svoimi-rukami.ru
komplektacya.ru
stroikairemont.com
www.maxvanrem.ru
instrumentprokat.ru
pregnant-club.ru
xn----7sbaati7bjfzfeu7c.xn--p1ai
www.pervenez.ru
www.opendveri.ru
stroi-specialist.ru
remont-stroitelstvo77.ru
ves-fundament.ru
www.biokrasota.ru
poleznie-otvety.ru
www.opendveri.ru
www.nanya.ru
instrument-63.ru
www.nashatorba.ru
nashatorba.ru
www.stroy38.ru
www.terem-pro.ru
www.gilkomplekt.ru
www.uralstroymet.ru
mastertim.ru
nttur.ru
d4w.ru
posba.ru
www.marinbiz.ru
marinbiz.ru
ornet.com.ua
domisad.org
newlesenka.ru
kazan.tiu.ru
gutaclinic.ru
terem-pro.ru
ideafirst.ru
spark-decor.com.ua
rubimsrub59.ru
sk-gorod.com
nalivnoj.ru
kozhalitsa.ru
sk-kuban.ru
am-aliance.ru
1comfort.by
radosti-v-zhizni.ru
ukrluki.com
bymed.ru
remontnn-ru.ru
remvk.ru
stroemtut.ru
nsnbr.nichost.ru
easytobook.com
srochnyremont.ru
active-personnel.ru
cenmart.ru
basis-pro.ru
pro-gnosis.ru
atinyexperience.blogspot.com
placen.com.ua
rosferrum.ru
stroi-specialist.ru
lnebo.ru
quick-step.spb.ru
chelyabinsk.tiu.ru
fix-news.ru
maxi.by
tdvasya.ru
novoselie-pereezd.ru
cenmart.ru
krovlia.od.ua
uznatvse.ru
kerama-center.com.ua
soter.kiev.ua
dohod-s-nulya.ru
vektor77.ru
ufaotdelka.ru
irinafefelova.ru
uznatvse.ru
balidreams.ru
nattik.ru
bytovuha.net
plitkalux.ru
w9601816777.narod.ru
nesiditsa.ru
biomed.ua
viart-tm.ru
antik-invest.ru
ecole-studio.com
lmoroshkina.ru
antik-invest.ru
dk-dom.ru
prikormrebenka.ru
dvertorg.ru
ekodomostroy.ru
vashdom.ru
sm-kk.ru
kovrolustry.ru
stroika-smi.ru
stroyedom.ru
kurortklinika.ru
www.dk.ru
dkvartal.ru
missis-x.com
isk-monolit.ru
veneciya-groupp.ru
svarplastik.ru
scobro.ru
lrknadzor.ru
tranio.ru
fitdeal.ru
prostozdorov.by
vistco.kiev.ua
vist.ua
ikonu.ru
lmoroshkina.ru
womanshappiness.com
news-medical.net
avonrussia.info
nesiditsa.ru
lumi.com.ua
galalux.ru
machineryzone.ru
nesiditsa.ru
sport-kosa.ru
gamaun.ru
rapz.net
shoone.ru
macus.pp.ua
look-films.org
getdohod.ru
wordpress-book.ru
gameswinx.ru
linstyle.ru
vse-sekrety.ru
jenskoezdorovye.ru
vse-sekrety.ru
linstyle.ru
sklad-servise.ru
gamanoid.ru
dv-pro.ru
lichnycabinet.ru
lyubovm.ru
da-sha.ru
sky-blog.net
kinotelik.net
globaldialog.ru
carpis.ru
doctor-notebookov.ru
kasko-vse.ru
diland.ru
beewoman.ru
topauthor.ru
medotvet.com
svetodiod96.ru
hino-chel.ru
stihi-dari.ru
invapolis.ru
haircare.knolab.com
dcreative.ru
fabrika-shkola.ru
gerasimovich.pro
oribelarus.by
site-ok.com.ua
obzorsystem.ru
radio-med.com.ua
lenexp.ru
montre-rose.com
all-remont.ru
spk-up.ru
womanshappiness.com
automotobike.ru
auto-profi.nn.ru
keramo-mama.ru
soblakami.ru
cleanter.by
thairent.ru""".split(
        "\n"
    )
    # wikipedia.org

    domens0 = [get_domen_from_url(x, want_www=False) for x in domens0]

    return domens0


def get_abuzniki_part():
    """не домены абузные, а именно части урла"""

    domens0 = """.ru.com
habrahabr.ru/qa/
youtube.
rutube.
79.174.66.165""".split(
        "\n"
    )

    return domens0


def get_yaca_provereno():
    return """klk.pp.ru
ka.pp.ru
koi8.pp.ru
vk.pp.ru
detektiv.pp.ru
frolov.pp.ru
cadebou.pp.ru
prikol.pp.ru
front.pp.ru
trali-vali.pp.ru
allstars.pp.ru
vagon.pp.ru
enigma.pp.ru
norilsk.pp.ru
smekalka.pp.ru
bog.pp.ru
krolik.pp.ru
gratis.pp.ru
mama.pp.ru
japancar.pp.ru
esperanto-mv.pp.ru
baidary.com
az-ua.com.ua
kmbooks.com.ua
darkside.kiev.ua
soho.com.ua""".split(
        "\n"
    )


def get_telderi_already():
    # тут сайты, которые я уже через телдери проверял - их опускаю
    f = r"d:\kyxa\!code\!actual\!temp\telderi\domens_already.txt"
    if not os.path.isfile(f):
        return []
    text = text_from_file(f)
    return text.split("\n")


def guess_expires(domen, text, bads={}):
    text = no_probely(text, {"..": "~"})
    text = no_probely(text, {"~~": "~"})
    text = text.replace("~", "")

    text2 = do_lower(text)

    if (
        text.find(" доступен к&nbsp;регистрации.</h2>") != -1
        or text.find('<div class="whois_domain_price_value">') != -1
    ):
        r = {
            "life": -1000,
            "status": True,
            "domen": domen,
        }
        return r

    # if text.find('mnt-by:           ua.imena')==-1 or text.find('mnt-by:           ua.iname')==-1:
    # 	continue

    expires = find_from_to_one("expires:          ", " ", text)

    if expires == "":
        expires = find_from_to_one("status:</td><td>ok-until ", "<", text2)

    if expires == "":
        expires = find_from_to_one("status:</td><td>ok-until ", "<", text2)

    if expires == "":
        expires = find_from_to_one("expires:</td><td>", "<", text)

    if expires == "":
        expires = find_from_to_one("Expiration Date:", "<", text)

        # Created on..............: 1994-12-14.
        # Expires on..............: 2021-12-13.
        # Record last updated on..: 2013-09-24.
    if expires == "":
        expires = find_from_to_one("Expires on..............: ", ".", text)

    if expires == "":
        expires = find_from_to_one("Expiry Date:", "\n", text)

    if expires == "":
        expires = find_from_to_one("Expires on:", "\n", text)

    if expires == "":
        expires = find_from_to_one("expires on ", "utc", text2)

    if expires == "":
        expires = find_from_to_one("expires on ", ".", text2)

    if expires == "":
        expires = find_from_to_one("expires on ", "\n", text2)

    if expires == "":
        expires = find_from_to_one("expires:", "<", text2)

    if expires == "":
        expires = find_from_to_one("expiration date:", "\n", text2)

    # modified:     2011-12-08 12:59:31 UTC
    # expires:      2013-12-11 15:54:50 UTC
    # query-source: 31.31.205.43
    if expires == "":
        expires = find_from_to_one("expires:", "UTC", text)

    if expires == "":
        expires = find_from_to_one("paid-till: ", "<", text2)

    if expires == "":
        expires = find_from_to_one("expire on", "\n", text2)

    if expires == "":
        expires = find_from_to_one(
            "Дата окончания регистрации:", "</tr>", text
        )
        expires = kl(expires)

    if expires == "":
        expires = find_from_to_one("Дата освобождения:", "</tr>", text)
        expires = kl(expires)

    if expires == "":
        expires = find_from_to_one("OK-UNTIL ", "\n", text)

    if expires == "":
        logger.warning("empty_expires")

    if domen.find(".mk.ua") != -1:
        expires = "?"

    if domen.find(".lv") != -1:
        expires = "?"

    if text.find("% No entries found for domain") != -1:
        expires = "!!!"

    expires = expires.strip()
    if expires.find(" ") != -1:
        expires = find_from_to_one("nahposhuk", " ", expires)
    if expires.find("\n") != -1:
        expires = find_from_to_one("nahposhuk", "\n", expires)

    if expires == "":
        bads["expires0"] = bads.get("expires0", 0) + 1

        if (
            text.find("whois.rrpproxy.net:</b>") == -1
            and text.find("http://who.godaddy.com/whoischeck.aspx?domain=")
            == -1
        ):
            bads["rrpproxy"] = bads.get("rrpproxy", 0) + 1
            # webbrowser.open(f)
            # wait_for_ok('not godaddy?')
            return {"status": False}
            # continue
        else:
            return {"status": False}
            # continue

    lasts = ["."]
    if expires[-1] in lasts:
        expires = expires[:-1]

    # uni(text)
    # wait_for_ok()
    registered = find_from_to_one("Дата регистрации:", "</tr>", text)
    registered = kl(registered)

    if expires == "":
        expires = find_from_to_one("expiration date:", "\n", text2)

    date = expires
    # logger.debug('%s %s' % (date, len(date)))

    # 20140518051532  - такие даты обрезаю
    if len(date) == 14:
        date = date[:8]

    want_frmt = "%Y.%m.%d"

    try:
        t_f = "%Y.%m.%d"
        seconds_registered = time.mktime(time.strptime(registered, t_f))
    except Exception as er:
        seconds_registered = time.time()

    # seconds_registered = time.time()
    seconds_now = time.time()

    formats = [
        "%Y%m%d",
        "%Y-%m-%d",
        "%Y.%m.%d",
        "%d-%b-%Y",
        r"%Y/%m/%d",
    ]  # тут описаны форматы http://docs.python.org/2/library/datetime.html

    new_date = ""
    seconds = ""
    life = ""

    # logger.debug('|%s|'%expires)
    if expires not in ["!!!", "?"]:
        temp = "?"
        for frmt in formats:
            try:
                temp = time.strptime(date, frmt)
                break
            except Exception as er:
                pass
        # logger.debug('%s %s' % (date, frmt))
        if temp == "?":
            return {"status": False}
            # continue
            webbrowser.open(f)
            wait_for_ok("unknown date |%s| for domen %s" % (date, domen))

        new_date = "%04d.%02d.%02d" % (temp[0], temp[1], temp[2])
        seconds = time.mktime(time.strptime(date, frmt))
        life = int((seconds - seconds_now) / (60 * 60 * 24))

        life = "%05d" % life

        life_full = int((seconds - seconds_registered) / (60 * 60 * 24))
        life_full = "%05d" % life_full

    r = {
        "domen": domen,
        "expires": expires,
        "new_date": new_date,
        "registered": registered,
        "life": life,  # сколько до смерти
        "life_full": life_full,  # сколько уже живет
        "seconds": seconds,
        "status": True,
    }

    return r


def check_page_tupo_bad(text):
    """входной текст должен быть в утф-8"""
    task = hitro_dict(text, "text")
    func_before = task.get("func_before", False)
    more_typo_bad = task.get("more_typo_bad", "")

    text = task["text"]  # в утф-8

    # 	text = text_to_charset(text, 'utf8')

    text2 = text
    if func_before != False:
        text2 = func_before(text)

    if text2.find("</allh>") > 0:
        text2 = find_from_to_one("</allh>", "nahposhuk", text2)
    # 	wait_for_ok()
    if text2.strip() == "":
        logger.debug("EmptyPage")
        return False

    phrases = """has been suspended</TITLE>
<title>Server is temporarily
color=red>Мы переехали
http-equiv="refresh"
http-equiv=Refresh
content="0; url=http:
<title>Internet Archive Wayback Machine</title>
<title>Hacked By
Данный сайт блокирован!<br>
<title>Server stoped</title>
<title>Under construction</title>
revenuedirect.com
function Decode()
<title>разработка</title>
Error: Could not connect to database.  Please try again later.
connect to local MySQL server through socket '/tmp/mysql.sock' (61)
Server Error-wbcgi
<title>500 Internal Server Error</title>
<title>404 Not Found</title>
<P>404/Not found</P>
<p class="mainTitle">Not in Archive.<br><br>
<p class="mainTitle">Path Index Error.<br><br>
<p class="mainTitle">File Retrieve Error
<title>Извините,
<title>Сайт закрыт
Site under construction
<title>Сайт временно заблокирован
<title>Парковая страница
<TITLE>[ Welcome to Web-hosting
upload your website into the public_html directory
<title>Not Found</title>
<title>Ошибка: несуществующий домен</title>
<title>ERROR 404</title>
<TITLE>Test Page
<title>Хостинг PeterHost
<title>Invision Power Board Database Error
This domain is for sale
<title>Domain Name Renewal
godaddy.com/gdshop
godaddy.com/parked
and is pending renewal or deletion</div>
the page you are looking for is not available
'Location': 'http://liveweb.archive.org
?redir=frame&uid
Cant connect to mysql server.
404" about="/404.html"
<center>This IP is being shared among many domains
&laquo;free-date&raquo;
<title>Services are suspended for this server</title>

<title>Обслуживание данного сайта было приостановлено
<b>Этот сайт заблокирован.</b>
этот сайт блокирован в связи с
Ошибка доступа к неактивному аккаунту
<p>This request could not be forwarded to the origin server
<title>ERROR: The requested URL could not be retrieved</title>
<h2>The requested URL could not be retrieved</h2>
<title>Services are suspended for this server
Account Has Been Suspended
Действие данного аккаунта временно прекращено
<title>Ошибка |
<title>Сайт недоступен
<title>Ошибка: запрошенный виртуальный сервер не существует
<title>Хостинг-Центр</title>
<p>В настоящее время доступ к сайту временно прекращен.</p>
<title>Services are suspended
<title>503 Service Temporarily Unavailable
http://expired.reg.ru/img/
<title>Аккаунт временно приостановлен
<title>Срок регистрации домена
<title>Runtime Error</title>
"convert_me">Истек срок регистрации домена
<title>Лучший хостинг в Екатеринбурге
<title>Срок регистрации домена
<title>Информация о домене</title>
<h1>Срок регистрации домена
<title>Истек срок регистрации домена</title>
<h1 class="blocked">Сайт
 expired</title>
<title>Object not found!</title>
<title>NetAngels - Хостинг сайтов Екатеринбург</title>
<title>Хостинг-провайдер TimeWeb.ru
sedoparking.com/
response at crawl time</p>
<title>Данный хостинг аккаунт был заблокирован
<b>Account disabled by server administrator.</b></font>
<h1><br><br>404 File (site) not found<br>
<title>Account Suspended</title>
"""
    phrases = text_to_charset(phrases, "utf8", "cp1251")

    # http://mdou-17.ru/

    ##эти обычно вирусные - проверять надо
    # String.fromCharCode(

    try:
        if more_typo_bad != "":
            phrases = phrases + "\n" + more_typo_bad
    except Exception as er:
        pass

    phrases = phrases.split("\n")

    for bad in phrases:
        if bad.strip() == "":
            continue
        # if text.find(bad)>0:
        if text.find(bad) != -1 or ifind(text, bad) != -1:
            logger.debug('TUPO BAD with "%s"' % bad)
            return True
    return False


if __name__ == "__main__":
    t = 1
    if t:
        u = "http://www.easternhotelier.com/where-can-i-buy-cheap-diazepam"
        logger.debug(get_domen_from_url(u))

        u2 = url_to_idna(u)
        logger.debug(u2)
        os._exit(0)

    t = 0
    t = 1
    if t:
        urls = """красота.рф
http://красота.рф/nolink
http://красота.рф/
http://google.com/
		"""

        urls = text_to_charset(urls, "utf8", "cp1251")
        urls = urls.split("\n")
        for url in urls:
            url = url.strip()
            if url == "":
                continue
            idna = url_to_idna(url)
            logger.debug("\n" * 2 + "%s %s" % (url, idna))

        os._exit(0)

    t = False
    t = True
    if t:
        urls = """http://pawn-portal.ru/showthread.php/2528-C-HUD-by-ANdy-Cardozo-Ghetto-King?s=f7a415a692b856b9c9c7e565dc588b8c&p=8635#post8635
http://adobe-flash-player.ru/forum/index.php?PHPSESSID=b7pauamaq2ckrc59s77g42mr97&board=2.0#good
http://adobe-flash-player.ru/forum/index.php?board=2.0&PHPSESSID=b7pauamaq2ckrc59s77g42mr97#good
http://adobe-flash-player.ru/forum/index.php?board=2.0&nahi=b7pauamaq2ckrc59s77g42mr97
http://adobe-flash-player.ru/forum/index.php?PHPSESSID=b7p.uamaq2ckrc59s77g42mr97&board=2.0#bad
http://adobe-flash-player.ru/forum/index.php?PHPSESSID=b7Pauamaq2ckrc59s77g42mr97&board=2.0#bad
http://adobe-flash-player.ru/forum/index.php?x=y&sec_sess=b7pauamaq2ckrc59s77g42mr97&board=2.0#good
http://adobe-flash-player.ru/forum/index.php?sec_sess=b7pauamaq2ckrc59s77g42mr97&board=2.0#good
http://adobe-flash-player.ru/forum/index.php?sec_sess=aaaaaaaaaaaaaaaaaaaaaaaaaa#bad
http://adobe-flash-player.ru/?
line
""".split(
            "\n"
        )
        for url in urls:
            logger.debug("\n" * 2 + url)
            new_url = remove_sessions_from_url({"u": url,})
            logger.debug("	new_url=%s" % new_url)
        os._exit(0)

    t = False
    t = True
    if t:
        page = "hello"
        # 		page = '
        logger.debug(check_page_tupo_bad(page))
        os._exit(0)

    t = False
    t = True
    if t:
        urls = """http://google.com:80/1""".split("\n")
        for url in urls:
            logger.debug("\n" * 2 + "%s %s" % (url, url_without_port(url)))
        os._exit(0)

    # text = text_from_file(r'd:\kyxa\!code\!actual\monitore\avtomonitore_ru\temp\uknown_situations\d1ff185b01420bfe3e6fae6824d46a24.html')
    # domen = 'sportway.in.ua'
    # text = text_from_file(r'temp/whois.html')
    # domen = 'eavatars.ru'
    # logger.debug(guess_expires(domen, text))

    domen = "vsesmski.ru"
    text = text_from_file(r"temp/whois.html")
    logger.debug(guess_expires(domen, text))

    os._exit(0)

    logger.debug(get_domen_from_url("http://www.skirda.www.net/adf", False))
    os._exit(0)
    urls = """http://ezcreditoffers.com/news/insurance_news.html?PHPSESSID=9c6ad507ea3023d5d6e51ce3e1370b59
http://ezcreditoffers.com/news/insurance_news.html?PHPSESSID=9c6ad507ea3023d5d6e51ce3e1370b59&""".split(
        "\n"
    )
    for url in urls:
        logger.debug("%s %s" % (url, remove_vars_from_url(url)))
    os._exit(0)

    get_all_links_from_html("", "")
    os._exit(0)

    # 	logger.debug(get_vars_from_url('http://forum.onthewheels.ru/viewtopic.php?pid=218&utm_source=direct_click_sergijko&utm_medium=ppc&utm_term=audi100_asoc&utm_campaign=m-audi100-1&utm_content=audi100-1-7'))
    urls = [
        "phpbb2/viewtopic.php?t=4734&start=0&postdays=0&postorder=asc&highlight=&sid=d9d49ce97790f50385e5742a47d3ab35"
    ]
    for url in urls:
        logger.debug(url)
        logger.debug(
            remove_vars_from_url(url, "PHPSESSID phpsessid sid highlight sid")
        )
    # 	urls = ['/?var1=p&s=1', '/index.php?var1=s2', 'http://index.p/set?vaq=x&var1=x&var2=y']
    # 	for url in urls:
    # 		print
    # 		logger.debug(url)
    # 		logger.debug(remove_vars_from_url(url, 'var1 var2'))
    os._exit(0)

    # 	url = 'http://www.sub.vitaminov.net/rus-drugsafety-0-0-6352.html'
    # 	url = 'http://joblink.delaware.gov/ada/leavesite.cfm?title=State+of+Delaware+Job+Opportunities&url=http://oulary.org.ru'
    #
    # 	poddomen = get_domen_from_url(url)
    # 	domen = get_domen_from_poddomen(poddomen)
    # 	good_url = get_good_url(url, True)
    # 	logger.debug('%s %s' % (poddomen, domen))
    # 	logger.debug(good_url)

    # 	u = '/job/?PHPSESSID=05f79672cc31819dd26d2c8832605bda'
    # 	logger.debug(remove_vars_from_url(u, 'PHPSESSID'))

    html = """<TD width=96 height=121 align=center valign=top background=/new_img/base/tkani.gif>
 <a style=text-decoration:none href=http://frobsersere.pp.ru/?mod=page&prefix=tkani&page=1&lang=en&PHPSESSID=21749adcf98755f8281143fbcded6306 class=white_menu_tkani>
<img src=/new_img/base/empty.gif width=50 height=80 border=0>
<br>
</a>

  <a style=text-decoration:none href=http://frobsersere.pp.ru/?PHPSESSID=21749adcf98755f8281143fbcded6306 class=white_menu_tkani>
Upholstery fabrics</a>

  <a style=text-decoration:none href=http://frobsersere.pp.ru/?mod=page&prefix=tkani&page=1&lang=en&PHPSESSID=21749adcf98755f8281143fbcded6306 class=white_menu_tkani>
Upholstery fabrics</a>"""

    html = remove_sessions_from_page(html)
    logger.debug("html=%s" % html)
