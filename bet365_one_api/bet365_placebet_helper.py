#!/usr/bin/python
# -*- coding: utf-8 -*-

from modules import *
from modules_valui.funcs_odds import convert_odds_fractional_to_decimal

logger = get_logger(__name__)


def get_multiple_info(bets=[]):
    # logger.debug(f"{bets=}")
    infos = []
    hashes = []
    hashes_with_odds = []
    for bet in bets:
        # show_dict(bet)
        win = bet.get("win", -1)
        h = get_hash_of_url(bet)
        hashes.append(h)

        h_with_odds = get_hash_of_url(bet, with_odds=True)
        hashes_with_odds.append(h_with_odds)

        # f = bet.get("f", "")
        # fp = bet.get("f", "fp")
        life = round(bet.get("life", -1), 4)
        odds = bet.get("odds", "")
        # sport = bet.get("sport", "")
        # market = bet.get("sport", "")
        info = f"l={life} w={win} {odds=} {h}"
        infos.append(info)
    hashes.sort()
    h = ",".join(hashes)

    hashes_with_odds.sort()
    h_with_odds = ",".join(hashes_with_odds)
    _ = {
        "infos": infos,
        "hash": h,
        "hash_with_odds": h_with_odds,
    }
    return _


def get_hash_of_multiple(bets: List):
    hashes = []
    for bet in bets:
        h = get_hash_of_url(bet)
        hashes.append(h)
    hashes.sort()
    h = ",".join(hashes)
    return h


def get_hash_of_url(url: DictStr, with_odds: bool = False) -> str:
    """
    получаем хеш - но может быть не только текстовый урл, но и:
    any_link=
    {f: , fp: }
    {any_link:}
    """
    any_link = url
    f = None
    fp = None
    if isinstance(url, dict):
        any_link = url.get("any_link")
        f = url.get("f")
        fp = url.get("fp")
        odds = url.get("odds")

    h = ""
    if (fp is None) and "bet365" in any_link:  # текстовый линк
        vars = get_vars_from_bet365url(any_link)
        f, fp = vars["f"], vars["fp"]
        odds = vars["odds"]

    if fp:
        if with_odds:
            h = f"{f}-{fp}-{odds}"
        else:
            h = f"{f}-{fp}"

    if not h:
        logger.critical(f"no f-fp in {any_link=}")
        os._exit(0)
        h = to_hash(any_link)
    return h


def convert_rawBet365PostData_to_tpl(line=""):
    '''
    переводим сырую дату
        # &ns=pt=N#o=16/5#f=110862887#fp=252857647#so=#c=1#sa=61940958-D897CDC8#mt=2#|TP=BS110862887-252857647#ust=0.10#st=0.10#tr=0.42#||&betsource=FlashInPLay&tagType=WindowsDesktopBrowser&bs=1&qb=1
    в шаблон:
        post_tpl = """&ns=pt=N#o=[odds_fractional]#f=[f]#fp=[fp]#so=#c=1#mt=0#|TP=BS[f]-[fp]#ust=[stake]#st=[stake]#tr=[money_return]#||&betsource=FlashInPLay&tagType=WindowsDesktopBrowser&bs=1&qb=1"""
    '''
    f = find_from_to_one("#f=", "#", line)
    fp = find_from_to_one("#fp=", "#", line)
    odds = find_from_to_one("#o=", "#", line)
    ust = find_from_to_one("#ust=", "#", line)
    st = find_from_to_one("#st=", "#", line)
    tr = find_from_to_one("#tr=", "#", line)
    repl = {
        # '#f=%s#' % f: '#f=[f]#',
        f: "[f]",
        fp: "[fp]",
        "#o=%s#" % odds: "#o=[odds_fractional]#",
        # odds: '[odds_fractional]',
        "#ust=%s#" % ust: "#ust=[stake]#",
        # ust: '[stake]',
        "#st=%s#" % st: "#st=[stake]#",
        # st: '[stake]',
        "#tr=%s#" % tr: "#tr=[money_return]#",
        # tr: '[money_return]',
    }
    return no_probely_one(line, repl)


def convert_rawBet365PostData_to_url(line="", raw_addbet_data=""):
    fun = "convert_rawBet365PostData_to_url"

    line = urldecode(
        line
    )  # pt=N#o=8/13#f=102900837#fp=1743935847#so=#c=1#mt=11#id=102900837-1743935847Y#|TP=BS102900837-1743935847#||

    if raw_addbet_data:
        # &ns=pt%3DN%23o%3D14%2F1%23f%3D110489339%23fp%3D219478994%23so%3D%23c%3D1%23mt%3D16%23id%3D110489339-219478994Y%23%7CTP%3DBS110489339-219478994%23%7C%7C&betsource=FlashInPLay&bs=1&qb=1&cr=1
        line = urldecode(
            raw_addbet_data
        )  # pt=N#o=8/13#f=102900837#fp=1743935847#so=#c=1#mt=11#id=102900837-1743935847Y#|TP=BS102900837-1743935847#||
        # wait_for_ok(raw_addbet_data )

    f = find_from_to_one("#f=", "#", line)
    fp = find_from_to_one("#fp=", "#", line)
    odds = find_from_to_one("#o=", "#", line)

    url = "https://www.bet365.com/dl/sportsbookredirect?bs=%s-%s~%s&bet=1" % (
        f,
        fp,
        odds,
    )
    logger.debug(f"                 {url=} from {line=}")
    return url


def convert_bet365BetDict_to_url(obj={}, debug=False):
    odds = obj["odds"]
    f = obj["f"]
    fp = obj["fp"]
    url = "https://www.bet365.com/dl/sportsbookredirect?bs=%s-%s~%s&bet=1" % (
        f,
        fp,
        odds,
    )
    if debug:
        logger.debug(" url=`%s` from obj %s" % (url, obj))
    return url


def create_bet365Urls_from_any_data(urls_txt=""):
    urls_txt = urls_txt.replace("||pt=", "\n").replace("%7C%7Cpt%3D", "\n")
    urls = clear_list(urls_txt, bad_starts="#")

    urls = [create_bet365Url_from_any_data(url)[0] for url in urls]
    urls = unique_with_order(urls)
    logger.debug("%s urls %s" % (len(urls), urls))
    return urls


def create_bet365Url_from_any_data(data="", mt=None):
    """url = '',
    raw_post_data='',
    raw_addbet_data = '&ns=pt%3DN%23o%3D8%2F5%23f%3D110536452%23fp%3D223174885%23so%3D%23c%3D1%23mt%3D16%23id%3D110536452-223174885Y%23%7CTP%3DBS110536452-223174885%23%7C%7C&betsource=FlashInPLay&bs=1&qb=1&cr=1',
    """
    any_link = ""
    if isinstance(data, dict):
        any_link = convert_bet365BetDict_to_url(data)
    elif data.startswith("http"):
        any_link = data
    else:
        any_link = convert_rawBet365PostData_to_url(data)
    return any_link, mt


def convert_bet365Url_to_addbetData(
    url="",
    mt=None,
    tpl_post_data="&ns=[ns]||&betsource=FlashInPLay&bs=1&qb=1&cr=1",
    tpl_ns="pt=N#o=[odds]#f=[f]#fp=[fp]#so=#c=[c]#mt=[mt]#id=[f]-[fp]#|TP=BS[f]-[fp]#",
):
    if mt is None:
        mt = 16
        mt = 1

    ns_repl = {
        "[mt]": mt,
    }
    vars = get_vars_from_bet365url(url)
    odds = vars["odds"]
    new_f, new_fp = vars["f"], vars["fp"]
    new_repl = {
        "[f]": new_f,
        "[fp]": new_fp,
        "[odds]": odds,
        "[c]": "1",
    }
    ns_repl = add_defaults(new_repl, ns_repl)
    # logger.debug("ns_repl from url=%s " % ns_repl)
    ns = no_probely_one(tpl_ns, ns_repl)
    repl = {
        "[ns]": ns,
    }
    post_data = no_probely_one(tpl_post_data, repl)
    return post_data


def get_vars_from_bet365url(url="", want_odds_decimal=False):
    odds = find_from_to_one("~", "&", url).split("|")[0]
    bs = find_from_to_one("bs=", "~", url)
    if bs:
        f, fp = bs.split("-")
    else:
        f, fp = "", ""

    _ = {
        "odds": odds,
        "f": f,
        "fp": fp,
    }
    if want_odds_decimal:
        odds_decimal = convert_odds_fractional_to_decimal()
        _["odds_decimal"] = odds_decimal

    return _


def stake_to_postStake(stake=0.25):
    """если кончается на 0 - удалем этот 0"""
    stake = round(stake, 2)
    post_stake = "%.02f" % stake
    post_stake = cut_zeros_after_dot(post_stake)
    return post_stake


def checked_want_place(num, place_on=[0]):
    """
    хочу ставить на эту ставку?
    """
    if place_on == "all" or (isinstance(place_on, list) and num in place_on):
        return True
    return False


def parse_refreshslip(answer={}):
    """
    парсю refreshslip
        {"bg":"6932b73d-feb2-47d9-9acf-42f428ebf860","sr":14,"mr":false,"ir":false,"at":0,"cc":"MBvLjdoSG/JVKzkFgzeN2Cdkq+tK+NwcNbiLTZMxgAU=","pc":"11618041144572168102","vr":"511","cs":1,"st":1,"mi":"selections_changed_mobile","mv":"","bt":[{"ob":[{"oc":"PSSOCCER","ot":3},{"oc":"PREMAC","ot":1}],"cl":1,"sa":"61bb1b91-B223C1A0","tp":"BS110881909-254355839","fb":0.0,"mt":1,"nf":110881909,"mr":false,"cs":0,"bt":1,"pf":"N","od":"18/1","fi":110881909,"fd":"Liverpool v Newcastle","pt":[{"pi":254355839,"bd":"Newcastle","md":"Full Time Result"}],"sr":0},{"ob":[{"oc":"PSSOCCER","ot":3},{"oc":"PREMAC","ot":1}],"cl":1,"sa":"61bb1b91-6582F8EC","tp":"BS110881907-254355811","fb":0.0,"mt":1,"nf":110881907,"mr":false,"cs":0,"bt":1,"pf":"N","od":"14/1","fi":110881907,"fd":"Chelsea v Everton","pt":[{"pi":254355811,"bd":"Everton","md":"Full Time Result"}],"sr":0},{"ob":[{"oc":"PSSOCCER","ot":3},{"oc":"PREMAC","ot":1}],"cl":1,"sa":"61bb1b91-C83B2242","tp":"BS110881905-254355786","oc":True,"fb":0.0,"mt":1,"nf":110881905,"mr":false,"cs":0,"bt":1,"pf":"N","od":"8/5","fi":110881905,"fd":"Leicester v Tottenham","pt":[{"pi":254355786,"bd":"Tottenham","md":"Full Time Result"}],"sr":0}],"dm":{"bt":3,"od":"697.25/1","bd":"Treble","bc":1,"ea":false,"ew":false,"cb":false,"ap":5.00,"ma":100000},"mo":[{"bt":-1,"bd":"","bc":3,"ea":false,"ew":false,"cb":false,"ma":0},{"bt":2,"od":"","bd":"Doubles","bc":3,"ea":false,"ew":false,"cb":false,"ma":0},{"bt":14,"od":"","bd":"Trixie","bc":4,"ea":false,"ew":false,"cb":false,"ma":0},{"bt":15,"od":"","bd":"Patent","bc":7,"ea":false,"ew":false,"cb":false,"ma":0}],"bs":[1,2],"sc":4}
    """
    # show_dict(answer)
    multiples = [answer.get("dm", [])] + answer.get("mo", [])
    multiples = [_ for _ in multiples if _]

    bets = []
    answer_bets = answer["bt"]
    for answer_bet in answer_bets:
        odds = answer_bet["od"]
        bet_info = answer_bet["pt"][0]

        is_bad = ""
        if answer_bet.get("su"):
            is_bad = "the_selection_is_no_longer_available"

        bet = {
            "odds": odds,
            "sa": answer_bet["sa"],
            "f": answer_bet["fi"],
            "fp": bet_info["pi"],
            "mt": answer_bet.get("mt", ""),
            "is_bad": is_bad,
        }
        bets.append(bet)

    res = {
        "multiples": multiples,
        "bets": bets,
    }
    return res


def leave_bets_with_unchanged_odds(bets=[], odds_list=[]):
    good_bets = []
    for num in range(len(bets)):
        bet = bets[num]
        odds = bet["odds"]
        if odds_list:
            odds_must_be = odds_list[num]
        else:
            odds_must_be = ""

        good = ""
        if not odds_list:
            good = "empy_odds_list"
        elif odds == odds_must_be:
            good = "odds_not_changed"
        if good:
            good_bets.append(bet)
    return good_bets


def check_games_are_unique_in_bets_for_multiple(
    bets: List[DictStr], debug: bool = False
) -> bool:
    """
    Проверяю - точно нет дублей игры для мультиплов?
    В мультиплах нельзя ставить.
    """
    game_ids = set()
    for bet in bets:
        f = None
        if isinstance(bet, dict):
            f = bet.get("f")
            any_link = bet.get("any_link")
        else:
            any_link = bet
        if f is None:
            vars = get_vars_from_bet365url(any_link)
            f = vars["f"]

        if f in game_ids:
            if debug:
                logger.debug(f" game not unique: {f=} in {game_ids=}")
            return False
        game_ids.add(f)
    return True


def create_pseudoSurebet_from_one_bet(
    bet: DictStr, win: float = 0, live: str = "live"
):
    """
    для валуек нужно типа вилка?
    """
    bet = create_mybet_from_bet(bet, win=win, live=live)

    # show_dict(bet)
    # wait_for_ok()

    h = get_hash_of_url(bet)
    surebet = {
        "life": bet["life"],
        "market": bet["market"],
        "live": bet["live"],
        "win": bet["win"],
        "odds": [bet["odds"], bet["odds"]],
        "fresh": 0,
        "t_started_human": 0,
        "t_parsed_human": 0,
        "hash": h,
        "sport_country_liga": bet["sport_country_liga"],
        "bets": [bet, bet],
    }
    return surebet


def convert_bets_from_refreshslip_to_my_format(bets: List = None):
    """
    перегоняю инфу из рефрешслипа в мой стандартный вид
    {'odds': '16/5', 'sa': '61c5a62f-30E0B414', 'f': 111880512, 'fp': 347877657, 'mt': 1} - > {"any_link": ...}
    """
    my_bets = []
    for bet in bets:
        any_link = convert_bet365BetDict_to_url(bet)
        _ = {
            "any_link": any_link,
        }
        _.update(bet)
        my_bets.append(_)
    return my_bets


def create_mybet_from_bet(
    bet: DictStr, win: float = 0, live: str = "live"
) -> dict:

    if isinstance(bet, str):  # значит урл
        bet = {
            "any_link": bet,
        }
    any_link = bet["any_link"]
    vars = get_vars_from_bet365url(any_link, want_odds_decimal=True)
    default_bet_values = {
        "life": 0,
        "market": "",
        "live": live,
        "sport_country_liga": "",
        "odds": vars["odds_decimal"],
        "win": win,
        "bk": "bet365.com",
    }
    for k, v in default_bet_values.items():
        if k not in bet:
            bet[k] = v
    return bet


def get_placebet_types_to_skip():
    return "put_stake_successfully,game_active_but_selection_not_available,game_finished,multiples_impossible"  # selection_not_available,


def parse_max_stake_from_answer(answer={}):
    if "mo" in answer:
        max_stake = answer["mo"][0]["ms"]  # для мультипла - так?
    else:
        max_stake = answer["bt"][0]["ms"]
    return max_stake


if __name__ == "__main__":
    from valuebets_getter.demo_valuebets import get_demo_bets

    special = "convert_rawBet365PostData_to_url"
    special = "convert_bet365Url_to_addbetData"

    special = "prepare_composerData_for_placebet_after_addbet"
    special = "leave_bets_with_unchanged_odds"
    special = "check_games_are_unique_in_bets_for_multiple"
    special = "convert_bets_from_refreshslip_to_my_format"
    special = "get_hash_of_url"
    special = "get_multiple_info"
    special = "parse_max_stake_from_answer"
    special = "parse_refreshslip"

    if special == "nah":
        pass
    elif special == "parse_max_stake_from_answer":
        answer = {
            "sr": 11,
            "vr": "520",
            "cs": 2,
            "st": 1,
            "mi": "stakes_above_max_stake",
            "mv": "Trebles|0.00",
            "bt": [
                {
                    "ob": [],
                    "ms": 0.0,
                    "er": False,
                    "ra": 0.0,
                    "rp": 0.0,
                    "bt": 1,
                    "od": "6/4",
                    "fi": 111817232,
                    "pt": [{"hd": "6.5", "pi": 343375286, "ha": "6.5"}],
                    "sr": 0,
                },
                {
                    "ob": [],
                    "ms": 0.0,
                    "er": False,
                    "ra": 0.0,
                    "rp": 0.0,
                    "bt": 1,
                    "od": "17/20",
                    "fi": 112219210,
                    "pt": [{"hd": "+0.5", "pi": 378222657, "ha": "0.5"}],
                    "sr": 0,
                },
                {
                    "ob": [],
                    "ms": 0.0,
                    "er": False,
                    "ra": 0.0,
                    "rp": 0.0,
                    "bt": 1,
                    "od": "10/11",
                    "fi": 112513442,
                    "pt": [{"hd": "+16.5", "pi": 404446544, "ha": "+16.5"}],
                    "sr": 0,
                },
            ],
            "mo": [
                {
                    "bt": 3,
                    "st": 0.18,
                    "re": 1.58,
                    "od": "7.82/1",
                    "ms": 0.0,
                    "sr": 11,
                    "ra": 0.0,
                    "rp": 0.0,
                    "ap": 0.0,
                    "ba": 0.0,
                    "ma": 0,
                },
                {
                    "bt": 2,
                    "ms": 0.0,
                    "sr": 0,
                    "ra": 0.0,
                    "rp": 0.0,
                    "ap": 0.0,
                    "ba": 0.0,
                    "ma": 0,
                },
                {
                    "bt": 14,
                    "ms": 0.0,
                    "sr": 0,
                    "ra": 0.0,
                    "rp": 0.0,
                    "ap": 0.0,
                    "ba": 0.0,
                    "ma": 0,
                },
            ],
        }

        max_stake = parse_max_stake_from_answer(answer)
        logger.info(f"{max_stake=}")

    elif special == "convert_bets_from_refreshslip_to_my_format":
        refreshslip_bets = [
            {
                "odds": "16/5",
                "sa": "61c5a62f-30E0B414",
                "f": 111880512,
                "fp": 347877657,
                "mt": 1,
            },
            {
                "odds": "27/10",
                "sa": "61c5a62f-333F21C5",
                "f": 112618000,
                "fp": 412701615,
                "mt": 1,
            },
        ]
        bets = convert_bets_from_refreshslip_to_my_format(refreshslip_bets)
        show_list(bets)

    elif special == "get_hash_of_url":
        any_link = "https://www.bet365.com/dl/sportsbookredirect?bs=112425338-396686663~7/2&bet=1"
        tasks = [
            any_link,
            {"f": 1, "fp": 2,},
            {"any_link": any_link},
        ]
        with_odds = True
        for _ in tasks:
            h = get_hash_of_url(_, with_odds=with_odds)
            logger.debug(f"hash={h} for {_}")

    elif special == "check_games_are_unique_in_bets_for_multiple":
        bets = clear_list(
            """
            https://www.bet365.com/dl/sportsbookredirect?bs=112425338-396686663~7/2&bet=1
            https://www.bet365.com/dl/sportsbookredirect?bs=112425338-22222222~9/2&bet=1
            # https://www.bet365.com/dl/sportsbookredirect?bs=112425338-22222223~9/2&bet=1
        """,
            bad_starts="#",
        )
        can_be_multiple = check_games_are_unique_in_bets_for_multiple(bets)
        logger.info(f"{can_be_multiple=} for {bets=}")

    elif special == "convert_bet365Url_to_addbetData":
        url = "https://www.bet365.com/dl/sportsbookredirect?bs=110536452-223174885~8/5&bet=1"
        data = convert_bet365Url_to_addbetData(url)
        logger.info("data=%s from url %s" % (data, url))

    elif special == "convert_rawBet365PostData_to_url":
        data = "&ns=pt=N#o=1/5#f=110875602#fp=253865333#so=#c=13#sa=6194e5df-EC2BBD1B#mt=7#|TP=BS110875602-253865333#ust=0.10#st=0.10#tr=0.12#||&betsource=FlashInPLay&tagType=WindowsDesktopBrowser&bs=1&qb=1"
        # tpl = convert_rawBet365PostData_to_url(data)
        tpl = convert_rawBet365PostData_to_tpl(data)
        logger.info("tpl=%s" % tpl)

    elif special == "parse_refreshslip":
        # one bet
        answer = """{"bg":"47f8a80c-28bf-4bd3-bae5-d90d45444ff2","sr":0,"mr":False,"ir":False,"at":0,"cc":"EgDfx7B+4sYohzvN8rlftJX2IVJhSCf5sXyTd48+GdM=","pc":"15787926477364239805","vr":"511","cs":1,"st":1,"bt":[{"ob":[{"oc":"PSSOCCER","ot":3}],"cl":1,"sa":"61bb5410-D24FEC7F","tp":"BS110881909-254355839","fb":0.0,"mt":1,"nf":110881909,"mr":False,"cs":0,"bt":1,"pf":"N","od":"18/1","fi":110881909,"fd":"Liverpool v Newcastle","pt":[{"pi":254355839,"bd":"Newcastle","md":"Full Time Result"}],"sr":0}],"bs":[]}"""

        answer = """{"bg":"a421f26f-5dee-43c1-ac17-3e361b22baca","sr":2,"mr":True,"ir":False,"at":0,"cc":"/mBL1PkNMu3hxVwvtrCJBLXvqa5mCZesLS4YCRVQqeg=","pc":"3818164792527955116","vr":"510","cs":1,"st":1,"mi":"","mv":"","bt":[{"ob":[],"cl":1,"sa":"61b9ee69-A3FDB2F6","tp":"BS110881903-254355763","fb":0.0,"mt":16,"nf":110881903,"mr":True,"cs":0,"bt":1,"pf":"N","od":"13/5","fi":110881903,"fd":"Arsenal v West Ham","pt":[{"pi":254355763,"bd":"Draw","md":"Full Time Result"}],"sr":2},{"ob":[{"oc":"PSSOCCER","ot":3}],"cl":1,"sa":"61b9ef1d-F6BAFC7D","tp":"BS110881903-254355764","fb":0.0,"mt":16,"nf":110881903,"mr":True,"cs":0,"bt":1,"pf":"N","od":"23/10","fi":110881903,"fd":"Arsenal v West Ham","pt":[{"pi":254355764,"bd":"West Ham","md":"Full Time Result"}],"sr":2},{"ob":[{"oc":"PSSOCCER","ot":3}],"cl":1,"sa":"61b9ef1e-9F07FB8D","tp":"BS110881897-254355381","fb":0.0,"mt":16,"nf":110881897,"mr":True,"cs":0,"bt":1,"pf":"N","od":"23/10","fi":110881897,"fd":"Brighton v Wolverhampton","pt":[{"pi":254355381,"bd":"Wolverhampton","md":"Full Time Result"}],"sr":2},{"ob":[],"cl":1,"sa":"61b9efe4-7854C434","tp":"BS110881897-254355380","fb":0.0,"mt":16,"nf":110881897,"mr":True,"cs":0,"bt":1,"pf":"N","od":"2/1","fi":110881897,"fd":"Brighton v Wolverhampton","pt":[{"pi":254355380,"bd":"Draw","md":"Full Time Result"}],"sr":2},{"ob":[{"oc":"PSSOCCER","ot":3}],"cl":1,"sa":"61b9f04e-472BDD15","tp":"BS110881901-254355692","fb":0.0,"mt":16,"nf":110881901,"mr":False,"cs":0,"bt":1,"pf":"N","od":"13/5","fi":110881901,"fd":"Crystal Palace v Southampton","pt":[{"pi":254355692,"bd":"Southampton","md":"Full Time Result"}],"sr":0}],"dm":{"bt":3,"od":"","bd":"Trebles","bc":4,"ea":False,"ew":False,"cb":False,"ma":0},"mo":[{"bt":-1,"bd":"","bc":5,"ea":False,"ew":False,"cb":False,"ma":0},{"bt":2,"od":"","bd":"Doubles","bc":8,"ea":False,"ew":False,"cb":False,"ma":0},{"bt":14,"od":"","bd":"Trixie","bc":16,"ea":False,"ew":False,"cb":False,"ma":0}],"bs":[1,2]}"""  # with multiples
        answer = """{"bg":"17f9c709-5d62-4842-929a-4da2e8f8be49","sr":2,"mr":False,"ir":False,"at":0,"cc":"IHFytr+2gJS6ZOkenCdv4Fav3Gs7eJAN9l3NzBPF7w8=","pc":"6787182493914708494","vr":"515","cs":1,"st":1,"mi":"","mv":"","bt":[{"ob":[],"cl":2,"sa":"61c0d029-454B8706","tp":"BS112425394-396693716","ed":5,"et":"1/5¬3","ex":True,"os":True,"fb":0.0,"mt":1,"mr":False,"oo":1,"cs":0,"bt":1,"pf":"N","od":"22/1","fi":112425394,"fd":"7.00 Wolverhampton (Race 7)","pt":[{"pi":396693716,"bd":"Northern Charm","md":"Win and Each Way"}],"sr":0},{"ob":[],"cl":2,"sa":"61c0d029-2D064D18","tp":"BS112425394-396693709","ed":5,"et":"1/5¬3","ex":True,"os":True,"fb":0.0,"mt":1,"mr":False,"oo":1,"cs":0,"bt":1,"pf":"N","od":"28/1","fi":112425394,"fd":"7.00 Wolverhampton (Race 7)","pt":[{"pi":396693709,"bd":"Fliss Floss","md":"Win and Each Way"}],"sr":0}],"bs":[1,2]}"""  # no multiples
        answer = """{"bg":"9a7afd20-66e3-4c1e-8e8c-39940b2d8fb0","sr":14,"mr":false,"ir":true,"at":0,"cc":"O7SIPdjzrFfOX1XVjJUeqc/CIvlKZJhmpMp3uBGM9oc=","pc":"17486122640663945122","vr":"522","cs":1,"st":1,"mi":"selections_changed","mv":"","bt":[{"ob":[],"cl":1,"sa":"61d42d41-67691366","tp":"BS113152516-455952098","fb":0.0,"mt":1,"nf":113152516,"mr":false,"cs":0,"bt":1,"pf":"N","od":"6/5","fi":113152516,"fd":"Belenenses U23 v SC Farense U23","pt":[{"pi":455952098,"bd":"SC Farense U23","md":"Draw No Bet"}],"sr":0},{"ob":[],"cl":1,"sa":"61d42d41-58852FA4","tp":"BS112217195-397455388","fb":0.0,"mt":1,"nf":112217195,"mr":false,"cs":0,"bt":1,"pf":"N","od":"8/13","fi":112217195,"fd":"Annecy v Bourg-Peronnas","pt":[{"pi":397455388,"bd":"Annecy","md":"Draw No Bet"}],"sr":0},{"ob":[],"cl":13,"sa":"61d42d41-9F06C3F1","tp":"BS113151216-456778030","su":true,"fb":0.0,"mt":1,"nf":113098155,"mr":false,"cs":0,"bt":1,"pf":"N","od":"1/2","fi":113151216,"fd":"Tereza Martincova v Ana Konjuh","pt":[{"pi":456778030,"bd":"Ana Konjuh (Svr) to win 2nd game","md":"Next Game"}],"sr":0}],"dm":{"bt":2,"od":"2.55/1","bd":"Double","bc":1,"ea":false,"ew":false,"cb":false,"ma":0},"mo":[{"bt":-1,"bd":"","bc":3,"ea":false,"ew":false,"cb":false,"ma":0}],"bs":[1,2],"sc":8}"""
        answer = obj_from_json(answer.strip())
        parsed = parse_refreshslip(answer)
        logger.info("parsed=%s" % parsed)
        show_dict(parsed)

    elif special == "leave_bets_with_unchanged_odds":
        bets = [
            {"odds": "1/2"},
            {"odds": "3/4"},
        ]
        odds_list = ["1/2", "3/3"]
        good = leave_bets_with_unchanged_odds(bets, odds_list)
        logger.info("good=%s/%s %s" % (len(good), len(bets), good))

    elif special == "get_multiple_info":
        bets = get_demo_bets()
        # wait_for_ok(bets)

        info = get_multiple_info(bets)
        show_dict(info)
        logger.debug(f"{info=}")

    else:
        logger.error("unknown special=%s" % special)
