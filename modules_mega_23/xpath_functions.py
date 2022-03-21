#!/usr/bin/python
# -*- coding: utf-8 -*-
from modules import *

# from modules.text_functions import no_probely
# # from modules.my_translit_ import *  #Bunch, add_defaults
# from modules.logging_functions import get_logger

logger = get_logger(__name__)
# wait_for_ok(no_probely)


class Xpather:
    """
    using:
        special = 'youtube'
        xpather = Xpather(special=special)
        logger.debug((xpather.xpath('next'))
        logger.debug(xpather.bxpath.next)
    
    В общем классе:
    
        class Helpers_parse_bet365(Xpather):
            '''
                весь парсинг вынесли отдельно
            '''

            def __init__(self):
                self.direct_bk_urls = {}
                # xpather = Xpather(xpaths)
                Xpather.__init__(self, special=['bet365'])
    
    """

    def __init__(self, dct={}, special=""):
        dct_more = {}
        if special != "":
            if isinstance(special, str):
                special = [special]

            for key in special:
                if key == "youtube":
                    dct_more = get_xpaths_youtube()
                elif key == "bet365":
                    dct_more = get_xpaths_bet365()
                elif key in ["betvictor"]:
                    pass
                else:
                    wait_for_ok("ERROR Xpather: unknown special=%s" % special)

        dct = add_defaults(dct, dct_more)

        self.xpath_dict = dct
        self.xpath_bunch = Bunch(dct)
        setattr(self, "bxpath", self.xpath_bunch)

    def get_xpaths_with_modes(self, lst=[], mode="inner"):
        fun = "get_xpaths_with_modes"
        xpaths_with_modes = []
        for _ in lst:
            if not isinstance(_, list):
                _ = [_]
            if len(_) == 2:
                xpath, xpath_mode = _
            elif len(_) == 1:
                xpath = _[0]
                xpath_mode = mode
            else:
                wait_for_ok("ERROR %s - unknown line %s" % (fun, _))

            xpaths_with_modes.append(
                [self.xpathkey_or_xpath(xpath), xpath_mode]
            )
        return xpaths_with_modes

    def xpathkey_or_xpath(self, xpath=""):
        """
        список == краткие все
        если нашли краткое по имени - возвращаем
        иначе считаем что это и есть xpath
        """
        if isinstance(xpath, list):
            return self.xpath(xpath)

        return self.xpath_dict.get(xpath, xpath)

    def get_named_xpath(self, xpath="", name=""):
        xpath_real = self.xpath(xpath)
        if xpath_real:
            dotted_name = name.replace(",", ".")
            value = xpath_real % name
            repl = {
                "{dotted_name}": dotted_name,
            }
            value = no_probely(value, repl)
            return value
        else:
            return ""

    def xpath(self, xpath_key="", xpath_if_not_exists=None):
        """
            тут специфические пути к конкретным действиям
        """
        fun = "xpath"
        dct = self.xpath_dict

        if not isinstance(xpath_key, list):
            xpath_keys = [xpath_key]
        else:
            xpath_keys = xpath_key[:]

        xpaths = []
        for xpath_key in xpath_keys:
            xpath = dct.get(xpath_key, None)

            if xpath is None:
                if not xpath_if_not_exists:
                    m = "%s ERROR: no xpath for key `%s` (dct %s)" % (
                        fun,
                        xpath_key,
                        dct,
                    )
                    logger.error(m)
                    os._exit(0)
                else:
                    xpath = xpath_if_not_exists

            if not xpath:
                continue

            if xpath:
                xpaths.append(xpath)

        xpath = " | ".join(xpaths)

        return xpath


def get_xpath_bet365_coupons():
    xpaths = {
        "coupon_root_inplay": '//div[contains(@class, "bss-StandardBetslip bss-StandardBetslip_HasInPlayBet")]',  # для лайв-игр
        "coupon_root": '//div[contains(@class, "bss-StandardBetslip ")]',  # для любых игр
        "coupon_remove": './/div[contains(@class, "bs-ControlBar_RemoveAll") and contains(text(),"Remove all")]',
        "coupon_title": './/div[contains(@class, "bss-NormalBetItem_Title ")]',  # <div class="bss-NormalBetItem_Title " style="">Over<div class="bss-NormalBetItem_Handicap bss-NormalBetItem_HandicapChanged " style=""> 1.5</div></div>
        "coupon_centered_name": './/div[contains(@class, "bss-NormalBetItem_Handicap ")]',  # <div class="bss-NormalBetItem_Title " style="">Over<div class="bss-NormalBetItem_Handicap bss-NormalBetItem_HandicapChanged " style=""> 1.5</div></div>
        "coupon_market": './/div[contains(@class, "bss-NormalBetItem_Market")]',
        "coupon_teams": './/div[contains(@class, "bss-NormalBetItem_FixtureDescription ")]',
        "coupon_odds": './/span[contains(@class, "bsc-OddsDropdownLabel ")]/span',
        "coupon_footer_message": './/div[contains(@class, "bss-Footer_MessageBody ")]',
        "coupon_button_accept_changes": './/div[contains(@class, "bs-AcceptButton_Text")]',
        # """
        # <div class="bss-PlaceBetButton_Wrapper"><div class="bss-PlaceBetButton_TopRow"><div class="bss-PlaceBetButton_Text ">Place Bet</div><div class="bss-PlaceBetButton_StakeAmount ">€0.00</div></div><div class="bss-PlaceBetButton_BottomRow"><div class="bss-PlaceBetButton_ToReturnLabel ">Total To Return</div><div class="bss-PlaceBetButton_ReturnValue ">€0.00</div></div></div>
        # """
        "coupon_button_place_bet": '//div[@class="bss-PlaceBetButton_Text " and text()="Place Bet"]',
        # <div class="bss-StakeBox_StakeValue bss-StakeBox_StakeValue-empty bss-StakeBox_StakeValue-focused ">Stake</div>
        "coupon_stake_text": '//div[contains(@class, "bss-StakeBox_StakeValue ")]',
        # 'coupon_stake_text_on_button': '//div[contains(@class, "bss-PlaceBetButton_StakeAmount ")]',
        "coupon_stake": '//input[contains(@class, "bss-StakeBox_StakeValueInput ")]',
        "coupon_balance": '//div[contains(@class, "bs-Balance_Value ")]',
        ######## placed bets
        "placed_root": '//div[contains(@class, "-StandardBetslip_HasReturns")]',  # bss-StandardBetslip bss-StandardBetslip_HasInPlayBet bss-StandardBetslip_HasReturns bss-StandardBetslip-receipt
        "placed_title": '//div[contains(@class, "-ReceiptContent_Title ")]',
        "placed_ref": '//div[contains(@class, "-ReceiptContent_BetRef ")]',
        "placed_stake": '//div[contains(@class, "-PlaceBetButton_StakeAmount ")]',
        "placed_to_return": '//div[contains(@class, "-PlaceBetButton_ReturnValue ")]',
        "placed_button_done": '//div[contains(@class, "-ReceiptContent_Done ")]',
        ######## competition
        "competition_block": '//div[contains(@class, "ovm-Competition ")]',
        "competition_liga": '//div[contains(@class, "ovm-CompetitionHeader_Name ")]',
        "competition_event_container": '//div[contains(@class, "ovm-Fixture_Container")]',
        "competition_event_teams": '//div[contains(@class, "ovm-FixtureDetailsTwoWay_TeamName ")]',
        "competition_event_timer": '//div[contains(@class, "ovm-FixtureDetailsTwoWay_Timer ")]',
        ######## history
        "history_header": '//div[@id="HeaderTitle" and contains(text(), "Settled Sports Bets")]',
        "history_container": '//div[contains(@class, "deeplinkpage")]',
        "history_show_more": '//div[contains(@class, "show-more-button")]',
        "history_wait": '//div[contains(text(), "Please wait 30 seconds before requesting this information again")]',
    }
    return xpaths


def get_xpaths_bet365():
    xpaths_coupons = get_xpath_bet365_coupons()
    dct = {
        "header": '//div[contains(@class, "hm-MainHeaderWide ")]',
        "title": "//title",
        # <div class="bl-Preloader" id="__-plContainer"><div class="bl-Preloader_Header"><div class="bl-Preloader_ProductHeader "></div><div class="bl-Preloader_MainHeader "><div class="bl-Preloader_MainHeaderLogo "></div></div></div><div class="bl-Preloader_SpinnerContainer "><div class="bl-Preloader_Spinner "></div></div></div>
        # 'preloader': '//div[@id="__-plContainer"]',
        "preloader": '//div[contains(@class, "bl-Preloader_SpinnerContainer "]',
        # <div id="header"><h1>Server Error</h1></div>
        "server_error": '//div[@id="header"]/h1[text()="Server Error"]',
        # <div class="bl-Preloader"><div class="bl-Preloader_Header"><div class="bl-Preloader_ProductHeader "></div><div class="bl-Preloader_MainHeader "><div class="bl-Preloader_MainHeaderLogo "></div></div></div><div class="bl-Preloader_SpinnerContainer "><div class="bl-Preloader_Spinner "></div></div></div>
        "loading": '//div[@class="bl-Preloader"]',
        "competitions": '//div[@class="ovm-CompetitionList "]',
        ############################################################## bet365
        #   change language
        # <div class="fm-Menu_Language fm-DropDownLabel " style="">Sprache<div class="fm-DropDownLabel_Chevron "><div id="fm-DropDownLabel_Chevron"><svg xmlns="http://www.w3.org/2000/svg" width="8" height="5" viewBox="0 0 12 7"><path class="fm-SVGComponent_Chevron" fill="#b5b5b5" fill-rule="evenodd" d="M12 .784L11.243 0 6 5.431.757 0 0 .784l5.243 5.432L6 7l.757-.784z"></path></svg></div></div></div>
        "menu_language": "//div[contains(@class, 'fm-Menu_Language')]",
        # <div class="fm-LanguageDropDown "><div class="fm-LanguageDropDownItem ">Español</div><div class="fm-LanguageDropDownItem " style="">English</div><div
        "english_language": "//div[contains(@class, 'fm-LanguageDropDownItem') and text() = 'English']",
        #   login
        # <div class="hm-MainHeaderRHSLoggedOutWide_Login ">Log In</div>
        "link_login": "//div[contains(@class, 'hm-MainHeaderRHSLoggedOut') and text() = 'Log In']",
        # 'link_login': '//div[@class="hm-MainHeaderRHSLoggedOutWide_Login "]', # hm-MainHeaderRHSLoggedOutNarrow_Login
        # <input type="text" placeholder="Username" autocapitalize="off" autocomplete="off" autocorrect="off" class="lms-StandardLogin_Username ">
        "login": "//input[@placeholder='Username']",
        # <input type="password" placeholder="Password" autocapitalize="off" autocomplete="off" autocorrect="off" class="lms-StandardLogin_Password ">
        "password": "//input[@placeholder='Password']",
        # <div class="lms-StandardLogin_LoginButton "><div class="lms-StandardLogin_LoginButtonText " style="">Log In</div></div>
        "button_login": "//div[contains(@class, 'StandardLogin_LoginButton')]",
        # class="hm-MainHeaderMembersNarrow_Balance hm-Balance "
        "balance": "//div[contains(@class, 'hm-MainHeaderMembers') and contains(@class, 'hm-Balance')]",
        "cnt_live_bets": "//span[contains(@class, 'hm-HeaderMenuItemMyBets_MyBetsCount ')]",
        "open_market": '//div[@class="sip-MarketGroupButton "]',
        "market_root": '//div[@class="ipe-EventViewDetail_ContentContainer "]',
        "teams": '//div[@class="ipe-EventHeader_Fixture "]',
        "event_info": '//div[@class="ipe-EventHeader "]',
        #  <div class="pm-PushTargetedMessageOverlay_CloseButton " style="">Close</div>
        #  <div class="pm-PushTargetedMessageOverlay_CloseButton " style="">Close</div>
        "close_readme": "//div[contains(@class, 'CloseButton') and text() = 'Close']",
        "iframe_message": "//iframe[@name='messageWindow']",
        "close_button_in_iframe": '//span[@class="wmeCloseButton"]',
        # <div class="alm-ActivityLimitAlert_Button ">Remain Logged In</div>
        "remain_logged_in": "//div[contains(@class, 'ActivityLimitAlert_Button ') and text() = 'Remain Logged In']",
    }
    dct = add_defaults(dct, xpaths_coupons)
    return dct


def get_xpaths_youtube():
    dct = {
        #    что нужно переименовать?
        "rename_paper_button": '//paper-button[@id="button"]',
        "next": '//*[text()="Далее"] | //*[text()="Next"]',
        "done": '//*[text()="Done"]',
        "ok": '//paper-button[@id="button"][@aria-label="ОК"]',
        "scroll_down": '//div[@aria-label="Scroll to agree"]',
        "read_policy_now": '//ytd-button-renderer[@id="review-button"]',
        "email": "//*[@id='identifierId']",
        "password": "//input[@name='password']",
        "choose_account": '//*[text()="Use another account"]',
        "skip_ads": '//div[text()="Skip Ads"] | //div[text()="Skip Ad"] ',
        # //*[@id="ad-text:jg"]
        "close_ads": '//button[@class="ytp-ad-overlay-close-button"]',
        "like_video": '//button[contains(@aria-label, "Видео понравилось")] | //button[starts-with(@aria-label, "like this")]',
        "dislike_video": '//button[contains(@aria-label, "Видео не понравилось")] | //button[@id="button" and contains(@aria-label, "dislike this")]',
        "survey_vneshnij_vid": "//ytd-single-option-survey-option-renderer",
        "subscribe_to_random_chanel": '//*[@id="button" and @aria-label="Subscribe"] | //ytd-subscribe-button-renderer',
        "links_in_left_userMenu": "//ytd-guide-entry-renderer",
        "links_to_all_channnels": '//div[@id="image-container"] | //a[@id="channel-info"]',
        "links_to_all_videos": "//ytd-thumbnail",
        "buttons": '//*[@id="button"]',  # 77 кнопок в среднем на странице
        # google search
        "query": "//input[@name='q']",
        # 'search_button_on_main': "//input[@name='btnK'] #number=1|", # на главной странице кнопка поиска
        # 'search_button_on_search_results': "//*[@aria-label='Google Search']", # На странице результатов
        "search_button": "//*[@aria-label='Google Search'] #number=1|",
        # 1 - для главной страницы
        # На странице результатов
    }
    return dct


if __name__ == "__main__":
    special = "bet365"
    special = "youtube"
    xpather = Xpather(special=special)
    # logger.debug(xpather.xpath('next'))
    logger.debug(xpather.xpath(["next", "done"]))
    # logger.debug(xpather.bxpath.next)
    # logger.debug(xpather.xpath.next)

    fun_xpath = get_xpath_bet365_coupons
    xpaths = fun_xpath()
    rows = []
    for name, xpath in xpaths.items():
        rows.append("%s\t%s" % (name, xpath))
    rows.sort()
    txt = "\n".join(rows)
    text_to_file(txt, "temp/xpaths.txt")
