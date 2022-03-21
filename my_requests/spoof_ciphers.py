if 1:
    import http.client

    http.client.HTTPConnection.debuglevel = 5

from modules import *

logger = get_logger(__file__)

import ssl
import requests

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
from requests.packages.urllib3.util import ssl_


from http.client import HTTPConnection


def request(self, method, url, body=None, headers={}, *, encode_chunked=False):
    self._send_request(method, url, body, headers, encode_chunked)
    logger.warning(f"cipher={self.sock.cipher()}")


HTTPConnection.request = request


def check_session(session):
    url = "https://www.howsmyssl.com/a/check"

    try:
        response = session.request("GET", url)
        logger.debug(f"text={response.text}")
        logger.debug(f"{response=}")
    except Exception as exception:
        logger.error(exception)
    dct = response.json()
    logger.debug(f"{pretty_dict(dct, 'reponse')}")
    return dct


def spoof_session(session, ssl_options=0, ciphers=None):
    adapter = TlsAdapter(ssl_options=ssl_options, ciphers=ciphers,)
    session.mount("https://", adapter)
    session.adapter = adapter


class TlsAdapter(HTTPAdapter):
    def __init__(self, ssl_options=0, ciphers=None, **kwargs):
        ssl_options = self.get_ssl_options(ssl_options)
        ciphers = self.get_ciphers(ciphers)

        logger.debug(f" init TlsAdapter: {ssl_options=} {ciphers=} {kwargs=}")
        self.ssl_options = ssl_options
        self.ciphers = ciphers
        super(TlsAdapter, self).__init__(**kwargs)

    def get_ciphers(self, ciphers=None):
        if ciphers is None:
            ciphers = "ECDHE-RSA-AES256-GCM-SHA384"
            ciphers = "AES_256_GCM_SHA384"
            ciphers = "TLS_AES_256_GCM_SHA384"
            # ciphers = "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384"
            ciphers = "ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-SHA256:AES256-SHA"  # main full
            ciphers = "ECDHE-ECDSA-AES256-GCM-SHA384"
        elif 1:
            os_ciphers = get_ciphers_for_openssl(ciphers)
            ciphers = ":".join(os_ciphers)
        return ciphers

    def get_ssl_options(self, ssl_options=0):
        """
        You can control which TLS versions to restrict using the parameters of the TlsAdapter. It can take the following arguments:
            ssl.OP_NO_TLSv1 (For restricting TLS V1)
            ssl.OP_NO_TLSv1_1 (For restricting TLS V1.1)
            ssl.OP_NO_TLSv1_2 (For restricting TLS V1.2)
            ssl.OP_NO_TLSv1_3 (For restricting TLS V1.3)
        """
        if ssl_options == "1.1":
            ssl_options = (
                ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_2 | ssl.OP_NO_TLSv1_3
            )
        elif ssl_options == "1.2":
            ssl_options = (
                ssl.OP_NO_TLSv1_1 | ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_3
            )
        elif ssl_options == "1.3":
            ssl_options = (
                ssl.OP_NO_TLSv1_1 | ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_2
            )
        elif isinstance(ssl_options, str):
            logger.critical(f"unknown {ssl_options=}")
            os._exit(0)
        # wait_for_ok(f"{ssl_options=}")
        return ssl_options

    def init_poolmanager(self, *pool_args, **pool_kwargs):
        ciphers = self.ciphers
        ctx = ssl_.create_urllib3_context(
            ciphers=ciphers,
            cert_reqs=ssl.CERT_REQUIRED,
            options=self.ssl_options,
        )
        self.poolmanager = PoolManager(
            *pool_args, ssl_context=ctx, **pool_kwargs
        )


def get_ciphers_for_openssl(
    txt="", cipher_dict=None, skipping=["TLS_EMPTY_RENEGOTIATION_INFO_SCSV"]
):
    f = None
    if txt in [
        "ciphers_ubuntu_20.04_chrome.txt",
        "ubuntu_chrome",
    ]:
        f = get_f_from_data("ciphers_ubuntu_20.04_chrome.txt")

    elif file_exists(get_f_from_data(txt)):
        f = get_f_from_data(txt)

    if f:
        txt = text_from_file(f)

    if not cipher_dict:
        cipher_dict = load_cipher_equivalents()

    openssl_ciphers = []
    ciphers = parse_wireshark_ciphers(txt)
    for cipher in ciphers:
        if cipher in skipping:
            continue
        os_cipher = cipher_dict.get(cipher, cipher)
        # os_cipher = cipher
        if not os_cipher:
            logger.warning(f"    not openssl cipher for {cipher=}")
            continue
        openssl_ciphers.append(os_cipher)
    return openssl_ciphers


def parse_wireshark_ciphers(txt="", cipher_dict={}):
    """
    Cipher Suites (2 suites)
    Cipher Suite: TLS_RSA_WITH_AES_256_CBC_SHA (0x0035)
    Cipher Suite: TLS_EMPTY_RENEGOTIATION_INFO_SCSV (0x00ff)
    """
    if not cipher_dict:
        cipher_dict = load_cipher_equivalents()

    items = clear_list(txt)
    ciphers = []
    for item in items:
        item = item.strip()
        cipher = find_from_to_one("Cipher Suite:", "(", item).strip()
        if not cipher and (
            item in cipher_dict or item in cipher_dict.values()
        ):
            cipher = item
        if not cipher:
            continue
        ciphers.append(cipher)
    return ciphers


def load_cipher_equivalents():
    """
    wireshark -> openssl

    from https://stackoverflow.com/questions/41886533/use-client-cert-and-tls-rsa-with-aes-256-cbc-sha-and-other-cipher-suites:
        You can map the IANA cipher suite names like TLS_RSA_WITH_AES_128_CBC_SHA
        to OpenSSL cipher string names, like AES128-SHA
        using the openssl ciphers man page
            https://www.openssl.org/docs/man1.1.1/man1/ciphers.html
    """
    f = get_f_from_data("cipher_suites.txt")
    items = clear_list(text_from_file(f))
    ciphers = {}
    for item in items:
        items = clear_list(item.split(" "))
        if len(items) == 2:
            x, y = items
            ciphers[x] = y
    return ciphers


def get_f_from_data(name):
    f = pathlib.Path(__file__).parent / "data" / "ciphers" / name
    return f


if __name__ == "__main__":
    special = "load_cipher_equivalents"
    special = "parse_wireshark_ciphers"
    special = "explore"

    if not special:
        pass

    elif special == "load_cipher_equivalents":
        ciphers = load_cipher_equivalents()
        logger.debug(pretty_dict(ciphers, "ciphers"))

    elif special == "parse_wireshark_ciphers":
        txt = """
        Cipher Suite: TLS_RSA_WITH_AES_256_CBC_SHA (0x0035)
        Cipher Suite: TLS_EMPTY_RENEGOTIATION_INFO_SCSV (0x00ff)
        """
        txt = "ubuntu_chrome"
        ciphers = parse_wireshark_ciphers(txt)
        logger.info(f"{ciphers=}")

        os_ciphers = get_ciphers_for_openssl(txt)
        logger.info(f"{len(os_ciphers)} {os_ciphers=}")

    elif special == "explore":
        spoof_mode = "auto"
        spoof_mode = "manual"

        step = 1
        step = 2
        step = 3

        ciphers = None
        if step == 1:
            spoof_kwargs = {
                "ssl_options": "1.1",
                "ciphers": None,
            }

        elif step == 2:
            spoof_kwargs = {
                "ssl_options": "1.2",
                "ciphers": "AES256-SHA",
            }

        elif step == 3:
            spoof_kwargs = {
                "ssl_options": 0,
                "ssl_options": "1.3",
                "ssl_options": "1.2",
                "ciphers": "ubuntu_chrome",
                "ciphers": "ciphers_windows_cloudflare_requests.txt",
                "ciphers": "AES256-SHA",  # openssl
                "ciphers": "Cipher Suite: TLS_AES_256_GCM_SHA384 (0x1302)",
                "ciphers": "AES_256_GCM_SHA384",
                "ciphers": "TLS_AES_256_GCM_SHA384",  # 1.2 - Не существует?
                "ciphers": "TLS_RSA_WITH_AES_256_CBC_SHA",  # wireshark
                "ciphers": None,
            }

        session = requests.session()

        logger.debug(f"{spoof_kwargs=}")
        if spoof_mode == "manual":
            adapter = TlsAdapter(
                spoof_kwargs["ssl_options"], ciphers=spoof_kwargs["ciphers"]
            )
            session.mount("https://", adapter)
            session.adapter = adapter

        elif spoof_mode == "auto":
            spoof_session(session, **spoof_kwargs)

        else:
            logger.critical(f"unknown {spoof_mode=}")
            os._exit(0)

        url = "https://google.com"
        url = "https://bet365.es"
        url = "https://www.howsmyssl.com/a/check"
        try:
            response = session.request("GET", url)
            logger.debug(f"text={response.text}")
            logger.debug(f"{response=}")
        except Exception as exception:
            logger.error(exception)

        ciphers_list = session.adapter.ciphers.split(":")
        logger.info(f"have {len(ciphers_list)} ciphers: {ciphers_list}")

        """
        from https://hussainaliakbar.github.io/restricting-tls-version-and-cipher-suites-in-python-requests-and-testing-with-wireshark/
        """
        check_session(session)

    else:
        logger.critical(f"unknown {special=}")
