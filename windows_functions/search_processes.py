#!/usr/bin/python
# -*- coding: utf-8 -*-
from modules import *

import subprocess


def check_active_by_port(port=6814):
    pid = get_pid_by_port(port)
    if pid:
        return pid
    else:
        return False


def get_pid_by_port(port="", debug=False, max_tries=10):
    """
    получаем pid процесса, который использует этот порт
    """
    # debug = True
    fun = "get_pid_by_port"
    port = str(port)
    t_start = time.time()
    ports = [port]

    cmd = ["netstat", "-lpn"]
    cmd = r"netstat -aon | findstr LISTENING | findstr :[port] ".replace(
        "[port]", str(port)
    )
    if debug:
        logger.debug("cmd %s" % cmd)
    mode = "check_output"
    if mode == "check_output":
        step = 0
        while True:
            step += 1
            if step > max_tries:
                m = "error %s - max_tries=%s reached" % (fun, max_tries)
                logger.critical(m)
                raise ValueError(m)
            try:
                data = subprocess.check_output(cmd, shell=True)
                break

            except Exception as er:
                error = str(er)
                if "returned non-zero exit status 1" in error:
                    data = ""
                    break

                logger.debug(f"ERROR {fun} {step=} ({error=}, retry")
                # sleep_(1)

                continue
            # pids = subprocess.Popen([cmd], stdout=subprocess.PIPE).communicate()
    else:
        popen = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE)
        (data, err) = popen.communicate()

    if debug:
        logger.debug("data: %s" % data)

    if data:
        # data = str(data)
        data = data.decode("utf-8")

    found_pid = ""
    for line in data.split("\n"):
        line = line.strip()
        if not line:
            continue
        #   TCP    0.0.0.0:60856          0.0.0.0:0              LISTENING       14816
        pid_port = find_from_to_one(":", " ", line)
        items = line.split(" ")
        # show_list(items)
        pid = items[-1].strip()
        if debug:
            logger.debug(
                "  pid_port=%s, pid=%s, line=%s" % (pid_port, pid, line)
            )

        if pid_port == port:
            found_pid = pid
            break

        continue

    if found_pid:
        found_pid = int(found_pid)

    if 0 or debug:
        duration = time.time() - t_start
        logger.debug(
            "done (pid=%s for port %s) in %.2f seconds"
            % (found_pid, port, duration)
        )

    return found_pid


def parse_tasklist(debug=False):
    fun = "parse_tasklist"
    t0 = time.time()
    t = 0
    if t:
        cmd = "tasklist /V"
        cmd = "tasklist"
        r = os.system(cmd)
        return r
    else:
        # output = check_output(['tasklist'])
        output = subprocess.Popen(
            ["tasklist"], stdout=subprocess.PIPE
        ).communicate()[0]
        if debug:
            logger.debug("output=%s" % output)

        # wait_for_ok()
        # tasks = output.splitlines()
        spliter = "\n\r"
        spliter = "\n"
        spliter = "\r\n"
        output = output.decode("cp866")
        if debug:
            logger.debug("output=%s" % output)

        tasks = output.split(spliter)
        # logger.debug('tasks=%s' % tasks)
        processes = []
        for task in tasks:
            # m = re.match("(.+?) +(\d+) (.+?) +(\d+) +(\d+.* K).*",task)
            m = re.match("(.+?) +(\d+) (.+?) +(\d+) +(\d+.*).*", task)
            if m is None:
                continue

            mem_usage = m.group(5)
            # mem_usage = mem_usage.replace("\xa0", "").replace(" K", "000")
            try:
                mem_usage = int(mem_usage)
            except Exception as er:
                logger.error("mem_usage %s not int" % mem_usage)

            processes.append(
                {
                    "image": m.group(1),
                    "pid": int(m.group(2)),
                    "session_name": m.group(3),
                    "session_num": m.group(4),
                    "mem_usage": mem_usage,
                }
            )

        seconds = time.time() - t0
        logger.debug(
            "[%s found %s processes in %.2f seconds]"
            % (fun, len(processes), seconds)
        )
        return processes


if __name__ == "__main__":
    special = "parse_tasklist"
    special = "get_pid_by_port"

    if special == "parse_tasklist":
        lst = parse_tasklist()
        show_list(lst)

    elif special == "get_pid_by_port":
        ports_txt = """
        # 60
        # 6004
        # 56004
        # 6472
        # 57763
        # 6077
        # 6814
        55606
        55555
        """
        ports = clear_list(ports_txt, bad_starts="#")
        for port in ports:
            debug = False
            pid = get_pid_by_port(port, debug=debug)
            active = check_active_by_port(port)
            logger.debug(f"{port=}, {pid=} {active=}")

        os._exit(0)

    else:
        logger.error("unknown special=%s" % special)
