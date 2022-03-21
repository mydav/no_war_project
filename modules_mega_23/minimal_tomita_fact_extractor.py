#!/usr/bin/python
# -*- coding: utf-8 -*-

from modules import *

# from modules_mega_23.kombinatorika import get_perestanovki_from_dct

logger = get_logger(__name__)


def prepare_new_phrases_from_facts(
    tpl="$GAMEPART$", facts=[], vars={}, more_vars={}, debug=False
):
    """
    tpl = 'sport: $SPORT$, так что по русски это $SPORT:ru$ (в британии $SPORT:en$), часть игры: $GAMEPART:new_value$'
    new_facts = prepare_new_phrases_from_facts(tpl=tpl, facts=facts, vars=vars)

    Для каждого факта делаю новую фразу
    факт - это по сути словарь, который присутствует в шаблоне
    	$GAMEPART$
			"1st Quarter"
        $NUMBER$
                "0.5"
        $NUMBER1$
                "25.5"
        $SPORT$
                "Football"
    В vars для каждого ключа факта - дополнительная инфа
    	$GAMEPART$
			{'1st Quarter': '1/4', '2nd Quarter': '2/4'}
        $SPORT$
                {'Football': {'ru': '\xd0\xa4\xd1\x83\xd1\x82\xd0\xb1\xd0\xbe\xd0\xbb', 'en': 'Soccer'}, 'Basketball': '\xd0\x91\xd0\xb0\xd1\x81\xd0\xba\xd0\xb5\xd1\x82'}

    NUMBER:comma
    :new_value

    """
    fun = "prepare_new_phrases_from_facts"
    # debug = True

    tpl = tpl.replace("$SCORES$", more_vars.get("SCORES", "SCORES_NOT_FOUND"))

    phrases = []
    allowed_number_options = [
        "comma",
        "minus_znak",
        "plus_znak",
        "znak",
        "cut_zeros",
        "fora",
        "tm_tb",
    ]
    for num_fact, fact in enumerate(facts, 1):
        if debug:
            logger.debug(
                "fact %s/%s for tpl `%s`:" % (num_fact, len(facts), tpl)
            )
            show_dict(fact)

        repl = add_defaults({}, fact)

        tplvars = get_vars_with_settings_from_template(tpl, vars=vars)
        if debug:
            logger.debug("found %s tplvars:" % len(tplvars))
            show_list(tplvars)

        for num_var, tplvar in enumerate(tplvars, 1):
            if debug:
                logger.debug(
                    "replacing %s/%s %s" % (num_var, len(tplvars), tplvar)
                )
            raw = tplvar["raw"]
            reason = tplvar["reason"]
            name = tplvar["name"]
            options = tplvar["options"]

            if "fora" in options or "tm_tb" in options:
                options = options + ["comma", "cut_zeros"]

            if not name in fact:
                continue

            # value = ''
            value = fact[name]
            value_lower = fact[name].lower()

            if reason == "number":

                unallowed_options = list_minus_list(
                    options, allowed_number_options
                )
                if unallowed_options:
                    wait_for_ok(
                        "%s ERROR: unallowed_options for number: %s"
                        % (fun, unallowed_options)
                    )

                if "comma" in options:
                    value = value.replace(".", ",")

                if "cut_zeros" in options:
                    value = cut_zeros_after_dot(value)

                if (
                    "minus_znak" in options
                    or "plus_znak" in options
                    or "znak" in options
                ):
                    znak_option = ""
                    if "minus_znak" in options:
                        znak_option = "minus_znak"
                    elif "plus_znak" in options:
                        znak_option = "plus_znak"
                    elif "znak" in options:
                        znak_option = "znak"
                    else:
                        wait_for_ok(
                            "ERROR %s - unknown znak_option %s"
                            % (fun, options)
                        )
                    value = value_with_znak(value, option=znak_option)

            elif reason == "var":
                if name in vars:
                    vars_variants = vars[name]
                    vars_variants_lower = {}
                    if isinstance(vars_variants, dict):
                        for k, v in vars_variants.items():
                            vars_variants_lower[k.lower()] = vars_variants[k]

                        if debug:
                            logger.debug(
                                "vars_variants_lower %s" % vars_variants_lower
                            )
                        # show_dict(vars_variants_lower)
                    else:
                        wait_for_ok(
                            "unknown vars_variants with type "
                            % vars_variants_lower
                        )

                    if value_lower not in vars_variants_lower:
                        wait_for_ok(
                            "ERROR %s - found name=%s with value=%s, but value_lower `%s` not in vars_variants_lower=%s"
                            % (
                                fun,
                                name,
                                value,
                                value_lower,
                                vars_variants_lower,
                            )
                        )

                    # more_info = vars[name].get(value, vars[name].get(value_lower))
                    more_info = vars_variants_lower.get(value_lower)
                    # have more info about name $SPORT$=<type 'dict'> {'ru': '\xd0\xa4\xd1\x83\xd1\x82\xd0\xb1\xd0\xbe\xd0\xbb', 'en': 'Soccer'}
                    if debug:
                        logger.debug(
                            "have more_info about name %s with value=%s: %s %s"
                            % (name, value, type(more_info), more_info)
                        )
                        # wait_for_ok()

                    if options == []:
                        if debug:
                            logger.debug(
                                "    no options, so value=%s" % (value)
                            )
                        # value = value
                    else:
                        known_options = []

                        for option in options:
                            if 0:
                                pass
                            elif isinstance(more_info, str):
                                if option == "new_value":
                                    known_options.append(option)
                                    value = more_info
                                    if debug:
                                        logger.debug(
                                            "    add %s for option %s"
                                            % (value, option)
                                        )
                                    break

                            elif (
                                isinstance(more_info, dict)
                                and option in more_info
                            ):  # {en: '', ru: ''}
                                known_options.append(option)
                                value = more_info[option]
                                if debug:
                                    logger.debug(
                                        "    add %s for option %s"
                                        % (value, option)
                                    )
                                break

                        unallowed_options = list_minus_list(
                            options, known_options
                        )
                        if unallowed_options:
                            logger.debug("options: %s" % options)
                            logger.debug("known_options: %s" % known_options)
                            wait_for_ok(
                                "%s ERROR: unallowed_options for var: %s"
                                % (fun, unallowed_options)
                            )

                else:
                    logger.debug(
                        "%s ERROR: name %s not in vars %s" % (fun, name, vars)
                    )
                    wait_for_ok()

            else:
                wait_for_ok("%s ERROR: unknown reason %s" % (fun, reason))

            if debug:
                logger.debug("    replace `%s` with `%s`" % (raw, value))

            repl[raw] = value

        if debug:
            logger.debug("final repl:")
            show_dict(repl)
            # wait_for_ok()

        phrase = no_probely(tpl, repl).strip()

        # замена спец-переменных: {asia_fora(-0,75 2 0)}
        phrase = calculate_functions_in_text(
            phrase, "asia_fora", asia_fora_from_txt
        )
        phrase = calculate_functions_in_text(
            phrase, "noscore_handicap", noscore_handicap_from_txt
        )
        phrase = calculate_functions_in_text(
            phrase, "score_handicap", score_handicap_from_txt
        )
        phrase = calculate_functions_in_text(
            phrase, "dve_fory", dve_fory_from_txt
        )

        phrases.append(phrase)

    if debug:
        logger.debug("have %s phrases:" % len(phrases))
        show_list(phrases)

    return phrases


def multiTemplate_tomita_extract_facts(re_titles=[], *args, **kwargs):
    if not isinstance(re_titles, list):
        re_titles = [re_titles]

    hashes = set()
    all_facts = []
    for re_title in re_titles:
        # facts = minimal_tomita_extract_facts(re_title, *args, **kwargs)
        facts = minimal_tomita_extract_facts_for_multititles(
            re_title, *args, **kwargs
        )
        for fact in facts:
            h = to_hash(str(fact))
            if h in hashes:
                continue
            hashes.add(h)
            all_facts.append(fact)
    return all_facts


def minimal_tomita_extract_facts_for_multititles(
    re_title="",
    titles=[],
    vars={},
    ignore_spaces=True,
    ignore_case=True,
    debug=False,
):
    fun = "minimal_tomita_extract_facts_for_multititles"
    if not isinstance(titles, list):
        titles = [titles]

    all_facts = []
    for title in titles:
        facts = minimal_tomita_extract_facts(
            re_title=re_title,
            title=title,
            vars=vars,
            ignore_spaces=ignore_spaces,
            ignore_case=ignore_case,
            debug=debug,
        )
        for fact in facts:
            all_facts.append(fact)
    return all_facts


def minimal_tomita_extract_facts(
    re_title="",
    title="",
    vars={},
    ignore_spaces=True,
    ignore_case=True,
    debug=False,
):
    fun = "minimal_tomita_extract_facts"
    # debug = True

    t_start = time.time()

    if title is None:
        if debug:
            logger.debug("[%s: title=`%s` so no facts" % (fun, title))
        return []

    # ignore_spaces = False

    fun_no_probely = no_probely_tupo
    fun_no_probely = no_probely

    prepared_title = title
    re_title_prepared = re_title
    if 1 and ignore_spaces:
        prepared_title = fun_no_probely(prepared_title)
        re_title_prepared = fun_no_probely(re_title_prepared)

    # if ignore_case:
    #     prepared_title = prepared_title.lower()

    if debug:
        logger.debug(
            "[%s: re_title=`%s` for title=`%s` with vars=%s"
            % (fun, re_title, title, vars)
        )
        # wait_for_ok()

    # теперь ищем еще возможные варианты
    name_to_possible_values = {}
    # это float по дефолту
    numberfloat_vars = clear_list(
        """
        $NUMBER_FLOAT$
        $NUMBER1_FLOAT$
        $NUMBER2_FLOAT$
    """
    )
    numberint_vars = clear_list(
        """
        $NUMBER_INT$
        $NUMBER_INT1$
        $NUMBER_INT2$
    """
    )
    numberintfloat_vars = clear_list(
        """
        $NUMBER$
        $NUMBER1$
        $NUMBER2$
        $NUMBER_INT_FLOAT$
        $NUMBER_INT_FLOAT1$
        $NUMBER_INT_FLOAT2$
    """
    )
    any_vars = clear_list(
        """
    $ANY$
    $ANY1$
    $ANY2$
    """
    )
    regex_number_float = "[+-]?[0-9]+[\.,][0-9]+"
    regex_number_int = "[+-]?[0-9]+"
    # regex_number_float = regex_number_int

    regex_any = ".+"
    regex_any = ".*"

    list_of_regex_numbers = [
        regex_number_float,
        regex_number_int,
    ]
    regex_number_int_float = "|".join(list_of_regex_numbers)

    real_replaces = []

    dict_with_args = {}
    for var_name, var_replaces in vars.items():
        # может на вход поступить {'$sport$': {'football': 'futbol, 'hockey': 'hokei'}
        if isinstance(var_replaces, dict):
            var_values = var_replaces.keys()
        # a может {'$sport$': ['football': 'hockey']}
        else:
            var_values = var_replaces
        dict_with_args[var_name] = var_values

    if debug:
        logger.debug("dict_with_args:")
        show_dict(dict_with_args)
        # wait_for_ok()

    regex_replaces = {}
    if debug:
        logger.debug("prepare regular expression")
    for k, values in dict_with_args.items():
        if k not in re_title:
            if debug:
                logger.debug(
                    "     skip %s - not in re_title `%s`" % (k, re_title)
                )
            continue

        if 1 and ignore_spaces:
            values = [no_probely(_).strip() for _ in values]

        # сначала нужно проверять длинные строки
        new_list = [[-len(_), _] for _ in values]
        new_list.sort()
        # show_list(new_list)
        # wait_for_ok()
        sorted_values = [_[1] for _ in new_list]
        sorted_text = "|".join(sorted_values)
        sorted_text = ekran_regex(sorted_text)
        # wait_for_ok(sorted_text)
        # show_list(sorted_values)
        # wait_for_ok()
        var_name = k.replace("$", "")
        regex = r"(?P<%s>(%s))" % (var_name, sorted_text)
        if debug:
            logger.debug("%s regex: %s" % (k, regex))
        regex_replaces[k] = regex

    for k in numberfloat_vars:
        if k not in re_title:
            if debug:
                logger.debug(
                    "     skip %s - not in re_title `%s`" % (k, re_title)
                )
            continue
        var_name = k.replace("$", "")
        regex = r"(?P<%s>%s)" % (var_name, regex_number_float)
        regex_replaces[k] = regex

    for k in numberint_vars:
        if k not in re_title:
            if debug:
                logger.debug(
                    "     skip %s - not in re_title `%s`" % (k, re_title)
                )
            continue
        var_name = k.replace("$", "")
        regex = r"(?P<%s>%s)" % (var_name, regex_number_int)
        regex_replaces[k] = regex

    for k in numberintfloat_vars:
        if k not in re_title:
            if debug:
                logger.debug(
                    "     skip %s - not in re_title `%s`" % (k, re_title)
                )
            continue
        var_name = k.replace("$", "")
        regex = r"(?P<%s>%s)" % (var_name, regex_number_int_float)
        regex_replaces[k] = regex

    for k in any_vars:
        if k not in re_title:
            if debug:
                logger.debug(
                    "     skip %s - not in re_title `%s`" % (k, re_title)
                )
            continue
        var_name = k.replace("$", "")
        regex = r"(?P<%s>%s)" % (var_name, regex_any)
        regex_replaces[k] = regex

    if debug:
        logger.debug("regex_replaces:")
        show_dict(regex_replaces)

    possible_variant = re_find_vars(
        re_title_prepared, prepared_title, regex_replaces, debug=debug
    )
    if possible_variant:
        real_replaces.append(possible_variant)

    # wait_for_ok('mode %s done' % mode)

    seconds = time.time() - t_start
    if debug:
        logger.debug("%s real_replaces" % (len(real_replaces)))
        show_list(real_replaces)
        logger.debug("%s in %.3f seconds" % (fun, seconds))

    return real_replaces


def re_find_vars(re_title="", title="", regex_dict={}, debug=False):
    """Поиск рынка с помощью регулярки NUMBER
        re_title = 'Point spread ($NUMBER$) - 2nd Quarter: Basketball: $NUMBER1$'
        title = "Point spread (0.5) - 2nd Quarter: Basketball: 25.5"
    """
    args0 = locals()
    fun = "re_find_vars"
    # debug = True

    # экранирую
    re_title = ekran_regex(re_title)
    # wait_for_ok(re_title)

    # adding spaces
    re_title = "[SPACE_OR_EMPTY]%s[SPACE_OR_EMPTY]" % re_title.strip()
    space = r"[ \t]"
    re_space_or_empty = "%s*" % space
    repl_spaces = {
        " ": "%s*" % space,
        # '[SPACE_OR_EMPTY]': '%s*' % space,
    }
    re_title = no_probely_one(re_title, repl_spaces)
    re_title = re_title.replace("[SPACE_OR_EMPTY]", re_space_or_empty)
    # wait_for_ok(re_title)
    regex_str = no_probely(re_title, regex_dict, one=True)

    # тут начало и конец строки должен быть
    regex_str = r"^%s$" % regex_str

    t = 1
    t = 0
    if t:
        regex_str = "^(?P<DELIMITER>(-|))[ \t]*(?P<TOTALS>(TOTAL GAMES|Total points|Total Goals|Totals|Total))[ \t]*(?P<OVER_UNDER>(OVER / UNDER|OVER/UNDER|O/U|U/O))[ \t]*$"
        title = "Total Games Over/Under"

    if debug:
        logger.info("regex_str=`%s`, title=`%s`" % (regex_str, title)),
        show_dict(regex_dict)

    try:
        regex = re.compile(regex_str, re.IGNORECASE)
    except Exception as er:
        logger.debug("error %s: %s, args=%s" % (fun, er, args0))
        wait_for_ok("wrong regex_str `%s`" % regex_str)

    m = re.match(regex, title)
    try:
        dct_num = m.groupdict()
    except Exception as er:
        if debug:
            logger.debug("error %s" % er)
        dct_num = None

    if debug:
        logger.debug("dct_num=%s" % dct_num)

    real_dct_num = None
    if dct_num:
        real_dct_num = {}
        for k in dct_num:
            k_new = "$%s$" % k
            real_dct_num[k_new] = dct_num[k]

    if debug:
        logger.debug("real_dct_num=%s" % real_dct_num)

        if 0 and real_dct_num != None:
            wait_for_ok("found real_dct_num")

    return real_dct_num


def get_vars_with_settings_from_template(tpl="", vars={}):
    """
    Шаблон может быть с $NUMBER:...$ $var:new_value$ ...
    """
    fun = "get_vars_with_settings_from_template"
    debug = True
    debug = False
    if debug:
        logger.debug("[%s: tpl=`%s`, vars=%s" % (fun, tpl, vars))
    found_vars = []
    items = tpl.split("$")[1:]
    for num_var, var_with_options in enumerate(items, 1):
        # var_with_options = find_from_to_one('nahposhuk', '$', item)
        item = ""
        if debug:
            logger.debug(
                "  check %s/%s `%s` from item `%s`"
                % (num_var, len(items), var_with_options, item)
            )
        if ":" in var_with_options:
            var_name = find_from_to_one("nahposhuk", ":", var_with_options)
            var_options = find_from_to_one(
                ":", "nahposhuk", var_with_options
            ).split(":")
            # wait_for_ok(var_options)
        else:
            var_name = var_with_options
            var_options = []

        var_name_real = "$%s$" % var_name
        reason = False
        if vars and var_name_real in vars:
            reason = "var"
        elif var_name_real.startswith("$NUMBER"):
            reason = "number"

        if reason:
            if debug:
                logger.debug(
                    "     +`%s`, reason=%s" % (var_with_options, reason)
                )
        else:
            if debug:
                logger.debug("     -`%s` not in possible vars" % var_name_real)
            continue
        var_with_options_real = "$%s$" % var_with_options
        found_var = {
            "raw": var_with_options_real,
            "name": var_name_real,
            "options": var_options,
            "reason": reason,
        }
        if debug:
            logger.debug("found_var=%s" % found_var)
        found_vars.append(found_var)
    return found_vars


def ekran_regex(str=""):
    repl_title = {
        "(": r"\(",
        ")": r"\)",
        "?": r"\?",
    }
    re_title = no_probely(str, repl_title, one=True)
    return re_title


def score_handicap_from_txt(txt):
    """
    """
    parts = txt.split(" ")
    return score_handicap_api(parts[0], parts[1], parts[2])


def score_handicap_api(*args, **kwargs):
    """
    у апи пинки значения фор одни
    1 -0.75 2:0 ф2(-2,75)
    2 -0.75 2:0 ф2(+2.75)
    :return: 
    """
    kwargs["mode"] = "api"
    return score_handicap(*args, **kwargs)


def score_handicap(
    team="", fora="", score="", score_1=None, score_2=None, mode="+-"
):
    """
    score_handicap(1, +1,5, 0:3} -> Ф1(+4.5)
    """
    fun = "score_handicap"
    debug = True
    debug = False

    if debug:
        logger.debug(
            "[%s team=%s, fora=%s, score=%s" % (fun, team, fora, score)
        )

    znak = fora[0]
    if znak not in ["+", "-"]:
        znak = ""

    fora_now = get_fora_value_from_text(fora, fun=float)
    abs_fora = abs(fora_now)

    if score_1 is None:
        score_1 = 0
        score_2 = 0
        try:
            scores = score.split(":")
            if len(scores) == 2:
                score_1, score_2 = [int(_) for _ in scores]
        except Exception as er:
            logger.debug("score=`%s`" % score)
            logger.debug("ERROR %s: %s" % (fun, er))

    score_diff = score_2 - score_1
    abs_score_diff = abs(score_diff)

    if team not in ["1", "2"]:
        print_error("ERROR %s - unknown team %s" % (fun, team))
        team = "X"

    if 0 and debug:
        show_dict(locals())
        wait_for_ok(fun)

    fora_with_score = fora_now + score_diff
    if team in ["1"]:
        starting = "Ф1"
    else:
        if mode == "+-":
            fora_with_score = fora_now - score_diff
        else:
            fora_with_score = -fora_now - score_diff
        starting = "Ф2"

    # fora_with_score = abs_fora + abs_score_diff

    fora_with_score = "%s" % fora_with_score
    fora_with_score = cut_zeros_after_dot(fora_with_score)
    if debug:
        logger.debug("fora_with_score=%s" % fora_with_score)

    if float(fora_with_score) > 0:
        fora_with_score = "+%s" % fora_with_score

    tpl = "[starting]([znak][fora_with_score])"
    tpl = "[starting]([fora_with_score])"
    if fora_with_score == "0":
        tpl = "[starting](0)"

    repl = {
        "[starting]": starting,
        "[fora_with_score]": fora_with_score,
        "[znak]": znak,
    }
    value = no_probely(tpl, repl, one=1).replace(".", ",")

    # value = value.replace('.', ',')
    return value


def noscore_handicap_from_txt(txt):
    """
    {-0,75 2 0)} -> -2.75
    :param txt:
    :return:
    """
    parts = txt.split(" ")
    return noscore_handicap(parts[0], parts[1])


def noscore_handicap(team="", fora=""):
    """
    noscore_handicap(1, -4)} -> 1(4:0)
    """
    fun = "noscore_handicap"
    debug = True
    debug = False

    if debug:
        logger.debug("[%s team=%s, fora=%s" % (fun, team, fora))

    znak = fora[0]

    fora_now = get_fora_value_from_text(fora, fun=int)
    abs_fora = abs(fora_now)

    score_1 = 0
    score_2 = 0

    if team not in ["1", "2"]:
        team = "X"

    if team in ["1"]:
        score_1 = fora_now

    # elif team in ['2']:
    else:
        score_2 = fora_now

    min_score = abs(min(score_1, score_2))
    score_1_from_0 = score_1 + min_score
    score_2_from_0 = score_2 + min_score

    if debug:
        logger.debug("%s %s" % (score_1, score_2))
        logger.debug("from 0: %s %s" % (score_1_from_0, score_2_from_0))
        # wait_for_ok()

    tpl = "[team]([score_1]:[score_2])"

    repl = {
        "[team]": team,
        "[score_1]": str(score_1_from_0),
        "[score_2]": str(score_2_from_0),
    }
    value = no_probely(tpl, repl, one=1)

    # value = value.replace('.', ',')
    return value


def asia_fora_from_txt(txt):
    """

    {-0,75 2 0)} -> -2.75
    :param txt:
    :return:
    """
    parts = txt.split(" ")
    return asia_fora(parts[0], int(parts[1]), int(parts[2]))


def asia_fora(fora="-0.75", goals_1=2, goals_2=0):
    """
    {asia_fora(-0,75, 2, 0)} -> -2.75
    """
    debug = True
    debug = False
    score_diff = int(goals_1 - goals_2)
    znak = fora[0]

    fora_now = get_fora_value_from_text(fora)

    znak_plus = 1
    znak_minus = -1
    znak_diff = znak_chisla(score_diff)
    znak_fora = znak_chisla(fora_now)
    if znak_diff == znak_fora:
        znak = 1
    else:
        znak = -1

    # value = znak * (abs(score_diff) + abs(fora_now))
    abs_fora_now = abs(fora_now)
    abs_score_diff = abs(score_diff)

    rule = ""

    if fora_now == 0:
        rule = 0
        value = -score_diff

    elif znak_diff > 0:
        if znak_fora <= 0:
            rule = 11
            value = fora_now - score_diff
        else:
            rule = 12
            value = fora_now + score_diff

    elif znak_diff < 0:
        if znak_fora <= 0:
            rule = 21
            value = -fora_now + abs_score_diff - 1
        else:
            rule = 22
            value = -fora_now - (abs_score_diff - 1)  # - score_diff

    else:
        wait_for_ok("ERROR %s - unknown case" % fun)

    t = 0
    if t:
        if fora_now == 0:
            rule = 0
            value = -score_diff

        elif znak_diff != znak_fora:
            if znak_diff == znak_minus:
                rule = 11
                value = abs_fora_now + score_diff
            else:
                rule = 12
                value = -abs_fora_now - score_diff

        elif znak_diff == znak_fora:
            if znak_diff == znak_plus:
                rule = 21
                znak = 1
                value = znak * (abs(fora_now) + abs(score_diff))
            else:
                rule = 22
                # znak = - znak_diff
                # t = abs(fora_now) + abs(score_diff) - 1
                # value = znak * (t)
                # value = abs_score_diff - abs_fora_now
                # znak = - znak_diff
                value = abs_fora_now + abs_score_diff - 1
                # value = abs_fora_now + score_diff
                # value = fora_now + score_diff

        else:
            rule = 4
            znak = -znak_diff
            value = znak * (abs(fora_now) + abs(score_diff) - 1)

    if debug:
        logger.debug(
            "rule=%s, fora_now=%s, score_diff=%s, abs_fora_now=%s, abs_score_diff_=%s"
            % (rule, fora_now, score_diff, abs_fora_now, abs_score_diff),
            value,
            znak,
            znak_diff,
            znak_fora,
            abs(score_diff),
            abs(fora_now),
        )
    # wait_for_ok()

    value_float = value
    if floats_almost_equals(value, int(value)):
        value = int(value)

    if value > 0:
        value = "+%s" % value
    else:
        value = "%s" % value
    value = value.replace(".", ",")
    return value


def dve_fory_from_txt(txt):
    """
    home 1 1.5 -> ф1(1.25)
    """
    parts = txt.split(" ")
    return dve_fory(parts[0], parts[1], parts[2])


def dve_fory(team="", fora="", fora2=""):
    """
    """
    fun = "dve_fory"
    debug = True
    debug = False

    team = team.lower()

    if debug:
        logger.debug(
            "[%s team=%s, fora=%s, fora2=%s" % (fun, team, fora, fora2)
        )

    team_nums = {
        "home": 1,
        "away": 2,
        "over": "ТБ",
        "under": "ТМ",
    }

    team_num = team_nums.get(team, None)
    if team_num is None:
        if debug:
            logger.debug("%s error - bad team %s" % (fun, team))
        return False

    fora_now = get_fora_value_from_text(fora, fun=float)
    fora_now2 = get_fora_value_from_text(fora2, fun=float)

    fora_real = (fora_now + fora_now2) / 2.0
    fora_real = str(fora_real)
    fora_real = fora_real.replace(".", ",")
    fora_real = cut_zeros_after_dot(fora_real)

    if debug:
        logger.debug("fora_real %s" % fora_real)
        # wait_for_ok()

    if team in ["home", "away"]:
        tpl = "Ф[team_num]([fora_real])"
    else:
        tpl = "[team_num]([fora_real])"

    repl = {
        "[team_num]": team_num,
        "[fora_real]": fora_real,
    }
    value = no_probely_one(tpl, repl)

    return value


def znak_chisla(value):
    if value < 0:
        znak = -1
    else:
        znak = 1
    return znak


def delete_args_from_number_variable(phrase="ТБ($NUMBER:comma$)"):
    """ТБ($NUMBER:comma$) -> ТБ($NUMBER$)"""
    repl = {}
    delim = "$NUMBER"
    parts = phrase.split(delim)
    for part in parts[1:]:
        args = find_from_to_one("nahposhuk", "$", part)
        if ":" in args:
            number = find_from_to_one("nahposhuk", ":", args)
        else:
            number = args
        old_value = "%s%s$" % (delim, args)
        new_value = "%s%s$" % (delim, number)

        repl[old_value] = new_value
    # show_dict(repl)
    phrase = no_probely(phrase, repl)
    return phrase


def get_fora_value_from_text(fora, fun=float):
    if fora in ["0"]:
        fora_now = 0

    else:
        fora_now = fora.replace(",", ".")
        fora_now = fun(fora_now)
    return fora_now


def score_handicap_api_from_txt(txt=""):
    logger.warning("ubil function score_handicap_api_from_txt")
    return ""


if __name__ == "__main__":
    special = "get_vars_with_settings_from_template"
    special = "delete_args_from_number_variable"
    special = "asia_fora"
    special = "noscore_handicap"
    special = "dve_fory"
    special = "tomita_extract_facts"
    special = "score_handicap_api"
    special = "score_handicap"

    if special == "nah":
        pass

    elif special == "delete_args_from_number_variable":
        lines_txt = """
            ТБ($NUMBER:comma$)
            ТМ($NUMBER:comma$)
            Ф2($NUMBER:comma:znak$)
            Ф1($NUMBER:comma:znak$)
            4/4 ТБ($NUMBER:comma$)
            4/4 ТМ($NUMBER:comma$)
            4/4 ТМ($NUMBER1:comma$)
           """
        lines = clear_list(lines_txt)
        for line in lines:
            var = delete_args_from_number_variable(line)
            logger.debug("var=%s, line=%s" % (var, line))

    elif special == "dve_fory":
        lines_txt = """
        HOME 0 -0,5 Ф1(-0,25)
        AWAY 0 +0.5 Ф2(0,25)
        AWAY 1.5 2 Ф2(1,75)
        Over 3 3.5 ТБ(3,25)
        Under 3 3.5 ТМ(3,25)
        """
        lines = clear_list(lines_txt, bad_starts="#")
        for line in lines:
            if line.startswith("+"):
                continue
            parts = clear_list(line.split(" "))
            if len(parts) != 4:
                logger.debug("bad parts %s" % parts)
                continue
            txt = " ".join(parts[:3])
            fora_must_be = parts[-1].replace(".", ",")
            fora = dve_fory_from_txt(txt)
            status = ""
            if fora != fora_must_be:
                status = "ERROR != %s" % fora_must_be
            logger.debug("fora=%s %s (txt=`%s`)" % (fora, status, txt))

    elif special == "noscore_handicap":
        lines_txt = """
        1 +4 1(4:0)
        # x -2 x(2:0)
        2 -4 2(4:0)
        
        1 +3 1(3:0)
        2 -3 2(3:0)
        """
        lines = clear_list(lines_txt, bad_starts="#")
        for line in lines:
            if line.startswith("+"):
                continue
            parts = clear_list(line.split(" "))
            if len(parts) != 3:
                logger.debug("bad parts %s" % parts)
                continue
            txt = " ".join(parts[:2])
            fora_must_be = parts[-1].replace(".", ",")
            fora = noscore_handicap_from_txt(txt)
            status = ""
            if fora != fora_must_be:
                status = "ERROR != %s" % fora_must_be
            logger.debug("fora=%s %s (txt=`%s`)" % (fora, status, txt))

    elif special == "score_handicap_api":
        lines_txt = """
        1 -0.75 2:0 Ф1(-2,75)
        2 -0.75 2:0 Ф2(+2,75)
        """
        lines = clear_list(lines_txt, bad_starts="#")
        for line in lines:
            if line.startswith("+"):
                continue
            parts = clear_list(line.split(" "))
            if len(parts) != 4:
                logger.debug("bad parts %s" % parts)
                continue
            txt = " ".join(parts[:3])
            fora_must_be = parts[-1].replace(".", ",")
            fora = score_handicap_api_from_txt(txt)
            status = ""
            if fora != fora_must_be:
                status = "ERROR != %s" % fora_must_be
            logger.debug("fora=%s %s (txt=`%s`)" % (fora, status, txt))

    elif special == "score_handicap":
        lines_txt = """
        1 +1.5 0:3 Ф1(+4,5)
        2 -1.5 0:3 Ф2(-4,5)
        1 -1 0:1 Ф1(0)
        """
        # 2 -1 1:1 Ф2(-1)
        # 1 -1 1:0 Ф1(0)
        lines = clear_list(lines_txt, bad_starts="#")
        # wait_for_ok(lines)
        for line in lines:
            # logger.debug(line)
            if line.startswith("+"):
                continue
            parts = clear_list(line.split(" "))
            if len(parts) != 4:
                logger.debug("bad parts %s" % parts)
                continue
            txt = " ".join(parts[:3])
            fora_must_be = parts[-1].replace(".", ",")
            fora = score_handicap_from_txt(txt)
            status = ""
            if fora != fora_must_be:
                status = "ERROR != %s" % fora_must_be
            logger.debug("fora=%s %s (txt=`%s`)" % (fora, status, txt))

    elif special == "asia_fora":
        lines_txt = """
        # 3 Way Handicap (-2) - 90 Mins * home (-2) == 1(0:2)
        # 3 Way Handicap (-1) - 90 Min * home(-1) == 1(0:1)
        """

        lines_txt_old = """

        0.5 0 0 +0.5
        
        # sam
        -0.75 0 0 -0.75
        -0.75 1 0 -1.75
        
        -0.75 2 0 -2.75
        -0.75 2 1 -1.75
        -0.75 2 2 -0.75
        -0.75 1 2 +0.75
        -0.75 0 2 +1.75
        
        -0.5 2 0 -2.5
        -0.5 2 1 -1.5
        -0.5 2 2 -0.5
        -0.5 1 2 +0.5
        -0.5 0 2 +1.5
        
        -0.25 0 2 +1.25
        
        -2 0 2 +2
        -1 0 2 +1
        0 0 2 +2
        
        0.5 2 0 +2.5
        0.5 2 1 +1.5
        0.5 2 2 +0.5
        0.5 1 2 -0.5
        0.5 0 2 -1.5
        
        -1 2 0 -3
        -1 1 0 -2
        -1 0 0 -1
        -1 0 1 0
        -1 0 2 +1
        
        0 2 0 -2
        0 1 0 -1
        0 0 0 0
        0 0 1 +1
        0 0 2 +2
        0 0 3 +3
        
        # sam
        2 2 0 +2
        1 1 0 +2
        1 0 0 +1
        1 0 1 0
        1 0 2 -1
        """

        lines_txt0 = """
        # -0.75 1 2 +0.75
        # -0.25 0 1 +0.25
        # -0.75 0 1 +0.75
        -0.5 2 0 -2.5
        0.5 2 0 +2.5
        -0.75 0 2 +1.75
        0.5 0 2 -1.5
        """
        lines = clear_list(lines_txt)
        for line in lines:
            if line.startswith("+"):
                continue
            parts = line.split(" ")
            if len(parts) != 4:
                continue
            txt = " ".join(parts[:3])
            fora_must_be = parts[-1].replace(".", ",")
            fora = asia_fora_from_txt(txt)
            status = ""
            if fora != fora_must_be:
                status = "ERROR != %s" % fora_must_be
            logger.debug("fora=%s %s (txt=`%s`)" % (fora, status, txt))

    elif special == "regex":
        regex = r"Total Goals - Over/Under ([+-]?[0-9]+\.[0-9]) - 90 Mins"
        nums = re.findall(regex, title)
        logger.debug("nums=%s" % (nums))

    elif special == "tomita_extract_facts":
        vars = {}
        t_1_2 = {
            "1": "",
            "2": "",
        }
        football_info = {
            "ru": "Футбол",
            "en": "Soccer",
        }
        sport_values = {
            "Football": football_info,
            "Basketball": "Баскет",
        }
        gamepart_values = {
            "1st Quarter": "1/4",
            "2nd Quarter": "2/4",
            "90 Mins": "",
        }
        pobedy_values = {
            "1": "",
            "X": "",
            "2": "",
        }
        delimiter_values = {
            "": "",
            "-": "",
        }
        empty_or_no_values = {
            "": "",
            "FULL GAME": "",
        }
        fora0_values = {
            "Ф1(0)": "",
            "Ф2(0)": "",
        }
        home_away_values = {
            "HOME": "",
            "AWAY": "",
        }
        over_under_values = {
            "over/uNder": "",
            "over / under": "",
            "o/u": "",
        }
        for _ in range(10):
            key = "random_%s" % _
            gamepart_values[key] = key
        vars["$SPORT$"] = sport_values
        vars["$GAMEPART$"] = gamepart_values
        vars["$POBEDY$"] = pobedy_values
        vars["$FORA0$"] = fora0_values
        vars["$DELIMITER$"] = delimiter_values
        vars["$EMPTY_OR_NO$"] = empty_or_no_values
        vars["$num_1_2$"] = t_1_2
        # show_dict(vars)

        unused_values = {}
        for _ in range(100):
            key = "unused_%s" % _
            unused_values[key] = key
        vars["$unused_values$"] = unused_values

        re_title = "Point spread ($NUMBER$) - $GAMEPART$: $SPORT$: $NUMBER1$"
        title = "Point spread (+0.5) - 1st Quarter: Football: 25.5"
        title = "Point spread (0.5) - 1st Quarter: Football: 25.5"

        re_title = "Point spread ($NUMBER$) - $GAMEPART$: $SPORT$: $NUMBER1$"
        title = "Point spread (+0.5) - 1st Quarter: Football: 25.5"

        t = 0
        t = 1
        if t:
            re_title = "Draw No Bet - $GAMEPART$"
            title = "Draw No Bet - 90 Mins"
            title = "Draw no bet - 90 Mins"  # lower

        t = 1
        t = 0
        if t:
            re_title = "Total Goals - Over/Under $NUMBER$ - $GAMEPART$"
            title = "Total Goals - Over/Under 6.5 -  90 Mins"
            title = "Total Goals - Over/Under 6.5 - 90 Mins"

        t = 1
        t = 0
        if t:
            re_title = "$POBEDY$"
            re_title = "Ф1($NUMBER_INT$)"
            re_title = "Ф1($NUMBER_INT_FLOAT$)"
            re_title = "$FORA0$"
            re_title = "Ф1($NUMBER$)"
            re_title = "Ф$num_1_2$($NUMBER_INT$)"
            title = "Ф1"
            title = "12"
            title = "1"
            title = "X"
            title = "1Ф"
            title = "Ф1(0.5)"
            title = "Ф1(0,5)"
            title = "Ф1(0,55)"
            title = "Ф1(0)"

        t = 0
        t = 1
        if t:
            re_title = "Asian Goal Line (O/U $NUMBER$) - 90 Mins"
            title = "Asian Goal Line (O/U 2) - 90 Mins"

        t = 0
        t = 1
        if t:
            re_title = "oppa $OVER_UNDER$ $DELIMITER$ $EMPTY_OR_NO$"
            title = "oppa over/UndeR"

            vars = {}
            vars["$DELIMITER$"] = delimiter_values
            vars["$EMPTY_OR_NO$"] = empty_or_no_values
            vars["$OVER_UNDER$"] = over_under_values

        t = 1
        t = 0
        if t:
            re_title = "ТБ($NUMBER$)"
            re_title = "4/4 ТБ($NUMBER$)"
            title = "4/4 ТБ(2.5)"
            vars = {}

        t = 0
        t = 1
        if t:
            re_title = "$HOME_or_AWAY$ $NUMBER$, $NUMBER2$"
            title = "HOME 0, -0.5"

            vars = {}
            vars["$HOME_or_AWAY$"] = home_away_values

        t = 0
        t = 1
        if t:
            re_title = "$ANY$$it12bm$$ANY1$"
            title = "ИТ1М(1,5)"

            vars = {}
            vars["$it12bm$"] = {
                "ИТ1М": "",
            }

        t = 0
        t = 1
        if t:
            re_title = "$Both_Teams$"
            title = "Both teams to Score"

            re_title = "$Both_Teams$?"
            title = "Both teams to Score?"

            vars = {}
            vars["$Both_Teams$"] = {
                "Both teams to Score": "",
            }

        logger.debug("vars:")
        show_dict(vars)

        cnt_tries = 1000
        cnt_tries = 1
        t_start = time.time()
        debug = False
        for _ in range(cnt_tries):
            t0 = time.time()
            facts = minimal_tomita_extract_facts(
                re_title, title, vars=vars, debug=debug
            )
            duration_one = time.time() - t0
            if _ == 0:
                logger.debug("step1 in %.3f seconds" % duration_one)

        duration = time.time() - t_start
        logger.debug(
            "duration: %.3f seconds for %s steps" % (duration, cnt_tries)
        )

        logger.debug("%s facts=%s" % (len(facts), facts))
        wait_for_ok()
        # facts = [{'$GAMEPART$': '90 mins', '$NUMBER$': '6.5'}]
        # facts = [{'$GAMEPART$': '90 Mins', '$NUMBER$': '6.5'}]

        tpl = "number_comma: $NUMBER:comma$, minus_znak: $NUMBER:comma:minus_znak$ sport: $SPORT$, так что по русски это $SPORT:ru$ (в британии $SPORT:en$), часть игры: $GAMEPART:new_value$"
        new_facts = prepare_new_phrases_from_facts(
            tpl=tpl, facts=facts, vars=vars
        )
        logger.debug("new_facts:")
        show_list(new_facts)

    elif special == "get_vars_with_settings_from_template":
        tpl = "number_comma: $NUMBER:comma$, minus_znak: $NUMBER:comma:minus_znak$ sport: $SPORT$, так что по русски это $SPORT:ru$ (в британии $SPORT:en$), часть игры: $GAMEPART:new_value$"
        vars = get_vars_with_settings_from_template(tpl)
        show_list(vars)

    else:
        wait_for_ok("unknown special=%s" % special)

"""
todo: 
    перевести на поиск по регуляркам:   
        zoot: #upgrade поиск одной из фраз
    """
