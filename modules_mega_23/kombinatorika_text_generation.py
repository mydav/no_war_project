# -*- coding: utf-8 -*-

from modules import *
import random
import re

# from my_machine_learning import *
from modules_mega_23.kombinatorika import *


def prettify_text(text):
    """убираем из текста новые строки и т.д."""
    new_text = no_probely(
        text,
        {"  ": " ", " ,": ",", " .": ".", "..": ".", "\n": " ", "    ": " "},
    )
    new_text = no_probely(new_text)
    return new_text


def generate_text0(text, d1="((", d2="))", ili="%", debug=False):
    """получаем шаблон текста, и генерируем все тексты из него"""
    items = text.split(ili)
    phrases = []
    zsuv = 0
    if debug:
        logger.debug("base text: " + text)

    while len(text) > 0:
        pos2 = text.find(ili, zsuv)
        item = text[:pos2]
        if debug:
            logger.debug(
                "pos2 %s %s %s" % (pos2, item.count(d1), item.count(d2))
            )
            # logger.debug(item)
        #        if pos2<0:
        if pos2 < 0:
            if debug:
                logger.debug("appending: " + text)

            phrases.append(text)
            break
        if item.count(d1) == item.count(d2):
            phrases.append(item)
            text = text[pos2 + len(ili) :]
            zsuv = 0
            if debug:
                logger.debug(
                    "     found phrase: " + item + "\n\nleave text: " + text
                )
        else:
            zsuv = pos2 + len(ili)

    if debug:
        logger.debug("found phrases: ")
        show_list(phrases)
    real_phrases = []
    for phrase in phrases:
        real_phrases.append(generate_text_min(phrase))
    real_phrases = slitj_list_listov(real_phrases, 0)
    return real_phrases


def generate_text_re(text, d1="{", d2="}", ili=r"|"):

    variants = [""]
    tpl = f"([{d1}{ili}{d2}])"
    tpl = f"([{d1}{ili}{d2}])"
    print(f"{tpl=}")
    # tpl = r"([{\|}])"
    elements = re.split(tpl, text)

    inside = False
    options = []
    for elem in elements:
        if elem == "{":
            inside = True
            continue
        if not inside:
            variants = [v + elem for v in variants]
        if inside and elem not in "|}":
            options.append(elem)
        if inside and elem == "}":
            variants = [v + opt for opt in options for v in variants]
            options = []
            inside = False

    print(*variants, sep="\n")


def generate_text_min(text, d1="((", d2="))", ili="%", debug=False):
    """получаем шаблон текста, и генерируем все тексты из него"""
    new_text = text
    if text.find(d1) == -1:
        return [text]

    #    ищем индексы того что нам заменять надо
    items = text.split(d1)
    indexes = []
    index_to_word = {}
    i = 0
    for item in items:
        phrase = find_from_to_one("nahposhuk", d2, item)
        if phrase == "":
            continue

        new_text = new_text.replace(d1 + phrase + d2, d1 + str(i) + d2)
        words = phrase.split(ili)
        if debug:
            show_list(words)
        words_i = range(0, len(words))
        indexes.append(words_i)
        for j in words_i:
            if i not in index_to_word:
                index_to_word[i] = {}
            index_to_word[i][j] = words[j]

        i += 1

    all_perestanovki = get_perestanovki(indexes)
    if debug:
        logger.debug("all_words: %s" % index_to_word)
        logger.debug("indexes: " % indexes)
        logger.debug("all_perestanovki: %s" % all_perestanovki)
        logger.debug(f"{new_text=}")
        logger.debug("col variantov: %s" % len(all_perestanovki))

    variants = []
    for perest in all_perestanovki:
        variant = new_text
        j = 0
        for k in perest:
            variant = variant.replace(d1 + str(j) + d2, index_to_word[j][k])
            j += 1
        if debug:
            logger.debug("    " + variant)
        variants.append(variant)

    return variants


def generate_text(text, d1="((", d2="))", ili="%", debug=False):
    """ф-я генерации текста"""
    new_text = text

    cnt = 0
    search_is_doned = False
    all_phrases = []
    while True:
        cnt += 1
        levels = vlozhennostj(new_text, d1=d1, d2=d2, debug=debug)
        if debug:
            logger.debug(f"{cnt=} {levels=}")

        levels_to_change = levels.keys()
        if len(levels_to_change) == 0 or search_is_doned:
            break

        last_level = max(levels_to_change)
        levels_to_change = list_minus_list(levels_to_change, [last_level])
        levels_to_change.sort()
        levels_to_change.reverse()
        if debug:
            logger.debug(f"{levels_to_change=}")
        #    делаем на 1 уровень меньше
        #    level = 1
        #    levels_to_change = [1]
        if last_level == -1:
            break

        if last_level == 0:
            changing_now = [last_level]
        else:
            changing_now = [last_level - 1]

        for level in changing_now:
            if debug:
                logger.debug(f"{level=} ({changing_now=}")

            if len(levels_to_change) == 0:
                all_phrases = generate_text0(new_text)

                search_is_doned = True
                if debug:
                    logger.debug("the end")
                break

            for w in levels[level]:
                all_phrases = generate_text0(w)
                new_text = new_text.replace(
                    d1 + w + d2, d1 + ili.join(all_phrases) + d2
                )

        #        levels = vlozhennostj(new_text)
        #        show_dict( levels )

    if debug:
        print(f"всех фраз: {len(all_phrases)}")
    return all_phrases


def vlozhennostj(text, d1="((", d2="))", debug=False):
    """ищем уровень вложенности условий"""

    #    находим максимальную вложенность
    items = text.split(d2)
    urovni = [0]
    for item in items:
        urovni.append(item.count(d1))
    max_urovenj = max(urovni)
    if debug:
        logger.debug(f"{max_urovenj=} for {urovni=}")

    #    находим все фразы на максимальном уровне
    phrases = []
    levels = {}
    zsuv = 0
    while True:
        pos2 = text.find(d2, zsuv)
        item = text[:pos2]
        zsuv = pos2 + len(d2)
        if pos2 < 0:
            break
        #        logger.debug(item)
        phrase = find_phrase(item)[len(d1) :]
        text_do = find_from_to_one("nahposhuk", phrase + d2, text) + phrase
        cnt_d1 = text_do.count(d1)
        cnt_d2 = text_do.count(d2)
        level = cnt_d1 - cnt_d2 - 1
        if level not in levels:
            levels[level] = []
        levels[level].append(phrase)

        if cnt_d1 - cnt_d2 == max_urovenj:
            phrases.append(phrase)

    if debug:
        logger.debug(f"{levels=}")
    return levels


def find_phrase(text, d1="((", d2="))", debug=False):
    """ищу кусок текста до разделителя"""
    #    ищу позицию незакрытой скобки
    text = reverse_text(text)
    if debug:
        logger.debug(text)
    d11 = reverse_text(d1)
    d22 = reverse_text(d2)
    zsuv = 0
    while True:
        pos1 = text.find(d11, zsuv)
        pos2 = text.find(d22, zsuv)
        zsuv = pos1 + len(d11)
        if debug:
            logger.debug("%s %s" % (pos1, pos2))
        if pos2 > pos1 or pos1 < 0 or pos2 < 0:
            break
    phrase = reverse_text(text[: pos1 + len(d11)])
    if debug:
        logger.debug(phrase)
    return phrase


def reverse_text(text):
    new_text = []
    for i in text:
        new_text.append(i)
    new_text.reverse()
    text = "".join(new_text)
    return text


def check_sintaxis(text):
    """проверка синтаксиса"""
    pass


def get_real_variants(template_title, cnt, WORDS_1, WORDS_2, WORDS_3, WORDS_4):

    variants = generate_text(template_title)

    variants = sample(
        variants, min(len(variants), 10000)
    )  #    оставляю нужное количество вариантов (пока 2000)
    #    варианты ложу в один файл
    for i in range(0, len(variants)):
        variants[i] = no_probely(
            variants[i], {"  ": " ", " ,": ",", " .": ".", "..": "."}
        )
    shuffle(variants)

    #    теперь подставляю в шаблон мои значения
    real_variants = []
    WORDS1 = WORDS_1.split(",")
    WORDS2 = WORDS_2.split(",")
    WORDS3 = WORDS_3.split(",")
    WORDS4 = WORDS_4.split(",")

    show_list(WORDS1)

    WORDS_1 = ", ".join(sample(WORDS1, min(2, len(WORDS1))))
    WORDS_2 = ", ".join(sample(WORDS2, min(2, len(WORDS2))))
    WORDS_3 = ", ".join(sample(WORDS3, min(2, len(WORDS3))))
    WORDS_4 = ", ".join(sample(WORDS4, min(2, len(WORDS4))))
    logger.info("WORDS_1 %s" % WORDS_1)

    WORDS1 = sample(WORDS1, min(2, len(WORDS1)))
    WORDS2 = sample(WORDS2, min(2, len(WORDS2)))
    WORDS3 = sample(WORDS3, min(2, len(WORDS3)))
    WORDS4 = sample(WORDS4, min(2, len(WORDS4)))
    for i in range(0, len(variants)):
        variant = variants[i]
        num_key = choice(range(0, len(WORDS1)))
        w1 = WORDS1[num_key]
        w2 = WORDS2[num_key]
        w3 = WORDS3[num_key]
        w4 = WORDS4[num_key]

        shuffle(WORDS1)
        shuffle(WORDS2)
        shuffle(WORDS3)
        shuffle(WORDS4)

        text1 = ", ".join(WORDS1)
        text2 = ", ".join(WORDS2)
        text3 = ", ".join(WORDS3)
        text4 = ", ".join(WORDS4)
        #        new_variant = no_probely(variant, {'WORDS1_1':w1, 'WORDS2_1':w2, 'WORDS3_1':w3, 'WORDS4_1':w4, 'SITE':SITE})
        new_variant = no_probely(
            variant,
            {
                "WORDS1_1": text1,
                "WORDS2_1": text2,
                "WORDS3_1": text3,
                "WORDS4_1": text4,
                "SITE": SITE,
            },
        )
        new_variant = no_probely(
            new_variant,
            {
                "WORDS1": WORDS_1,
                "WORDS2": WORDS_2,
                "WORDS3": WORDS_3,
                "WORDS4": WORDS_4,
            },
        )
        new_variant = no_probely(new_variant, {"    ": " "})
        new_variant = no_probely(new_variant)
        real_variants.append(new_variant)
        if i >= cnt:
            break
    return real_variants


def generate_predlozhenia(phrases, replaces={"  ": " "}):
    rez = []
    for phrase in phrases:
        phrase = phrase.strip()
        if phrase == "":
            continue

        phrases = generate_text(phrase)
        if len(phrases) > 0:
            pr = choice(phrases)
            pr = no_probely(pr, replaces)
            if pr != "":
                rez.append(pr)
    return rez


def generate_text_get_random(text, d1="((", d2="))", ili="%"):
    parts = generate_text_min(text, d1, d2, ili)
    random.seed(int(time.time() + randint(1, 1000)))

    shuffle(parts)
    return parts[0]


def insert_rand_chislo(new_body, ot0="[rand-", do0="]", delim="-"):
    random.seed(int(time.time() + randint(1, 1000)))

    # ВСТАВКА РАНДОМОГО Ч�?СЛА
    items = new_body.split(ot0)
    news = [items[0]]
    for item in items[1:]:
        ot_do = find_from_to_one("nahposhuk", do0, item)
        after = find_from_to_one(do0, "nahposhuk", item)
        ot, do = ot_do.split(delim)
        ot = int(ot)
        do = int(do)
        chislo = randint(ot, do)
        news.append(str(chislo))
        news.append(after)
    new_body = "".join(news)
    return new_body


def tpl_to_more_names(items=[], replaces="auto", otl=0):
    """
    '[i]':'0-5','[1-2]':'1-2', '[0-9]':'0-9',
    на вход получаем шаблоны, и размножим его
        "p[i]name",
        "p[i]balance",

    regions_poker = [
        #"no_template",

        #"p[i]name",
        #"p[i]balance",

        "p[i]new[1-2]test",

        "x[0-1]y[1-2]z[0-1]",
        "x1[0-1]y1[1-2]",
        "x2[0-1]",
    ]
    replaces = {'[i]':'0-5', '[1-2]':'1-2'}
    """
    fun = "tpl_to_more_names"
    # otl = 0
    # otl = 0

    if otl:
        logger.debug("[%s" % fun)

    if type(items) != type([]):
        items = [items]

    if replaces == "auto":
        replaces = {
            "[ints]": 1,
        }

    if otl:
        logger.debug("items:")
        show_list(items)

        logger.debug("replaces0:")
        show_dict(replaces)

    if replaces.get("[ints]", 0) == 1:
        if otl:
            logger.debug("searching [x-y]")
        del replaces["[ints]"]
        new_items = []

        for item in items:
            parts = item.split("[")[1:]
            i = 0
            for part in parts:
                i += 1
                v = find_from_to_one("nahposhuk", "]", part)
                try:
                    x, y = v.split("-")
                    x = int(x)
                    y = int(y)
                    key0 = "[%s]" % (v)
                    key = "[%s:%s]" % (i, v)
                    item = item.replace(key0, key, 1)
                    replaces[key] = v
                    #'[1-2]':'1-2'
                except Exception as er:
                    logger.error("%s ERROR %s" % (fun, er))
                    continue
            new_items.append(item)
        items = new_items[:]

    if otl:
        logger.debug("replaces:")
        show_dict(replaces)
        logger.debug("new_items:")
        show_list(items)

    for k in replaces:
        v = replaces[k]
        x, y = v.split("-")
        replaces[k] = [int(x), int(y)]

    if otl:
        show_dict(replaces)

    checked = set()
    new_items_all = []
    for name in items:
        if otl:
            Show_step(name)

        new_items = []
        to_check = [name]
        while True:
            if len(to_check) == 0:
                break

            name = to_check.pop()

            if otl:
                logger.debug("to_check %s" % to_check)

            if name in checked:
                continue

            checked.add(name)

            keys = replaces.keys()
            found = 0
            for repl in keys:
                if name.find(repl) != -1:
                    found = 1
                    ot, do = replaces[repl]
                    tpl = name
                    for i in range(ot, do + 1):
                        name = tpl.replace(repl, str(i))

                        if name not in checked:
                            to_check.append(name)

                    if otl:
                        logger.debug("replaced %s %s" % (repl, new_items))

            if not found:
                new_items.append(name)

            if otl:
                logger.debug("new_items: %s" % new_items)
            new_items_all.append(new_items)

    new_items_all = slitj_list_listov(new_items_all)
    new_items_all = unique_with_order(new_items_all)

    if otl:
        logger.debug("final:")
        show_list(new_items_all)

    if otl:
        logger.debug("+%s all items %s]" % (len(new_items_all), fun))

    return new_items_all


if __name__ == "__main__":
    special = "generate_text_re"
    special = "generate_text"

    if special == "generate_text_re":
        text = "{Hello|Good morning|Hi}{. We|, we} have a {good |best }offer for you."
        generate_text_re("")

    elif special == "generate_text":
        templates = clear_list(
            """
        # Пропаганда (убийств%войны% продолжения войны% продолжения военных действий%продолжения войны) (на Украине%в Украине)
        #Пропаганда (%истребления%убийства%) (украинского народа%украинцев%украинской нации%украинских людей%жителей Украины)
        ((11%12)%(21%22%(31%32))) (01%02)
        """,
            bad_starts=["#"],
        )
        debug = True
        func = generate_text_min
        d1 = "("
        d2 = ")"
        ili = "%"
        for tpl in templates:
            logger.info(f"{tpl=}")
            t_start = time.time()
            variants = func(tpl, d1=d1, d2=d2, ili=ili, debug=debug)
            duration = time.time() - t_start
            logger.info(f"{duration:.3f} seconds for {variants=}")

            step = 0
            while True:
                step += 1
                variant = variants[0]
                logger.info(f"{step=} {variant=}")

                logger.info(f"{duration:.3f} seconds for {variants=}")

                t_start = time.time()
                variants = func(variant, d1=d1, d2=d2, ili=ili, debug=debug)
                duration = time.time() - t_start
                logger.debug(
                    f"  +{step=} {duration:.3f} seconds for {variant=}, all {variants=}"
                )
                break

    else:
        logger.critical(f"unknown {special=}")

    os._exit(0)
    t = 1
    t = 0
    if t:
        t = 1
        t = 0
        if t:
            replaces = {
                "[ints]": 1,
            }
            replaces = "auto"

            otl = 0

            keys_money = [
                "c0pot[0-1]",
                #'p[0-10]balance',
                #'p[0-10]bet',
            ]
            logger.debug("replaces=%s" % replaces)
            keys_money = tpl_to_more_names(
                keys_money, replaces=replaces, otl=otl
            )
            logger.debug("keys_money %s" % keys_money)
            # wait_for_ok()

            keys_money2 = [
                "c0pot[0-1]",
                #'p[0-10]balance',
                #'p[0-10]bet',
            ]
            keys_money2 = tpl_to_more_names(
                keys_money2, replaces=replaces, otl=otl
            )
            logger.debug("keys_money2 %s" % keys_money2)

            os._exit(0)

        # что в покере?
        regions_poker = [
            # "no_template",
            # "p[0-1]name",
            # "p[i]name",
            # "p[i]balance",
            # "p[i]new[1-2]test",
            "x[0-1]y[1-2]z[0-1]",
            "x1[0-1]y1[1-2]",
            "x2[0-1]",
        ]

        regions = tpl_to_more_names(regions_poker)
        show_list(regions)
        os._exit(0)

    os._exit(0)
    d1 = "(("
    d2 = "))"
    ili = "%"
    end_delimiter = "\n###\n"

    f_to = "variants.txt"

    text = "Звонок. Диалог. ((Альо%Да%Я Вас слушаю)) ((по телефону%по мобильному%))"
    text2 = "((((Звучит%Я услышал)) ((звонок%дзелень)) % Зазвенело)). Диалог. ((Альо%Да%Я Вас слушаю)) ((по телефону%по мобильному%))"  # "0 ((1%((a%b%c)) 2)) 0" #
    text4 = "SEO club party - это%Сеошникам ((гарантируем%обеспечиваем))"
    text4 = "много%"
    text4 = (
        "по ((приятным%минимальным%оптимальным)) ценам%на выгодных условиях"
    )
    text4 = "различно((й степени%го уровня)) сложности"
    text3 = """(( ((SEO club party - это%Сеошникам ((гарантируем%обеспечиваем)) ))
    оперативные поставки ((много%))((пива%пивища))
    ((по ((приятным%минимальным%оптимальным)) ценам%на выгодных условиях)).%))
    ((Наш клуб это - ((поддерживаемый в актуальном состоянии%регулярно пополняемый)) чайник с пивом (( и водой%)) ((, а так же банка варенья%)).%))
    ((Клуб ((профессионально%)) реализует проекты
        ((различно((й степени%го уровня)) сложности))
        с ламерами и лузерами ((типа %)) поднимая    ((, и забодясь о ((супер%)) присутствии в выдаче)).%
    ))
    ((Также сео клуб предлагает бублики
        (( ((пряник%))ванильные%((анчоусо%))кучери)).%))
        ((Наши специалисты ((производят%выполняют)) ((профессиональный%)) подбор ((слов%фраз)) ((исходя из%на основании)) индивидуальных ((потребностей%нужд)) ((клиента%партнера)).%
    ))
    ((
        ((Клуб ((выполняет%производит))%Осуществляется ))
        обслуживание на честном слове.%
    )) """

    text_mamba = """Я ((очень%)) ((горячая%жгучая%темпераментная%опасная%сексуальная%)) ((штучка%блондинка%брюнетка%ведьмочка%девочка%выдумщица)) и ((люблю%обожаю%непрочь)) ((побаловаться%развлечься))...
Не каждый мне ((подойдет%пара%союзник)), я ((хочу%жажду%ищу)) ((сильнейшего%самого сильного%самого лучшего)) ((самца%мужчину))...
Здесь я не ((могу%смогла)) ((выложить%опубликовать%показать)) все ((фото%достоинства)) моего ((прекрасного%совершенного)) тела, поэтому увидеть ЗА ЧТО вы будете ((бороться%бросать своих подружек%бросать все свои дела)) можно [url="{{url}}"]здесь[/url]"""

    text_subject = """((привет%приветики%приветульки%хаюшки%хочу сказать%посмотрите на меня%посмотрите%я вас хочу%вы такое не видели%хочу вам показать%хочу показать%посмотрите%вникните%зацените%обалдеть))"""

    text_subject = """((((Привет%Приветики%Хай%Хаюшки%))((!!!%,%)) ((вот и я%а вот и я%это я%вот я%вот я какая))((!!!%!%.)))) ((((((Посмотри%Полюбуйся)) ((на меня%))))%Оцени)), какая я ((классная%клевая%красивая%суперская)) ((девчонка%девушка))((!%!!!%!!!!%.))"""

    #    text3 = """(( ((SEO club party - это%Сеошникам гарантируем %Сеошникам обеспечиваем )) %))""" #оперативные поставки ((много%))((пива%пивища)) ((по приятным ценам%по минимальным ценам%по оптимальным ценам%на выгодных условиях))."""
    #
    #    text3 = """((SEO club party - это%Сеошникам гарантируем %SEO club party - это%Сеошникам обеспечиваем )) оперативные поставки ((много%))((пива%пивища)) ((по приятным ценам%по минимальным ценам%по оптимальным ценам%на выгодных условиях)) % просто фраза % ((1%2))"""

    #    описания магазинов
    text_subject = """(( ((Предлагаем%Продаем)) велосипеды % Продажа велосипедов )) ((по ((приятным%минимальным%оптимальным)) ценам%на ((самых%очень%реально самых)) ((выгодных%приятных%оптовых%оптимальных)) условиях)). ((Попробуйте%Заходите)) и ((убедитесь%узнаете)) сами. """

    text_subject = """((Попробуйте%Заходите%Заходите на сайт%Посмотрите на наши кондиционеры)) и ((убедитесь%узнаете)) сами. (( ((Предлагаем%Продаем%У нас%Только у нас)) кондиционеры % Продажа велосипедов )) ((по ((приятным%минимальным%оптимальным)) ценам%на ((самых%очень%реально самых)) ((выгодных%приятных%оптовых%оптимальных)) условиях))."""

    text_subject = """(( Самые%Только ((самые%)) )) ((лучшие%дешевые%фирменные%брендовые%качественные)) кондиционеры ((%((от%на)) icondition.ru )) % icondition.ru ((это%-)) ((самые%)) ((лучшие%дешевые%фирменные%брендовые%качественные)) кондиционеры"""

    text_subject = """Кондиционеры от ((всех%)) ((самых%действительно%)) ((лучших%брендовых%мировых)) производителей """

    text_subject = """((�?нтернет магазин%Магазин%Продажа%Подбор)) ((самых%)) ((лучших%дешевых%фирменных%брендовых%качественных)) кондиционеров"""

    text_subject = """icondition.ru - (( продажа кондиционеров% ((предлагаем%продаем%)) кондиционеры)) ((по ((приятным%минимальным%оптимальным)) ценам%на ((самых%очень%реально самых)) ((выгодных%приятных%оптовых%оптимальных)) условиях)) ((от ((мировых%брендовых)) производителей%))"""

    text_subject = """(( Продажа кондиционеров% ((Предлагаем%Продаем%)) кондиционеры)) ((по ((приятным%минимальным%оптимальным%лучшим%выгодным)) ценам%на ((самых%очень%реально самых)) ((выгодных%приятных%оптовых%оптимальных)) условиях)) ((от ((мировых%брендовых)) производителей%)) на icondition.ru"""

    text_title = """((Магазин звука%Аудиотехника от%Техника от%Техника на%�?нтернет-магазин%Магазин техники)) ((Zvikii.ru)). ((%Фанаты звука?%Мы просто продаем НЕРЕАЛЬНЫЙ ЗВУК.%Любите звук?%Обсуждение техники.%Описание аудиотехники.)) ((Акустические системы%Комплекты акустики%Музыкальные центры%Усилители и ресиверы)) - ((у нас лучший выбор%выбирайте лучших%выбирайте только лучшее%выбирайте%всегда лучшее)). % (( Продажа аудиотехники% ((Предлагаем%Продаем)) аудиотехнику)) ((по ((приятным%минимальным%оптимальным%лучшим%выгодным)) ценам%на ((самых%очень%реально самых)) ((выгодных%приятных%оптовых%оптимальных)) условиях)) ((от ((мировых%брендовых)) производителей%))."""

    want_generate_titles_description = True  # False#
    want_generate_pages = True  # False#

    #    SITE = 'SportoSHOP.ru'
    #    phone = '+7(495) 778-49-57 '
    #    WORDS_1 = "mp3-плееры, наушники"
    #    WORDS_2 = "mp3-плееров, наушников"
    #    WORDS_3 = "mp3-плеерах, наушниках"
    #    WORDS_4 = "mp3-плеерам, наушникам"
    #
    #    WORDS_1 = "беговые дорожки,велотренажеры,палатки,спальные мешки"
    #    WORDS_2 = "беговых дорожек,велотренажеров,палаток,спальных мешков"
    #    WORDS_3 = "беговых дорожках,велотренажерах,палатках,спальных мешках"
    #    WORDS_4 = "беговым дорожкам,велотренажерам,палаткам,спальникам"

    SITE = "SantehnoShop.ru"
    phone = "+7(495) 979-0121 "
    WORDS_1 = "смесители, ванны, душевые кабины"
    WORDS_2 = "смесителей, ванн, душевых кабин"
    WORDS_3 = "смесителях, ваннах, душевых кабинах"
    WORDS_4 = "смесителям, ваннам, душевым кабинам"

    SITE = "DomTehno.ru"
    phone = "+7(495) 972-21-22 "
    WORDS_1 = "пылесосы, утюги, стиральные машины, швейные машины"
    WORDS_2 = "пылесосов, утюгов, стиральных машин, швейных машин"
    WORDS_3 = "пылесосах, утюгах, стиральных машин, швейных машин"
    WORDS_4 = "пылесосам, утюгам, стиральным машинам, швейным машинам"

    SITE = "KUHNOteh.ru"
    phone = "+7(495) 977-45-61 "
    WORDS_1 = "встраиваемые духовые шкафы, встраиваемые рабочие поверхности, вытяжки, микроволновые печи, посудомоечные машины"
    WORDS_2 = "встраиваемых духовых шкафов, встраиваемых рабочих поверхностей, вытяжек, микроволновых печей, посудомоечных машин"
    WORDS_3 = "встраиваемых духовых шкафах, встраиваемых рабочих поверхностях, вытяжках, микроволновых печах, посудомоечных машинах"
    WORDS_4 = "встраиваемым духовым шкафам, встраиваемым рабочим поверхностям, вытяжкам, микроволновым печам, посудомоечным машинам"

    SITE = "СarСommunity.ru"
    phone = "+7(495) 970-53-92 "
    WORDS_1 = "автоакустика, автомагнитолы, колесные диски, шины"
    WORDS_2 = "автоакустики, автомагнитол, колесных дисков, шин"
    WORDS_3 = "автоакустике, автомагнитолах, колесных дисках, шинах"
    WORDS_4 = "автоакустике, автомагнитолам, колесным дискам, шинам"

    SITE = "inditehnika.ru"
    phone = "+7(495) 973-22-13 "
    WORDS_1 = "фены, приборы для укладки, напольные весы, мужские лектробритвы, эпиляторы, женские электробритвы"
    WORDS_2 = "фенов, приборов для укладки, напольных весов, мужских лектробритв, эпиляторов, женских электробритв"
    WORDS_3 = "фенах, приборах для укладки, напольных весах, мужских лектробритвах, эпиляторах, женских электробритвах"
    WORDS_4 = "фенам, приборам для укладки, напольным весам, мужским лектробритвам, эпиляторам, женским электробритвам"

    SITE = "KLIMATizator.ru"
    phone = "+7(495) 977-90-27 "
    WORDS_1 = "вентиляторы, водонагреватели, обогреватели, очистители воздуха, увлажнители воздуха"
    WORDS_2 = "вентиляторов, водонагревателей, обогревателей, очистителей воздуха, увлажнителей воздуха"
    WORDS_3 = "вентиляторах, водонагревателях, обогревателях, очистителях воздуха, увлажнителях воздуха"
    WORDS_4 = "вентиляторам, водонагревателям, обогревателям, очистителям воздуха, увлажнителям воздуха"

    SITE = "vashej-dache.ru"
    phone = "+7(495) 971-22-29 "
    WORDS_1 = "газонокосилки, мойки высокого давления"
    WORDS_2 = "газонокосилок, моек высокого давления"
    WORDS_3 = "газонокосилках, мойках высокого давления"
    WORDS_4 = "газонокосилкам, мойкам высокого давления"

    if want_generate_pages:
        d_to = "pages"
        f_dostavka = os.path.join(d_to, "доставка.txt")
        f_o_nas = os.path.join(d_to, "о нас.txt")
        f_garantia = os.path.join(d_to, "гарантия.txt")

        text_dostavka = """

%<h3>Условия и стоимость доставки</h3>%Доставка ((%по Москве))

(( При заблаговременном заказе ((%(желательно за сутки) )) доставка % Доставка ((товара%товаров)) ((%клиенту)) в нашем ((интернет-магазине%магазине)) )) ((происходит%осуществляется)) ((%по мере возможности)) ((%уже%сразу)) на следующий день после ((заказа%отгрузки товара поставщиком на наш склад)).

((Практика показывает, что%Обычно)) сроки доставки не превышают ((1 дня%1-2 дней)) ((при наличии ((%свободных)) курьеров)).

((Если доставку произвести невозможно%При невозможности произвести доставку%Если Вам доставка не нужна)), товар ((всегда%до 19.00%обычно%)) можно забрать ((у нас в офисе%в нашем офисе)) ((%(обязательно согласовав это с нашими менеджерами) )).

((Если клиент отказывается от заказа%В случае отказа клиента от приемки и оплаты заказа)) из личных соображений, клиент ((должен оплатить%оплачивает%обязан оплатить)) доставку ((%независимо от суммы заказа%типа доставки)).

((%<h3>Доставка по Москве</h3>))               ((У нас%В нашем ((%�?нтернет)) магазине)) доставка ((заказа, стоимость которого%товаров, стоимость которых)) превышает ((5%10%15%20)) ((тысяч%тыс.)) ((руб.%рублей)), осуществляется ((совершенно%)) бесплатно в пределах МКАД.

((%Доставка ((товаров%заказа%)) за пределами МКАД ((считается%рассчитывается)) индивидуально в зависимости от конкретных условий доставки. ))

((<h3>Доставка в регионы России</h3>% ))               Доставка ((товаров%заказа)) в регионы России ((происходит%осуществляется)) только после 100% предоплаты ((Почтой России%коммерческим перевозчиком)) по согласованию с клиентом ((%за его счет)).

((Получить дополнительную информацию%Уточнить о выполнение заказа%Оформить новый заказ)) ((желательно%можно)) ((всегда%с 9 до 19.00)) ((%по телефону)): [phone] % Возможность доставки ((просьба%необходимо)) уточнять у ((нас%наших менеджеров)) по телефону [phone].

"""

        text_o_nas = """

Для Вас ((%, наши покупатели,%, наши посетители,)) мы предлагаем: % Покупая у нас, Вы получаете:

%((комфортные%качественные)) покупки% при минимальной трате личного времени

%((%только)) ((лучше цены%одни из лучших цен)) ((%среди интернет-магазинов%рунета))

%((%только)) ((лучшую%качественную)) продукцию ((%лучших)) ((%мировых)) производителей

%((%только)) ((лучшие)) модели, с ((лучшими%)) параметрами, ((по самым низким розничным ценам%с лучшим сочетанием цены и качества))

%гарантию ((%фирм-))производителей. Весь ((%наш)) товар, предлагаемый нами, сертифицирован.

%((регулярное%ежедневное%)) обновление ассортимента ((электронной витрины%витрины%каталога%магазина))

%((гарантируем%обеспечиваем)) ((%Вам)) ((очень%)) ((быструю%оперативную)) доставку

%((гарантируем%обеспечиваем)) ((%Вам)) внимательное обслуживание

Оформить заказ вы можете ((через сайт%по электронной почте%по телефону )).

%<h3>((Всегда готовы Вас выслушать%Спрашивайте%Звоните%Ждем Вашего звонка)): [phone]</h3>


"""

        text_garantia = """
(( Мы продаем%SITE ((предоставляет%продает))%Наш магазин ((предоставляет%продает)) )) только (( (("белую"%белую)) технику % (("белые"%белые%)) товары )).

% Гарантия ((%на все товары)) ((%идет%предоставляется)) от производителя.

((Гарантия подтверждается%Гарантийные обязательства подтверждаются)) гарантийным талоном от производителя, заверенным нашей печатью.

На все товары ((дается%распространяется%)) официальная гарантия от ((2%3%4%5%6)) ((мес.%месяцев)) до ((1 года%2 лет%3 лет%4 лет%5 лет)) в зависимости от ((товара%производителя)).

"""
        text2 = """


        """

        logger.info("dostavka")
        phrases = text_dostavka.strip().split("\n")
        #        phrases_dostavka = sample(phrases, len(phrases))#6
        phrases_dostavka = phrases

        #        phrases_dostavka = "%".join(phrases_dostavka)
        #        article_dostavka = generate_text(phrases_dostavka)[0]
        #        article_dostavka = no_probely(article_dostavka, {'  ':' ', '[phone]':phone})

        generated_predlozhenia = generate_predlozhenia(
            phrases_dostavka,
            {"  ": " ", " :": ":", "[phone]": phone, "SITE": SITE},
        )
        article_dostavka = "\n\n".join(generated_predlozhenia)
        text_to_file(article_dostavka, f_dostavka)

        logger.info("o nas")
        #        о нас
        phrases = text_o_nas.strip().split("\n")
        generated_predlozhenia = generate_predlozhenia(
            phrases, {"  ": " ", " :": ":", "[phone]": phone, "SITE": SITE}
        )
        article = "\n\n".join(generated_predlozhenia)
        text_to_file(article, f_o_nas)

        logger.info("garantia")
        #        гарантия
        phrases = text_garantia.strip().split("\n")
        generated_predlozhenia = generate_predlozhenia(
            phrases, {"  ": " ", " :": ":", "[phone]": phone, "SITE": SITE}
        )
        article = "\n\n".join(generated_predlozhenia)
        text_to_file(article, f_garantia)

    if want_generate_titles_description:

        ##    делаю свой новый генератор, который все генерирует
        #    phrases = """((Онлайн%Официальный)) сайт ((%интернет-))магазина ((%по продаже WORDS2_1))
        # ((Независимое%)) ((�?здание%�?нтернет-издание))  (( о ((WORDS3_1)) %, посвященное ((WORDS4_1)) ))
        # ((Магазин%Продажа)) WORDS2_1
        # ((Предлагаем%)) WORDS1_1
        # (( ((�?нформация%Общая информация%Портал)) ((о WORDS3_1%по теме WORDS1_1))
        # WORDS1_1. ((Форум%Статьи%Обзоры%Тесты%Новости%Руководства пользователей%Цены%Лента новостей%Ответы на вопросы)) ((по теме%)).
        # WORDS1_1. ((�?стория%Сведения о%�?нформация о)) компании%Контактная информация%Контакты%Новости компании%Дистрибьюторам%Каталог продукции%�?нформация для реселлеров%�?нформация о сервисных центрах%Где купить%Тесты продуктов%Список ((представительств%сервис-центров%сервисных центров)) % Рубрикация по производителям.
        # ((Публикуются%)) (( ((материалы%новости%статьи)) о WORDS3_1 % ((тесты%результаты тестирования%обзоры%технические характеристики%характеристики%описания%сравнения%помощь в выборе%описание технологий)) ((различных моделей%)) WORDS2_1))
        # WORDS1_1. Подборка ((советов%обзоров%статей%материалов%новостей%тестов%обзоров%результатов тестирования%технических характеристик%описаний%сравнений)) по тематике.
        # ((Каталог%Описания)) WORDS2_1 % ((Каталог продукции: WORDS1 ((и др.%)) )) % ((Цены на %Прайс-лист%Прайс)) на WORDS1_1""".split("\n")

        phrases = """((Магазин % ((Онлайн%Официальный)) сайт ((%интернет-))магазина)) ((%по продаже WORDS2_1))
    ((Независимое%)) ((�?здание%�?нтернет-издание))  (( о ((WORDS3_1)) %, посвященное WORDS4_1 ))
    ((Магазин%Продажа)) WORDS2_1
    ((Предлагаем%)) WORDS1_1
    ((�?нформация%Общая информация%Портал)) ((о WORDS3_1%по теме WORDS1_1))
    ((Публикуются%)) (( ((материалы%новости%статьи)) о WORDS3_1 % ((тесты%результаты тестирования%обзоры%технические характеристики%характеристики%описания%сравнения%описание технологий)) ((различных моделей%)) WORDS2_1))
    ((Помощь при выборе%Помощь в выборе%Советы при выборе)) WORDS2_1
    ((Каталог%Описания)) WORDS2_1 % ((Каталог продукции: WORDS1 ((и др.%)) )) % ((Цены на %Прайс-лист%Прайс)) на WORDS1_1
    """.strip().split(
            "\n"
        )

        phrases2 = """
    ((Форум%Статьи%Обзоры%Тесты%Новости%Руководства пользователей%Лента новостей%Ответы на вопросы)) ((по теме%))
    ((�?стория%Сведения о%�?нформация о)) компании%Цены%Контактная информация%Контакты%Новости компании%Дистрибьюторам%Каталог продукции%�?нформация для реселлеров%�?нформация о сервисных центрах%Где купить%Тесты продуктов%Список ((представительств%сервис-центров%сервисных центров)) % Рубрикация по производителям
    Подборка ((советов%обзоров%статей%материалов%новостей%тестов%обзоров%результатов тестирования%технических характеристик%описаний%сравнений))
    """.strip().split(
            "\n"
        )

        phrases4 = sample(phrases, len(phrases))
        phrases5 = sample(phrases, len(phrases))
        phrases_text4 = "%".join(phrases4)
        phrases_text5 = "%".join(phrases5)

        cnt = 2000  # сколько именно описаний нужно

        f_to_titles = "%s__тайтлы.txt" % SITE
        f_to_descr_short = "%s__краткое_описание.txt" % SITE
        f_to_descr_full = "%s__полное_описание.txt" % SITE
        #    генерим названия

        phrases_text = "%".join(phrases)
        #    phrases2 = phrases
        #    shuffle(phrases2)
        phrases_text2 = "%".join(phrases2)

        Show_step("генерация названия")
        template_title = "((SITE.%" + "SITE - )) ((%s)). ((%s))." % (
            phrases_text,
            phrases_text2,
        )
        #        template_title = "((SITE.%" + "SITE - )) ((%s))." % (phrases_text)
        logger.debug(template_title)
        real_variants = get_real_variants(
            template_title, cnt, WORDS_1, WORDS_2, WORDS_3, WORDS_4
        )
        text_to_file("\n".join(real_variants), f_to_titles)

        Show_step("генерация описания")
        template_title = "((%s)). ((%s))." % (phrases_text4, phrases_text5)
        logger.debug(template_title)
        real_variants = get_real_variants(
            template_title, cnt, WORDS_1, WORDS_2, WORDS_3, WORDS_4
        )
        text_to_file("\n".join(real_variants), f_to_descr_short)

        Show_step("генерация полного описания")
        template_title = "((%s)). ((%s)). ((%s))." % (
            phrases_text4,
            phrases_text5,
            phrases_text2,
        )
        logger.debug(template_title)
        real_variants = get_real_variants(
            template_title, cnt, WORDS_1, WORDS_2, WORDS_3, WORDS_4
        )
        text_to_file("\n".join(real_variants), f_to_descr_full)
