#!/usr/bin/python
# -*- coding: utf-8 -*-

from modules import *
import itertools
from bet365_one_api.bet365_placebet_helper import (
    create_bet365Urls_from_any_data,
)

# from bet365_one_api.bet365_placebet_helper import (
#     convert_bet365Url_to_addbetData, get_hash_of_url
# )
from bet365_one_api.bet365_parse_answer_tip import (
    parse_answer_tip,
    get_short_history,
    get_last_history,
    parse_tip,
)
from bet365_one_api.bet365_requests import *
from bet365_one_api.bet365_multiplacebet_helper import *  # select_best_multiple_after_refreshslip


logger = get_logger(__name__)


def submit_multistakes_with_pirxt_server(
    urls: List = None,
    bets: List = None,  # возможно есть ставки-словари - тут с винами, для просчета мультимаркетов
    pirxt_headers="",
    more_pirxt_headers=[],
    session_headers="",
    nst_headers="",
    session=None,
    want_addbet=True,
    want_placebet=True,
    betsource="FlashInPLay",  # Lite
    place_on=None,
    stake=0.1,
    stakes=None,
    want_save_raw_requests=False,  # хочу сохранять запросы?
    f_raw_requests=os.path.abspath("temp/raw_requests.txt"),
    f_last_raw_requests=os.path.abspath("temp/last_raw_requests.txt"),
    multiple_selector: MultipleSelector = None,  # если надо - выберу лучший мультипл
    skipper: ValuebetsSkipperWithSaving = None,
    debug: bool = True,
    select_multiple_by=None,
    want_leave_only_bets_with_unchanged_odds=True,  # Хочу только неизменные одсы - Но я их потом вытяну
    want_retry_when_stakes_above_max_stake=False,
    want_add_unavailable_bets_to_skipper: bool = True,  # хочу в скипер добавить плохие?
    multi_support: dict = None,  # для поддержки мульти-ставок (если есть одинарная, а я хочу сделать мульти)
    domain: str = "com",
    want_empty_nst: bool = True,  # в линуксе он пустой?
):
    """
    ставка в одной ф-ии использую пирхт-сервер
    """
    fun = "submit_multistakes_with_pirxt_server"

    if domain == "es":
        func_com_to_es = com_to_es_polube
    else:
        func_com_to_es = com_to_es_no

    if not urls:
        urls = [bet["any_link"] for bet in bets]

    bets_important = bets[:]
    urls_important = urls[:]  # это главные урлы

    # урлы для мультисапорта
    if not multi_support:
        multi_support = {
            "bets": [],
        }
    bets_support = multi_support["bets"][:]
    # урлов всего должно быть до 20
    bets_support = bets_support[: 20 - len(urls)]
    shuffle(bets_support)
    urls_support = [bet["any_link"] for bet in bets_support]
    support_hashes = [get_hash_of_url(_) for _ in urls_support]

    # f_headers = r"s:\python2.7\Lib\site-packages\universal_bookmaker\api_bet365\temp\headers.txt"
    # f_auto_pirxt = r"s:\python2.7\Lib\site-packages\universal_bookmaker\api_bet365\temp\auto_pirxt.txt"
    # f_answer = r"s:\python2.7\Lib\site-packages\universal_bookmaker\api_bet365\temp\answer.txt"

    if place_on is None:

        place_on = [2, 3]

    if bets_support:
        place_on = [2]

    place_on_real = place_on[:]

    bets = bets_important + bets_support

    urls = urls_important + urls_support  # по ним всё будем делать
    urls = leave_unique_from_list_for_hashfunc(urls, hash_func=get_hash_of_url)
    odds_must_be = [get_vars_from_bet365url(url)["odds"] for url in urls]

    if pirxt_headers:
        more_pirxt_headers.insert(0, pirxt_headers)

    logger.debug2(
        f"[{fun} {domain} {len(urls_important)} bets (+multi_support {len(urls_support)}): {odds_must_be=} {place_on=} with {len(more_pirxt_headers)} pirxts for {urls_important=} ({urls_support=})"
    )
    logger.debug(f"{session=}")
    # wait_for_ok()
    # wait_for_ok()
    if not want_leave_only_bets_with_unchanged_odds:
        odds_must_be = None

    # wait_for_ok()
    if want_empty_nst:
        logger.warning(f"want_empty_nst")
        nst_headers = ""
    else:
        if not nst_headers:
            m = f"empty {nst_headers=}"
            logger.critical(m)
            inform_critical(m)
            # raise ValueError(m)

    raw_requests = []
    durations = []
    history = []
    responses = []
    stats = {}
    step = 0
    tip = None
    # answer = None
    addbet_answer = {}
    answer = {}
    error = ""
    error_details = {}
    best_multiple = None
    all_bad_bets = []  # бетка скажет что они недоступны
    while True:

        step += 1
        t_start_step = time.time()

        if step > 1:
            # logger.warning('step %s, so break' % step)
            break

        Show_step(f"{fun} step {step}")

        error_addbet = ""
        addbet_answer = {}

        t_start_addbet = time.time()
        if want_addbet:

            # отладка - если ошибка
            t = 0
            if t:
                tip = "connection_error"
                error_addbet = tip
                break

            step_addbet = 0
            while True:
                step_addbet += 1
                t_start_addbet_one = time.time()
                logger.debug2(f"addbet {step_addbet}")

                if len(urls) == 1:
                    if 1 not in place_on_real:
                        error_addbet = "not_multistake__only_1"
                        break

                elif len(urls) == 0:
                    error_addbet = "not_multistake__only_0"
                    break

                if step_addbet > 1:
                    pass
                    # wait_for_ok('make step?')

                addbet_headers = prepare_headers_for_bet365_placebet(
                    session_headers=session_headers,
                    nst_headers=nst_headers,
                    final_process_func=func_com_to_es,
                )

                tpl_refreshslip = (
                    f"&ns=[ns]||&ms=[ms]||&betsource={betsource}&bs=1&cr=1"
                )
                ms = "id=2#bc=1#||id=-1#bc=2#"
                kwargs = {
                    "urls": urls,
                    "debug": 0,
                }
                r_data = convert_multiple_bet365Urls_to_addbetData(**kwargs)
                # logger.debug(f"refreshslip {r_data=}")
                # post_data = r_data['data']
                repl = {
                    "[ns]": quote_plus(r_data["ns"]),
                    "[ms]": quote_plus(ms),
                }
                # wait_for_ok(repl)
                post_data = no_probely_one(tpl_refreshslip, repl)

                """
                раньше делал через адбет - сейчас только через рефрешслип
                                    url = "https://www.bet365.com/BetsWebAPI/addbet"
                                    post_data = convert_bet365Url_to_addbetData(
                                        url=any_link, mt=mt
                                    )
                """

                # logger.debug("post_data=%s" % post_data)
                # wait_for_ok()

                url = func_com_to_es(
                    "https://www.bet365.com/BetsWebAPI/refreshslip"
                )
                # url = func_com_to_es(
                #     "https://www.bet365.com/BetsWebAPI/addbet"
                # )
                kwargs = {
                    "url": url,
                    "headers": addbet_headers,
                    "data": post_data,
                }

                r_response = request_with_requests(session=session, **kwargs)

                duration = r_response["duration"]
                post_error = r_response["error"]
                response = r_response["response"]
                raw_request = r_response["raw_request"]
                addbet_answer = r_response["json"]
                responses.append(response)

                # получаю запрос, можно будет поанализировать
                if want_save_raw_requests:
                    join_text_to_file("\n\n" + raw_request, f_raw_requests)
                raw_requests.append(raw_request)

                tip = parse_answer_tip(
                    answer=addbet_answer,
                    post_error=post_error,
                    response=response,
                )

                history.append(tip)

                stats[tip] = stats.get(tip, 0) + 1

                if tip in ["connection_error"]:
                    error_addbet = tip
                    break

                elif post_error:
                    error_addbet = f"addbet_error__{post_error}"

                    break

                duration_addbet = round(time.time() - t_start_addbet, 3)
                duration_addbet_one = round(
                    time.time() - t_start_addbet_one, 3
                )
                durations.append(duration_addbet_one)

                logger.debug2(
                    f"  +addbet in {duration_addbet} s, {duration} seconds {tip=} with {addbet_answer=}"
                )

                logger.info(f"{step=}, {response=}")
                logger.debug(f"{durations=} {history=}")
                # logger.debug(get_last_history(history))
                logger.debug(f"{stats=}")

                if tip in ["not_logined"]:
                    error_addbet = "addbet_not_logined"
                    break

                if tip in ["bot_ip", "no_cookies", "automation_detected"]:
                    logger.warning(f"{tip=}, so break")
                    break

                if tip in ["wrong get_new_X-Net-Sync-Term"]:
                    error_addbet = "addbet_wrong_nst"
                    break

                r_refreshslip = parse_refreshslip(addbet_answer)
                logger.debug(
                    f"{want_leave_only_bets_with_unchanged_odds=} {r_refreshslip=}"
                )

                bets_from_bk = r_refreshslip[
                    "bets"
                ]  # [{'odds': '16/5', 'sa': '61c5a62f-30E0B414', 'f': 111880512, 'fp': 347877657, 'mt': 1}]

                # проверка - возможно некоторые уже недоступны
                bad_bets = [_ for _ in bets_from_bk if _.get("is_bad")]
                if bad_bets:
                    all_bad_bets.append(bad_bets)
                    bets_from_bk = list_minus_list(bets_from_bk, bad_bets)
                    logger.debug(
                        f" found {len(bad_bets)} unavailable selections, {len(bets_from_bk)}/{len(urls)} available"
                    )

                bets_with_stable_odds = leave_bets_with_unchanged_odds(
                    bets_from_bk, odds_must_be
                )
                changed_odds = list_minus_list(
                    [_["odds"] for _ in bets_from_bk],
                    [_["odds"] for _ in bets_with_stable_odds],
                )
                logger.info(
                    f"have {len(bets_with_stable_odds)}/{len(bets_from_bk)} {bets_with_stable_odds=} ({changed_odds=})"
                )

                if place_on_real and len(bets_with_stable_odds) < min(
                    place_on_real
                ):
                    error_addbet = f"not_multistake__odds_changed__stable:{len(bets_with_stable_odds)}/{len(bets_from_bk)}"
                    break

                t = 0
                if t:
                    show_list(bets_with_stable_odds)
                    m = f"{bets_with_stable_odds=}"
                    logger.debug(m)
                    wait_for_ok()

                # если нужно выбирать только какой-то один лучший мультипл
                if debug:
                    logger.debug(f"{multiple_selector=} {skipper=}")

                if not bets_with_stable_odds:
                    error_addbet = "not_multistake__no_bets_with_stable_odds"
                    break

                if not multiple_selector:
                    logger.debug(
                        "no multiple_selector, so placebet one maximum multiple"
                    )
                elif best_multiple:
                    logger.debug("already selected best_multiple")
                else:
                    kwargs_multiple = {
                        "bets": bets,
                        "bets_support": bets_support,
                        "bets_with_stable_odds": bets_with_stable_odds,
                        "multiple_selector": multiple_selector,
                        "skipper": skipper,
                        "select_multiple_by": select_multiple_by,
                        # "debug": debug,
                        "debug": False,
                    }
                    best_multiple = select_best_multiple_after_refreshslip(
                        **kwargs_multiple
                    )
                    if debug:
                        logger.debug(f"{best_multiple=}")

                    error_addbet = get_api_error(best_multiple)

                    if error_addbet:
                        error_details = {
                            "kwargs": kwargs_multiple,
                            "result": best_multiple,
                        }
                        break

                    bets_from_best = best_multiple["bets"]
                    cnt_not_support = best_multiple.get("cnt_not_support", 0)

                    # опять создаю задание для рефрешслипа
                    hashes_from_bets = [
                        get_hash_of_url(_) for _ in bets_from_best
                    ]
                    bets_with_stable_odds = [
                        _
                        for _ in bets_with_stable_odds
                        if get_hash_of_url(_) in hashes_from_bets
                    ]
                    place_on_real = [len(bets_from_best)]

                    if debug:
                        logger.debug(
                            f"new {len(bets_with_stable_odds)} (non_support {cnt_not_support}) {bets_with_stable_odds=}"
                        )
                        # wait_for_ok()

                    # если одсы поменялись - пересоздаю задание
                if len(bets_with_stable_odds) != len(bets_from_bk):
                    logger.warning(
                        f"another refreshslip for new {len(bets_with_stable_odds)=}"
                    )
                    urls = [
                        create_bet365Url_from_any_data(_)[0]
                        for _ in bets_with_stable_odds
                    ]
                    logger.debug(f"new {len(urls)} {urls=}")

                    odds_must_be = [_["odds"] for _ in bets_with_stable_odds]

                    if not want_leave_only_bets_with_unchanged_odds:
                        odds_must_be = None

                    logger.debug("new odds_must_be=%s" % odds_must_be)
                    continue

                break

        if error_addbet:
            tip = error_addbet
            break

        bg = addbet_answer.get("bg")
        if want_placebet and not error_addbet:
            t_start_placebet = time.time()
            if bg:
                logger.info(f"SUCCESS, {bg=}")
            else:
                if bg == "":
                    logger.error("not_logined")
                    tip = "addbet_not_logined"
                    error = "addbet_not_logined"

                elif bg is None:
                    logger.error(
                        "unsuccess, no bg in answer, error=%s" % error
                    )
                    tip = parse_tip(addbet_answer)
                    if tip is not None:
                        tip = f"addbet_{tip}"
                    else:
                        tip = "addbet_no_betguid"
                    error = tip

                break

            # func_com_to_es = com_to_es_polube
            kwargs_for_creating_placebetKwargs = {
                "answer": addbet_answer,
                "detailed": True,
                "stake": stake,
                "stakes": stakes,
                "place_on": place_on_real,
                "odds_must_be": odds_must_be,
                "func_com_to_es": func_com_to_es,
            }

            # если stakes_above_max_stake - пробую поставить меньше
            step_placebet = 0
            while True:
                step_placebet += 1

                r_placebet_kwargs = prepare_composerData_for_placebet_after_addbet(
                    **kwargs_for_creating_placebetKwargs
                )
                error = get_api_error(r_placebet_kwargs)
                if error:
                    logger.error(f"{error=} from {r_placebet_kwargs=}")
                    error_details = r_placebet_kwargs.get("error_details", {})
                    break

                url = r_placebet_kwargs["url"]
                post_data = r_placebet_kwargs["post_data"]

                if more_pirxt_headers:
                    pirxt_headers = more_pirxt_headers.pop(0)
                pirxt_headers = pirxt_headers.replace("Cookie: ", "# Cookie: ")

                placebet_headers = prepare_headers_for_bet365_placebet(
                    session_headers=session_headers,
                    pirxt_headers=pirxt_headers,
                    nst_headers=nst_headers,
                    final_process_func=func_com_to_es,
                )

                kwargs = {
                    "url": url,
                    "headers": placebet_headers,
                    "data": post_data,
                }

                t = 0
                if t:
                    logger.warning(f"пробую подождать - возможно фейлы оттуда")
                    sleep_(0.5)

                r_response = request_with_requests(session=session, **kwargs)

                duration = r_response["duration"]
                post_error = r_response["error"]
                response = r_response["response"]
                raw_request = r_response["raw_request"]
                answer = r_response["json"]
                responses.append(response)

                # получаю запрос, можно будет поанализировать
                if want_save_raw_requests:
                    join_text_to_file("\n\n" + raw_request, f_raw_requests)
                raw_requests.append(raw_request)

                tip = parse_answer_tip(
                    answer=answer, post_error=post_error, response=response
                )

                history.append(tip)

                stats[tip] = stats.get(tip, 0) + 1

                if (
                    want_retry_when_stakes_above_max_stake
                    and step_placebet == 1
                    and tip == "stakes_above_max_stake"
                ):
                    if not more_pirxt_headers:
                        error = "stakes_above_max_stake_but_not_pirxt_headers"
                        tip = "stakes_above_max_stake_but_not_pirxt_headers"
                        break

                    max_stake = parse_max_stake_from_answer(answer)
                    max_stake = round(float(max_stake) * 0.9, 2)
                    kwargs_for_creating_placebetKwargs["stake"] = max_stake
                    logger.warning(
                        f"stakes_above_max_stake, but retry with {max_stake=} from {stake=}"
                    )

                    if not max_stake:
                        tip = "max_stake_is_zero"
                        logger.warning(tip)
                        break

                    continue

                break

            if tip in ["connection_error"]:
                pass

            elif post_error:
                tip = f"placebet_post_error__{post_error}"

            if tip in ["put_stake_successfully"]:
                logger.info("put_stake_successfully")
            else:
                logger.error(f"{tip=}")

            duration_placebet = round(time.time() - t_start_placebet, 3)
            durations.append(duration_placebet)
            logger.debug2(
                "  +placebet in %s s, %s seconds tip=%s with answer=%s"
                % (duration_placebet, duration, tip, answer)
            )

            logger.info("step=%s, response=%s" % (step, response))
            logger.debug("durations=%s history=%s" % (durations, history))

            logger.debug(get_last_history(history))

            if tip in ["bot_ip", "no_cookies"]:
                logger.warning(f"tip={tip}, so break")
                break

    if want_save_raw_requests:
        text_to_file("\n\n".join(raw_requests), f_last_raw_requests)

    if error in ["multiples_impossible"]:
        tip = error

    if all_bad_bets and want_add_unavailable_bets_to_skipper:
        bad_bets = slitj_list_listov(all_bad_bets)
        bad_links = [create_bet365Url_from_any_data(_)[0] for _ in bad_bets]
        logger.debug(
            f"will skip {len(bad_links)} bad links - check {bad_links=}"
        )
        show_list(bad_links)
        # inform_me_one("check links")
        if skipper:
            hashes = [get_hash_of_url(_) for _ in bad_links]
            logger.debug(f"will skip {hashes=}")
            skipper.mark_used(
                hashes,
                reason="found error in refreshslip",
                # support_hashes=support_hashes, # тут не надо пропускать - реально такого не надо использовать
            )
        # wait_for_ok()

    # сохраню инфу для анализа фейлов
    want_save_pirxt_log = True
    if want_save_pirxt_log:
        f_pirxts_success = "temp/!!!pirxts_success.txt"
        f_pirxts_failed = "temp/!!!pirxts_failed.txt"
        if tip in ["failed"]:
            f_pirxt_log = f_pirxts_failed
        else:
            f_pirxt_log = f_pirxts_success

        if addbet_answer is None:
            addbet_answer = {}
        add_to_full_log(
            [
                tip,
                addbet_answer.get("cc"),
                addbet_answer.get("pc"),
                addbet_answer.get("bg"),
                "\n",
                pirxt_headers,
                "\n",
                addbet_answer,
                "\n",
                answer,
                "\n" * 3,
            ],
            f_pirxt_log,
        )

    details = {
        "stats": stats,
        "durations": durations,
        "history": history,
        "short_history": get_short_history(history),
    }
    result = {
        "tip": tip,
        "addbet_answer": addbet_answer,
        "answer": answer,
        "responses": responses,
        "urls_posted": urls,
        "details": details,
        "placed_multiple": best_multiple,
        "error_details": error_details,
    }
    if error:
        result["error"] = error
    logger.debug1(
        f"     +{fun} {stats=}, check {want_save_raw_requests=} in {f_raw_requests}"
    )
    return result


def prepare_composerData_for_placebet_after_addbet(
    answer={},
    tpl="",
    sa=None,
    f=None,
    fp=None,
    odds=None,
    url=None,
    stake=0.10,
    stakes=None,
    place_on=[2, 3],
    want_multiples=True,
    detailed=True,
    betsource="FlashInPLay",  # Lite
    # betsource="Lite",
    odds_must_be=[],  # как одсы должны быть
    func_com_to_es: callable = com_to_es,
    debug=True,
):
    fun = "prepare_composerData_for_placebet_after_addbet"
    logger.debug(f"{fun} {place_on=}")
    error = ""
    error_details = {}
    # 	https://www.bet365.com/BetsWebAPI/placebet?betGuid=f12772a6-4907-4482-9b18-86a4e72860e7&c=l8Snns/SlXrY9Caz889TDt6rh8+ua4plnt7WZyQPqLE=&p=4298115802939912836

    if url is not None:
        # `https://www.bet365.com/dl/sportsbookredirect?bs=111138733-279083557~4/1&bet=1`
        t = find_from_to_one("bs=", "~", url)
        f, fp = t.split("-")
        odds = find_from_to_one("~", "&", url)
        logger.debug("  f=%s, fp=%s, odds=%s from url %s" % (f, fp, odds, url))

    if want_multiples:
        r_refreshslip = parse_refreshslip(answer)
        multiples = r_refreshslip["multiples"]
        if debug:
            logger.debug(f" {multiples=}")

        if not multiples and 1 not in place_on:
            error = "multiples_impossible"
            error_details = {
                "kwargs": answer,
                "r_refreshslip": r_refreshslip,
            }

        # multiples = []  # тест

    cc0 = answer["cc"]
    pc0 = answer["pc"]
    bet_guid = answer["bg"]

    pc = quote_plus(pc0)
    cc = quote_plus(cc0)

    # cc = cc + "specialError"
    # pc = pc[:5] + "12345"

    # поменял урл
    url = func_com_to_es(
        "https://www.bet365.com/BetsWebAPI/placebet?betGuid=[bet_guid]&c=[cc]&p=[pc]"
    )
    repl = {
        "[cc]": cc,
        "[pc]": pc,
        "[bet_guid]": bet_guid,
    }
    url = no_probely_one(url, repl)

    # post_data = "&ns=pt=N#o=[odds]#f=[f]#fp=[fp]#so=#c=[cl]#sa=[sa]#mt=[mt]#oto=[oto]#|TP=[tp]#ust=[stake]#st=[stake]#tr=[money_return]#||&betsource=FlashInPLay&tagType=WindowsDesktopBrowser&bs=1&qb=1"
    post_data_tpl = "pt=N#o=[odds]#f=[f]#fp=[fp]#so=#c=[cl]#sa=[sa]#mt=[mt]#oto=[oto]#|TP=[tp]#"
    ms_tpl = "id=[id]#bc=[bc]#"

    bets_items = []
    ms_items = []
    bets = answer["bt"]
    for num_bet, bet in enumerate(bets, 1):
        logger.debug("%s/%s %s" % (num_bet, len(bets), bet))
        pt = bet["pt"][0]

        odds0 = bet["od"]
        if odds_must_be:
            odd_must_be = odds_must_be[num_bet - 1]
            if odds0 != odd_must_be:
                logger.warning(
                    "    odds %s != %s must be, so skip" % (odds0, odd_must_be)
                )
                continue
        f0 = bet["fi"]
        fp0 = pt["pi"]
        sa0 = bet.get("sa", "")
        mt = bet["mt"]
        tp0 = bet["tp"]
        cl = bet.get("cl", "")
        oto = bet.get("oo", "")
        bc = bet.get("bc", "")

        if 0 and num_bet == 1 and debug:
            odds0 = "2/1"
            logger.warning("fixing odds for debug: odds0=%s" % odds0)

        t = 0
        if t:
            if sa is None:
                sa = sa0

            if f is None:
                f = f0

            if fp is None:
                fp = fp0

            if not odds:
                odds = odds0
        else:
            sa = sa0
            f = f0
            fp = fp0
            odds = odds0

        if f is not None and fp is not None:
            repl = {
                str(f0): str(f),
                str(fp0): str(fp),
            }
            # tp = tp0.replace(f0, f).replace(fp0, fp)
            tp = no_probely_one(tp0, repl)
        else:
            tp = tp0
        # logger.debug(
        #     "tp=%s from tp0=%s, f=%s (f0=%s), fp=%s (fp0=%s)"
        #     % (tp, tp0, f, f0, fp, fp)
        # )

        post_stake = stake_to_postStake(stake)
        odds_fractional = odds
        odds_to_eval = "1. * %s" % odds_fractional
        # logger.debug("odds_to_eval=`%s`" % odds_to_eval)
        odds_float = eval(odds_to_eval) + 1
        money_return = "%.02f" % round(odds_float * float(stake), 2)
        # wait_for_ok(money_return)
        # &ns=pt=N#o=15/4#f=109873988#fp=157938934#so=#c=1#sa=619b64d4-FE0B9643#mt=16#|TP=BS109873988-157938934#ust=0.10#st=0.10#tr=0.47#||&betsource=FlashInPLay&tagType=WindowsDesktopBrowser&bs=1&qb=1

        # logger.debug('cc=`%s` from `%s`' % (cc, cc0))
        repl = {
            "[url]": url,
            "[cc]": cc,
            "[cl]": cl,
            "[pc]": pc,
            "[bet_guid]": bet_guid,
            "[odds]": odds,
            "[f]": f,
            "[fp]": fp,
            "[sa]": sa,
            "[mt]": mt,
            "[tp]": tp,
            "[oto]": oto,
            "[bc]": bc,
        }

        tpl = post_data_tpl
        if checked_want_place(1, place_on):
            tpl = tpl + "ust=[stake]#st=[stake]#tr=[money_return]#"
            # wait_for_ok(tpl)

        post_data = no_probely_one(tpl, repl)
        bets_items.append(post_data)

        ms_item = no_probely_one(ms_tpl, repl)
        ms_items.append(ms_item)

    if len(bets_items) != len(bets):
        logger.warning(
            f"have {len(bets_items)}/{len(bets)} bets with the same odds"
        )

    bets_post_data = "||".join(bets_items)
    ms_post_data = "||".join(ms_items)

    cnt_bets = len(bets_items)
    if 1 and cnt_bets == 1:
        post_data_tpl = "&ns=[bets_post_data]#ust=[stake]#st=[stake]#tr=[money_return]#||&betsource=[betsource]&tagType=WindowsDesktopBrowser&bs=1&qb=1"
    else:
        post_data_tpl = "&ns=[bets_post_data]#||&ms=[ms_post_data]||&betsource=[betsource]&tagType=WindowsDesktopBrowser&bs=1"
        # create ms
        if want_multiples:
            kwargs = {
                "multiples": multiples,
                "stake": stake,
                "stakes": stakes,
                "place_on": place_on,
            }
            r_ms = create_ms_for_placebet_from_multiples(**kwargs)
        else:
            kwargs = {
                "cnt_bets": cnt_bets,
                "stake": stake,
                "stakes": stakes,
                "place_on": place_on,
            }
            r_ms = create_ms_for_placebet(**kwargs)

        ms_post_data = r_ms["ms"]

        logger.debug(
            f"""    +{r_ms["cnt_selections"]} possible multiples: {ms_post_data=} {r_ms=}"""
        )
        # wait_for_ok(ms_post_data)

        if (
            1 and not r_ms["cnt_selections"]
        ):  # невозможные мультиплы с одной игры?
            error = "multiples_impossible"
            error_details = {
                "kwargs": kwargs,
                "r_ms": r_ms,
            }

    repl = {
        "[bets_post_data]": bets_post_data,
        "[ms_post_data]": ms_post_data,
        "[stake]": post_stake,
        "[money_return]": money_return,
        "[betsource]": betsource,
        "[cnt_bets]": cnt_bets,
    }
    post_data = no_probely_one(post_data_tpl, repl)
    post_data = post_data.replace("#oto=#", "#")
    # logger.debug("post_data=%s" % post_data)

    if error == "multiples_impossible":
        logger.debug(f"multiples_impossible, so post_data is empty")
        post_data = ""

    if detailed:
        return {
            "url": url,
            "post_data": post_data,
            "error": error,
            "error_details": error_details,
        }

    if not tpl:
        tpl = """
        POST [url]
        [headers]

        [data]
        """
    repl_tpl_data = {
        "[url]": url,
        "[data]": post_data,
    }
    tpl = no_probely(tpl, repl_tpl_data)
    data = no_probely_one(tpl, repl)
    data = data.strip()

    return data


def convert_multiple_bet365Urls_to_addbetData(
    urls=[],
    mt=None,
    tpl_post_data="&ns=[ns]||&ms=[ms]||&betsource=FlashInPLay&bs=1&qb=1&cr=1",
    stake=0.1,
    stakes={},
    place_on=[0],
    debug: bool = False,
):
    ns = []
    for url in urls:
        _ = convert_bet365Url_to_addbetData(url, mt, tpl_post_data="[ns]")

        # Одинарные ставки дописываются сюда
        if checked_want_place(1, place_on):
            post_stake = stake_to_postStake(stake)
            stake_info = "ust=[stake]#st=[stake]#".replace(
                "[stake]", post_stake
            )
            _ = _ + stake_info
        ns.append(_)
    ns = "||".join(ns)

    # create ms
    kwargs = {
        "cnt_bets": len(urls),
        "stake": stake,
        "stakes": stakes,
        "place_on": place_on,
        "debug": debug,
    }
    r_ms = create_ms_for_placebet(**kwargs)
    ms = r_ms["ms"]
    repl = {
        "[ns]": ns,
        "[ms]": ms,
    }
    data = no_probely_one(tpl_post_data, repl)
    if debug:
        logger.debug(
            "   +%s selections: %s"
            % (r_ms["cnt_selections"], r_ms["selections"])
        )
    _ = {
        "data": data,
        "ns": ns,
        "ms": ms,
        "selections": r_ms["selections"],
        "cnt_selections": r_ms["cnt_selections"],
    }
    return _


def create_ms_for_placebet_from_multiples(
    # cnt_bets=7,
    multiples=[],  # тут мультиплы от refreshslip
    stake=0.1,
    stakes=None,
    place_on=[0],
    # debug=True,
    debug=False,
):
    """
    ** -> id=6#bc=1#ust=0.10#st=0.10#||id=-1#bc=6#||id=2#bc=15#ust=0.12#st=0.12#||id=3#bc=20#ust=0.13#st=0.13#||id=4#bc=15#ust=0.14#st=0.14#||id=5#bc=6#ust=0.15#st=0.15#||id=34#bc=57#ust=0.16#st=0.16#

    place_on
        0 это только один главный мультипл
        1 ординары
        2 - двойные

    Доделать:
        sl - пока непонятно что такое. Возможно когда ставки нет?

    У бетки иногда с 0 в конце, иногда нет - у меня всегда с 0
        #ust=0.10#
    """
    stakes = get_default_multistakes(stakes)
    post_data_tpl = "id=[id]#bc=[bc]#"

    results = []

    cnt_selections = 0
    for multiple in multiples:
        bc = multiple.get(
            "bc"
        )  # сколько их получается. bc=3 для одинаров из 3-х ставок

        id = multiple.get("bt")
        num = id  # 1 - одинары, 2 - двойки, 3 - тройки
        # для одинаров ищем num
        if id == -1:
            num = 1

        post_stake = stakes.get(num, stake)
        post_stake = stake_to_postStake(post_stake)

        tpl = post_data_tpl
        if checked_want_place(num, place_on) and num != 1:
            tpl = tpl + "ust=[stake]#st=[stake]#"
            cnt_selections += bc

        repl = {
            "[stake]": post_stake,
            "[id]": id,
            "[bc]": bc,
        }
        # logger.debug("     %s, selections %s" ())
        result = no_probely_one(tpl, repl)
        # logger.debug()
        results.append(result)

    ms = "||".join(results)
    _ = {
        "ms": ms,
        "selections": [],
        "cnt_selections": cnt_selections,
    }
    return _


def create_ms_for_placebet(
    cnt_bets=7,
    stake=0.1,
    stakes=None,
    place_on=[0],
    multiples=[],  # тут мультиплы от refreshslip
    # debug=True,
    debug=False,
):
    """
    ** -> id=6#bc=1#ust=0.10#st=0.10#||id=-1#bc=6#||id=2#bc=15#ust=0.12#st=0.12#||id=3#bc=20#ust=0.13#st=0.13#||id=4#bc=15#ust=0.14#st=0.14#||id=5#bc=6#ust=0.15#st=0.15#||id=34#bc=57#ust=0.16#st=0.16#

    place_on
        0 это только один главный мультипл
        1 ординары
        2 - двойные

    Доделать:
        sl - пока непонятно что такое. Возможно когда ставки нет?

    У бетки иногда с 0 в конце, иногда нет - у меня всегда с 0
        #ust=0.10#
    """
    fun = "create_ms_for_placebet"
    stakes = get_default_multistakes(stakes)
    post_data_tpl = "id=[id]#bc=[bc]#"

    cnt_bets_to_id = {
        3: 14,
        4: 21,
        5: 27,
        6: 34,
        7: 40,
    }

    results = []
    all_cnt_selections = []
    all_selections = []

    if cnt_bets <= 2:
        num_last_bet = cnt_bets
    else:
        num_last_bet = cnt_bets + 1

    for num in range(num_last_bet):
        multiple = {}
        try:
            multiple = multiples[num]
            if debug:
                logger.debug("    use fixed multiple %s" % multiple)
        except Exception as er:
            pass

        post_stake = stakes.get(num, stake)
        post_stake = stake_to_postStake(post_stake)

        bc_list = list(
            itertools.combinations(map(str, range(1, cnt_bets + 1)), num)
        )
        selections = ["/".join(_) for _ in bc_list]
        cnt_selections = len(bc_list)

        id = None
        if num == 0:
            id = cnt_bets
            bc_list = list(
                itertools.combinations(
                    map(str, range(1, cnt_bets + 1)), cnt_bets
                )
            )
            selections = ["/".join(_) for _ in bc_list]
            cnt_selections = len(bc_list)

        elif num == 1:
            id = -1

        elif num == cnt_bets:
            id = cnt_bets_to_id.get(cnt_bets, (cnt_bets - 1) * 7)
            selections = []
            cnt_selections = sum(all_cnt_selections) - cnt_bets

        else:
            id = num

        if debug:
            logger.debug(
                f"{cnt_selections} {selections=}, cnt_selections={bc_list}"
            )

        tpl = post_data_tpl
        if checked_want_place(id, place_on):
            tpl = tpl + "ust=[stake]#st=[stake]#"
            all_selections.append(selections)

        bc = cnt_selections

        if multiple:
            if debug:
                logger.debug(f"   use {id=}, {bc=} from {multiple=}")
            id = multiple.get("bt", id)
            bc = multiple.get("bc", bc)
        repl = {
            "[stake]": post_stake,
            "[id]": id,
            "[bc]": bc,
        }
        # logger.debug("     %s, selections %s" ())
        result = no_probely_one(tpl, repl)
        # logger.debug()
        results.append(result)

        all_cnt_selections.append(cnt_selections)

    all_selections = sum(all_selections, [])
    if debug:
        logger.debug(f"{all_selections=}")

    ms = "||".join(results)
    _ = {
        "ms": ms,
        "selections": all_selections,
        "cnt_selections": len(all_selections),
    }

    if debug:
        logger.debug(f"  +{fun} {ms=} for {cnt_bets} bets, {place_on=}")
    return _


def get_default_multistakes(stakes=None):
    if stakes is None:
        stakes = {
            0: 0.1,
            # 1: 0.11,
            # 2: 0.12,
            # 3: 0.13,
            # 4: 0.14,
            # 5: 0.15,
            # 6: 0.16,
        }
    return stakes


if __name__ == "__main__":

    special = "convert_multiple_bet365Urls_to_addbetData"
    special = "create_ms_for_placebet_from_multiples"
    special = "create_ms_for_placebet"
    special = "prepare_composerData_for_placebet_after_addbet"

    if special == "create_ms_for_placebet":
        special = 2

        if special == 7:
            kwargs = {
                "cnt_bets": 7,
                "stake": 0.22,
                "stakes": {7: 0.22,},
                "place_on": [0, 7],
            }
            must_be = "id=7#bc=1#ust=0.22#st=0.22#sl=0#||id=-1#bc=7#||id=2#bc=21#sl=0#||id=3#bc=35#sl=0#||id=4#bc=35#sl=0#||id=5#bc=21#sl=0#||id=6#bc=7#sl=0#||id=40#bc=120#ust=0.22#st=0.22#sl=0#"

        elif special == 6:
            kwargs = {
                "cnt_bets": 6,
                # "stake": 0.22,
                "place_on": [0, 1, 2, 3, 4, 5, 6],
            }
            must_be = """
    # 6 folds
id=6#bc=1#ust=0.10#st=0.10#||

	# Singles (6)
id=-1#bc=6#||

# doubles (15)
id=2#bc=15#ust=0.12#st=0.12#||

	# Trebles (20)
id=3#bc=20#ust=0.13#st=0.13#||

 # 4 folds (15)
id=4#bc=15#ust=0.14#st=0.14#||

 # 5 folds (6)
id=5#bc=6#ust=0.15#st=0.15#||

 # Heinz (57)
id=34#bc=57#ust=0.16#st=0.16#
            """
        elif special == 5:
            kwargs = {
                "cnt_bets": 5,
                "place_on": [0, 1, 2, 3, 4, 5],
            }
            must_be = """
            id=5#bc=1#ust=0.1#st=0.1#||
id=-1#bc=5#||
id=2#bc=10#ust=0.12#st=0.12#||
id=3#bc=10#ust=0.13#st=0.13#||
id=4#bc=5#ust=0.14#st=0.14#||
id=27#bc=26#ust=0.15#st=0.15#||
            """

        elif special == 2:
            kwargs = {
                "cnt_bets": 2,
                "place_on": [2, 3],
            }
            must_be = ""
        else:
            logger.critical("unknown special=%s" % special)

        r_ms = create_ms_for_placebet(**kwargs)
        answer = r_ms["ms"]
        must_be = "".join(clear_list(must_be, bad_starts="#"))
        must_be = (
            must_be.replace("#sl=0", "")
            .replace("\n", "")
            .replace(" ", "")
            .replace("\t", "")
            .strip()
        )
        logger.debug("  my: %s `%s`" % (type(answer), answer))
        logger.debug("real: %s `%s`" % (type(must_be), must_be))
        if answer == must_be:
            print_success("good converted")
        else:
            print_error("bad converted")

    elif special == "convert_multiple_bet365Urls_to_addbetData":
        ns = "pt=N#o=11/4#f=111216582#fp=285683181#so=#c=1#sa=61b63532-7B9AF706#mt=16#|TP=BS111216582-285683181#olc=1#||pt=N#o=11/2#f=110882748#fp=254388147#so=#c=1#sa=61b63536-F32124C8#mt=16#|TP=BS110882748-254388147#||"
        urls = clear_list(ns.replace("||", "\n"))
        urls = [create_bet365Url_from_any_data(url)[0] for url in urls]
        # wait_for_ok(urls)
        kwargs = {
            "urls": urls,
            "place_on": [0, 1],
        }
        data = convert_multiple_bet365Urls_to_addbetData(**kwargs)
        logger.info("data= `%s` from %s urls %s" % (data, len(urls), urls))

    elif special == "prepare_composerData_for_placebet_after_addbet":

        special = "double_stake"
        special = "one_stake"
        special = "multi_stake"

        place_on = [2, 3]

        if special == "one_stake":
            answer = """{"bg":"28c59b20-405e-4719-b817-19307e1de684","sr":0,"mr":false,"ir":false,"at":0,"cc":"Io+6VeaVY7HGDnGiLcgTEL72DuY2MmTLQ8cgDwVnaUI=","pc":"1003226322479832779","vr":"504","cs":1,"st":1,"bt":[{"ob":[{"oc":"PSSOCCER","ot":3}],"cl":1,"sa":"61b51a4d-991E6554","tp":"BS110881864-254354090","fb":0.0,"mt":16,"mr":false,"cs":0,"bt":1,"pf":"N","od":"1/1","fi":110881864,"fd":"Burnley v West Ham","pt":[{"pi":254354090,"bd":"West Ham","md":"Full Time Result"}],"sr":0}],"bs":[]}"""
            post_data_must_be = """&ns=pt=N#o=1/1#f=110881864#fp=254354090#so=#c=1#sa=61b51a4d-991E6554#mt=16#|TP=BS110881864-254354090#ust=0.10#st=0.10#tr=0.20#||&betsource=Lite&tagType=WindowsDesktopBrowser&bs=1&qb=1"""

        elif special == "double_stake":
            answer = """{"bg":"d2dee637-c928-471f-a6dd-b29bb7e81cdc","sr":0,"mr":false,"ir":false,"at":0,"cc":"K5tXaYwtydkIEJzv9/kRmQAXa29ORD/LbkjDjr4C980=","pc":"14688034457912982505","vr":"504","cs":1,"st":1,"bt":[{"ob":[{"oc":"PSSOCCER","ot":3}],"cl":1,"sa":"61b4e815-65052CFF","tp":"BS111216561-285682352","fb":0.0,"mt":16,"mr":false,"cs":0,"bt":1,"pf":"N","od":"13/5","fi":111216561,"fd":"Athletic Bilbao v Sevilla","pt":[{"pi":285682352,"bd":"Sevilla","md":"Full Time Result"}],"sr":0},{"ob":[],"cl":1,"sa":"61b4e818-F3F32247","tp":"BS111847796-345161006","fb":0.0,"mt":16,"mr":false,"cs":0,"bt":1,"pf":"N","od":"8/5","fi":111847796,"fd":"Portland Timbers v New York City FC","pt":[{"pi":345161006,"bd":"New York City FC","md":"Full Time Result"}],"sr":0}],"dm":{"bt":2,"od":"8.36/1","bd":"Doubles","bc":1,"ea":false,"ew":false,"cb":false,"ma":0},"mo":[{"bt":-1,"bd":"","bc":2,"ea":false,"ew":false,"cb":false,"ma":0}],"bs":[1,2]}"""
            post_data_must_be = """&ns=pt=N#o=13/5#f=111216561#fp=285682352#so=#c=1#sa=61b4e815-65052CFF#mt=16#|TP=BS111216561-285682352#||pt=N#o=8/5#f=111847796#fp=345161006#so=#c=1#sa=61b4e818-F3F32247#mt=16#|TP=BS111847796-345161006#||&ms=id=2#bc=1#ust=0.1#st=0.1#||id=-1#bc=2#||&betsource=FlashInPLay&tagType=WindowsDesktopBrowser&bs=1"""

        elif special == "multi_stake":
            answer = """{"bg":"e986d214-a427-4bfc-9e38-1c06267d39c6","sr":0,"mr":false,"ir":true,"at":0,"cc":"hU2XnFgadqjFngE2a3jzXz1/xMWmatkuAn3rC7Oe2tg=","pc":"16523973679417713397","vr":"504","cs":1,"st":1,"bt":[{"ob":[],"cl":1,"tp":"BS112049282-363087958","fb":0.0,"mt":2,"mr":false,"cs":0,"bt":1,"pf":"N","od":"17/4","fi":112049282,"fd":"WAA Banjul v Banjul United","pt":[{"pi":363087958,"bd":"Banjul United","md":"Fulltime Result"}],"sr":0},{"ob":[],"cl":1,"tp":"BS112049211-363080714","fb":0.0,"mt":2,"mr":false,"cs":0,"bt":1,"pf":"N","od":"7/5","fi":112049211,"fd":"CSD Solola v Antigua GFC","pt":[{"pi":363080714,"bd":"Antigua GFC","md":"Fulltime Result"}],"sr":0},{"ob":[],"cl":1,"tp":"BS112069420-365324587","fb":0.0,"mt":2,"mr":false,"cs":0,"bt":1,"pf":"N","od":"9/4","fi":112069420,"fd":"Olancho FC v Juticalpa","pt":[{"pi":365324587,"bd":"Juticalpa","md":"Fulltime Result"}],"sr":0}],"dm":{"bt":3,"od":"39.95/1","bd":"Trebles","bc":1,"ea":false,"ew":false,"cb":false,"ma":0},"mo":[{"bt":-1,"bd":"","bc":3,"ea":false,"ew":false,"cb":false,"ma":0},{"bt":2,"od":"","bd":"Doubles","bc":3,"ea":false,"ew":false,"cb":false,"ma":0},{"bt":14,"od":"","bd":"Trixie","bc":4,"ea":false,"ew":false,"cb":false,"ma":0}],"bs":[1,2]}"""
            answer = """{"bg":"4a73d839-be75-4b92-9ea3-093cb7943fcf","sr":0,"mr":false,"ir":true,"at":0,"cc":"0oLFQL86fhjK28AcwBnrepD2QKVaXm6wHOaaVQrx7sw=","pc":"16523973679417713397","vr":"504","cs":1,"st":1,"bt":[{"ob":[],"cl":1,"sa":"61b51ee4-617D093C","tp":"BS112049282-363087958","fb":0.0,"mt":2,"mr":false,"cs":0,"bt":1,"pf":"N","od":"17/4","fi":112049282,"fd":"WAA Banjul v Banjul United","pt":[{"pi":363087958,"bd":"Banjul United","md":"Fulltime Result"}],"sr":0},{"ob":[],"cl":1,"sa":"61b51ee4-F37F2F1F","tp":"BS112049211-363080714","fb":0.0,"mt":2,"mr":false,"cs":0,"bt":1,"pf":"N","od":"7/5","fi":112049211,"fd":"CSD Solola v Antigua GFC","pt":[{"pi":363080714,"bd":"Antigua GFC","md":"Fulltime Result"}],"sr":0},{"ob":[],"cl":1,"sa":"61b51ee4-5248C439","tp":"BS112069420-365324587","fb":0.0,"mt":2,"mr":false,"cs":0,"bt":1,"pf":"N","od":"9/4","fi":112069420,"fd":"Olancho FC v Juticalpa","pt":[{"pi":365324587,"bd":"Juticalpa","md":"Fulltime Result"}],"sr":0}],"dm":{"bt":3,"od":"39.95/1","bd":"Trebles","bc":1,"ea":false,"ew":false,"cb":false,"ma":0},"mo":[{"bt":-1,"bd":"","bc":3,"ea":false,"ew":false,"cb":false,"ma":0},{"bt":2,"od":"","bd":"Doubles","bc":3,"ea":false,"ew":false,"cb":false,"ma":0},{"bt":14,"od":"","bd":"Trixie","bc":4,"ea":false,"ew":false,"cb":false,"ma":0}],"bs":[1,2]}"""
            post_data_must_be = """&ns=pt=N#o=17/4#f=112049282#fp=363087958#so=#c=1#sa=61b51ee4-617D093C#mt=2#|TP=BS112049282-363087958#||pt=N#o=7/5#f=112049211#fp=363080714#so=#c=1#sa=61b51ee4-F37F2F1F#mt=2#|TP=BS112049211-363080714#||pt=N#o=9/4#f=112069420#fp=365324587#so=#c=1#sa=61b51ee4-5248C439#mt=2#|TP=BS112069420-365324587#||&ms=id=3#bc=1#ust=0.1#st=0.1#||id=-1#bc=3#||id=2#bc=3#||id=14#bc=4#||&betsource=FlashInPLay&tagType=WindowsDesktopBrowser&bs=1"""

            t = 0
            if t:
                # кони
                answer = """{"bg":"28a4ad43-a835-4f1a-bbb8-b51c935e49c4","sr":2,"mr":false,"ir":false,"at":0,"cc":"nhhPiKYYxCrTeEqiUDyUjowtsfAewVdkzvQ7un+eec0=","pc":"7797777640841711494","vr":"506","cs":1,"st":1,"mi":"","mv":"","bt":[{"ob":[],"cl":2,"sa":"61b5cfb1-D3A43CA4","tp":"BS112019813-360387406x2x2","fb":0.0,"mt":13,"mr":false,"oo":2,"cs":0,"bt":1,"pf":"N","od":"21/10","fi":112019813,"fd":"Race 1 Newcastle","pt":[{"pi":360387406,"bd":"A Real Riot","md":"Fixed Place"}],"sr":0},{"ob":[],"cl":2,"sa":"61b5cfb7-3749246","tp":"BS112019813-360387433x2x2","fb":0.0,"mt":13,"mr":false,"oo":2,"cs":0,"bt":1,"pf":"N","od":"10/1","fi":112019813,"fd":"Race 1 Newcastle","pt":[{"pi":360387433,"bd":"Buckin' Rippa","md":"Fixed Place"}],"sr":0},{"ob":[],"cl":2,"sa":"61b5cfbd-A2D9101A","tp":"BS112019813-360387498x2x2","fb":0.0,"mt":13,"mr":false,"oo":2,"cs":0,"bt":1,"pf":"N","od":"10/1","fi":112019813,"fd":"Race 1 Newcastle","pt":[{"pi":360387498,"bd":"Superclaid","md":"Fixed Place"}],"sr":0},{"ob":[],"cl":2,"sa":"61b5cfbf-E80CC945","tp":"BS112019813-360387533x2x2","fb":0.0,"mt":13,"mr":false,"oo":2,"cs":0,"bt":1,"pf":"N","od":"3/4","fi":112019813,"fd":"Race 1 Newcastle","pt":[{"pi":360387533,"bd":"Hettinger","md":"Fixed Place"}],"sr":0}],"bs":[1,2]}"""
                post_data_must_be = """&ns=pt=N#o=21/10#f=112019813#fp=360387406#so=#c=2#sa=61b5cfb1-D3A43CA4#mt=13#oto=2#|TP=BS112019813-360387406x2x2#||pt=N#o=10/1#f=112019813#fp=360387433#so=#c=2#sa=61b5cfb7-3749246#mt=13#oto=2#|TP=BS112019813-360387433x2x2#||pt=N#o=10/1#f=112019813#fp=360387498#so=#c=2#sa=61b5cfbd-A2D9101A#mt=13#oto=2#|TP=BS112019813-360387498x2x2#||pt=N#o=3/4#f=112019813#fp=360387533#so=#c=2#sa=61b5cfbf-E80CC945#mt=13#oto=2#|TP=BS112019813-360387533x2x2#ust=0.10#st=0.10#tr=0.17#||&betsource=FlashInPLay&tagType=WindowsDesktopBrowser&bs=1"""

            answer = """{"bg":"5536e504-1de6-4c65-9aca-900677ec473e","sr":2,"mr":true,"ir":false,"at":0,"cc":"MI3QLPNfXdwpto2h2g/OLDGlzkyQE4a3NLwpFQ93Gbc=","pc":"3646635711229564245","vr":"506","cs":1,"st":1,"mi":"","mv":"","bt":[{"ob":[],"cl":2,"sa":"61b5cfbf-E80CC945","tp":"BS112019813-360387533x2x2","fb":0.0,"mt":13,"mr":true,"oo":2,"cs":0,"bt":1,"pf":"N","od":"3/4","fi":112019813,"fd":"Race 1 Newcastle","pt":[{"pi":360387533,"bd":"Hettinger","md":"Fixed Place"}],"sr":2},{"ob":[],"cl":2,"sa":"61b5d395-2C3036C8","tp":"BS112019813-360387559x2x2","fb":0.0,"mt":13,"mr":true,"oo":2,"cs":0,"bt":1,"pf":"N","od":"30/1","fi":112019813,"fd":"Race 1 Newcastle","pt":[{"pi":360387559,"bd":"Le Bernadin","md":"Fixed Win"}],"sr":2},{"ob":[],"cl":2,"sa":"61b5d396-F10A120A","tp":"BS112019813-360387575x2x2","fb":0.0,"mt":13,"mr":true,"oo":2,"cs":0,"bt":1,"pf":"N","od":"17/10","fi":112019813,"fd":"Race 1 Newcastle","pt":[{"pi":360387575,"bd":"Nayziair","md":"Fixed Place"}],"sr":2},{"ob":[{"oc":"PSSOCCER","ot":3}],"cl":1,"sa":"61b5d3a2-DD4D5946","tp":"BS110881876-254354619","fb":0.0,"mt":16,"mr":false,"cs":0,"bt":1,"pf":"N","od":"23/10","fi":110881876,"fd":"Crystal Palace v Everton","pt":[{"pi":254354619,"bd":"Everton","md":"Full Time Result"}],"sr":0},{"ob":[{"oc":"PSSOCCER","ot":3}],"cl":1,"sa":"61b5d3a4-A70CD5C0","tp":"BS111549403-316966114","fb":0.0,"mt":16,"mr":false,"cs":0,"bt":1,"pf":"N","od":"8/15","fi":111549403,"fd":"Hearts v Rangers","pt":[{"pi":316966114,"bd":"Rangers","md":"Full Time Result"}],"sr":0},{"ob":[{"oc":"PSSOCCER","ot":3}],"cl":1,"sa":"61b5d3ae-6EECC889","tp":"BS110882748-254388147","fb":0.0,"mt":16,"mr":false,"cs":0,"bt":1,"pf":"N","od":"11/2","fi":110882748,"fd":"PSG v Monaco","pt":[{"pi":254388147,"bd":"Monaco","md":"Full Time Result"}],"sr":0}],"dm":{"bt":4,"od":"","bd":"4 Folds","bc":3,"ea":false,"ew":false,"cb":false,"ma":0},"mo":[{"bt":-1,"bd":"","bc":6,"ea":false,"ew":false,"cb":false,"ma":0},{"bt":2,"od":"","bd":"Doubles","bc":12,"ea":false,"ew":false,"cb":false,"ma":0},{"bt":3,"od":"","bd":"Trebles","bc":10,"ea":false,"ew":false,"cb":false,"ma":0},{"bt":21,"od":"","bd":"Yankee","bc":33,"ea":false,"ew":false,"cb":false,"ma":0}],"bs":[1,2]}"""
            post_data_must_be = """&ns=pt=N#o=3/4#f=112019813#fp=360387533#so=#c=2#sa=61b5cfbf-E80CC945#mt=13#oto=2#|TP=BS112019813-360387533x2x2#||pt=N#o=30/1#f=112019813#fp=360387559#so=#c=2#sa=61b5d395-2C3036C8#mt=13#oto=2#|TP=BS112019813-360387559x2x2#||pt=N#o=17/10#f=112019813#fp=360387575#so=#c=2#sa=61b5d396-F10A120A#mt=13#oto=2#|TP=BS112019813-360387575x2x2#||pt=N#o=23/10#f=110881876#fp=254354619#so=#c=1#sa=61b5d3a2-DD4D5946#mt=16#|TP=BS110881876-254354619#||pt=N#o=8/15#f=111549403#fp=316966114#so=#c=1#sa=61b5d3a4-A70CD5C0#mt=16#|TP=BS111549403-316966114#||pt=N#o=11/2#f=110882748#fp=254388147#so=#c=1#sa=61b5d3ae-6EECC889#mt=16#|TP=BS110882748-254388147#||&ms=id=4#bc=3#ust=0.1#st=0.1#||id=-1#bc=6#||id=2#bc=12#||id=3#bc=10#||id=21#bc=33#||&betsource=FlashInPLay&tagType=WindowsDesktopBrowser&bs=1"""

            t = 1
            if t:
                answer = """"""
                post_data_must_be = """&ns=pt=N#o=11/20#f=111549403#fp=316966114#so=#c=1#sa=61b5e158-62EB0533#mt=16#|TP=BS111549403-316966114#||pt=N#o=20/1#f=111549405#fp=316966366#so=#c=1#sa=61b5e15a-67C1D3E2#mt=16#|TP=BS111549405-316966366#||pt=N#o=11/4#f=111216582#fp=285683181#so=#c=1#sa=61b5e15b-4FCCC265#mt=16#|TP=BS111216582-285683181#||&ms=id=3#bc=1#ust=0.1#st=0.1#||id=-1#bc=3#||id=2#bc=3#||id=14#bc=4#||&betsource=FlashInPLay&tagType=WindowsDesktopBrowser&bs=1"""

            t = 1
            if t:
                answer = """{"bg":"92a7305c-1ce5-494b-be7a-188984b35387","sr":0,"mr":false,"ir":false,"at":0,"cc":"MVuFBajrTI8etx76tAwkiOyv3bmKdDkcvf5Oq/5ZbSk=","pc":"13855235137618031214","vr":"509","cs":1,"st":1,"bt":[{"ob":[{"oc":"PSSOCCER","ot":3},{"oc":"PREMAC","ot":1}],"cl":1,"sa":"61b9d72c-85C01F39","tp":"BS110881903-254355764","fb":0.0,"mt":1,"mr":false,"cs":0,"bt":1,"pf":"N","od":"23/10","fi":110881903,"fd":"Arsenal v West Ham","pt":[{"pi":254355764,"bd":"West Ham","md":"Full Time Result"}],"st":0.10,"sr":0},{"ob":[{"oc":"PSSOCCER","ot":3},{"oc":"PREMAC","ot":1}],"cl":1,"sa":"61b9d72c-88E7E416","tp":"BS110881897-254355381","fb":0.0,"mt":1,"mr":false,"cs":0,"bt":1,"pf":"N","od":"23/10","fi":110881897,"fd":"Brighton v Wolverhampton","pt":[{"pi":254355381,"bd":"Wolverhampton","md":"Full Time Result"}],"st":0.10,"sr":0},{"ob":[{"oc":"PSSOCCER","ot":3},{"oc":"PREMAC","ot":1}],"cl":1,"sa":"61b9d72c-9B902E28","tp":"BS110881899-254355521","fb":0.0,"mt":1,"mr":false,"cs":0,"bt":1,"pf":"N","od":"12/5","fi":110881899,"fd":"Burnley v Watford","pt":[{"pi":254355521,"bd":"Watford","md":"Full Time Result"}],"st":0.10,"sr":0}],"dm":{"bt":3,"od":"36.02/1","bd":"Trebles","bc":1,"ea":false,"ew":false,"cb":false,"ap":5.00,"ma":100000},"mo":[{"bt":-1,"bd":"","bc":3,"ea":false,"ew":false,"cb":false,"ma":0},{"bt":2,"od":"","bd":"Doubles","bc":3,"ea":false,"ew":false,"cb":false,"ma":0},{"bt":14,"od":"","bd":"Trixie","bc":4,"ea":false,"ew":false,"cb":false,"ma":0},{"bt":15,"od":"","bd":"Patent","bc":7,"ea":false,"ew":false,"cb":false,"ma":0}],"bs":[1,2]}"""
                post_data_must_be = """&ns=pt=N#o=13/5#f=110881901#fp=254355692#so=#c=1#sa=61b9d898-C1ECC0CD#mt=16#|TP=BS110881901-254355692#ust=0.11#st=0.11#tr=0.39#||pt=N#o=12/5#f=110881899#fp=254355521#so=#c=1#sa=61b9d898-CEA18C05#mt=16#|TP=BS110881899-254355521#ust=0.11#st=0.11#tr=0.37#||pt=N#o=23/10#f=110881897#fp=254355381#so=#c=1#sa=61b9d898-730650E1#mt=16#|TP=BS110881897-254355381#ust=0.11#st=0.11#tr=0.36#||pt=N#o=23/10#f=110881903#fp=254355764#so=#c=1#sa=61b9d89a-333D2419#mt=16#|TP=BS110881903-254355764#ust=0.11#st=0.11#tr=0.36#||&ms=id=4#bc=1#ust=0.1#st=0.1#||id=-1#bc=4#||id=2#bc=6#ust=0.12#st=0.12#||id=3#bc=4#||id=21#bc=11#||&betsource=FlashInPLay&tagType=WindowsDesktopBrowser&bs=1"""

            if t:
                # невозможный тройно мультипл
                place_on = [3]
                answer = """{"bg":"141e3a54-7b08-40ef-ae84-bb06fdb68640","sr":2,"mr":true,"ir":false,"at":0,"cc":"IZWXAuMfRtvDex1H6qW70z2uJkhdGI7UXj8n0EyCKBs=","pc":"1336710427972090661","vr":"521","cs":1,"st":1,"mi":"","mv":"","bt":[{"ob":[],"cl":1,"sa":"61d3311e-32AF614A","tp":"BS113133250-454081767","fb":0.0,"mt":1,"mr":true,"oo":2,"cs":0,"bt":1,"pf":"N","od":"5/4","fi":113133250,"fd":"Jamshedpur FC v Northeast United","pt":[{"hd":"0.0,+0.5","pi":454081767,"bd":"Northeast United","ha":"0.25","md":"Alternative Asian Handicap"}],"sr":2},{"ob":[],"cl":1,"sa":"61d3311e-4C6618D7","tp":"BS113133249-452825459","fb":0.0,"mt":1,"mr":true,"cs":0,"bt":1,"pf":"N","od":"5/6","fi":113133249,"fd":"Jamshedpur FC v Northeast United","pt":[{"pi":452825459,"bd":"Jamshedpur FC","md":"Full Time Result"}],"sr":2},{"ob":[],"cl":13,"sa":"61d3311e-D4DC00E0","tp":"BS113138077-454525885","fb":0.0,"mt":1,"mr":false,"cs":0,"bt":1,"pf":"N","od":"1/1","fi":113138077,"fd":"Holger Vitus Nodskov Rune vs Corentin Moutet","pt":[{"pi":454525885,"bd":"Under 9.5","ha":"9.5","md":"1st Set Total Games"}],"sr":0}],"dm":{"bt":2,"od":"","bd":"Doubles","bc":2,"ea":false,"ew":false,"cb":false,"ma":0},"mo":[{"bt":-1,"bd":"","bc":3,"ea":false,"ew":false,"cb":false,"ma":0}],"bs":[1,2]}"""
                post_data_must_be = """"""

        else:
            logger.critical("unknown special=%s" % special)
            os._exit(0)

        tpl = ""
        tpl = "[data]"

        answer = obj_from_json(answer.strip())

        kwargs = {
            "answer": answer,
            "tpl": tpl,
            # "place_on": [0, 1],
            "place_on": place_on,
            "detailed": 1,
        }
        r_post_data = prepare_composerData_for_placebet_after_addbet(**kwargs)

        post_data = r_post_data["post_data"]
        post_data_must_be = post_data_must_be.strip()
        logger.debug("  my: %s `%s`" % (type(post_data), post_data))
        logger.debug(
            "real: %s `%s`" % (type(post_data_must_be), post_data_must_be)
        )
        if post_data == post_data_must_be:
            print_success("good converted")
        else:
            print_error("bad converted")

    elif special == "create_ms_for_placebet_from_multiples":
        answer = """
{"bg":"5aa0089e-1553-44e7-9599-ca896205ea8a","sr":2,"mr":true,"ir":false,"at":0,"cc":"HTKZzp6ZOkKZP+sS/21hlVk12+b6PKD6iCsZE98pzcY=","pc":"10538788035381558340","vr":"511","cs":1,"st":1,"mi":"","mv":"","bt":[{"ob":[{"oc":"PSSOCCER","ot":3}],"cl":1,"sa":"61ba09c5-BDC0D8F0","tp":"BS110881903-254355764","fb":0.0,"mt":16,"nf":110881903,"mr":true,"cs":0,"bt":1,"pf":"N","od":"23/10","fi":110881903,"fd":"Arsenal v West Ham","pt":[{"pi":254355764,"bd":"West Ham","md":"Full Time Result"}],"sr":2},{"ob":[],"cl":1,"sa":"61ba23ec-D284D42A","tp":"BS110881903-254355763","fb":0.0,"mt":16,"nf":110881903,"mr":true,"cs":0,"bt":1,"pf":"N","od":"13/5","fi":110881903,"fd":"Arsenal v West Ham","pt":[{"pi":254355763,"bd":"Draw","md":"Full Time Result"}],"sr":2},{"ob":[{"oc":"PSSOCCER","ot":3}],"cl":1,"sa":"61ba2400-DE6DA6D9","tp":"BS110881897-254355381","fb":0.0,"mt":16,"nf":110881897,"mr":false,"cs":0,"bt":1,"pf":"N","od":"11/5","fi":110881897,"fd":"Brighton v Wolverhampton","pt":[{"pi":254355381,"bd":"Wolverhampton","md":"Full Time Result"}],"sr":0},{"ob":[{"oc":"PSSOCCER","ot":3}],"cl":1,"sa":"61ba2410-89F10BC6","tp":"BS110881901-254355692","fb":0.0,"mt":16,"nf":110881901,"mr":false,"cs":0,"bt":1,"pf":"N","od":"12/5","fi":110881901,"fd":"Crystal Palace v Southampton","pt":[{"pi":254355692,"bd":"Southampton","md":"Full Time Result"}],"sr":0}],"dm":{"bt":3,"od":"","bd":"Trebles","bc":2,"ea":false,"ew":false,"cb":false,"ma":0},"mo":[{"bt":-1,"bd":"","bc":4,"ea":false,"ew":false,"cb":false,"ma":0},{"bt":2,"od":"","bd":"Doubles","bc":5,"ea":false,"ew":false,"cb":false,"ma":0},{"bt":14,"od":"","bd":"Trixie","bc":8,"ea":false,"ew":false,"cb":false,"ma":0}],"bs":[1,2]}"""
        must_be = "id=3#bc=2#ust=0.1#st=0.1#||id=-1#bc=4#||id=2#bc=5#ust=0.2#st=0.2#||id=14#bc=8#"

        answer = obj_from_json(answer.strip())
        parsed = parse_refreshslip(answer)
        multiples = parsed["multiples"]
        # logger.info("parsed=%s" % parsed)

        kwargs = {
            "multiples": multiples,
            "place_on": [2, 3],
            "stakes": {2: 0.2, 3: 0.1,},
        }
        r_ms = create_ms_for_placebet_from_multiples(**kwargs)
        logger.info("r_ms=%s" % r_ms)
        # wait_for_ok(r_ms)
        answer = r_ms["ms"]
        must_be = "".join(clear_list(must_be, bad_starts="#"))
        must_be = (
            must_be.replace("#sl=0", "")
            .replace("\n", "")
            .replace(" ", "")
            .replace("\t", "")
            .strip()
        )
        logger.debug("  my: %s `%s`" % (type(answer), answer))
        logger.debug("real: %s `%s`" % (type(must_be), must_be))
        if answer == must_be:
            print_success("good converted")
        else:
            print_error("bad converted")

    else:
        logger.error("unknown special=%s" % special)
