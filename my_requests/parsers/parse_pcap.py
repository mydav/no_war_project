from modules import *
from collections import OrderedDict
import pyshark
import pprint

logger = get_logger(__name__)


def read_as_json(f, display_filter="", stream_number=""):
    fun = "read_as_json"
    if not display_filter:
        if stream_number:
            display_filter = f"tcp.stream eq {stream_number}"

    kwargs = {
        # 'only_summaries': True,
        # 'keep_packets': False,
        # 'use_json': True,
        # 'include_raw': True,
    }
    logger.debug(f"[{fun}: {display_filter=} for {f=}")
    cap = pyshark.FileCapture(f, display_filter=display_filter, **kwargs)
    cap.set_debug()
    # cap = pyshark.FileCapture(f)
    logger.debug(f"size {len(cap)}, {cap=}")
    print(cap)

    t = 1
    if t:
        logger.warning("debug first cap")
        t_start = time.time()
        pkt = cap[0]
        duration = time.time() - t_start
        print(f"full packet: {pkt}")
        logger.debug(f"{dir(pkt)=}")
        logger.debug(f"{pkt.highest_layer=}")
        logger.debug(
            f"Stream Index: {pkt.tcp.stream}"
        )  # to print stream index at the start
        logger.debug(f"HTTP LAYER: {pkt.http}")
        logger.debug(f"{dir(pkt.http)}")
        logger.debug(f"done in {get_human_duration(duration)} seconds")

        logger.info(f"all keys:")
        for k in dir(pkt.http):
            logger.debug(f"{k=}")
            value = getattr(pkt.http, k)
            logger.debug(f"    {value}")
        # print(pkt.http)

    logger.debug(f"stream = {pkt.tcp.stream}")
    t = 0
    if t:
        ol_arr = []
        logger.debug(f"{pkt.tcp._all_fields}")
        for x in pkt.tcp._all_fields.values():
            if x.name == "tcp.option_len":
                print(x.all_fields)
                for k in x.all_fields:
                    print(k.get_default_value())
                    ol_arr.append(k.get_default_value())
                break
        logger.info(f"{ol_arr=}")

    t = 1
    if t:
        logger.debug(f"{pkt.ip}")

    # wait_for_ok()

    t = 0
    if t:
        logger.debug("start reading 2...")
        num = 0
        real_num = 0
        for packet in cap:
            num += 1
            if 0 and num < 25:
                continue
            # adjusted output
            t = 1
            if t:
                # Getting a list of all fields of this packet on the level of this specific layer
                # looking somthing like this :['fc_frag', 'fc_type_subtype',..., 'fc_type']
                logger.debug(f"{num=} {packet=}")

            try:
                # get timestamp
                localtime = time.asctime(time.localtime(time.time()))

                # get packet content
                protocol = packet.transport_layer  # protocol type
                src_addr = packet.ip.src  # source address
                src_port = packet[protocol].srcport  # source port
                dst_addr = packet.ip.dst  # destination address
                dst_port = packet[protocol].dstport  # destination port

                # output packet info
                real_num += 1
                logger.debug(
                    f"{real_num}/{num} {localtime} IP {src_addr}:{src_port} <-> {dst_addr}:{dst_port} ({protocol})"
                )
            except AttributeError as e:
                # ignore packets other than TCP, UDP and IPv4
                pass
        wait_for_ok()

    t = 0
    if t:
        logger.debug(f"start reading 2...")
        step = 0
        while True:
            step += 1
            if step % 100 == 0:
                logger.debug(f"{step=}")
            else:
                print(f"{step=}", end=" ")

            try:
                p = cap.next()
            except StopIteration:  # Reached end of capture file.
                break

            print(f"data={p.data}")
            try:
                # print data from the selected stream
                print(f"{step=} data={p.data.data.binary_value}")
            except Exception as er:  # Skip the ACKs.
                error = str(er)
                if 0 or "No attribute named data" in error:
                    pass
                else:
                    logger.error(f" {er=}")
        wait_for_ok("finished 1")

    t = 0
    if t:
        logger.debug(f"get sess_index...")
        sess_index = []  # to save stream indexes in an array
        num = 0
        for pkt in cap:
            num += 1
            logger.debug(f"{num=}")
            if num % 100 == 0:
                print(f"{num}", end=" ")
            try:
                sess_index.append(pkt.tcp.stream)
            except Exception as er:
                pass

        logger.debug(f"+{sess_index=}")
        if len(sess_index) == 0:
            max_index = 0
            logger.warning("No TCP Found")
        else:
            max_index = (
                int(max(sess_index)) + 1
            )  # max function is used to get the highiest number

        logger.debug(f"{max_index=}")

        for session in range(0, max_index):
            for pkt in cap:
                try:
                    logger.debug(f"{pkt.tcp.stream} {pkt.http=}")
                    if int(pkt.tcp.stream) == session:
                        pass
                        if pkt.http > 0:
                            logger.debug(
                                f"Stream Index: {pkt.tcp.stream}"
                            )  # to print stream index at the start
                            logger.debug(f"HTTP LAYER: {pkt.http}")
                except Exception as er:
                    pass
        cap.close()
    return pkt


def explore_pyshark():
    logger.debug(f"[explore_pyshark: ")
    capture = pyshark.LiveCapture(interface="eth0")
    logger.debug(f"start capturing...")
    for packet in capture.sniff_continuously(packet_count=5):
        logger.debug(f"{packet=}")


def explore_tshark(f):
    """
    "c:\Program Files\Wireshark\tshark.exe" -r "s:\!kyxa\!code\!documentation\py4seo\advanced\08\dor_minimum\my_requests\data\pcap\http.cap" -O http

    flags:
        -n flag to get it not to do DNS lookups in that case.
    """
    f_exe = r"c:\Program Files\Wireshark\tshark.exe"
    cmd = (
        f'" "{f_exe}" -r "{f}" -n -O http '
        f'-Y "http.request || http.response" "'
    )  # display filters https://wiki.wireshark.org/DisplayFilters
    logger.debug(f"{cmd=}")
    os.system(cmd)


def prepare_request_from_text(txt=""):
    """
    Hypertext Transfer Protocol
    GET /download.html HTTP/1.1\r\n
        [Expert Info (Chat/Sequence): GET /download.html HTTP/1.1\r\n]
            [GET /download.html HTTP/1.1\r\n]
            [Severity level: Chat]
            [Group: Sequence]
        Request Method: GET
        Request URI: /download.html
        Request Version: HTTP/1.1
    Host: www.ethereal.com\r\n
    User-Agent: Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.6) Gecko/20040113\r\n
    Accept: text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,image/jpeg,image/gif;q=0.2,*/*;q=0.1\r\n
    Accept-Language: en-us,en;q=0.5\r\n
    Accept-Encoding: gzip,deflate\r\n
    Accept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.7\r\n
    Keep-Alive: 300\r\n
    Connection: keep-alive\r\n
    Referer: http://www.ethereal.com/development.html\r\n
    \r\n
    [Full request URI: http://www.ethereal.com/download.html]
    [HTTP request 1/1]
    """
    url_start = "[Expert Info (Chat/Sequence):"
    rn = r"\r\n"

    url = ""
    first = find_from_to_one("Hypertext Transfer Protocol\n", rn, txt).strip()
    full_uri = find_from_to_one("[Full request URI: ", "]\n", txt)
    if not full_uri:
        full_uri = find_from_to_one("[Request URI: ", "]\n", txt)
    headers = OrderedDict()

    items = txt.split("\n")
    for item in items:
        item = item.strip()
        if item.startswith(url_start) and rn in item:
            logger.debug(f"{item=}")
            url = find_from_to_one(url_start, rn, item).strip()

        if 0:
            pass
        elif item.endswith(rn):
            k = find_from_to_one("nahposhuk", ":", item).strip()
            if k:
                v = find_from_to_one(":", rn, item).strip()
                headers[k] = v

    res = {
        "first": first,
        # 'url': url,
        "full_uri": full_uri,
        # 'headers': headers,
    }
    return res


if __name__ == "__main__":
    f = r"s:\!kyxa\!code\!documentation\py4seo\advanced\08\dor_minimum\my_requests\data\pcap\android.pcap"
    f = r"s:\!kyxa\!code\!documentation\py4seo\advanced\08\dor_minimum\my_requests\data\pcap\http.cap"
    special = "get_requests_to_replay"
    special = "explore_pyshark"
    special = "read_as_json"
    special = "explore_tshark"
    special = "prepare_request_from_text"

    if special == "explore_pyshark":
        explore_pyshark()

    elif special == "prepare_request_from_text":
        f = r"s:\!kyxa\!code\!documentation\py4seo\advanced\08\dor_minimum\my_requests\data\pcap\response_headers.txt"
        f = r"s:\!kyxa\!code\!documentation\py4seo\advanced\08\dor_minimum\my_requests\data\pcap\request_headers.txt"
        txt = text_from_file(f)
        r = prepare_request_from_text(txt)
        logger.info(f"final {pretty_dict(r)}")

    elif special == "explore_tshark":
        r = explore_tshark(f)
        logger.info(f"final {r=}")

    elif special == "read_as_json":
        kwargs = {
            # "stream_number": 17,
            "stream_number": "",
            "display_filter": "http",
        }
        pkt = read_as_json(f, **kwargs)
        # explore_bet365_har(har)

    # elif "get_requests_to_replay":
    #     to_replay = get_requests_to_replay(f)
    #     logger.info(f"{len(to_replay)} {to_replay=}")

    else:
        logger.error(f"unknown {special=}")
