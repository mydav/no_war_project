from modules import *


def check_cloudflare_status(text):
    title = find_from_to_one("<title>", "</title>", text).strip()
    if (
        "<title>bet365 - Apuestas deportivas en la red</title>" in text
        or "<title>Bet with bet365" in text
        or """<Error><Message>The requested resource does not support http method 'GET'.</Message></Error>"""
        in text
        or title == "bet365"  # members login
    ):
        logger.info(f"SOLVED cloudflare")
        status = "solved"

    elif "used Cloudflare to restrict access</title>" in text:
        logger.critical(f"cloudflare BLOCK")
        status = "cloudflare_block"

    elif "<title>Attention Required! | Cloudflare</title>" in text:
        logger.critical(f"cloudflare CAPTCHA")
        status = "cloudflare_captcha"

    elif "error code: 1020" == text:
        status = "cloudflare_1020_wrong_headers"
        logger.critical(status)

    else:
        logger.warning(f"unknown cloudflare status for {text=}")
        # logger.critical(f"unknown status")
        status = "unknown"
    return status
