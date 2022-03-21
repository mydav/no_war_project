from modules import *
from modules.logging_functions import *
import json
from collections import OrderedDict

logger = get_logger(__name__)


def get_requests_to_replay_from_har(
    har_file, searching=None, debug: bool = False
):
    fun = "get_requests_to_replay_from_har"
    searching = get_searching_filter(searching)
    har = read_har_as_json(har_file)
    important_entries = find_har_entries(har, searching=searching, debug=debug)
    logger.debug(
        f"{fun}: found {len(important_entries)} entries for {searching=} to replay"
    )
    # wait_for_ok()
    all_replay = []
    for entry in important_entries:
        to_replay = prepare_request_from_har_entry(entry)
        all_replay.append(to_replay)
        if debug:
            logger.debug(f" {to_replay=}")
    return all_replay


def read_har_as_json(har_file):
    with open(har_file, encoding="utf-8") as f:
        har_txt = json.loads(f.read())
    return har_txt


def explore_bet365_har(har, debug: bool = False):
    keys = har["log"].keys()
    logger.info(f"{type(har)=}")
    logger.debug(f"{keys=}")
    entries = har["log"]["entries"]
    logger.debug(f"have {len(entries)} entries")
    for num_entry, entry in enumerate(entries, 1):
        request = entry["request"]
        url = request["url"]
        method = request["method"]
        logger.debug(f"{num_entry}/{len(entries)} {method: >7} {url}")

        if url in ["https://members.bet365.es/members/lp/default.aspx"]:
            prepared = prepare_request_from_har_entry(entry)
            break

    searching = get_searching_filter()
    important_entries = find_har_entries(har, searching, debug=debug)
    for entry in important_entries:
        to_replay = prepare_request_from_har_entry(entry)
        logger.debug(f"{to_replay=}")


def find_har_entries(har, searching={"url": []}, debug: bool = False):
    """фильтр - урл должен быть один из url"""
    fun = "find_har_entries"
    good_entries = []
    entries = har["log"]["entries"]
    if debug:
        logger.debug(f"[{fun}: have {len(entries)} entries, {searching=}")
    url_searching = searching.get("url", [])
    for num_entry, entry in enumerate(entries, 1):
        request = entry["request"]
        url = request["url"]
        method = request["method"]
        if debug:
            logger.debug(f"{num_entry}/{len(entries)} {method: >7} {url}")

        # filtering
        skip_reason = ""
        while True:
            if url_searching:
                found = False
                for _ in url_searching:
                    if _ in url:
                        found = True
                        break
                if not found:
                    skip_reason = f"url not in url_searching"
                    break

            break

        if skip_reason:
            if debug:
                logger.debug(f"     {skip_reason=} for {url=}")
            continue
        good_entries.append(entry)
    if debug:
        logger.debug(f"   +{len(good_entries)}/{len(entries)} good entries]")
    return good_entries


def prepare_request_from_har_entry(entry, debug: bool = False):
    request = entry["request"]
    url = request["url"]
    method = request["method"]
    headers = request["headers"]
    # show_list(headers)
    headers_dict = OrderedDict([(_["name"], _["value"]) for _ in headers])

    post_data = request.get("postData", {})
    data = post_data.get("text")

    res = {
        "url": url,
        "headers": headers_dict,
    }
    if data:
        res["data"] = data
    if debug:
        logger.debug(f"{pretty_dict(res)}")
    return res


def get_searching_filter(searching=None):
    if searching is None:
        searching = {
            "url": [
                # "BetsWebAPI/refreshslip",
                "/BetsWebAPI/addbet",
            ],
        }
    return searching


if __name__ == "__main__":
    har_file = r"s:\!kyxa\!code\!documentation\py4seo\advanced\08\dor_minimum\bet365_one_api\data\www.bet365.es_success_login.har"
    har_file = r"s:\!kyxa\!code\!documentation\py4seo\advanced\08\dor_minimum\bet365_one_api\data\www.bet365.es_refreshslip.har"
    special = "read_har_as_json"
    special = "get_requests_to_replay_from_har"

    if special == "read_har_as_json":
        har = read_har_as_json(har_file)
        explore_bet365_har(har)

    elif "get_requests_to_replay_from_har":
        to_replay = get_requests_to_replay_from_har(har_file)
        logger.info(f"{len(to_replay)} {to_replay=}")

    else:
        logger.error(f"unknown {special=}")
