# -*- coding: utf-8 -*-
# from opentele.tl import TelegramClient

from telethon.tl.types import (
    PeerChannel,
    InputPeerUser,
    InputPeerChannel,
    InputReportReasonOther,
    ChannelParticipantsSearch,
    InputChannel,
)

from telethon.tl.functions.channels import (
    GetParticipantsRequest,
    JoinChannelRequest,
)
from telethon.tl.functions.account import ReportPeerRequest
from telethon.tl.functions.messages import CheckChatInviteRequest


# from telethon import functions

from ky_telegram.telegram_clients import *
from ky_async.async_functions import run_async


from modules import *
import platform

import asyncio

# on windows: RuntimeError: Event loop is closed.      On Windows seems to be a problem with EventLoopPolicy, use this snippet to work around it:
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


logger = get_logger(__name__)


async def join_channel(client, channel):
    """присоединиться к каналу"""
    joined = await client(JoinChannelRequest(channel))
    logger.debug(f"{joined=}")
    return joined


async def send_report(
    client, channel="", message="", d_sent=None, f_sent=None
):
    """главная цель - отправить репорт на канал!
    при ошибке получаем

        {'status': False, 'details': '', 'error': 'user_not_exists', 'error_full': 'No user has "znrespnotexists" as username', 'error_path': []}

    """
    fun = "send_report"
    if not f_sent:
        name = channel.split("/")[-1]
        if not d_sent:
            d_sent = f"temp/!sent_telegram_reports"
        f_sent = f"{d_sent}/{name}"
    logger.debug(f"[send report to {channel=} {message=} {f_sent=}")
    details = ""
    error = {}
    while True:
        if file_exists(f_sent):
            details = "already_sent"
        else:
            peer = await get_peer(client, channel, to_return="entity")
            logger.debug(f"{peer=}")
            if is_api_error(peer):
                error = peer
                break

            sent = await client(
                ReportPeerRequest(
                    peer=peer,
                    reason=InputReportReasonOther(),
                    message=message,
                )
            )
            if sent:
                text_to_file(message, f_sent)
            logger.debug(f"+{sent=}]")
            if sent:
                details = "sent"

        break

    if details and not error:
        status = True
    else:
        status = False

    res = {
        "status": status,
        "details": details,
        # "sent": sent,
    }
    if error:
        res.update(error)
    return res


async def get_peer(
    client, url, debug=False, to_return: Literal["entity", "id"] = "entity",
):
    fun = "get_peer"
    try:
        entity = await client.get_entity(url)
    except Exception as er:
        error = str(er)
        error_short = ""
        error_full = ""

        # 'No user has "zvpered3" as username
        if "No user has " in error and " as username" in error:
            error_short = "user_not_exists"
        elif (
            "Cannot find any entity corresponding to" in error
        ):  # Cannot find any entity corresponding to
            error_short = "entity_not_exists"
        elif "Join the group and retry" in error:
            error_short = "join_group_and_retry"

        logger.warning(f"{error_short=} {error=} for {url}")

        if error_short:
            error_full = error
            error = error_short

        if error_short in [
            "entity_not_exists",
            # "join_group_and_retry",
        ]:  # проверим - возможно это инвайт
            invite_hash = url.split("/")[-1]
            logger.debug(f"possible {invite_hash=}")
            if invite_hash.startswith("+"):
                invite_hash = invite_hash[1:]
            logger.debug(f"found {invite_hash=}, recheck")
            return await get_peer_from_invite(
                client=client, invite_hash=invite_hash
            )

        return api_error(error, error_full=error_full)
        # os._exit(0)
    id = entity.id
    if debug:
        logger.debug(
            f"+{fun}: id={entity.id} entity={entity.stringify()}"
        )  # All paratmeters
    if to_return == "entity":
        result = entity
    elif to_return == "id":
        result = id
    else:
        m = f"unknown {to_return=}"
        logger.critical(m)
        os._exit(0)
    return result


async def get_peer_from_invite(client, invite_hash: str = ""):
    """
    How to obtain chatid of a private channel by given joinlink using Telegram API
      invite_hash=A4LmkR23G0IGxBE71zZfo1
    """
    try:
        chatinvite = await client(CheckChatInviteRequest(invite_hash))
    except Exception as er:
        # telethon.errors.rpcerrorlist.InviteHashExpiredError: The chat the user tried to join has expired and is not valid anymore (caused by CheckChatInviteRequest)
        error_full = str(er)
        error = ""
        logger.warning(f"{error_full=} for {invite_hash=}")

        # 'No user has "zvpered3" as username
        if (
            "The chat the user tried to join has expired and is not valid anymore"
            in error_full
        ):
            error = "chat_not_exists"

        return api_error(error, error_full=error_full)
        # os._exit(0)

    # logger.debug(f"{chatinvite.stringify()=}")
    # logger.debug(f"{pretty_dict(chatinvite.__dict__)}")
    # # channel_id = chatinvite.chat.id
    # # access_hash_channel = chatinvite.chat.access_hash
    # channel = InputChannel(channel_id, access_hash_channel)
    # logger.debug(f"{channel=} from {channel_id=} {access_hash_channel=}")
    channel = chatinvite.chat
    logger.debug(f" +{channel=}]")
    return channel


async def send_message_to_user(client, user_id_hash=(1, 1), message: str = ""):
    user_id, user_hash = user_id_hash
    receiver = InputPeerUser(user_id, user_hash)

    sent = await client.send_message(receiver, message, parse_mode="html")
    return sent


async def get_client_groups(
    client: TelegramClient, want_save_to_file=False, good_ids=[], debug=False
):
    """получить мои все группы"""
    infos = []
    dialogs = []
    async for dialog in client.iter_dialogs():
        # logger.debug(f"{dialog=} {dialog.stringify()}")
        entity = dialog.entity
        id = entity.id
        access_hash = getattr(
            entity, "access_hash", ""
        )  # AttributeError: 'Chat' object has no attribute 'access_hash'

        if good_ids and id not in good_ids:
            continue

        info = "\t".join(
            map(
                str,
                [
                    id,
                    access_hash,
                    dialog.is_group,
                    dialog.is_channel,
                    dialog.name,
                ],
            )
        )
        infos.append(info)

        if debug or (not dialog.is_group and dialog.is_channel):
            if debug:
                logger.debug(f"{dialog=} {dialog.stringify()}")
            logger.debug(f"dialog id={id} name={dialog.name}")
            dialogs.append(dialog)
            # await dialog.delete()

    if want_save_to_file:
        f_to = os.path.abspath("temp/channels.txt")
        logger.debug(f"save {len(infos)} channels to {f_to}")
        txt = "\n".join(infos)
        text_to_file(txt, f_to)
        logger.debug()
    return dialogs


async def get_channel_users(client, user_input_channel):
    if user_input_channel.isdigit():
        entity = PeerChannel(int(user_input_channel))
    else:
        entity = user_input_channel

    channel = client.get_entity(entity)
    logger.debug(f"{channel=} for {user_input_channel=} ({entity=}")

    offset = 0
    limit = 100
    all_participants = []

    while True:
        participants = await client(
            GetParticipantsRequest(
                channel, ChannelParticipantsSearch(""), offset, limit, hash=0,
            )
        )
        if not participants.users:
            break
        all_participants.extend(participants.users)
        offset += len(participants.users)

    all_user_details = []
    for participant in all_participants:
        all_user_details.append(
            {
                "id": participant.id,
                "first_name": participant.first_name,
                "last_name": participant.last_name,
                "user": participant.username,
                "phone": participant.phone,
                "is_bot": participant.bot,
            }
        )
    return all_user_details


def explore_machine():
    system = (
        platform.uname()
    )  # [DEBUG][telegram_helper.py:12:explore_machine]                 system=uname_result(system='Windows', node='dellatg', release='10', version='10.0.18362', machine='AMD64', processor='Intel64 Family 6 Model 42 Stepping 7, GenuineIntel')

    machine = system.machine

    logger.debug(f"{system=}")
    logger.debug(f"{machine=}")

    if system.machine in ("x86_64", "AMD64"):
        default_device_model = "PC 64bit"
    elif system.machine in ("i386", "i686", "x86"):
        default_device_model = "PC 32bit"
    else:
        default_device_model = machine
    default_system_version = re.sub(r"-.+", "", system.release)
    logger.debug(f"{default_device_model=} {default_system_version=}")


def explore_opentele(username="kyxa"):
    async def main():
        f_cache = "temp/client.obj"
        t = 1
        if t:
            func = get_client_from_telegram_desktop
            func = get_client_from_phone
            client = await func(username=username)
            t = 0
            if t:
                saved = obj_to_file(client, f_cache)
                logger.debug(f"{saved=}")
        else:
            client = obj_from_file(f_cache)
        logger.debug(f"{client=}")

        # Although Telegram Desktop doesn't let you authorize other
        # sessions via QR Code (or it doesn't have that feature),
        # it is still available across all platforms (APIs).

        # Connect and print all logged in devices
        connected = await client.connect()
        logger.debug(f"{connected=}")

        authorized = await client.is_user_authorized()
        logger.debug(f"{authorized=}")

        t = 0
        if t:
            myself = await client.get_me()
            logger.debug(f"myself {myself.stringify()}")

        t = 1
        if t:
            await client.PrintSessions()

        special = "get_client_groups"
        special = "get_channel_users"
        special = "send_message"
        special = "get_peer_from_invite"
        special = "get_peer"
        special = "send_report"

        logger.info(f"{special=}")

        if special == "":
            pass

        elif special == "get_peer_from_invite":
            urls = clear_list(
                """
            # https://t.me/ZNResp
            # https://t.me/vagner_group
            # https://t.me/ZNRespnotexists
            # http://t.me/8FClvPjO2NtlNWEy
            # http://t.me/joinchat/8FClvPjO2NtlNWEy
            # tg://join?invite=8FClvPjO2NtlNWEy
            # 8FClvPjO2NtlNWEy
            # https://t.me/joinchat/C2corrpo4SA4OWNk
            C2corrpo4SA4OWNk
            """,
                bad_starts="#",
            )
            for num, url in enumerate(urls, 1):
                channel = await get_peer_from_invite(client, url)
                logger.info(f"{num}/{len(urls)} {url=} finished {channel=}")
                break

        elif special == "send_report":
            channels = clear_list(
                """
            # https://t.me/ZNResp
            # https://t.me/vagner_group
            # https://t.me/ZNRespnotexists
            # http://t.me/8FClvPjO2NtlNWEy
            # http://t.me/joinchat/8FClvPjO2NtlNWEy
            # tg://join?invite=8FClvPjO2NtlNWEy
            # 8FClvPjO2NtlNWEy
            https://t.me/+C2corrpo4SA4OWNk
            """,
                bad_starts="#",
            )
            for num, channel in enumerate(channels, 1):
                message = get_random_report()
                report = await send_report(client, channel, message)
                logger.info(
                    f"{num}/{len(channels)} {channel=} finished {report=}"
                )
                break

        elif special == "get_peer":
            urls = clear_list(
                """
            # https://t.me/ZNResp
            # https://t.me/vagner_group
            https://t.me/+C2corrpo4SA4OWNk
            """,
                bad_starts=["#"],
            )
            kwargs = {
                "to_return": "id",
                # "debug": True,
            }
            for num, url in enumerate(urls, 1):
                peer = await get_peer(client, url, **kwargs)
                logger.info(f"{num}/{len(urls)} {url=} found {peer=}")

        elif special == "send_message":
            user_id_hash = (832207298, -4413438556642330680)
            message = f"<b>Я тебе люблю</b>"
            sent = await send_message_to_user(
                client, user_id_hash=user_id_hash, message=message
            )
            logger.debug(f"{sent=}")

        elif special == "get_channel_users":
            # не работает?
            channel_id = "562503548118177911"
            all_user_details = await get_channel_users(client, channel_id)
            f_to = f"temp/user_data/{channel_id}.json", "w"
            with open(f_to) as outfile:
                json.dump(all_user_details, outfile)
            logger.debug(f"saved users to {f_to=}")

        elif special == "get_client_groups":
            logger.debug(f"get_client_groups")
            good_ids = [832207298]
            good_ids = []
            want_save_to_file = True
            want_save_to_file = False
            groups = await get_client_groups(
                client,
                good_ids=good_ids,
                debug=True,
                want_save_to_file=want_save_to_file,
            )
            logger.debug(f"{len(groups)} groups: {groups=}")

        else:
            logger.critical(f"unknown {special=}")

    asyncio.run(main())


def explore_telegram():
    from opentele.tl import TelegramClient
    from opentele.api import API
    import asyncio

    async def main():
        api = API.TelegramDesktop

        client = TelegramClient("telethon.session", api=api)
        await client.connect()

    asyncio.run(main())


def get_random_report():
    from no_war_project.report_templates import get_default_report_templates
    from no_war_project.settings import get_text_rewriter

    fun = "get_random_report"
    templates = clear_list(get_default_report_templates())
    rewriter = get_text_rewriter()
    tpl = choice(templates)
    logger.debug(f"{fun}: selected {tpl=} from {len(templates)} templates")

    message = rewriter.get_random_text_variation(tpl)
    return message


if __name__ == "__main__":
    special = "explore_telegram"

    if special == "":
        pass

    elif special == "explore_telegram":
        # r = explore_telegram()
        # r = explore_machine()
        r = explore_opentele()
        logger.info(f"{r=}")

    else:
        logger.critical(f"unknown {special=}")
