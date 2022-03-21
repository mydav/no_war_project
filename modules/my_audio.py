#!/usr/bin/python
# -*- coding: utf-8 -*-

import threading

try:
    import winsound
    from winsound import Beep, PlaySound
except Exception as er:
    print("ERROR: CAN NOT IMPORT winsound, er=%s" % er)
import os
import time
import logging


def inform_critical(message="", *args, **kwargs):
    kwargs["limit"] = 0
    kwargs["preffix"] = "inform_critical"
    kwargs["func_beep"] = "beep_wav"
    m = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

    logging.critical("inform_critical %s: %s" % (m, message))
    return inform_me(message, *args, **kwargs)


def inform_me_one(message="", *args, **kwargs):
    kwargs["limit"] = 1
    return inform_me(message, *args, **kwargs)


def inform_me(
    message="",
    limit=1000,
    duration=200,
    frequency=2500,
    name="",
    preffix="",
    func_beep=None,
):
    vars0 = locals()
    # print(vars0)

    if preffix:
        if message:
            print(preffix, message)
    else:
        if message:
            print(message)
    step = 0
    t_last_print = time.time()

    while True:
        life = time.time() - t_last_print

        step += 1
        want_print = True if step <= 1 else False
        beep(
            duration=duration,
            frequency=2500,
            name=name,
            func_beep=func_beep,
            want_print=want_print,
        )
        if limit and step >= limit:
            break

        if 0 and life > 10:
            t_last_print = time.time()
            # print(message),

        time.sleep(1)


def beep(
    duration=200,
    frequency=2500,
    name="",
    func_beep="async_beep_wav",
    debug=False,
    want_print=True,
):
    """
    Set Frequency To 2500 Hertz
    """
    fun = "beep"
    import winsound

    if func_beep == "beep_wav":
        func = beep_wav
    else:
        func = async_beep_wav

    if debug:
        logging.debug("%s func_beep=%s (%s)" % (fun, func_beep, func))

    try:
        # beep_wav(name=name)
        func(name=name)
    except Exception as er:
        print(er)
        try:
            winsound.Beep(frequency, duration)
        except Exception as er:
            if want_print:
                print(
                    "beeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeep "
                )
                print("%s %s " % (fun, er))
    # winsound.Beep()


def beep_wav(name=""):
    debug = False

    if name in ["no", "-", None]:
        if debug:
            print("no beep")

        return

    if name == "":
        name = "Alarm10"

    f_default = r"c:/windows/media/Alarm10.wav"

    if "." not in name:
        name = "%s.wav" % name

    f = r"c:/windows/media/%s" % name
    if not os.path.isfile(f):
        if debug:
            print("no file %s, get default file" % f)
        f = f_default

    if debug:
        print("play")
    # winsound.PlaySound(f, winsound.SND_ASYNC | winsound.SND_ALIAS)
    # winsound.PlaySound(f, winsound.SND_FILENAME)   # андрюхе нравится
    winsound.PlaySound(f, False)

    if debug:
        print("+played")

    # winsound.PlaySound('c:/windows/media/Chord.wav', winsound.SND_FILENAME | winsound.SND_ASYNC)
    # winsound.PlaySound('c:/windows/media/tada.wav', winsound.SND_FILENAME)
    # wait_for_ok()
    # winsound.PlaySound('SystemQuestion', winsound.SND_ALIAS)


def async_beep_wav(*args, **kwargs):
    fun = "async_beep_wav"
    # print '%s' % fun, args
    d = threading.Thread(target=beep_wav, args=args, kwargs=kwargs)
    # d = threading.Thread(target=beep_wav)
    d.daemon = True
    d.start()
    # print '+'


if __name__ == "__main__":
    inform_me_one("done")
    # inform_critical("hello")
    time.sleep(10)
