#!/usr/bin/python
# -*- coding: utf-8 -*-

from bet365_one_api.bet365_placebet_helper import *
from valuebets_getter.multiples_selector import MultipleSelector
from valuebets_getter.valuebets_main import select_surebet_from_surebets
from valuebets_getter.valuebets_skipper import ValuebetsSkipperWithSaving

logger = get_logger(__name__)


def select_best_multiple_after_refreshslip(
    bets: list,
    bets_with_stable_odds: list,
    bets_support: list = [],  # для мультипла - вспомогательные. Они должны входить в bets (может признак бы ввести...)
    multiple_selector: MultipleSelector = None,
    skipper: ValuebetsSkipperWithSaving = None,
    select_multiple_by=None,
    debug=False,
    kwargs_multiple_selector: dict = None,
) -> dict:
    """
    я получаю мои ставки, и ставки с рефрешслипа - и выбираю из этого инфу для ставок
    """
    fun = "select_best_multiple_after_refreshslip"
    vars0 = locals()

    d_kwargs_multiple_selector = {"place_on": [2, 3]}
    if kwargs_multiple_selector is None:
        kwargs_multiple_selector = {}
    best_multiple = None
    error = ""
    reason = ""  # причина ошибки
    details = []

    if not multiple_selector:
        kwargs_multiple_selector = add_defaults(
            kwargs_multiple_selector, d_kwargs_multiple_selector
        )
        multiple_selector = MultipleSelector(**kwargs_multiple_selector)
        logger.debug(f"created {multiple_selector=}")

    support_hashes = [get_hash_of_url(_["any_link"]) for _ in bets_support]
    if debug:
        logger.debug(f"     have {len(support_hashes)} {support_hashes=}")

    while True:
        if not bets:
            error = f"no bets to calculate multiple_win"
            logger.critical(error)
            inform_critical(error)

        hashes_of_stable_odds = [
            get_hash_of_url(_["any_link"])
            for _ in convert_bets_from_refreshslip_to_my_format(
                bets_with_stable_odds
            )
        ]
        my_stable_bets = [
            _
            for _ in bets
            if get_hash_of_url(_["any_link"]) in hashes_of_stable_odds
        ]
        m = f"{len(hashes_of_stable_odds)} {hashes_of_stable_odds=}, {my_stable_bets=}"
        details.append(m)
        logger.debug(m)

        if bets and (len(bets_with_stable_odds) != len(my_stable_bets)):
            logger.debug(f"{len(bets)} bets:")
            show_list(bets)

            logger.debug(
                f"{len(bets_with_stable_odds)} bets_with_stable_odds:"
            )
            show_list(bets_with_stable_odds)

            logger.debug(f"{len(my_stable_bets)} my_stable_bets:")
            show_list(my_stable_bets)

            f_kwargs = os.path.abspath(f"temp/kwargs_{to_hash(vars0)}.obj")
            obj_to_file(vars0, f_kwargs)

            error = f"have bets, but found {len(my_stable_bets)=} != {len(bets_with_stable_odds)=} bets for selector, check vars0 in {f_kwargs=}"
            logger.critical(error)
            inform_critical(error)

        kwargs_selector = {
            "debug": debug,
            "bets": my_stable_bets,
        }
        multiples = multiple_selector.get_all_possible_multiples_from_bets(
            **kwargs_selector
        )
        m = f"+have {len(multiples)} multiples from {multiple_selector=}"
        details.append(m)
        logger.debug(m)
        if debug:
            logger.debug(f"     {multiples=}")

        if 0 and not multiples:
            error_addbet = "impossible_error"
            return api_error(error_addbet)

            error = f"impossible that multiple_selector did not found multiples ({multiples=}"
            logger.critical(error)
            inform_critical(error)

        if 0 and debug:
            m = f"{multiples=}"
            details.append(m)
            logger.debug(m)
            # show_list(multiples)
            # wait_for_ok()

        if skipper:
            good_multiples = []
            for num_multiple, multiple in enumerate(multiples, 1):
                if debug:
                    logger.debug(
                        f"check with skipper {num_multiple}/{len(multiples)}"
                    )
                skip_reason = skipper.can_not_use(
                    multiple["hash"], debug=debug
                )
                if skip_reason:
                    if debug:
                        logger.debug(
                            f"     skip {num_multiple}/{len(multiples)} {skip_reason=}"
                        )
                    continue

                good_multiples.append(multiple)

            m = f"after skipper have {len(good_multiples)}/{len(multiples)} multiples"
            details.append(m)
            logger.debug(m)
            multiples = good_multiples[:]

        if not multiples:
            error = "multiples_not_found_after_refreshslip"
            break

        # удаляю из мультиплов те, которые чисто с поддержки
        if support_hashes:
            good_multiples = []
            for num_multiple, multiple in enumerate(multiples, 1):
                bets_from_multiple = multiple["bets"]
                not_support = [
                    _
                    for _ in bets_from_multiple
                    if get_hash_of_url(_["any_link"]) not in support_hashes
                ]
                cnt_not_support = len(not_support)
                if debug:
                    logger.debug(
                        f" {num_multiple}/{len(multiples)} {cnt_not_support=}/{len(bets_from_multiple)}"
                    )
                if cnt_not_support == 0:
                    continue

                cnt_support = len(bets_from_multiple) - cnt_not_support
                if cnt_support > 1:
                    if debug:
                        logger.debug(
                            f" {num_multiple}/{len(multiples)} {cnt_support=}>1, so skip"
                        )
                    continue

                multiple["cnt_not_support"] = cnt_not_support
                multiple["cnt_support"] = cnt_support
                good_multiples.append(multiple)
            logger.debug(
                f"have {len(good_multiples)}/{len(multiples)} мультиплов, в которых есть хоть один валуй не из bets_support"
            )

            # оставляю мультиплы с минимальным количеством поддержки
            multiples_with_minimum_support = leave_only_multiples_with_minimum_support(
                good_multiples
            )
            logger.debug(
                f"have {len(multiples_with_minimum_support)}/{len(good_multiples)} мультиплов с минимальным количеством валуев не из bets_support"
            )
            multiples = multiples_with_minimum_support[:]

        if not multiples:
            error = "nonSupport_multiples_not_found_after_refreshslip"
            break

        # выбираю на какой ставить
        if select_multiple_by is None:
            dct_probabilities = {
                "random": 1,
                "highest": 1,
                "probabilities": 2,
            }
            select_multiple_by = probability_dict_value(dct_probabilities)

        best_multiple = select_surebet_from_surebets(
            multiples, select_by=select_multiple_by
        )
        logger.debug(f"found {best_multiple=}")
        best_multiple["select_multiple_by"] = select_multiple_by

        break

    if error:
        return api_error(error=error, reason=reason, details=details)
    else:
        return best_multiple


def leave_only_multiples_with_minimum_support(lst: list = []) -> list:
    """нужно оставлять только мультиплы с минимумом поддержки"""
    fun = "leave_only_multiples_with_minimum_support"
    if not lst:
        return lst

    minimum_support = min([_["cnt_support"] for _ in lst])
    filtered = [_ for _ in lst if _["cnt_support"] == minimum_support]
    logger.debug(
        f" +{fun}: {minimum_support=}, filtered {len(filtered)}/{len(lst)}"
    )
    return filtered


if __name__ == "__main__":
    special = "leave_only_multiples_with_minimum_support"
    special = "select_best_multiple_after_refreshslip"

    if special == "nah":
        pass
    elif special == "leave_only_multiples_with_minimum_support":
        lst = [
            {"x": 1, "cnt_support": 1,},
            {"x": 2, "cnt_support": 2,},
            {"x": 3, "cnt_support": 0,},
            {"x": 0, "cnt_support": 0,},
        ]
        lst = []
        filtered = leave_only_multiples_with_minimum_support(lst)
        logger.info(f"{filtered=}")

    elif special == "select_best_multiple_after_refreshslip":

        bets_txt = r"""
        [
            # {'sport_country_liga': 'Tennis - ATP Melbourne', 'bk': 'bet365.com', 'odds': 5.0, 'market': '1/3 гейм 2 П1', 'raw': "Tennis - ATP Melbourne;bet365.com;\r\nM=Кристофер Коннелл;Джодан Томпсон;05.01.2022 4:00:00;Christopher O'Connell;Jordan Thompson;False;836584588\r\nMOBL=https://www.bet365.com/#/IP/EV15694900245C13", 't_parsed_bk': 1641348783.0, 'life': 2.0, 'team1_ru': 'Кристофер Коннелл', 'team2_ru': 'Джодан Томпсон', 'team1': "Christopher O'Connell", 'team2': 'Jordan Thompson', 'started': '05.01.2022 4:00:00', 'true_false': 'False', 'line_id': '836584588', 'game_id': '2706066', 'moblink': 'https://www.bet365.com/#/IP/EV15694900245C13', 'sport': 'Tennis', 'country_liga': 'ATP Melbourne', 'max_stake': 0, 'inf_parts': ['113195091-459281242@4/1|/IP/EV15694900245C13'], 'direct_link': 'https://www.bet365.com/dl/sportsbookredirect?bs=113195091-459281242~4/1|/IP/EV15694900245C13&bet=1', 'more_details': {}, 'any_link': 'https://www.bet365.com/dl/sportsbookredirect?bs=113195091-459281242~4/1|/IP/EV15694900245C13&bet=1', 'propusk': '', 'edits': [], 'errors': [], 'selection_path': [], 'win': 0.703, 'market_short': '', 'selection': '', 'max_betting_duration': 10, 'odds_change_ot': None, 'odds_change_do': None, 'strategy': {'win_ot': 0.0, 'win_do': 1000.0, 'win_ot_multiple': 2.0, 'odds_do_multiple': 100.0, 'name': 'valui_pinka_live', 'comment': 'валуи, но чтобы больше ставило (как для теста)', 'priority': 111.0, 'source': 'forted', 'live_or_prematch': ['live'], 'stake': 1.0, 'round_stake': 1, 'win_ot_final': '-300.0', 'odds_ot': 1.1, 'want_check_coupon': 'no', 'want_alternative_markets': 'no', 'odds_change_ot': -0.01, 'odds_change_do': 0.01, 'bks': ['bet365.com'], 'bks_only': ['bet365.com', 'pinnacle.com'], 'odds_do': None, 'sport_period': None, 'odds_movement': None, 'hours_ot': None, 'hours_do': None, 'real_market': None, 'abb_market': None, 'sports': None, 'sports_minus': None, 'tipy_vilok': None, 'tipy_vilok_minus': None, 'max_betting_duration': None, 'life_ot': None, 'life_do': None, 'bks_minus': None}, 'want_alternative_markets': 'no'},
            {'sport_country_liga': 'Tennis - ITF W60 Bendigo', 'bk': 'bet365.com', 'odds': 1.444, 'market': '1/3 гейм 4 П2', 'raw': 'Tennis - ITF W60 Bendigo;bet365.com;\r\nM=;;05.01.2022 4:00:00;Hanna Chang;Coco Vandeweghe;False;-193716931\r\nMOBL=https://www.bet365.com/#/IP/EV15694885795C13', 't_parsed_bk': 1641348784.0, 'life': -10.0, 'team1_ru': '', 'team2_ru': '', 'team1': 'Hanna Chang', 'team2': 'Coco Vandeweghe', 'started': '05.01.2022 4:00:00', 'true_false': 'False', 'line_id': '-193716931', 'game_id': '2714096', 'moblink': 'https://www.bet365.com/#/IP/EV15694885795C13', 'sport': 'Tennis', 'country_liga': 'ITF W60 Bendigo', 'max_stake': 0, 'inf_parts': ['113193288-459283439@4/9|/IP/EV15694885795C13'], 'direct_link': 'https://www.bet365.com/dl/sportsbookredirect?bs=113193288-459283439~4/9|/IP/EV15694885795C13&bet=1', 'more_details': {}, 'any_link': 'https://www.bet365.com/dl/sportsbookredirect?bs=113193288-459283439~4/9|/IP/EV15694885795C13&bet=1', 'propusk': '', 'edits': [], 'errors': [], 'selection_path': [], 'win': 2.395, 'market_short': '', 'selection': '', 'max_betting_duration': 10, 'odds_change_ot': None, 'odds_change_do': None},
            {'sport_country_liga': 'Soccer - France Ligue 2', 'bk': 'bet365.com', 'odds': 1.5, 'market': 'Ф1(0)', 'raw': 'Soccer - France Ligue 2;bet365.com;\r\nM=По;Родез;08.01.2022 22:00:00;Pau;Rodez;False;-420708280\r\nMOBL=https://www.bet365.com/#/AC/B1/C1/D8/E112217189/F3/I3/P^1002/Q^62415325/O^40/', 't_parsed_bk': 1641348781.0, 'life': 4.0, 'team1_ru': 'По', 'team2_ru': 'Родез', 'team1': 'Pau', 'team2': 'Rodez', 'started': '08.01.2022 22:00:00', 'true_false': 'False', 'line_id': '-420708280', 'game_id': '1143941', 'moblink': 'https://www.bet365.com/#/AC/B1/C1/D8/E112217189/F3/I3/P^1002/Q^62415325/O^40/', 'sport': 'Soccer', 'country_liga': 'France Ligue 2', 'max_stake': 0, 'inf_parts': ['112217189-416042756@1/2|/AC/B1/C1/D8/E112217189/F3/P^1002/Q^62415325/O^40/'], 'direct_link': 'https://www.bet365.com/dl/sportsbookredirect?bs=112217189-416042756~1/2|/AC/B1/C1/D8/E112217189/F3/P^1002/Q^62415325/O^40/&bet=1', 'more_details': {}, 'any_link': 'https://www.bet365.com/dl/sportsbookredirect?bs=112217189-416042756~1/2|/AC/B1/C1/D8/E112217189/F3/P^1002/Q^62415325/O^40/&bet=1', 'propusk': '', 'edits': [], 'errors': [], 'selection_path': [], 'win': 0.549, 'market_short': '', 'selection': '', 'max_betting_duration': 10, 'odds_change_ot': None, 'odds_change_do': None},
            {'sport_country_liga': 'Basketball - NBA', 'bk': 'bet365.com', 'odds': 2.2, 'market': '1/2 ТБ(113,5)', 'raw': 'Basketball - NBA;bet365.com;\r\nM=;;05.01.2022 4:00:00;SA Spurs;TOR Raptors;False;673131909\r\nMOBL=https://www.bet365.com/#/IP/EV151131592915C18', 't_parsed_bk': 1641348780.0, 'life': 4.0, 'team1_ru': '', 'team2_ru': '', 'team1': 'SA Spurs', 'team2': 'TOR Raptors', 'started': '05.01.2022 4:00:00', 'true_false': 'False', 'line_id': '673131909', 'game_id': '2714123', 'moblink': 'https://www.bet365.com/#/IP/EV151131592915C18', 'sport': 'Basketball', 'country_liga': 'NBA', 'max_stake': 0, 'inf_parts': ['113159291-454946606@6/5|/IP/EV151131592915C18'], 'direct_link': 'https://www.bet365.com/dl/sportsbookredirect?bs=113159291-454946606~6/5|/IP/EV151131592915C18&bet=1', 'more_details': {}, 'any_link': 'https://www.bet365.com/dl/sportsbookredirect?bs=113159291-454946606~6/5|/IP/EV151131592915C18&bet=1', 'propusk': '', 'edits': [], 'errors': [], 'selection_path': [], 'win': 0.405, 'market_short': '', 'selection': '', 'max_betting_duration': 10, 'odds_change_ot': None, 'odds_change_do': None},
            # {'sport_country_liga': 'Basketball - NBA', 'bk': 'bet365.com', 'odds': 2.1, 'market': '1/2 ТБ(112,5)', 'raw': 'Basketball - NBA;bet365.com;\r\nM=;;05.01.2022 4:00:00;SA Spurs;TOR Raptors;False;673131909\r\nMOBL=https://www.bet365.com/#/IP/EV151131592915C18', 't_parsed_bk': 1641348785.0, 'life': 1.0, 'team1_ru': '', 'team2_ru': '', 'team1': 'SA Spurs', 'team2': 'TOR Raptors', 'started': '05.01.2022 4:00:00', 'true_false': 'False', 'line_id': '673131909', 'game_id': '2714123', 'moblink': 'https://www.bet365.com/#/IP/EV151131592915C18', 'sport': 'Basketball', 'country_liga': 'NBA', 'max_stake': 0, 'inf_parts': ['113159291-454946606@11/10|/IP/EV151131592915C18'], 'direct_link': 'https://www.bet365.com/dl/sportsbookredirect?bs=113159291-454946606~11/10|/IP/EV151131592915C18&bet=1', 'more_details': {}, 'any_link': 'https://www.bet365.com/dl/sportsbookredirect?bs=113159291-454946606~11/10|/IP/EV151131592915C18&bet=1', 'propusk': '', 'edits': [], 'errors': [], 'selection_path': [], 'win': 1.912, 'market_short': '', 'selection': '', 'max_betting_duration': 10, 'odds_change_ot': None, 'odds_change_do': None},
        ]
        """
        bets_support_txt = r"""
        [
            {'sport_country_liga': 'Tennis - ITF W60 Bendigo', 'bk': 'bet365.com', 'odds': 1.444, 'market': '1/3 гейм 4 П2', 'raw': 'Tennis - ITF W60 Bendigo;bet365.com;\r\nM=;;05.01.2022 4:00:00;Hanna Chang;Coco Vandeweghe;False;-193716931\r\nMOBL=https://www.bet365.com/#/IP/EV15694885795C13', 't_parsed_bk': 1641348784.0, 'life': -10.0, 'team1_ru': '', 'team2_ru': '', 'team1': 'Hanna Chang', 'team2': 'Coco Vandeweghe', 'started': '05.01.2022 4:00:00', 'true_false': 'False', 'line_id': '-193716931', 'game_id': '2714096', 'moblink': 'https://www.bet365.com/#/IP/EV15694885795C13', 'sport': 'Tennis', 'country_liga': 'ITF W60 Bendigo', 'max_stake': 0, 'inf_parts': ['113193288-459283439@4/9|/IP/EV15694885795C13'], 'direct_link': 'https://www.bet365.com/dl/sportsbookredirect?bs=113193288-459283439~4/9|/IP/EV15694885795C13&bet=1', 'more_details': {}, 'any_link': 'https://www.bet365.com/dl/sportsbookredirect?bs=113193288-459283439~4/9|/IP/EV15694885795C13&bet=1', 'propusk': '', 'edits': [], 'errors': [], 'selection_path': [], 'win': 2.395, 'market_short': '', 'selection': '', 'max_betting_duration': 10, 'odds_change_ot': None, 'odds_change_do': None},
            {'sport_country_liga': 'Basketball - NBA', 'bk': 'bet365.com', 'odds': 2.2, 'market': '1/2 ТБ(113,5)', 'raw': 'Basketball - NBA;bet365.com;\r\nM=;;05.01.2022 4:00:00;SA Spurs;TOR Raptors;False;673131909\r\nMOBL=https://www.bet365.com/#/IP/EV151131592915C18', 't_parsed_bk': 1641348780.0, 'life': 4.0, 'team1_ru': '', 'team2_ru': '', 'team1': 'SA Spurs', 'team2': 'TOR Raptors', 'started': '05.01.2022 4:00:00', 'true_false': 'False', 'line_id': '673131909', 'game_id': '2714123', 'moblink': 'https://www.bet365.com/#/IP/EV151131592915C18', 'sport': 'Basketball', 'country_liga': 'NBA', 'max_stake': 0, 'inf_parts': ['113159291-454946606@6/5|/IP/EV151131592915C18'], 'direct_link': 'https://www.bet365.com/dl/sportsbookredirect?bs=113159291-454946606~6/5|/IP/EV151131592915C18&bet=1', 'more_details': {}, 'any_link': 'https://www.bet365.com/dl/sportsbookredirect?bs=113159291-454946606~6/5|/IP/EV151131592915C18&bet=1', 'propusk': '', 'edits': [], 'errors': [], 'selection_path': [], 'win': 0.405, 'market_short': '', 'selection': '', 'max_betting_duration': 10, 'odds_change_ot': None, 'odds_change_do': None},
        ]
        """
        bets_with_stable_odds_txt = r"""
        [
            {'odds': '4/9', 'sa': '61d4e294-289E7FBA', 'f': 113193288, 'fp': 459283439, 'mt': 1, 'is_bad': ''},
            {'odds': '1/2', 'sa': '61d4e294-CB5E3E92', 'f': 112217189, 'fp': 416042756, 'mt': 1, 'is_bad': ''},
            {'odds': '6/5', 'sa': '61d4e294-9C4F5DDA', 'f': 113159291, 'fp': 454946606, 'mt': 1, 'is_bad': ''},
        ]
        """
        bets = eval(bets_txt.strip())
        bets_support = eval(bets_support_txt.strip())
        bets_with_stable_odds = eval(bets_with_stable_odds_txt.strip())
        kwargs_multiple_selector = {
            "place_on": [2],
        }

        t = 1
        if t:
            f = r"s:\!kyxa\!code\!documentation\py4seo\advanced\08\dor_minimum\bet365_one_api\data\kwargs_9b6cfd041c66f4182a43ee536c257645.obj"
            vars = obj_from_file(f)
            show_dict(vars)

            keys = clear_list(
                """
            bets_with_stable_odds
            bets_support
            
            """
            )
            wait_for_ok()

        bets = eval(bets_txt.strip())
        bets_support = eval(bets_support_txt.strip())
        bets_with_stable_odds = eval(bets_with_stable_odds_txt.strip())

        select_best_multiple_after_refreshslip(
            bets=bets,
            bets_support=bets_support,
            bets_with_stable_odds=bets_with_stable_odds,
            kwargs_multiple_selector=kwargs_multiple_selector,
            debug=True,
        )

    else:
        logger.critical(f"unknown {special=}")
