from modules import *

logger = get_logger(__name__)


def guess_telegram_url(url="", debug=False):
    """
    https://t.me/s/stoprussiachannel
    https://t.me/stoprussiachannel

    :param url:
    :param debug:
    :return:
    """
    want_private_chats = False
    final_url = None
    delims = []
    tip = None
    if url and ("/t.me/" in url):
        if want_private_chats and "/joinchat/" in url:
            tip = "telegram"
            delims = ["/joinchat/"]
            url_tpl = "https://t.me/joinchat/[chanel_name]"

        else:
            tip = "telegram"
            delims = [".me/"]
            url_tpl = "https://t.me/[chanel_name]"

    elif (
        want_private_chats and url and "join?invite=" in url
    ):  # tg://join?invite=8FClvPjO2NtlNWEy
        tip = "telegram"
        delims = ["join?invite="]
        url_tpl = "https://t.me/joinchat/[chanel_name]"

    # logger.debug(f"{tip=} for {url=}")
    if tip is None:
        if debug:
            logger.warning(f"unknown {tip=} for {url=}")
        else:
            logger.debug(f"unknown {tip=} for {url=}")
        pass

    elif tip in ["telegram"]:
        chanel_name = None
        for chanel_delim in delims:
            chanel_name = find_from_to_one(chanel_delim, "nahposhuk", url)
            if chanel_name:
                break

        # logger.debug(f'{chanel_name=}')
        if not chanel_name:
            m = f"unknown chanel in {url}"
            logger.critical(m)
            os._exit(0)

        splits = "/"
        for _ in splits:
            chanel_name = chanel_name.split(_)[-1]

        if not chanel_name:
            m = f"no chanel_name in {url=}"
            logger.critical(m)
            os._exit(m)

        if not want_private_chats and chanel_name.startswith("+"):
            pass
        else:

            repl = {
                "[chanel_delim]": chanel_delim,
                "[chanel_name]": chanel_name,
            }
            final_url = no_probely(url_tpl, repl)
    else:
        m = f"unknown {tip=}"
        logger.critical(m)
        os._exit(m)
    return final_url


def guess_instagram_url(url="", debug=False):
    """если урл"""
    final_url = None
    delims = []
    tip = None
    if url and ("instagram.com" in url):
        tip = "instagram"
        delims = ["instagram.com/"]
        url_tpl = "https://www.instagram.com/[chanel_name]/"

    # logger.debug(f'{tip=} for {url=}')
    if tip is None:
        if debug:
            logger.warning(f"unknown {tip=} for {url=}")
        else:
            logger.debug(f"unknown {tip=} for {url=}")
        pass

    elif tip in ["instagram"]:
        chanel_name = None
        for chanel_delim in delims:
            chanel_name = find_from_to_one(chanel_delim, "nahposhuk", url)
            if chanel_name:
                break

        # logger.debug(f'{chanel_name=}')
        if not chanel_name:
            m = f"unknown chanel in {url}"
            logger.critical(m)
            os._exit(0)

        splits = "/?&"
        for _ in splits:
            chanel_name = chanel_name.split(_)[0]

        if not chanel_name:
            m = f"no chanel_name in {url=}"
            logger.critical(m)
            os._exit(m)

        repl = {
            "[chanel_delim]": chanel_delim,
            "[chanel_name]": chanel_name,
        }
        final_url = no_probely(url_tpl, repl)
    else:
        m = f"unknown {tip=}"
        logger.critical(m)
        os._exit(m)
    return final_url


def guess_youtube_chanel_url(url="", debug=False):
    """если урл - ютубный"""
    final_url = None
    delims = []
    tip = None
    if url and ("youtube.com/" in url or "youtu.be/" in url):
        if "/channel/" in url or "/c/" in url:
            tip = "channel"
            delims = ["/channel/", "/c/"]
            url_tpl = (
                "https://www.youtube.com[chanel_delim][chanel_name]/about"
            )
        elif "/user/" in url:
            tip = "user"
            delims = ["/user/"]
            url_tpl = (
                "https://www.youtube.com[chanel_delim][chanel_name]/about"
            )

        else:
            if "watch?v=" in url or "/shorts/" in url:
                tip = "video"
                delims = ["watch?v=", "/shorts/"]
                url_tpl = "https://www.youtube.com/watch?v=[chanel_name]"
            else:
                parts = clear_list(url.split("/"))
                if len(parts) == 3:  # ['https:', 'youtu.be', '1vdiEABLFoo']
                    tip = "video"
                    delims = ["youtu.be/"]
                    url_tpl = "https://www.youtube.com/watch?v=[chanel_name]"
                else:
                    logger.debug(f"unknown {len(parts)} {parts=}")

    # logger.debug(f'{tip=} for {url=}')
    if tip is None:
        if debug:
            logger.warning(f"unknown {tip=} for {url=}")
        else:
            logger.debug(f"unknown {tip=} for {url=}")
        pass

    elif tip in ["channel", "user", "video"]:
        # url = find_from_to_one('', 'nahposhuk', url)
        chanel_name = None
        for chanel_delim in delims:
            chanel_name = find_from_to_one(chanel_delim, "nahposhuk", url)
            if chanel_name:
                break

        # logger.debug(f'{chanel_name=}')
        if not chanel_name:
            m = f"unknown chanel in {url}"
            logger.critical(m)
            os._exit(0)

        splits = "/?&"
        for _ in splits:
            chanel_name = chanel_name.split(_)[0]

        if not chanel_name:
            m = f"no chanel_name in {url=}"
            logger.critical(m)
            os._exit(m)

        # chanel_url = f'https://www.youtube.com{chanel_delim}{chanel_name}/about'
        repl = {
            "[chanel_delim]": chanel_delim,
            "[chanel_name]": chanel_name,
        }
        final_url = no_probely(url_tpl, repl)
    else:
        m = f"unknown {tip=}"
        logger.critical(m)
        os._exit(m)
    return final_url


if __name__ == "__main__":
    special = "guess_youtube_chanel_url"
    special = "guess_instagram_url"
    special = "guess_telegram_url"

    if special == "guess_telegram_url":
        # todo
        txt_url = """
            https://t.me/s/stoprussiachannel
            https://t.me/stoprussiachannel
            
            # my private channel
            https://t.me/+C2corrpo4SA4OWNk
            ## это то же что и https://t.me/joinchat/C2corrpo4SA4OWNk ?
            
            # # приглашения в закрытую группу
            http://t.me/joinchat/8FClvPjO2NtlNWEy
            tg://join?invite=8FClvPjO2NtlNWEy
            
            https://t.me/zvpered
        """

        txt = txt_url
        items = clear_list(txt, bad_starts="#")
        for item in items:
            telegram_url = guess_telegram_url(item)
            logger.debug(f"{telegram_url=} from {item=}")

    elif special == "guess_instagram_url":
        # todo
        txt_url = """
        ➡️ https://www.instagram.com/craterimpact/?utm_medium=copy_link
        ➡️ https://www.instagram.com/mara.mounn/
        ➡️ https://www.instagram.com/news_blog_rus/
        """

        txt = txt_url
        items = clear_list(txt, bad_starts="#")
        for item in items:
            instagram_url = guess_instagram_url(item)
            logger.debug(f"{instagram_url=} from {item=}")

    elif special == "guess_youtube_chanel_url":
        special = "guess_instagram_url"
        txt_channel = """
        https://www.youtube.com/c/rusvesnasu1945/videos
        https://www.youtube.com/watch?v=qmwzCk68p5I
        https://www.youtube.com/c/%D0%98%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F%D0%9E%D1%80%D1%83%D0%B6%D0%B8%D1%8F
        https://www.youtube.com/c/RTVIchannel/videos
        https://www.youtube.com/c/CzarTalks/community
        https://youtu.be/1vdiEABLFoo
        https://youtube.com/c/LentaruVideo
        https://youtube.com/channel/UCvC21u5aFO-tkYcLb22T0JA
        https://youtube.com/channel/UCQ4YOFsXjG9eXWZ6uLj2t2A
        https://www.youtube.com/c/RightHistory
        https://www.youtube.com/c/RightHistory
        https://nah.com/c/RightHistory
        """

        txt_user = """
        https://www.youtube.com/user/supersharij?app=desktop
        https://youtube.com/user/mikhailovetv
        https://www.youtube.com/watch?v=HBAxST7TbBs&t=75
        https://www.youtube.com/user/onttvchannel/community
        https://www.youtube.com/user/nstarikovru/videos
        """

        # todo
        txt_video = """
        https://www.youtube.com/watch?v=x0mEXifo8gU
        https://youtube.com/shorts/fti9lZA5S34?feature=share
        https://youtu.be/1vdiEABLFoo

        """

        txt = txt_video
        txt = txt_channel
        txt = txt_user
        items = clear_list(txt, bad_starts="#")
        for item in items:
            chanel_url = guess_youtube_chanel_url(item)
            logger.debug(f"{chanel_url=} from {item=}")
    else:
        logger.critical(f"unknown {special=}")
