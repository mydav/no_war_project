#!/usr/bin/python
# -*- coding: utf-8 -*-

r"""
!!!СИНХРОНИЗИРУЙ PY2-PY3 sync_py2_py3
s:\!kyxa\!code\!documentation\py4seo\advanced\08\dor_minimum\bet365_api\bet365_parse_answer_tip.py
s:\python2.7\Lib\site-packages\universal_bookmaker\api_bet365\bet365_parse_answer_tip.py
"""

from modules import *

# from modules.logging_functions import get_logger
logger = get_logger(__name__)


def parse_tip(answer={}):
    fun = "parse_tip"
    logger.debug("[%s %s %s" % (fun, type(answer), answer))
    tip = None
    if not isinstance(answer, dict):
        return tip

    # wait_for_ok(type(answer), answer)
    answer_txt = str(answer)
    answer_error = answer.get("error", "")
    if answer_error is None:
        answer_error = ""

    answer_message = answer.get(
        "Message", ""
    )  # {'Message': 'An error has occurred.'}

    details = answer.get("details", {})
    details_error = details.get("error", "")
    if details_error is None:
        details_error = ""

    mi = answer.get("mi")
    vr = answer.get("vr")
    sr = answer.get("sr")
    cs = answer.get("cs")
    html = answer.get("html", "")

    # wait_for_ok('sr %s=%s, cs=%s, mi %s=%s' % (type(sr), sr, cs, type(mi), mi))

    # print_h1('answer_txt=%s' % answer_txt)
    # wait_for_ok()
    if answer_error == "bot_ip":
        tip = answer_error
        # inform_critical(answer_error)
        # raise ValueError(tip)

    elif (
        answer.get("sr") == -1 and answer.get("cs") == 2
    ):  # sr -1 in addbet means automation_detected detected
        tip = "automation_detected"

    elif (
        answer_error == "connection_error"
        or "Max retries exceeded with url" in details_error
        or "HTTPSConnectionPool" in details_error
        or "ConnectionPool(host=" in details_error
    ):
        tip = "connection_error"
        # raise ValueError(tip)

    elif answer_message == "An error has occurred.":
        tip = "general_error"

    elif answer.get("cs") == 1 and sr == 19:
        tip = "wrong betGuid"

    # elif answer.get('cs') == 0 and answer.get('st') == 0 and answer.get('vr') == "305":
    elif (
        answer_txt
        in [
            """
        {'cs': 0, 'vr': '305', 'tx': True, 'st': 0}
        {'cs': 0, 'vr': '306', 'tx': True, 'st': 0}
        {'cs': 0, 'vr': '308', 'tx': True, 'st': 0}
		""",
        ]
        or (
            answer.get("cs") == 0
            and answer.get("tx") == True
            and answer.get("st") == 0
        )
    ):  # это еще когда слишком много накопилось неиспользованных (больше 20)
        tip = "wrong get_new_X-Net-Sync-Term"

    # elif answer.get('cs') == 1 and answer.get('sr') == -2:
    elif (cs == 1 and sr == -2) or (answer_txt == """{'cs': 1, 'sr': -2}"""):
        # elif answer_txt == '''{'sr':-2,'cs':1}''':
        """{"sr":-2,"cs":1}
            Until now i thought was because of very fast betting
            HMaker — 13.05.2021
            it means your can't place bet for some time, there is an enforced delay after bet is sucessfully placed
            """
        # tip = 'wrong multithreading_not_available'
        tip = "wrong wait_after_success_bet"

    elif answer.get("br"):
        """	br
                "XG5164941051F"
            bt
                    0	{"rp":0.0, "br":"XG5164941051F", "pt":"[{"pi":1715595950}]", "sr":0, "od":"7/10", "tr":"234231710844451214", "ob":"[]", "bt":1, "re":0.34, "ra":0.0, "ms":2142.86, "fi":102535486, "er":False}
            cs
                3
            la
                    0	{"cl":13, "ak":"20748467", "t2":"73401", "t1":"161648", "fd":"Simona Waltert v Mona Barthel", "fi":102514944}
            re
                0.34
            sr
                0
            st
                1
            tr
                ""
            ts
                0.2
            tu
                0.2
            vr
                "303"
        """
        tip = "put_stake_successfully"

    elif sr == 11 and mi == "unspecified":
        tip = "general_error"
        # wait_for_ok(tip)

    elif mi == "stakes_above_max_stake":
        tip = "stakes_above_max_stake"

    elif mi == "selections_changed" or "bg" in answer:
        """
        """
        bt = answer["bt"][0]

        if 0:
            pass
        # fake_answer
        # {"sr":14,"vr":"360","cs":2,"st":1,"mi":"selections_changed","mv":"","bt":[{"ob":[],"ms":0.0,"oc":true,"er":false,"ra":0.0,"rp":0.0,"bt":1,"od":"1/1","fi":105367961,"pt":[{"hd":"-2.0,-2.5","pi":1927696126,"ha":"-2.25"}],"re":0.4,"sr":0}]}
        # elif answer.get('mi') == 'selections_changed' and bt.get('oc') == True:
        #     tip = 'fake_answer'

        elif bt.get("xc") == True:
            tip = "game_finished"

        elif bt.get("su") == True and bt.get("oc") == True:
            if bt.get("od") == "0/0":
                tip = "empty_odds_selection_not_available"
            else:
                tip = "game_active_but_selection_not_available"

        elif bt.get("su") == True:
            tip = "selection_not_available"

        elif bt.get("oc"):
            """
                0	{"rp":0.0, "pt":"[{"pi":1724186244, "ha":"4", "hd":"4.0"}]", "sr":0, "od":"8/5", "oc":True, "ob":"[]", "bt":1, "re":0.52, "ra":0.0, "ms":0.0, "fi":102647868, "er":False}
            """
            tip = "selection_exists_but_odds_changed"

        else:
            tip = "selections_changed"

    elif mi:
        if mi == "invalid_funds":
            tip = "invalid_funds"

        elif mi == "invalid_penny_stake":
            tip = "invalid_penny_stake"

        elif mi == "invalid_min_stake":
            tip = "invalid_min_stake"

        elif mi == "allow_login_other":
            tip = "account_ban"

        elif mi == "allow_login_rg_questionnaire":
            tip = "answer_questions"

        elif mi == "missing_stake":
            logger.critical(f"todo {mi=} for {answer=}")
            inform_critical()

        else:
            logger.critical(f"todo {mi=} for {answer=}")
            inform_critical()

    elif vr in ["307"]:
        return "not_logined"

    elif sr == 8:
        tip = "not_logined"

    elif cs == 2 and sr == -1:
        tip = "not_logined"

    elif sr == 2:
        tip = "multiples_restricted"

    elif sr == 15:
        tip = "failed"

    elif "<productname> is currently unavailable due to routine" in html:
        tip = "bookmaker_maintance"

    else:
        logger.error("unknown type for answer %s" % answer)
        f_answer = os.path.abspath(
            "temp/!unknown_type/%s.html" % to_hash(answer)
        )
        text_to_file(answer, f_answer)
        logger.warning("saved page with unknown type to %s" % f_answer)
        tip = "unknown_type"

    return tip


def parse_tip_new(answer={}, post_error="", response=None):
    tip = None
    if "Max retries exceeded with url: http://localhost" in post_error:
        tip = "bot_ip"

    elif is_fiddler_error(post_error):
        tip = "Ставки при включенном Fiddler невозможны - обязательно выключите Fiddler!"
        logger.critical(tip)
        inform_critical(tip)

    elif (
        "Max retries exceeded with url" in post_error
    ):  # [ERROR][bet365_requests.py:65:request_with_requests]  HTTPSConnectionPool(host='www.bet365.com', port=443): Max retries exceeded with url: /BetsWebAPI/refreshslip (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1108)'))) [WARNING][my_forms.py:432:get_prepared_request]  request is unsuccessfull
        tip = "connection_error"

    elif post_error:
        tip = post_error

    elif not answer:
        tip = "answer_not_json"

    elif "bg" in answer:
        tip = "addbet_success"

    elif (
        answer.get("sr") == -1 and answer.get("cs") == 2
    ):  # sr -1 in addbet means automation_detected detected
        tip = "automation_detected"
        logger.error(tip)

    elif (
        answer.get("st") == 0
        and answer.get("cs") == 0
        and answer.get("se") == True
    ):  # {"se":true,"st":0,"cs":0,"vr":"488"}
        tip = "no_cookies"

    elif answer.get("br"):
        tip = "put_stake_successfully"

    elif answer.get("sr") == 15:
        tip = "failed"

    return tip


def parse_answer_tip(answer={}, post_error="", response=None):
    """
    для питон3 использую эту версию
    """
    tip = parse_tip_new(answer, post_error=post_error, response=response)

    if tip is None:
        tip = parse_tip(answer)

    if tip is None:
        tip = "unknown"
        m = "unknown tip for answer=`%s` from response `%s`" % (
            answer,
            response.text,
        )
        logger.error(m)
        wait_for_ok(m)

    return tip


def get_last_history(history, size=-3):
    return f"last history=...{history[size:]} from {len(history)} get_short_history(history)"


def get_short_history(history=[]):
    # хочу кратко вывести историю
    hirstory_shorter = {
        "addbet_success": "+",
        "automation_detected": "A",
        "addbet_automation_detected": "A",
        "unknown": "U",
        "bot_ip": "B",
        "put_stake_successfully": "$",
        "failed": "F",
        "selection_exists_but_odds_changed": "o",
    }
    short_history = "".join([hirstory_shorter.get(_, _) for _ in history])
    return short_history


def is_fiddler_error(post_error=""):
    if post_error and (
        "SSL: CERTIFICATE_VERIFY_FAILED" in post_error
    ):  # включен фидлер - [ERROR][bet365_requests.py:65:request_with_requests]  HTTPSConnectionPool(host='www.bet365.com', port=443): Max retries exceeded with url: / (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1108)'))) [WARNING][my_forms.py:432:get_prepared_request]  request is unsuccess
        tip = "Ставки при включенном Fiddler невозможны - обязательно выключите Fiddler!"
        logger.critical(tip)
        inform_critical(tip)
        return True
    return False


if __name__ == "__main__":
    from modules_mega_23.tester_functions import *

    special = "parse_tip"

    if special == "parse_tip":
        tasks = [
            # ['fake_answer', '{"sr":14,"vr":"360","cs":2,"st":1,"mi":"selections_changed","mv":"","bt":[{"ob":[],"ms":0.0,"oc":true,"er":false,"ra":0.0,"rp":0.0,"bt":1,"od":"1/1","fi":105367961,"pt":[{"hd":"-2.0,-2.5","pi":1927696126,"ha":"-2.25"}],"re":0.4,"sr":0}]}'],
            # ['selection_exists_but_odds_changed', '{"sr":14,"vr":"360","cs":2,"st":1,"mi":"selections_changed","mv":"","bt":[{"ob":[],"ms":0.0,"oc":true,"er":false,"ra":0.0,"rp":0.0,"bt":1,"od":"1/1","fi":105367961,"pt":[{"hd":"-2.0,-2.5","pi":1927696126,"ha":"-2.25"}],"re":0.4,"sr":0}]}'],
            # ['connection_error', {'html': '', 'details': {'code': '', 'g': '', 'url': '', 'raw_request': None, 'kod': '', 'headers': {}, 'error_short': '', 'html': '', 'location': '', 'error': "('Connection aborted.', error(10060, 'A connection attempt failed because the connected party did not properly respond after a period of time, or established connection failed because connected host has failed to respond'))", 'duration': 19.582}, 'error_path': [], 'error': 'code_'}],
            # ['', """{"sr":11,"vr":"377","cs":2,"st":1,"mi":"unspecified","mv":"","bt":[{"ob":[],"ms":0,"er":false,"ra":0,"rp":0,"bt":1,"od":"12/1","fi":106011594,"pt":[{"pi":1969401413}],"re":3.51,"sr":0}]}"""], # unknown answer from guy
            #             """
            #             {"sr":11,"vr":"377","cs":2,"st":1,"mi":"unspecified","mv":"","bt":[{"ob":[],"ms":0,"er":false,"ra":0,"rp":0,"bt":1,"
            # od":"12/1","fi":106011594,"pt":[{"pi":1969401413}],"re":3.51,"sr":0}]}
            # sr:11 ???
            # Знакомьтесь, это
            # Apollonia
            # !
            #  — Вчера, в 15:31
            # Ура,
            # pablogh
            #  теперь с нами!
            #  — Сегодня, в 0:59
            # HMaker — Сегодня, в 1:01
            # from what I know it means "stake above maximum", but mi should have another value"""
            # todo: general error
            # ['', {'sr': 15, 'mi': '', 'st': 1, 'bt': [{'rp': 0.0, 'pt': [{'pi': 1971088786, 'ha': '0.5', 'hd': '0.5'}], 'sr': 0, 'od': '11/50', 'ob': [], 'bt': 1, 're': 0.24, 'ra': 0.0, 'ms': 4261.36, 'fi': 105926511, 'er': False}], 'vr': '377', 'mv': '', 'cs': 2}], # todo: general error
            # ['', {'sr': 15, 'mi': '', 'st': 1, 'bt': [{'rp': 0.0, 'pt': [{'pi': 1985445147}], 'sr': 0, 'od': '6/5', 'ob': [], 'bt': 1, 're': 0.66, 'ra': 0.0, 'ms': 625.0, 'fi': 106213561, 'er': False}], 'vr': '382', 'mv': '', 'cs': 2}]
            # done
            # ['selection_not_available', {'bg': '62caa659-2e50-41c4-9d66-f95113f3c7a5', 'mr': False, 'sr': 0, 'ir': False, 'st': 1, 'bt': [{'fi': 102903152, 'pt': [{'bd': '', 'md': '', 'pi': 1743935847}], 'sr': 0, 'od': '', 'ob': [], 'su': True, 'bt': 1, 'mt': 1, 'fb': 0.0, 'fd': '', 'tp': 'BS102903152-1743935847', 'mr': False, 'cs': 0, 'pf': 'N', 'sa': ''}], 'vr': '377', 'at': 0, 'bs': [], 'cs': 1}],
            # ['wrong betGuid', """{"sr":19,"cs":1}"""],
            # ['stakes_above_max_stake', {'sr': 11, 'mi': 'stakes_above_max_stake', 'st': 1, 'bt': [{'rp': 0.0, 'pt': [{'pi': 2002252473}], 'rs': 0.53, 'sr': 11, 'od': '19/2', 'ob': [], 'bt': 1, 're': 10.5, 'ra': 0.0, 'ms': 0.53, 'fi': 106457518, 'er': False}], 'vr': '385', 'mv': '1 Japan U19 Women  (To Win Match)|0.53', 'cs': 2}],
            # ['general_error', {'sr': 11, 'mi': 'unspecified', 'st': 1, 'bt': [
            #     {'rp': 0.0,
            #      'pt': [{'pi': 2002605954, 'ha': '2.5', 'hd': '2.5'}], 'sr': 0,
            #      'od': '33/40', 'ob': [], 'bt': 1, 're': 1.82, 'ra': 0.0,
            #      'ms': 0.0, 'fi': 106408154, 'er': False}], 'vr': '385',
            #                    'mv': '', 'cs': 2}],
            # ['not_logined', {'cs': 1, 'sr': 8}],
            # ['account_ban', {'sr': 41, 'mi': 'allow_login_other', 'st': 1, 'bt': [{'rp': 0.0, 'pt': [{'pi': 2034621566}], 'sr': 0, 'od': '9/1', 'ob': [], 'bt': 1, 're': 2.0, 'ra': 0.0, 'ms': 0.0, 'fi': 106881354, 'er': False}], 'vr': '398', 'mv': '', 'cs': 2}]
            # ["multiples_restricted", {'sr':2}],
            # ["not_logined", {'cs': 2, 'sr': -1, 'vr': '422', 'cd': 'c04af8ff-9c37-4caa-a195-4e4562e1a43d'}],
            ## info
            # todo
            ## connection error
            # ['connection_error', {'html': '', 'details': {'code': '', 'g': '', 'url': '', 'raw_request': None, 'kod': '', 'headers': {}, 'error_short': '', 'html': '', 'location': '', 'error': "('Connection aborted.', error(10054, 'An existing connection was forcibly closed by the remote host'))", 'duration': 54.154}, 'error_path': [], 'error': 'code_'}],
            # ['connection_error', {'html': '', 'details': {'code': '', 'g': '', 'url': '', 'raw_request': None, 'kod': '', 'headers': {}, 'error_short': '', 'html': '', 'location': '', 'error': "HTTPSConnectionPool(host='www.bet365.com', port=443): Max retries exceeded with url: /BetsWebAPI/placebet?betGuid=587a67d6-11c7-45ee-8e20-986dfe252c2a&c=jRdPdVG%2F9ZiDtCREru%2FmN08wxKCi15OE6t8SqdmbO1M%3D (Caused by SSLError(SSLEOFError(8, u'EOF occurred in violation of protocol (_ssl.c:727)'),))", 'duration': 6.81}, 'error_path': [], 'error': 'code_'}],
            # ['connection_error', {'html': '', 'details': {'code': '', 'g': '', 'url': '', 'raw_request': None, 'kod': '', 'headers': {}, 'error_short': '', 'html': '', 'location': '', 'error': "('Connection aborted.', BadStatusLine('No status line received - the server has closed the connection',))", 'duration': 5.282}, 'error_path': [], 'error': 'code_'}],
            # ['connection_error', {'html': '{"Message":"The requested resource does not support http method \'GET\'."}', 'details': {'code': 405,}},],
            # ['connection_error', {'html': '', 'details': {'code': '', 'g': '', 'url': '',
            #                                 'raw_request': None, 'kod': '',
            #                                 'headers': {}, 'error_short': '',
            #                                 'html': '', 'location': '',
            #                                 'error': "HTTPSConnectionPool(host='www.bet365.com', port=443): Read timed out. (read timeout=30)",
            #                                 'duration': 30.327},                    'error_path': [], 'error': 'code_'}],
            # ['general_error', {'Message': 'An error has occurred.'}],
            # ['answer_questions', {'sr': 41, 'mi': 'allow_login_rg_questionnaire', 'st': 1, 'bt': [{'rp': 0.0, 'pt': [{'pi': 146953862, 'ha': '+4.5', 'hd': '+4.5'}], 'sr': 0, 'od': '7/5', 'ob': [], 'bt': 1, 're': 7.2, 'ra': 0.0, 'ms': 0.0, 'fi': 109760928, 'er': False}], 'vr': '453', 'mv': '', 'cs': 2}],
            ### sr 15 means just "failed", generally for invalid parameters on placebet request
            # ['failed', {'sr': 15, 'mi': '', 'st': 1, 'bt': [
            #     {'rp': 0.0, 'pt': [{'pi': 151901474, 'ha': '4', 'hd': '4.0'}],
            #      'sr': 0, 'od': '43/40', 'ob': [], 'bt': 1, 're': 10.37,
            #      'ra': 0.0, 'ms': 452.68, 'fi': 109732293, 'er': False}],
            #                    'vr': '453', 'mv': '', 'cs': 2}],
            # ['', '''{"sr":11,"vr":"470","cs":2,"st":1,"mi":"unspecified","mv":"","bt":[{"ob":[],"ms":0.0,"er":false,"ra":0.0,"rp":0.0,"bt":1,"od":"16/1","fi":110170856,"pt":[{"pi":188585975}],"re":85.0,"sr":0}]}'''],
            # ["failed", {"sr": 19, "cs": 1}],
            # ["", {"sr":-2,"cs":1},]
            # ['invalid_min_stake', {'sr': 12, 'mi': 'invalid_min_stake', 'st': 1, 'bt': [
            # {'rp': 0.0, 'pt': [{'pi': 353710863}], 'rs': 0.1, 'sr': 12,
            #  'od': '200/1', 'ob': [], 'bt': 1, 're': 14.07, 'ra': 0.0,
            #  'ms': 0.0, 'fi': 111948490, 'er': False}], 'vr': '503',
            #         'mv': '0.1', 'cs': 2}],
            # [
            #     "automation_detected",
            #     {
            #         "cs": 2,
            #         "sr": -1,
            #     },
            # ],
            # [
            #     "",
            #     {
            #         "cs": 2,
            #         "sr": -1,
            #         "vr": "512",
            #         "cd": "8a735029-033f-4b9c-b601-8dee06fabc30",
            #     },
            # ],
            # [
            #     "",
            #     {
            #         "sr": 9,
            #         "vr": "521",
            #         "cs": 2,
            #         "st": 1,
            #         "mi": "missing_stake",
            #         "mv": "",
            #         "bt": [
            #             {
            #                 "ob": [],
            #                 "ms": 0.0,
            #                 "er": False,
            #                 "ra": 0.0,
            #                 "rp": 0.0,
            #                 "bt": 1,
            #                 "od": "5/4",
            #                 "fi": 113133250,
            #                 "pt": [
            #                     {
            #                         "hd": "0.0,+0.5",
            #                         "pi": 454081767,
            #                         "ha": "0.25",
            #                     }
            #                 ],
            #                 "sr": 2,
            #             },
            #             {
            #                 "ob": [],
            #                 "ms": 0.0,
            #                 "er": False,
            #                 "ra": 0.0,
            #                 "rp": 0.0,
            #                 "bt": 1,
            #                 "od": "5/6",
            #                 "fi": 113133249,
            #                 "pt": [{"pi": 452825459}],
            #                 "sr": 2,
            #             },
            #             {
            #                 "ob": [],
            #                 "ms": 0.0,
            #                 "er": False,
            #                 "ra": 0.0,
            #                 "rp": 0.0,
            #                 "bt": 1,
            #                 "od": "1/1",
            #                 "fi": 113138077,
            #                 "pt": [{"pi": 454525885, "ha": "9.5"}],
            #                 "sr": 0,
            #             },
            #         ],
            #         "mo": [
            #             {
            #                 "bt": 2,
            #                 "ms": 0.0,
            #                 "sr": 0,
            #                 "ra": 0.0,
            #                 "rp": 0.0,
            #                 "ap": 0.0,
            #                 "ba": 0.0,
            #                 "ma": 0,
            #             }
            #         ],
            #     },
            # ],
            # [
            #     "",
            #     # """{'sr': 9, 'vr': '515', 'cs': 2, 'st': 1, 'mi': 'missing_stake', 'mv': '', 'bt': [{'ob': [], 'ms': 0.0, 'er': True, 'ra': 0.0, 'rp': 0.0, 'bt': 1, 'od': '22/1', 'fi': 112425394, 'pt': [{'pi': 396693716}], 'sr': 2}, {'ob': [], 'ms': 0.0, 'er': True, 'ra': 0.0, 'rp': 0.0, 'bt': 1, 'od': '28/1', 'fi': 112425394, 'pt': [{'pi': 396693709}], 'sr': 2}]}""",
            #     {
            #         "sr": 9,
            #         "vr": "515",
            #         "cs": 2,
            #         "st": 1,
            #         "mi": "missing_stake",
            #         "mv": "",
            #         "bt": [
            #             {
            #                 "ob": [],
            #                 "ms": 0.0,
            #                 "er": True,
            #                 "ra": 0.0,
            #                 "rp": 0.0,
            #                 "bt": 1,
            #                 "od": "22/1",
            #                 "fi": 112425394,
            #                 "pt": [{"pi": 396693716}],
            #                 "sr": 2,
            #             },
            #             {
            #                 "ob": [],
            #                 "ms": 0.0,
            #                 "er": True,
            #                 "ra": 0.0,
            #                 "rp": 0.0,
            #                 "bt": 1,
            #                 "od": "28/1",
            #                 "fi": 112425394,
            #                 "pt": [{"pi": 396693709}],
            #                 "sr": 2,
            #             },
            #         ],
            #     },
            # ],
            # ["failed", {"cs": 2, "sr": 15}],
            # [
            #     "",
            #     """{"tx":true,"st":0,"cs":0,"vr":"541","cd":"64efd52a-0d78-4695-bd66-b6ec91bcfa69"}""",
            # ],
            [
                "automation_detected",
                """{"cs":2,"sr":-1,"vr":"541","cd":"e7326b74-174d-4717-b088-4e2c93641a55"}""",
            ],
        ]
        tester_tasks = []
        for num, (expected, answer) in enumerate(tasks, 1):
            # logger.critical(f"{num}/{len(tasks)} {type(answer)} {answer=}")
            # wait_for_ok()
            # os._exit(0)
            if isinstance(answer, str):
                answer = obj_from_json(answer)
                # show_dict(answer)
            # wait_for_ok()
            tester_tasks.append([{"answer": answer}, expected])

        logger.debug("%s tester_tasks:" % len(tester_tasks))
        show_list(tester_tasks)
        func_to_check = parse_tip_new
        func_to_check = parse_tip
        my_tester(tester_tasks, func_to_check)

    else:
        wait_for_ok("unknown special %s" % special)
