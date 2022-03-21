# -*- coding: utf-8 -*-

from ky_telegram.telegram_helper import *
from telethon import functions
import socks


class TelegramReporter:
    def __init__(self, d="", d_sent="", phone="", proxy=None, **kwargs):
        if not d:
            d = "data/telegram"
        self.d = os.path.realpath(d)

        self.client = None
        self.phone = phone
        self.proxy = proxy

        normed_phone = norm_phone(phone)
        if not d_sent:
            d_sent = f"temp/!sent_telegram_reports/{normed_phone}"
        self.d_sent = os.path.realpath(d_sent)

    def send_report(self, channel: str = "", message: str = "", f_sent=None):
        """отправляем репорт"""
        fun = "send_report"
        logger.debug(f"[{fun} to {channel=}")

        if not self.client:
            logger.debug(f"no client, connecting")
            client = self.connect_client()
            logger.debug(f"+connected {client=}")

        coro = send_report
        coro_kwargs = {
            "client": self.client,
            "channel": channel,
            "message": message,
            "f_sent": f_sent,
            "d_sent": self.d_sent,
        }
        sent = run_async(coro=coro, coro_kwargs=coro_kwargs)
        logger.debug(f" +[{fun}: {sent=}]")
        return sent

    def connect_client(self):
        fun = "connect_client"
        coro = get_client_from_phone
        # f_session = f"{self.d}/telegram_session.session"
        coro_kwargs = {
            # "f_session": f_session,
            "name": self.phone,
            "phone": self.phone,
            "proxy": self.proxy,
        }
        client = run_async(coro=coro, coro_kwargs=coro_kwargs)
        logger.debug(f" +[{fun}: {client=}]")
        self.client = client
        return client

    def about_me(self):
        client = self.client
        logger.debug(f"about_me for {self.client}")
        t = 1
        if t:
            # myself = await client.get_me()
            myself = run_async(client.get_me)
            logger.debug(f"myself {myself.stringify()}")

        t = 1
        if t:
            # await client.PrintSessions()
            sessions = run_async(client.PrintSessions)

        t = 1
        if t:
            # list all sessions
            sessions = client.session.list_sessions()
            # sessions = run_async(client.session.list_sessions)
            logger.info(f"{len(sessions)} {sessions=}")

            t = 1
            if t:
                GetSessions = run_async(
                    client,
                    coro_args=(functions.account.GetAuthorizationsRequest(),),
                )
                logger.debug(f"{GetSessions=}")
                if len(GetSessions.authorizations) > 1:
                    print("Another Session    :\tYes")
                    for ss in GetSessions.authorizations:
                        # logger.debug(f"{ss.__dict__}")
                        SessionHash = ss.hash
                        SessionIp = ss.ip
                        logger.debug(f"{SessionIp=} {ss.country}")
                        # if SessionHash > 0:
                        #     result = run_async(
                        #         client,
                        #         coro_args=(
                        #             functions.account.ResetAuthorizationRequest(
                        #                 hash=SessionHash
                        #             ),
                        #         ),
                        #     )
                        #     print("Session Killed     :\t" + str(SessionIp))
                else:
                    print("Another Session    :\tNo")

    def __repr__(self):
        return (
            f"<TelegramReporter: {self.phone} d={self.d} d_sent={self.d_sent}"
        )


if __name__ == "__main__":
    special = "TelegramReporter"

    if special == "":
        pass

    elif special == "TelegramReporter":
        phone = "+380 66 858 37 10"  # мама
        phone = "+34 625 794 863"  # мой

        rdns = True
        proxy_http = (
            socks.HTTP,
            "188.143.169.28",
            30049,
            rdns,
            "iparchitect_9173_27_02_22",
            "idN6dAShS4eBB8bYS3",
        )
        proxy_socks = (
            socks.SOCKS5,
            "188.143.169.28",
            40049,
            rdns,
            "iparchitect_9173_27_02_22",
            "idN6dAShS4eBB8bYS3",
        )
        # proxy = None
        proxy = proxy_http
        proxy = proxy_socks
        _ = {
            "phone": phone,
            "proxy": proxy,
        }
        reporter = TelegramReporter(**_)
        logger.info(f"{reporter=}")
        # client = reporter.connect_client()
        # logger.info(f"{client=}")

        t = 0
        if t:
            reporter.connect_client()
            reporter.about_me()
            os._exit(0)

        channels = clear_list(
            """
        # https://t.me/ZNResp
        # https://t.me/vagner_group
        #     https://t.me/+C2corrpo4SA4OWNk
        https://t.me/joinchat/8FClvPjO2NtlNWEy
        """,
            bad_starts=["#"],
        )
        for num, channel in enumerate(channels, 1):
            message = get_random_report()
            report = reporter.send_report(channel, message)
            logger.info(
                f"+{num}/{len(channels)} {channel=} finished {report=}"
            )
            break

    else:
        logger.error(f"unknown {special=}")
