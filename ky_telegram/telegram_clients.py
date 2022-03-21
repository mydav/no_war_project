# -*- coding: utf-8 -*-

from modules import *

from opentele.tl import TelegramClient
from opentele.api import API, CreateNewSession, UseCurrentSession

# не надо - много места занимает, поэтому исключил
# from opentele.td import TDesktop

logger = get_logger(__name__)


async def get_client_from_phone(
    f_session: str = "",
    phone: str = "",
    d_sessions=None,
    name="",
    proxy=None,
    **kwargs,
):
    """получаю клиента из папки телеграма
    """
    if not d_sessions:
        d_sessions = os.path.realpath("data/telegram_sessions")
    if not name:
        name = ".session"

    name = norm_phone(name)

    if not f_session:
        f_session = f"{d_sessions}/{name}"

    f_session = os.path.realpath(f_session)

    logger.debug(f"[get_client_from_phone, {f_session=}")
    # os._exit(0)

    api = API.TelegramAndroid.Generate(unique_id=f_session)

    logger.debug(f"{api=}")
    # os._exit(0)

    mkdir(f_session)
    if proxy:
        logger.debug(f"{proxy}")
    client = TelegramClient(f_session, api=api, proxy=proxy)
    # client = TelegramClient(phone, api=api)
    logger.debug(f"{client=}")
    connected = await client.connect()
    logger.debug(f"{connected=}")

    # logined = await client.QRLoginToNewClient()
    # logger.debug(f"{logined=}")
    is_authorized = await client.is_user_authorized()
    logger.debug(f"{is_authorized=}")
    # os._exit(0)

    if not is_authorized:
        logger.error(
            f"Вы сейчас не залогинены в телеграм, поэтому невозможно отправлять жалобы на канал. Давайте залогинимся."
        )
        if not phone:
            phone = input(
                f"Введите ваш НОМЕР ТЕЛЕФОНА для телеграма (в формате +380 97 777 77 77, пробелы обязательны иначе код не дойдет): "
            )

        sent_code = await client.send_code_request(phone)
        logger.debug(f"{sent_code=}")

        otp = input(
            f"Введите КОД, которые телеграм прислал на телефон: "
        )  # Telegram sent code to {phone}. Enter code

        me = await client.sign_in(phone=phone, code=otp)

        logger.debug(f"{me=}")
        # client.send_code_request(phone)
        # otp = getOTPCodeByPhone()
        # client.sign_up(code=otp, first_name=name.strip(), phone=phone)

        # теперь сохраняю сессию отдельно еще
        normed_phone = norm_phone(phone)
        f_session_with_phone = f"{d_sessions}/{normed_phone}"
        logger.debug(f"copy session to {f_session_with_phone}")
        mkdir(f_session)
        copy_file(f_session, f_session_with_phone)

    logger.debug(f"after login {client=}")
    return client


async def get_client_from_telegram_desktop(
    username: str = "", f_session: str = "newSession.session",
):
    """получаю клиента из папки телеграма"""
    # Load TDesktop client from tdata folder
    tdataFolder = r"C:\Users\<username>\AppData\Roaming\Telegram Desktop\tdata".replace(
        r"<username>", username
    )
    logger.debug(f"{tdataFolder=}")
    tdesk = TDesktop(tdataFolder)
    logger.debug(f"{tdesk=}")

    # Using official iOS API with randomly generated device info
    # print(api) to see more
    api = API.TelegramIOS.Generate()
    logger.debug(f"{api=}")

    # Convert TDesktop session to telethon client
    # CreateNewSession flag will use the current existing session to
    # authorize the new client by `Login via QR code`.
    client = await tdesk.ToTelethon(f_session, CreateNewSession, api)

    logger.debug(f"{client=}")
    return client


def norm_phone(phone=""):
    repl = {
        "+": "",
        " ": "",
    }
    normed = no_probely(phone, repl)
    return normed


if __name__ == "__main__":
    special = "norm_phone"
    if special == "norm_phone":
        phones = clear_list(
            """
                +38 097 777 77 77
        """
        )
        for phone in phones:
            normed = norm_phone(phone)
            logger.info(f"{normed=} from {phone}")
    os._exit(0)
