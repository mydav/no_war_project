from modules import *
import platform

logger = get_logger(__name__)


def get_telegram_settings(system_version=None):
    pc = clear_list(
        """
    PC:Windows:7
    PC:Windows:8.1
    PC:Windows:10
    """
    )
    pc = choice(pc)
    # ---- TDLib(example) - --- - IOS
    APP_CONFIG_API_ID = 94575
    APP_CONFIG_API_HASH = "a3406de8d171bb422bb6ddf3bbd800e2"

    ### real android

    # ---- Telegram X(Android) - ---
    APP_CONFIG_API_ID = 21724
    APP_CONFIG_API_HASH = "3e0cb5efcd52300aec5994fdfc5bdc16"

    # ---- TG for Android - ---
    APP_CONFIG_API_ID = 6
    APP_CONFIG_API_HASH = "eb06d4abfb49dc3eeb1aeb98ae0f581e"

    # ---- Telegram Desktop(example) - ---
    APP_CONFIG_API_ID = 17349
    APP_CONFIG_API_HASH = "344583e45741c457fe1862106095a5eb"

    # app_version
    # app_version = str(randint(10, 99))
    # Versions should comply with PEP440.
    # This line is parsed in setup.py:
    app_version = "1.24.0"  # telthon?

    lang_code = "en"
    system_lang_code = "en"  # "ru|ru-RU|ru-UA"  # 	{aa|ab|ace|ach|ada|ady|ae|af|af-NA|af-ZA|af|afa|afh|agq|agq-CM|agq|ain|ak|ak-GH|ak|akk|ale|alg|alt|am|am-ET|am|an|ang|anp|apa|ar|ar-001|ar-AE|ar-BH|ar-DJ|ar-DZ|ar-EG|ar-EH|ar-ER|ar-IL|ar-IQ|ar-JO|ar-KM|ar-KW|ar-LB|ar-LY|ar-MA|ar-MR|ar-OM|ar-PS|ar-QA|ar-SA|ar-SD|ar-SO|ar-SS|ar-SY|ar-TD|ar-TN|ar-YE|ar|arc|arn|arp|ars|art|arw|as|as-IN|as|asa|asa-TZ|asa|ast|ast-ES|ast|ath|aus|av|awa|ay|az|az-Cyrl|az-Cyrl-AZ|az-Latn|az-Latn-AZ|az|ba|bad|bai|bal|ban|bas|bas-CM|bas|bat|bax|bbj|be|be-BY|be|bej|bem|bem-ZM|bem|ber|bez|bez-TZ|bez|bfd|bg|bg-BG|bg|bh|bho|bi|bik|bin|bkm|bla|bm|bm-ML|bm|bn|bn-BD|bn-IN|bn|bnt|bo|bo-CN|bo-IN|bo|br|br-FR|br|bra|brx|brx-IN|brx|bs|bs-Cyrl|bs-Cyrl-BA|bs-Latn|bs-Latn-BA|bs|bss|btk|bua|bug|bum|byn|byv|ca|ca-AD|ca-ES|ca-FR|ca-IT|ca|cad|cai|car|cau|cay|cch|ce|ce-RU|ce|ceb|cel|cgg|cgg-UG|cgg|ch|chb|chg|chk|chm|chn|cho|chp|chr|chr-US|chr|chy|ckb|ckb-IQ|ckb-IR|ckb|cmc|co|cop|cpe|cpf|cpp|cr|crh|crp|cs|cs-CZ|cs|csb|cu|cus|cv|cy|cy-GB|cy|da|da-DK|da-GL|da|dak|dar|dav|dav-KE|dav|day|de|de-AT|de-BE|de-CH|de-DE|de-IT|de-LI|de-LU|de|del|den|dgr|din|dje|dje-NE|dje|doi|dra|dsb|dsb-DE|dsb|dua|dua-CM|dua|dum|dv|dyo|dyo-SN|dyo|dyu|dz|dz-BT|dz|dzg|ebu|ebu-KE|ebu|ee|ee-GH|ee-TG|ee|efi|egy|eka|el|el-CY|el-GR|el|elx|en|en-001|en-150|en-AG|en-AI|en-AS|en-AT|en-AU|en-BB|en-BE|en-BI|en-BM|en-BS|en-BW|en-BZ|en-CA|en-CC|en-CH|en-CK|en-CM|en-CX|en-CY|en-DE|en-DG|en-DK|en-DM|en-ER|en-FI|en-FJ|en-FK|enm|eo|eo|es|es-419|es-AR|es-BO|es-BR|es-BZ|es-CL|es-CO|es-CR|es-CU|es-DO|es-EA|es-EC|es-ES|es-GQ|es-GT|es-HN|es-IC|es-MX|es-NI|es-PA|es-PE|es-PH|es-PR|es-PY|es-SV|es-US|es-UY|es-VE|es|et|et-EE|et|eu|eu-ES|eu|ewo|ewo-CM|ewo|fa|fa-AF|fa-IR|fa|fan|fat|ff|ff-CM|ff-GN|ff-MR|ff-SN|ff|fi|fi-FI|fi|fil|fil-PH|fil|fiu|fj|fo|fo-DK|fo-FO|fo|fon|fr|fr-BE|fr-BF|fr-BI|fr-BJ|fr-BL|fr-CA|fr-CD|fr-CF|fr-CG|fr-CH|fr-CI|fr-CM|fr-DJ|fr-DZ|fr-FR|fr-GA|fr-GF|fr-GN|fr-GP|fr-GQ|fr-HT|fr-KM|fr-LU|fr-MA|fr-MC|fr-MF|fr-MG|fr-ML|fr-MQ|fr|frm|fro|frr|frs|fur|fur-IT|fur|fy|fy-NL|fy|ga|ga-IE|ga|gaa|gay|gba|gd|gd-GB|gd|gem|gez|gil|gl|gl-ES|gl|gmh|gn|goh|gon|gor|got|grb|grc|gsw|gsw-CH|gsw-FR|gsw-LI|gsw|gu|gu-IN|gu|guz|guz-KE|guz|gv|gv-IM|gv|gwi|ha|ha-GH|ha-NE|ha-NG|ha|hai|haw|haw-US|haw|he|he-IL|he|hi|hi-IN|hi|hil|him|hit|hmn|ho|hr|hr-BA|hr-HR|hr|hsb|hsb-DE|hsb|ht|hu|hu-HU|hu|hup|hy|hy-AM|hy|hz|ia|iba|ibb|id|id-ID|id|ie|ig|ig-NG|ig|ii|ii-CN|ii|ijo|ik|ilo|inc|ine|inh|io|ira|iro|is|is-IS|is|it|it-CH|it-IT|it-SM|it-VA|it|iu|ja|ja-JP|ja|jbo|jgo|jgo-CM|jgo|jmc|jmc-TZ|jmc|jpr|jrb|jv|ka|ka-GE|ka|kaa|kab|kab-DZ|kab|kac|kaj|kam|kam-KE|kam|kar|kaw|kbd|kbl|kcg|kde|kde-TZ|kde|kea|kea-CV|kea|kfo|kg|kha|khi|kho|khq|khq-ML|khq|ki|ki-KE|ki|kj|kk|kk-KZ|kk|kkj|kkj-CM|kkj|kl|kl-GL|kl|kln|kln-KE|kln|km|km-KH|km|kmb|kn|kn-IN|kn|ko|ko-KP|ko-KR|ko|kok|kok-IN|kok|kos|kpe|kr|krc|krl|kro|kru|ks|ks-IN|ks|ksb|ksb-TZ|ksb|ksf|ksf-CM|ksf|ksh|ksh|ksh-DE|ksh|ku|kum|kut|kv|kw|kw-GB|kw|ky|ky-KG|ky|la|lad|lag|lag-TZ|lag|lah|lam|lb|lb-LU|lb|lez|lg|lg-UG|lg|li|lkt|lkt-US|lkt|ln|ln-AO|ln-CD|ln-CF|ln-CG|ln|lo|lo-LA|lo|lol|loz|lt|lt-LT|lt|lu|lu-CD|lu|lua|lui|lun|luo|luo-KE|luo|lus|luy|luy-KE|luy|lv|lv-LV|lv|mad|maf|mag|mai|mak|man|map|mas|mas-KE|mas-TZ|mas|mde|mdf|mdr|men|mer|mer-KE|mer|mfe|mfe-MU|mfe|mg|mg-MG|mg|mga|mgh|mgh-MZ|mgh|mgo|mgo-CM|mgo|mh|mi|mic|min|mis|mk|mk-MK|mk|mkh|ml|ml-IN|ml|mn|mn-MN|mn|mnc|mni|mno|mo|moh|mos|mr|mr-IN|mr|ms|ms-BN|ms-MY|ms-SG|ms|mt|mt-MT|mt|mua|mua-CM|mua|mul|mun|mus|mwl|mwr|my|my-MM|my|mye|myn|myv|na|nah|nai|nap|naq|naq-NA|naq|nb|nb-NO|nb-SJ|nb|nd|nd-ZW|nd|nds|nds-DE|nds-NL|nds|ne|ne-IN|ne-NP|ne|new|ng|nia|nic|niu|nl|nl-AW|nl-BE|nl-BQ|nl-CW|nl-NL|nl-SR|nl-SX|nl|nmg|nmg-CM|nmg|nn|nn-NO|nn|nnh|nnh-CM|nnh|no|nog|non|nqo|nr|nso|nub|nus|nus-SS|nus|nv|nwc|ny|nym|nyn|nyn-UG|nyn|nyo|nzi|oc|oj|om|om-ET|om-KE|om|or|or-IN|or|os|os-GE|os-RU|os|osa|ota|oto|pa|pa-Arab|pa-Arab-PK|pa-Guru|pa-Guru-IN|pa|paa|pag|pal|pam|pap|pau|peo|phi|phn|pi|pl|pl-PL|pl|pon|pra|pro|ps|ps-AF|ps|pt|pt-AO|pt-BR|pt-CH|pt-CV|pt-GQ|pt-GW|pt-LU|pt-MO|pt-MZ|pt-PT|pt-ST|pt-TL|pt|qu|qu-BO|qu-EC|qu-PE|qu|raj|rap|rar|rm|rm-CH|rm|rn|rn-BI|rn|ro|ro-MD|ro-RO|ro|roa|rof|rof-TZ|rof|rom|ru|ru-BY|ru-KG|ru-KZ|ru-MD|ru-RU|ru-UA|ru|rup|rw|rw-RW|rw|rwk|rwk-TZ|rwk|sa|sad|sah|sah-RU|sah|sai|sal|sam|saq|saq-KE|saq|sas|sat|sba|sbp|sbp-TZ|sbp|sc|scn|sco|sd|se|se-FI|se-NO|se-SE|se|see|seh|seh-MZ|seh|sel|sem|ses|ses-ML|ses|sg|sg-CF|sg|sga|sgn|shi|shi-Latn|shi-Latn-MA|shi-Tfng|shi-Tfng-MA|shi|shn|shu|si|si-LK|si|sid|sio|sit|sk|sk-SK|sk|sl|sl-SI|sl|sla|sm|sma|smi|smj|smn|smn-FI|smn|sms|sn|sn-ZW|sn|snk|so|so-DJ|so-ET|so-KE|so-SO|so|sog|son|sq|sq-AL|sq-MK|sq-XK|sq|sr|sr-Cyrl|sr-Cyrl-BA|sr-Cyrl-ME|sr-Cyrl-RS|sr-Cyrl-XK|sr-Latn|sr-Latn-BA|sr-Latn-ME|sr-Latn-RS|sr-Latn-XK|sr|srn|srr|ss|ssa|ssy|st|su|suk|sus|sux|sv|sv-AX|sv-FI|sv-SE|sv|sw|sw-CD|sw-KE|sw-TZ|sw-UG|sw|swb|swc|syc|syr|ta|ta-IN|ta-LK|ta-MY|ta-SG|ta|tai|te|te-IN|te|tem|teo|teo-KE|teo-UG|teo|ter|tet|tg|tg-TJ|tg|th|th-TH|th|ti|ti-ER|ti-ET|ti|tig|tiv|tk|tkl|tl|tlh|tli|tmh|tn|to|to-TO|to|tog|tpi|tr|tr-CY|tr-TR|tr|trv|ts|tsi|tt|tt-RU|tt|tum|tup|tut|tvl|tw|twq|twq-NE|twq|ty|tyv|tzm|tzm-MA|tzm|udm|ug|ug-CN|ug|uga|uk|uk-UA|uk|umb|und|ur|ur-IN|ur-PK|ur|uz|uz-Arab|uz-Arab-AF|uz-Cyrl|uz-Cyrl-UZ|uz-Latn|uz-Latn-UZ|uz|vai|vai-Latn|vai-Latn-LR|vai-Vaii|vai-Vaii-LR|vai|ve|vi|vi-VN|vi|vo|vot|vun|vun-TZ|vun|wa|wae|wae-CH|wae|wak|wal|war|was|wen|wo|wo-SN|wo|xal|xh|xog|xog-UG|xog|yao|yap|yav|yav-CM|yav|ybb|yi|yi-001|yi|yo|yo-BJ|yo-NG|yo|ypk|yue|yue-Hans|yue-Hans-CN|yue-Hant|yue-Hant-HK|yue|za|zap|zbl|zen|zh|zh-Hans|zh-Hans-CN|zh-Hans-HK|zh-Hans-MO|zh-Hans-SG|zh-Hant|zh-Hant-HK|zh-Hant-MO|zh-Hant-TW|zh|znd|zu|zu-ZA|zu|zun|zxx|zza}
    lang_pack = "en"  # {ar|az|bg|bn|cs|da|de|dv|dz|el|en|es|et|fa|fr|he|hr|hu|hy|id|is|it|ja|ka|km|ko|lo|lt|lv|mk|mn|ms|my|ne|nl|pl|pt|ro|ru|sk|sl|th|tk|tr|uk|uz|vi}
    device_model = "PC 64bit"
    system = (
        platform.uname()
    )  # [DEBUG][telegram_helper.py:12:explore_machine]                 system=uname_result(system='Windows', node='dellatg', release='10', version='10.0.18362', machine='AMD64', processor='Intel64 Family 6 Model 42 Stepping 7, GenuineIntel')

    machine = system.machine
    default_system_version = re.sub(r"-.+", "", system.release)
    system_version = system_version or default_system_version or "1.0"

    _ = {
        "app_id": APP_CONFIG_API_ID,
        "app_hash": APP_CONFIG_API_HASH,
        "app_version": app_version,  # с этим что?
        # "pc": pc,
        "lang_code": lang_code,
        "system_lang_code": system_lang_code,
        "lang_pack": lang_pack,
        "device_model": device_model,
        "system_version": system_version,
    }
    return _


if __name__ == "__main__":
    special = "get_telegram_settings"

    if special == "get_telegram_settings":
        settings = get_telegram_settings()
        logger.info(f"{pretty_dict(settings)}")
    else:
        logger.critical(f"unknown {special=}")
