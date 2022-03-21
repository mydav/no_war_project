#!/usr/bin/python
# -*- coding: utf-8 -*-

import time

"""Для того чтобы и long и int определялись как int"""
from builtins import int

from modules import *

print("windows_funcs start...")
print(1)

logger = get_logger(__name__)

import getpass

# для
try:
    import win32process
    from win32com.client import GetObject

    import pywinauto
    from pywinauto import application
    from pywinauto.application import Application
    import pywinauto.handleprops as _handleprops
    import pywinauto.win32functions as _win32functions
    import win32api, win32con
    import win32gui
    import win32ui

except Exception as er:
    logger.error(f"can not import modules, {er=}")

print(2)

import math

import ctypes
import subprocess

# import pyautogui
# from subprocess import check_output

# from my_machine_learning import statistic_functions as ML
print(3)


t = 1
t = 0
if t:
    try:
        import my_machine_learning as ML
    except Exception as er:
        logger.error("error %s" % er)

logger.debug("main of %s" % __file__)

# get_window_title = ctypes.windll.user32.GetWindowTextW


def handle_close(handle):
    win32gui.PostMessage(handle, win32con.WM_CLOSE, 0, 0)


def handle_close_nah(handle):
    logger.debug("	kill handle %s" % handle)
    closed = 0

    pwa_app = pywinauto.application.Application()
    window = pwa_app.window_(handle=handle)
    try:
        window_close(window)
        closed = 1
        logger.debug("+")
    except Exception as er:
        logger.error("ERROR %s: %s" % (fun, er))

    return closed


def window_close(window):
    fun = "window_close"
    i = 0
    while True:
        i += 1
        if i > 10:
            return 0
        try:
            window.close()
            return 1
        except Exception as er:
            logger.error("%s ERROR_%s:" % (fun, i))
            error = str(er)
            pr("%s" % error)

            if (
                error.find("is not a vaild window handle") != -1
                or error.find("window handle") != -1
            ):
                return 1
            sleep_(3)


def get_cursor_pos():
    """
        позиции курсора найти
    """
    fun = "w_current"
    step = 0
    while True:
        step += 1
        try:
            current = win32api.GetCursorPos()
            break
        except Exception as er:
            logger.error("error %s step %s: %s" % (fun, step, er))

    return current


def move_mouse(x, y):
    """
        движение мышки полюбе
    """
    fun = "move_mouse"
    step = 0
    while True:
        step += 1
        try:
            win32api.SetCursorPos((x, y))
            w_setcursor(x, y)  # надо?
            break
        except Exception as er:
            logger.error("error %s step %s: %s" % (fun, step, er))

    return 1


def w_setcursor(x, y):
    # ставим курсор - сюда. По настоящему.
    # http://stackoverflow.com/questions/3720938/win32-moving-mouse-with-setcursorpos-vs-mouse-event

    # win32api.SetCursorPos((x,y)) is better to be replaced by win32api.mouse_event(win32con.MOUSEEVENTF_MOVE | win32con.MOUSEEVENTF_ABSOLUTE, int(x/SCREEN_WIDTH*65535.0), int(y/SCREEN_HEIGHT*65535.0)) in my experience for better integration with other application such as games. – Falcon May 31 '12 at 18:59

    t = 0
    if t:
        move_mouse(x, y)
    else:
        nx = x * 65535 / win32api.GetSystemMetrics(0)
        ny = y * 65535 / win32api.GetSystemMetrics(1)
        win32api.mouse_event(
            win32con.MOUSEEVENTF_ABSOLUTE | win32con.MOUSEEVENTF_MOVE, nx, ny
        )


def window_move_points(points=[]):
    # двигаемся по точкам - контуры обводим
    fun = "window_move_points"
    i = 0
    for point in points:
        i += 1
        x, y = get_cursor_pos()
        # sx, sy = cx, cy
        new_x, new_y = point
        # logger.debug(str(['		', fun, i, new_x, new_y]))
        easingAmount = 1  # очень быстро
        easingAmount = 0.0005
        easingAmount = 0.00005  # медленно
        window_cursor_line(x, y, new_x, new_y, easingAmount=easingAmount)


def window_move_along_borders(x0, y0=0, x1=0, y1=0, seconds=5):
    """
    x0 может быть [x1, y1, x2, y2]
    движем по краям прямоугольника
    """
    if type(x0) == type([]):
        x0, y0, x1, y1 = x0[:]

    points = [
        [x0, y0],
        [x1, y0],
        [x1, y1],
        [x0, y1],
        [x0, y0],
    ]
    window_move_points(points)


def window_move_mouse_in_rectangle(x0, y0, x1, y1, seconds=5):
    # движем мышку в рандомные клетки rect нужное время

    start = time.time()
    last = time.time()
    i = 0
    while True:
        i += 1

        current = time.time()
        full = current - start
        tick = current - last

        if full > seconds:
            break

        last = current

        x, y = get_cursor_pos()
        # sx, sy = cx, cy
        new_x = randint(x0, x1)
        new_y = randint(y0, y1)
        logger.debug(str(["   ", i, new_x, new_y]))
        easingAmount = 1
        easingAmount = 0.00005
        window_cursor_line(x, y, new_x, new_y, easingAmount=easingAmount)
    # sleep_(1)


def window_cursor_line(cx, cy, mx, my, seconds=2, easingAmount=0.05):
    # движем курсор от х к у
    # http://gamedevelopment.tutsplus.com/tutorials/quick-tip-smoothly-move-an-entity-to-the-position-of-the-mouse--gamedev-7356 - описание алгоритма
    # https://processing.org/examples/easing.html
    # easingAmount = 0.05
    # easingAmount *= 0.5
    sx, sy = cx, cy
    w_setcursor(cx, cy)

    # https://gist.github.com/phoboslab/2998372
    distance = math.sqrt((mx - cx) * (mx - cx) + (my - cy) * (my - cy))
    # logger.debug('distance: %s' % distance)
    # wait_for_ok()

    start = time.time()
    last = time.time()

    t = 1
    if t:
        i = 0
        while True:
            i += 1
            # if i>100:
            if i > 1000 * 1000:
                break

            current = time.time()
            full = current - start
            tick = current - last

            # if full>seconds:
            # 	break

            last = current

            xDistance = mx - cx
            yDistance = my - cy
            distance = math.sqrt(xDistance * xDistance + yDistance * yDistance)
            if distance > 1:
                cx += xDistance * easingAmount
                cy += yDistance * easingAmount
            else:
                break

            # if full>2:
            # 	logger.debug(str(['	', distance, cx, cy]))

            w_setcursor(cx, cy)

    t = 0
    if t:
        vx = 300
        vy = 100

        while True:
            # if win32api.GetAsyncKeyState(ord('Q')):
            # 	sys.exit()

            current = time.time()
            full = current - start
            tick = current - last
            if full > 5:
                os._exit(0)

            last = current
            if mx > 0:
                cx += vx * tick
                if cx > mx + sx or cx < sx:
                    vx = -vx
                    cx = max(sx, min(mx + sx, cx))
            if my > 0:
                cy += vy * tick
                if cy > my + sy or cy < sy:
                    vy = -vy
                    cy = max(sy, min(my + sy, cy))
            w_setcursor(cx, cy)
            time.sleep(0.001)
            pass


def windows_click(x, y, clicks=1):
    """
        клик в точке
    """
    # или http://stackoverflow.com/questions/1181464/controlling-mouse-with-python

    fun = "windows_click"
    logger.debug("[%s" % fun)

    t = 1
    t = 0
    sposob = "down_up"
    sposob = "left_click"
    # sposob = 'pyautogui'#не смог установить

    for i in range(clicks):
        w_setcursor(x, y)

        if sposob == "down_up":
            # win32api.SetCursorPos((x,y)) is better to be replaced by win32api.mouse_event(win32con.MOUSEEVENTF_MOVE | win32con.MOUSEEVENTF_ABSOLUTE, int(x/SCREEN_WIDTH*65535.0), int(y/SCREEN_HEIGHT*65535.0))
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

        elif sposob == "left_click":
            ctypes.windll.user32.mouse_event(2, 0, 0, 0, 0)
            # sleep_(1)
            ctypes.windll.user32.mouse_event(4, 0, 0, 0, 0)

        elif sposob == "pyautogui":
            pyautogui.click(x, y)

    logger.debug("+%s]" % fun)


def text_to_pywinauto(t):
    repl = {
        "+": "{+}",
        #':':'{:}',
        #'/':'{/}',
        "%": "{%}",
        "^": "{^}",
        "(": "{(}",
        ")": "{)}",
        "[": "{[}",
        "]": "{]}",
    }
    t = no_probely(t, repl, 1)
    return t


def pwa_tvvod(htmlpres, window="", title="save_as"):
    fun = "pwa_tvvod"
    logger.debug("	%s:%s" % (fun, htmlpres))
    htmlpres = str(htmlpres)

    window = pwa_get_real_window(window, title)
    pwa_mySetFocus(window)  # TypeError: The object is not a PyHANDLE object

    r = window.type_keys(htmlpres, with_spaces=True)
    # window.TypeKeys(htmlpres, with_spaces = True, set_foreground=True)

    # def pwa_mySetFocus_handle(handle):
    # 	win32gui.SetForegroundWindow(handle)
    # 	win32gui.SetActiveWindow(handle)
    return r


def pwa_get_real_window(window="", title="save_as"):
    fun = "pwa_get_real_window"
    if type(window) == type(123):  # значит случайно отправил хендл
        window = pwa_handle_to_window(window)

    if window in ["", 0]:
        # window =
        # app = Application().Connect(title=u'\u0421\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c \u043a\u0430\u043a', class_name='#32770')
        # app = Application().Connect(title=u'Сохранить как')
        # window = app.Dialog

        if title == "save_as":
            title = ["Сохранение", "Сохранить как", "Save As"]

        window = pwa_find_window(title)
        if window == 0:
            window = pwa_find_window(title, 0, 1)

    logger.debug("	%s window: %s %s" % (fun, type(window), window))
    return window


def pwa_mySetFocus_by_pid(pid=""):
    fun = "pwa_mySetFocus_by_pid"
    try:
        t_start = time.time()
        # from pywinauto import Application
        app = Application().connect(process=pid)
        window = app.top_window()
        pwa_mySetFocus(window)
        duration = time.time() - t_start
        logger.debug(
            f"+pwa_mySetFocus_by_pid {pid=} in {duration:.2f} seconds"
        )
    except Exception as er:
        logger.error("ERROR %s: %s" % (fun, er))


def pwa_mySetFocus(window):
    fun = "pwa_mySetFocus"
    try:
        # return
        # chromium_on_top()
        window.set_focus()
        # pywinauto.win32functions.SetForegroundWindow(window)
        pass

    # window = app.top_window_()
    # window.SetFocus()
    # window.TypeKeys("{TAB 2}")
    # window.Click()
    except Exception as er:
        logger.error(f"ERROR {fun}: {er=}")


def pwa_mySetFocus0(window):
    """Set the focus to this control

    Activate the window if necessary"""

    fun = "mySetFocus"
    logger.debug("[%s" % fun)
    logger.debug("%s %s" % (window, type(window)))

    # find the current foreground window
    cur_foreground = get_foreground_handle()

    # if it is already foreground then just return
    if window.handle != cur_foreground:

        # get the thread of the window that is in the foreground
        cur_fore_thread = win32process.GetWindowThreadProcessId(cur_foreground)

        # get the thread of the window that we want to be in the foreground
        control_thread = win32process.GetWindowThreadProcessId(window)

        # if a different thread owns the active window
        if cur_fore_thread != control_thread:
            # Attach the two threads and set the foreground window
            win32process.AttachThreadInput(
                cur_fore_thread, control_thread, True
            )

            win32process.SetForegroundWindow(window)

            # detach the thread again
            win32process.AttachThreadInput(
                cur_fore_thread, control_thread, False
            )

        else:  # same threads - just set the foreground window
            win32process.SetForegroundWindow(window)

        # make sure that we are idle before returning
        win32process.WaitGuiThreadIdle(window)

        # only sleep if we had to change something!
        time.sleep(0.06)

    return window


def window_maximize(handle):
    """
        делаем окно большим
        https://stackoverflow.com/questions/2790825/how-can-i-maximize-a-specific-window-with-python
    """
    win32gui.ShowWindow(handle, win32con.SW_MAXIMIZE)


def window_activate(handle):
    """
        активация окна когда я знаю его хендл
    """
    fun = "window_activate"
    debug = False
    status = 0

    sposob = "pwa_mySetFocus"
    sposob = "new"
    sposob = "SetForegroundWindow"

    if debug:
        logger.debug("[%s %s, sposob %s" % (fun, handle, sposob))

    er = ""
    if sposob == "new":
        # https://stackoverflow.com/questions/11914152/how-to-send-the-tab-button-using-python-in-sendkey-and-pywinauto-modules
        try:
            window = pwa_handle_to_window(handle, "window")
            window.DrawOutline()  # Highlight the window
            window.Click()
            window.SetFocus()
            window.Click()

            status = 1
        except Exception as er:
            logger.error("error %s" % er)
            pass

    elif sposob == "SetForegroundWindow":
        # иногда не получается у него активировать окно. А иногда все супер...
        try:
            # https://www.blog.pythonlibrary.org/2014/10/20/pywin32-how-to-bring-a-window-to-front/
            win32gui.ShowWindow(handle, 5)
            win32gui.SetForegroundWindow(handle)

            main_window = get_foreground_handle()
            if debug:
                logger.debug("main_window %s" % main_window)
            status = 1
        # sleep_(1)
        except Exception as er:
            logger.error(f"ERROR {fun}: {er=}")
            sleep_(1)

    # sleep_(10)

    elif sposob == "pwa_mySetFocus":
        want_try = 0
        if not want_try:
            window = pwa_handle_to_window(handle)
            pwa_mySetFocus(window)
            status = 1
        else:
            try:
                window = pwa_handle_to_window(handle)
                pwa_mySetFocus(window)
                status = 1
            except Exception as er:
                logger.error("ERROR %s: %s" % (fun, er))

    else:
        wait_for_ok("unknown sposob %s" % sposob)

    er = str(er)
    if (
        er.find("not found") != -1
        or er.find("(1400, 'SetForegroundWindow'") != -1
    ):
        er = "not_found"

    if debug:
        logger.debug("%s]" % status)
    return status, er


def window_activate_polube(handle):
    """
        активируем и проверяем что активировано
    """
    fun = "window_activate_polube"
    status = 1
    er = ""

    step = 0
    while True:
        step += 1
        error = 0

        status, er = window_activate(handle)

        if not status:
            logger.error('	 error %s: "%s"' % (fun, er))
            error = 1

        if er.find("not_found") != -1:
            status = 0
            er = "not_found"
            break

        if not error:
            # проверяем - действительно оно активировано?
            properties = window_handle_get_properties(handle)
            if (
                properties["w_clientrectangle"] == 0
                or properties["h_clientrectangle"] == 0
            ):
                error = 1

        if error:
            logger.error(
                "	%s handle %s not activated %s" % (fun, handle, step)
            )
            sleep_(1)
            continue

        break

    # wait_for_ok('activated?')
    return status, er


def pwa_enter(htmlpres="", window0="", default_window="", sleep=-1):
    # старая - enter_with_pywinauto
    fun = "pwa_enter"

    logger.debug("			[%s %s" % (fun, htmlpres))

    if type(htmlpres) != type([]):
        htmlpres = [htmlpres]

    htmlpres = map(str, htmlpres)

    for want in htmlpres:
        if window0 == "":
            if default_window == "":
                default_window = find_chrome_window()

            window = default_window
        else:
            window = window0
        pwa_tvvod(want, window)
        # time.sleep(0.2*1)
        if sleep == -1:
            cnt = randint(5, 10)
            sleep = 0.2 * cnt
        time.sleep(sleep)


def pwa_send_all_values(task={}):
    # все вводим в окно
    # id_to_value.append(	{'tip':'input', 'id':'Edit5', 'value':T.ip} )
    # id_to_value.append(	{'tip':'click', 'id':u'Старт'} )
    fun = "pwa_send_all_values"
    d = {
        "id_to_value": [],
        "window": 0,
        "sleep": 0,  # сколько спим
    }
    task = add_defaults(task, d)
    T = Bunch(task)

    logger.debug("[%s " % fun)
    i = 0
    for t in T.id_to_value:
        i += 1
        logger.debug("	%s/%s %s" % (i, len(T.id_to_value), t))
        tip = t.get("tip", "input")
        id = t.get("id", 0)
        value = t.get("value", "")

        if tip == "input":
            tedit = T.window[id]
            tedit.SetFocus()
            pwa_enter(value, tedit, sleep=T.sleep)

        elif tip == "click":
            tbutton = T.window[id]
            tbutton.Click()

        else:
            wait_for_ok("%s - unknown tip" % fun)

    logger.debug("+%s clicked all]" % fun)
    return 1


# wait_for_ok()


def pwa_find_windows_one(title, handle=0, title_re=""):
    # ищем все окна
    fun = "pwa_find_windows_one"
    logger.debug('		[%s with title "%s"' % (fun, title))

    if title != "" and type(title) != type("unicode"):
        title = unicode(title, "utf8")

    # logger.debug('title: %s %s' % ( type(title), title ) )
    logger.debug("title=%s, title_re=%s" % (title, title_re))
    # wait_for_ok()

    if title_re:
        w_handles = pywinauto.findwindows.find_windows(
            title_re=title, top_level_only=True, visible_only=True,
        )
    else:
        w_handles = pywinauto.findwindows.find_windows(
            title=title,
            # top_level_only = True,
            # visible_only = True,
        )

    logger.debug("%s found %s handles]" % (fun, len(w_handles)))

    if handle:
        all_windows = w_handles[:]

    else:
        all_windows = []
        for w_handle in w_handles:
            window = pwa_handle_to_window(w_handle)
            all_windows.append(window)

    # return w_handles
    # else:
    # 	try:
    # 		w_handles = pywinauto.findwindows.find_windows(title_re=title,
    # 			top_level_only = True,
    # 			visible_only = True,
    # 				)
    # 		logger.debgu(len(w_handles))
    # 		wait_for_ok(fun)
    # 		w_handle = w_handles[0]
    # 		#w_handle = pywinauto.findwindows.find_windows(title=title)[0]
    # 		#logger.debug('%s: found window' % fun)
    # 		if handle:
    # 			return w_handle
    # 	except Exception as er:
    #   logger.error('%s: error, no window with title_re "%s" er=%s' % (fun, title, er))
    # 		return 0

    return all_windows


def find_handle_for_pid(pid):
    """
        есть pid, ищу окно
    """
    fun = "find_handle_for_pid"

    _ = {
        "pids": [pid],
    }
    windows = pwa_find_windows_with_titles(_)
    if len(windows) > 0:
        handle = windows[0]["handle"]
    else:
        handle = None
    logger.debug("  +[%s pid=%s handle=%s]" % (fun, pid, handle))
    return handle


def pwa_handle_to_window(w_handle, tip="window"):
    """
    handle to window
    """
    fun = "pwa_handle_to_window"
    logger.debug("[%s w_handle %s %s" % (fun, type(w_handle), w_handle))

    if type(w_handle) in [int]:  # int
        logger.debug("from_int_long")
        # w_handles = pywinauto.findwindows.find_windows(handle=w_handle)
        # logger.debug(w_handles)

        app = Application().connect(handle=w_handle)

        if tip == "window":
            # logger.debug('app %s' % app)
            # window = app.window_()
            window = app.top_window()

        elif tip == "app":
            window = app

        else:
            wait_for_ok('%s ERROR - unnown tip "%s"' % (fun, ip))

    # pwa_app = pywinauto.application.Application()
    # window = pwa_app.window_(handle=w_handle)
    else:
        logger.debug("ups, from type %s so do not change" % type(w_handle))
        window = w_handle

    logger.debug(
        "[%s w_handle %s %s, window %s %s]"
        % (fun, type(w_handle), w_handle, type(window), window)
    )
    # wait_for_ok()
    return window


def pwa_find_window_one(title, handle=0, title_re=0):
    # ищем одно окошко
    fun = "pwa_find_window_one"
    r = pwa_find_windows_one(title, handle, title_re)
    if len(r) == 0:
        return 0
    return r[0]


def pwa_find_windows_(title, handle=0, title_re=0):
    try:
        w = pwa_find_windows_one(title, handle, title_re)
        return w
    except Exception as er:
        logger.error("error=%s" % er)

    return []


def pwa_find_window(title, handle=0, title_re=0):
    ws = pwa_find_windows(title, handle, title_re)
    if len(ws) > 0:
        return ws[0]
    else:
        return 0

    t = 0
    if t:
        try:
            w = pwa_find_window_one(title, handle, title_re)
            return w
        except Exception as er:
            logger.error(er)
        return 0


def pwa_find_windows(titles=[], handle=0, title_re=0):
    fun = "pwa_find_windows"
    # частично тайтл:
    # title = '.*AUTOPLINK'
    # windows = pwa_find_windows_one(title, handle=0, title_re=1)
    logger.debug('[%s with titles "%s"' % (fun, titles))

    if type(titles) != type(["lst"]):
        titles = [titles]

    windows = []
    for title in titles:
        ws = pwa_find_windows_(title, handle, title_re)
        for w in ws:
            if w not in windows:
                windows.append(w)
    logger.debug("%s %s windows]" % (fun, len(windows)))
    return windows


def pwa_find_windows_simple_and_re(title="", handle=0):
    """
        найти хендл, зная часть имени
        сначала пробуем простой поиск, потом через ре
    """
    fun = "pwa_find_windows_simple_and_re"
    # частично тайтл:
    # title = '.*AUTOPLINK'
    # windows = pwa_find_windows_one(title, handle=0, title_re=1)

    logger.debug('[%s with title "%s"' % (fun, title))

    t = 1
    if t:
        windows_info = pwa_find_windows_with_titles([title])
        handles = [_["handle"] for _ in windows_info]

        if handle:
            windows = handles[:]
        else:

            windows = [
                pwa_handle_to_window(handle, "window") for handle in handles
            ]

    # это старая версия - нах сейчас, она некорректно находит
    else:

        title_re = ".*%s.*" % title

        windows = pwa_find_windows(title, handle=handle, title_re=0)

    if len(windows) == 0:
        logger.warning(
            "no windows found with simple search, try to search with RE"
        )
        windows = pwa_find_windows(title_re, handle=handle, title_re=1)

    logger.debug("windows: %s" % windows)
    logger.debug("%s %s windows]" % (fun, len(windows)))
    return windows

    # тут я думал сделать через хитрокласс, но проще поискать вручную как выше
    t = 0
    if t:

        _ = {
            "title": title_re,
            "title_re": 1,
        }
        tasks = [
            _,
        ]
        _ = {
            "tasks": tasks,
            "close_all": 0,
            "return_found_windows": 1,
        }
        closer = close_bad_windows_class(_)
        programs = closer.close()
        logger.debug("programs: %s" % programs)


def pwa_find_windows_with_titles(task={}):
    """
        есть список тайтлов который мне подходит. Нужно найти все их процессы.
    """
    fun = "pwa_find_windows_with_titles"
    task = hitro_dict(task, "titles")

    d = {
        "titles": [],
        "titles_exact": [],
        "pids": [],  # если есть идс - проверяем и их
        "otl": 0,
        "otl": 1,
    }
    task = add_defaults(task, d)
    T = Bunch(task)

    otl = T.otl

    if otl:
        logger.debug("[%s" % fun)

    w_title_re = ".*"
    windows = pwa_find_windows(w_title_re, handle=1, title_re=1)

    if otl:
        logger.debug("all %s windows:" % len(windows))

    good_windows = []
    all_titles = []
    i = 0
    for handle in windows:
        i += 1
        # handle = windows[0]
        info = window_handle_to_info(handle)

        t = 1
        t = 0
        if t and i == 1:
            logger.debug("handle: %s" % handle)
            logger.debug("info:")
            show_dict(info)

        title = info["title"]
        all_titles.append(title)

        # проверка - подходит?
        good = 0
        while True:
            if T.titles != []:
                if text_from_list1_in_list2(T.titles, [title]) != False:
                    good = 1
                    break

            if T.titles_exact != []:
                if title in T.titles_exact:
                    good = 1
                    break

            if T.pids != []:
                if info["pid"] in T.pids:
                    good = 1
                    break
            break

        if good:
            good_windows.append(info)

    if otl:
        text_to_file("\n".join(all_titles), "temp/all_titles_%s.txt" % fun)

    if otl:
        logger.debug("found %s windows]" % len(good_windows))

    return good_windows


def pwa_actions_on_windows(task={}):
    """
        есть список окон, над ними действия
    """
    fun = "pwa_actions_on_windows"
    task = hitro_dict(task, "actions")

    d = {
        "actions": [],  #'kill'
        "windows": [],
        "otl": 0,
        "otl": 1,
        "threadid": 0,
        "kill_handle": 0,
    }
    task = add_defaults(task, d)
    T = Bunch(task)

    otl = T.otl

    if otl:
        logger.debug("[%s" % fun)

    # если есть спец-задачи, что-то могу с ними сделать
    stat = {}  # подсчитываю сколько успехов-неуспеховj:w

    if "kill" in T.actions:
        if otl:
            logger.debug("killing %s windows" % len(T.windows))

        for window_info in T.windows:

            if T.kill_handle:
                pwa_app = pywinauto.application.Application()
                handle = window_info["handle"]

                handle_close(handle)
                continue

            pid = window_info["pid"]

            if T.threadid:
                pid = window_info["threadid"]

            ids_to_kill = [pid]

            for pid in ids_to_kill:
                logger.debug("	kill %s" % pid)
                killed = kill_with_id(pid, 0)
                # killed = 0
                if otl:
                    logger.debug("	killed %s, info %s" % (killed, window_info))

                dict_init(stat, ["kill", killed], 0)
                stat["kill"][killed] += 1

        # wait_for_ok()

    if otl:
        logger.debug("stat:")
        show_dict(stat)

    logger.debug("+%s]" % fun)

    return stat


def pwa_get_childs(window):
    # возвращаем всех детей
    fun = "pwa_get_childs"
    childs = window.Children()
    logger.debug("	%s - found %s childs]" % (fun, len(childs)))
    return childs


def pwa_texts_full(window):
    fun = "pwa_texts_full"
    try:
        props = window.GetProperties()
    except Exception as er:
        logger.error("	error %s: %s" % (fun, er))
        return ""

    texts = props["Texts"]
    items = []
    for t in texts:
        try:
            _ = t.encode("utf-8", "ignore")
        except Exception as er:
            _ = ""
        items.append(_)

    texts_full = "\n".join(items)
    t = 0
    if t:
        logger.debug("texts_full:")
        uni2(texts_full)
    return texts_full


class close_bad_windows_class:
    # закрываем все плохие окна

    # использование:
    # def close_bad_windows():
    # 	_ = {
    # 		'title' : 'nnCron',
    # 		'text_must_be':'Evaluation period has expired',
    # 	}

    # 	_2 = {
    # 		'title' : 'Mozilla Firefox',
    # 		'kill_after':60,
    # 		'kill_after':10,
    # 	}

    # 	tasks = [
    # 		#_,
    # 		_2,
    # 	]

    # 	_ = {
    # 		'tasks':tasks,
    # 		}
    # 	closing = close_bad_windows_class(_)
    # 	return closing
    # closing = close_bad_windows()
    # closing.close()

    def __init__(self, task={}):

        d = {
            "tasks": [],  # тут задачи входящие
            # у каждой задачи:
            # title имя задачи
            # text_must_be - какой текст должен быть в окне
            # kill_after - через сколько секунд после нахождения удалять
            "close_all": 1,  # если 0 - значит просто вывести эти проги
            "return_found_windows": 0,  # вернуть найденные окна?
            "id_to_seconds": {},
            "detailed": 0,
        }

        task = add_defaults(task, d)

        self.task = task
        self.id_to_seconds = task[
            "id_to_seconds"
        ]  # тут сохраняем все что было по времени
        self.detailed = task["detailed"]

    def close(self):
        fun = "close"
        T = Bunch(self.task)

        d_one_task = {
            "title": "",  # имя задачи
            "text_must_be": "",  # - какой текст должен быть в окне
            "kill_after": 0,  # - через сколько секунд после нахождения удалять
            "title_re": 0,  # через re ищем?
            "fun_check_window_title_is_good": None,
        }

        logger.debug("[%s" % fun)
        logger.debug("%s tasks" % len(T.tasks))
        logger.debug("id_to_seconds:")
        show_dict(self.id_to_seconds)

        # wait_for_ok()

        ids_start = self.id_to_seconds.keys()
        # logger.debug(keys_start=%s' % keys_start)
        # wait_for_ok()

        step = 0
        cnt_closed = 0
        all_found_windows = []
        while 1:
            ids_curent = []

            step += 1
            found = 0
            i = 0

            j = 0
            for task in T.tasks:
                j += 1
                logger.debug(
                    "	checking task %s/%s task %s" % (j, len(T.tasks), task)
                )
                task = add_defaults(task, d_one_task)
                R = Bunch(task)
                # wait_for_ok()

                i += 1

                logger.debug(
                    "\n" * 2
                    + "	step %s, %s/%s title: %s"
                    % (step, i, len(T.tasks), R.title)
                )
                all_windows = pwa_find_windows(
                    R.title, handle=1, title_re=R.title_re
                )
                logger.debug("found %s windows" % len(all_windows))
                # wait_for_ok()
                for num_handle, window_handle in enumerate(all_windows):
                    title = get_handle_title(window_handle)

                    if self.detailed:
                        try:
                            m = "	check %s/%s, handle %s, title `%s`" % (
                                num_handle + 1,
                                len(all_windows),
                                window_handle,
                                title,
                            )
                            logger.debug(m)

                        except Exception as er:
                            m = (
                                "	check %s/%s, handle %s, title impossible to print"
                                % (
                                    num_handle + 1,
                                    len(all_windows),
                                    window_handle,
                                )
                            )
                            logger.debug(m)

                    if (
                        R.fun_check_window_title_is_good is not None
                        and title is not None
                    ):
                        is_good = R.fun_check_window_title_is_good(title)
                        if self.detailed:
                            logger.debug(
                                "		is_good %s (checked with %s)"
                                % (is_good, R.fun_check_window_title_is_good)
                            )
                        if not is_good:
                            continue

                    close = 0

                    id = str(window_handle)

                    pwa_app = Application()
                    # window = pwa_get_window_for_app(pwa_app, handle=window_handle)

                    window = pwa_app.connect(handle=window_handle)

                    if window in [None, 0]:
                        if self.detailed:
                            logger.debug("		window is None, propusk")

                        continue

                    # logger.debug('window %s, id %s' % (window, id))
                    # wait_for_ok()

                    ids_curent.append(id)

                    # logger.debug('title: %s' % window.title_re)
                    # wait_for_ok()

                    if R.text_must_be != "":
                        texts_full = pwa_texts_full(window)

                        childs = pwa_get_childs(window)
                        for child in childs:
                            tf = pwa_texts_full(child)
                            if tf.find(R.text_must_be) != -1:
                                logger.debug("	found %s" % R.text_must_be)
                                close = 1
                                break
                        if not close:
                            # logger.debug('	propusk, not found %s' % R.text_must_be)
                            pass

                    elif R.kill_after != 0:
                        logger.debug("searching kill_after")
                        # pass

                        started_now = 0
                        seconds_now = int(time.time())
                        self.id_to_seconds[id] = self.id_to_seconds.get(
                            id, seconds_now
                        )

                        seconds_start = self.id_to_seconds[id]

                        if seconds_now == seconds_start:
                            started_now = 1

                        proshlo = seconds_now - seconds_start
                        logger.debug(
                            "	proshlo: %s (must be %s, id %s, seconds_start %s, started_now %s)"
                            % (
                                proshlo,
                                R.kill_after,
                                id,
                                seconds_start,
                                started_now,
                            )
                        )
                        if proshlo >= R.kill_after:
                            logger.debug("PORA ZAKRYVATJ!")
                            close = 1

                    # wait_for_ok('%s - todo with kill_after' % fun)

                    else:
                        close = 1

                    if close:
                        all_found_windows.append(window_handle)
                        closed = 0

                        if T.close_all == 0:
                            cnt_closed += 1

                        else:
                            found = 1
                            logger.debug("closing!")
                            logger.debug(
                                "window %s %s" % (type(window), window)
                            )
                            logger.debug(
                                "window_handle %s %s"
                                % (type(window_handle), window_handle)
                            )
                            # wait_for_ok('%s - close?')
                            try:
                                handle_close(window_handle)
                                # window_close(window)
                                closed = 1
                            except Exception as er:
                                logger.error(
                                    "%s - ERROR closing! %s" % (fun, er)
                                )

                            try:
                                del self.id_to_seconds[id]
                            except Exception as er:
                                logger.error(
                                    "%s - error deleting %s" % (fun, id)
                                )

                            if closed:
                                cnt_closed += 1

            for id in ids_start:
                if id not in ids_curent:
                    logger.debug("	id %s propal, deleting" % id)
                    try:
                        del self.id_to_seconds[id]
                    except Exception as er:
                        logger.error("%s - error deleting %s" % (fun, id))

            if not found or T.close_all == 0:
                break

        if self.task["return_found_windows"]:
            if self.detailed:
                logger.debug("found %s programs" % len(all_found_windows))
            return all_found_windows
        return cnt_closed


def kill_with_id(pid, otl=0):
    fun = "kill_with_id"
    if otl:
        logger.debug("[%s %s" % (fun, pid))
    pid = str(pid)
    try:
        cmd1 = "kill -9 " + pid
        cmd2 = "taskkill /pid " + str(pid) + " /F"
        cmd3 = "taskkill /pid " + str(pid)
        cmds = [cmd2, cmd1, cmd3]
        for cmd in cmds:
            r = os.system(cmd)
            if otl:
                logger.debug("		result: %s %s" % (r, cmd))
            break
            continue
        return 1

    # os.system("taskkill /im make.exe")
    # os.popen('TASKKILL /PID '+str(process.pid)+' /F')
    # to test: http://stackoverflow.com/questions/10948235/taskkill-window-spaces-in-its-title-name
    # taskkill /fi "WINDOWTITLE eq Administrator: My Window Title"
    # tasklist /V /FI "WindowTitle eq Administrator*"
    except Exception as er:
        logger.error("error %s: %s" % (fun, er))
        return 0
    # browser.binary.process is a Popen object...
    if otl:
        logger.debug("+]")


def get_current_user():
    # имя текущего пользователя
    _ = getpass.getuser()
    _ = unicode_user_to_str(_)
    return _


def unicode_user_to_str(_):
    _ = text_to_charset(
        _, "utf8"
    )  # оказалось юзер в кирилце Администратор как-то не так себя вел
    return _


def search_programs(
    names=["firefox.exe"], q="", detailed=0, check_user=1, special=""
):
    """
        https://devblogs.microsoft.com/scripting/use-the-like-operator-to-simplify-your-wql-queries/
    """
    fun = "search_programs"
    # полезные запросы:
    # q = 'select * from Win32_Process where Name="chrome.exe" and ExecutablePath like "%Chromium%"'
    # q = 'select * from Win32_Process where CommandLine LIKE "%server_3.bat%"'

    # чтобы можно было только запрос бросать
    if names == []:
        names = [""]

    # ищем программы только текущего юзера
    current_user = get_current_user()
    # logger.debug('user %s %s' % (type(current_user), current_user)

    spec = ""
    programs = []
    for name in names:
        if q == "":
            if name.find("%") == -1:
                q = 'select * from Win32_Process where Name LIKE "[name]"'
                q = "select * from Win32_Process"
                q = 'select * from Win32_Process where Name="[name]"'
            else:
                q = 'select * from Win32_Process where Name LIKE "[name]"'
        elif q == "like":
            q = 'select * from Win32_Process where Name LIKE "[name]"'
        elif q == "any":
            q = "select * from Win32_Process"
            spec = "any"
        elif q == "all":
            q = "select * from Win32_Process"

        q = q.replace("[name]", name)
        logger.debug(f"	[{fun} {name=} {q=}")

        processes = seach_programs_ExecQuery(q)
        logger.debug(f"know {len(processes)} processes: {processes}")

        for num_process, p in enumerate(processes, 1):
            logger.debug(".")
            logger.debug(f"{num_process}/{len(processes)} {p=}")

            if 1 and (q == "all" or special == "all"):
                logger.debug("found (all programs good)")
                programs.append(p)
                continue

            # ищу только свои скрипты, а то ведь их много где может быть
            # http://stackoverflow.com/questions/18146970/how-to-get-process-owner-by-python-using-wmi - тут посоветовали
            # owner = p.GetOwner
            if not check_user:
                logger.debug("do not check user")

            else:
                try:
                    owner = p.ExecMethod_("GetOwner")
                    username = owner.Properties_("User").Value
                    # username = unicode_user_to_str(username)  # вообще не получаем? # это str но в кирилице непонятно что...
                    logger.debug("	username=%s" % username)
                except Exception as er:
                    logger.error(
                        "	error %s with GetOwner in %s, continue" % (fun, er)
                    )
                    continue

                # owner = p.GetOwner()
                # logger.debug('owner %s, username %s' % (owner, username))
                # wait_for_ok()
                if username != current_user:
                    if detailed:
                        try:
                            logger.debug(
                                "	propusk - process of user %s!=current_user %s"
                                % (username, current_user)
                            )
                        except Exception as er:
                            logger.error("error %s" % er)
                            logger.debug(
                                "user %s %s"
                                % (type(username), type(current_user))
                            )
                            logger.error(
                                "error %s: with details but username!=current_user"
                                % (fun)
                            )
                            # logger.error('error with details but user %s!=%s curent user' % (username, current_user))
                            # wait_for_ok()
                    # wait_for_ok()
                    continue

            # import wmi
            # for i in wmi.WMI().Win32_Process():
            # 	print('%s, %s, %s' % (i.Name, i.ProcessId, i.GetOwner()[2]))

            # logger.debug('owner %s' % owner)
            # wait_for_ok()
            if detailed:
                logger.debug("\n" * 2 + "%s" % (len(programs) + 1))

            found = 0
            for prop in [prop.Name for prop in p.Properties_]:
                # logger.debug(str(['	', prop,"=",p.Properties_(prop).Value]))
                value = p.Properties_(prop).Value
                if prop in ["Name", "CommandLine"] and detailed:
                    logger.debug("		%s=%s" % (prop, p.Properties_(prop).Value))

                if spec == "any":
                    if type(value) in [type("str"), type("str")]:
                        if value.find(name) != -1:
                            logger.debug(
                                "found name %s in: %s %s" % (name, prop, value)
                            )
                            found = 1
                            wait_for_ok()

            # wait_for_ok()

            if found == 0 and spec == "any":
                continue

            programs.append(p)

    logger.debug("		%s - found %s programs]" % (fun, len(programs)))
    return programs


def check_popen_process_active(commands, want_kill=False):
    """
    Через
    """
    fun = "check_popen_process_active"
    print("[%s" % fun),

    # работает, но тупо - папку отдельно
    t = 0
    if t:
        mode = "tupo_profile_otdelno"
        mode = "explore"
        mode = "real"

        if mode == "tupo_profile_otdelno":
            cmd = " ".join(commands[1:-1])

            q = 'select * from Win32_Process where CommandLine like "%[program]%"'.replace(
                "[program]", cmd
            )
            q = q + ' and CommandLine like "%google_for_scrapping_googleUA%"'

        elif mode == "real":
            # cmd = '%s' % commands[0] + ' '.join(commands[1:])
            # пока ищу чисто по аргументам
            cmd = " ".join(commands[1:])
            cmd = cmd.replace("\\", r"\\")  # экранировать надо

            q = 'select * from Win32_Process where CommandLine like "%[program]%"'.replace(
                "[program]", cmd
            )
        # q = q + ' and CommandLine like "%google_for_scrapping_googleUA%"'

        elif mode == "explore":
            cmd = r"S:!data\\hello"
            q = 'select * from Win32_Process where CommandLine like "%[program]%"'.replace(
                "[program]", cmd
            )

        else:
            wait_for_ok("tupo_profile_otdelno")

    cmd = get_title_of_popen(commands)
    q = 'select * from Win32_Process where CommandLine like "%[program]%"'.replace(
        "[program]", cmd
    )
    logger.debug("commands=%s, q=%s" % (commands, q))
    # wait_for_ok('good q?')

    programs = search_programs([], q=q)
    logger.debug(" %s programs: %s" % (len(programs), programs))

    if want_kill and len(programs) > 0:
        kill_programs(programs=programs)
        r = False
    else:
        r = len(programs) > 0

    print("+ %s=%s]" % (fun, r))
    return r


def get_title_of_popen(commands):
    cmd = " ".join(commands[1:])
    cmd = cmd.replace("\\", r"\\")  # экранировать надо
    return cmd


def seach_programs_ExecQuery(q=""):
    programs = []
    WMI = GetObject("winmgmts:")
    # processes = WMI.InstancesOf('Win32_Process')
    try:
        programs = WMI.ExecQuery(q)
    except Exception as er:
        logger.debug("ERROR %s" % er)

    return programs


def kill_programs(
    names=["firefox.exe"],
    q="",
    detailed=1,
    check_user=1,
    programs=None,
    special="",
):
    fun = "kill_programs"
    if names == ["chromium"]:
        q = 'select * from Win32_Process where CommandLine LIKE "%Chromium%" and name="chrome.exe"'

    if programs is None:
        programs = search_programs(
            names, q, detailed=detailed, check_user=check_user, special=special
        )

    logger.debug("[%s - found %s programs to kill" % (fun, len(programs)))
    i = 0
    for p in programs:
        i += 1
        logger.debug("\n" * 0 + "	kill %s/%s" % (i, len(programs)))

        for prop in [prop.Name for prop in p.Properties_]:
            if prop in ["Name", "CommandLine"]:
                # logger.debug(str(['	', prop,"=",p.Properties_(prop).Value])
                pass

        id = str(p.Properties_("ProcessId").Value)

        # wait_for_ok('kill with id %s' % id)
        kill_with_id(id)


def kill_firefoxes(detailed=1):
    names = []
    qs = [
        'select * from Win32_Process where CommandLine LIKE "%-marionette%" and Name LIKE "firefox%.exe"',
        #'select * from Win32_Process where CommandLine LIKE "%-marionette%" and Name LIKE "firefox.exe"',
    ]
    for q in qs:
        # programs = search_programs(names=names, q=q, detailed=1)
        # wait_for_ok()
        kill_programs(names=names, q=q, detailed=detailed, check_user=1)


def kill_werfault(programs=["WerFault.exe", "helper.exe"]):
    # окно ошибки вылазит - и оно напрягает
    fun = "kill_werfault"
    mode = "new"
    if mode == "new":
        for program in programs:
            logger.debug("[%s - kill %s..." % (fun, program))
            q = 'select * from Win32_Process where CommandLine like "%[program]%"'.replace(
                "[program]", program
            )
            kill_programs([], q)

    elif mode == "old":
        q1 = 'select * from Win32_Process where CommandLine like "%WerFault.exe%"'  # ошибка фаерфокса
        q2 = 'select * from Win32_Process where CommandLine like "%helper.exe%"'  # это - ошибка плугинов
        qs = [q1, q2]
        for q in qs:
            # 	programs = search_programs([], q)
            # 	logger.debug('programs=%s' % programs)
            kill_programs([], q)


def window_change_size_and_move(handle="", task={}):
    # меняем окну размер и позиции рандомные
    fun = "window_change_size_and_move"
    logger.debug("[%s" % fun)

    d = {
        # координаты окна от-до
        "w_x_ot": 0,
        "w_x_do": 0,
        "w_y_ot": 0,
        "w_y_do": 0,
        # ширина окна
        "w_shirina_ot": None,
        "w_shirina_do": 100,
        "w_vysota_ot": 100,
        "w_vysota_do": 100,
    }
    task = add_defaults(task, d)
    T = Bunch(task)

    logger.debug(fun)

    if handle == "":
        handle = get_foreground_handle()
    # else:не сработало
    # 	handle = find_chrome_window()
    # 	logger.debug('handle %s %s' % (type(handle), handle))
    x = choice(range(T.w_x_ot, T.w_x_do + 1))
    y = choice(range(T.w_y_ot, T.w_y_do + 1))

    if T.w_shirina_ot == None:  # значит не надо изменять размер
        properties = window_handle_get_properties(handle)

        T.w_shirina_ot = properties["w_rectangle"]
        T.w_shirina_do = T.w_shirina_ot
        T.w_vysota_ot = properties["h_rectangle"]
        T.w_vysota_do = T.w_vysota_ot

    if T.w_shirina_ot != None:
        shirina = choice(range(T.w_shirina_ot, T.w_shirina_do + 1))
        vysota = choice(range(T.w_vysota_ot, T.w_vysota_do + 1))

        sizes = "%s*%s %s*%s" % (x, y, shirina, vysota)
        sizes = "pos x*y=%s*%s, shirina*vysota=%s*%s" % (x, y, shirina, vysota)
        win32gui.MoveWindow(handle, x, y, shirina, vysota, True)
    # win32gui.MoveWindow(handle, x, y)

    # ctypes.windll.user32.MoveWindow(handle, x, y, shirina, vysota, True)
    logger.debug("+%s %s]" % (fun, sizes))

    return sizes


# wait_for_ok()


def change_mac_address(task={}):
    fun = "change_mac_address"
    step = 0
    while True:
        step += 1
        changed = change_mac_address_one(task)
        if changed:
            return changed

        logger.debug("%s error - mac not changed" % fun)
        sleep_(5)
        continue


def change_mac_address_one(task={}):
    # смена мак-адреса
    # https://technitium.com/tmac/help.html

    # Apply Non-Persistent Random MAC Address & Restart NIC:
    # tmac -n Local Area Connection -nr -re
    # по идее моя
    # tmac -n Local Area Connection -r -re
    fun = "change_mac_address_one"
    d = {
        "tmac_f_exe": r"c:\Program Files (x86)\Technitium\TMACv6.0\TMAC.exe",  # путь к екзешнику
        "tmac_connection_name": "VirtualBox Host-Only Network",
        "tmac_connection_name": "Conexión de área local",
        "tmac_connection_name": "Local Area Connection",
        "tmac_template_exe": '"[exe]" -n [name] -r -re',
        "tmac_template_exe": 'start cmd /C "[exe]" -n [name] -r -re',
        "tmac_f_bat": "bat_change_mac.bat",
        "tmac_close": 1,
        "tmac_key_changed": "mac_changed",
        "IG": 0,  # сюда пишем все?
    }
    task = add_defaults(task, d)
    T = Bunch(task)

    key_changed = T.tmac_key_changed
    repl = {
        "[exe]": T.tmac_f_exe,
        "[name]": T.tmac_connection_name,
    }
    cmd = no_probely(T.tmac_template_exe, repl)

    logger.debug("[%s cmd: %s" % (fun, cmd))

    if not file_exists(T.tmac_f_exe):
        logger.warning("no file %s" % T.tmac_f_exe)
        return 0

    # проверяем - возможно мы уже его меняли
    if T.IG and T.IG.has_key(key_changed):
        logger.debug("	already changed")

    # wait_for_ok('good cmd?')

    text_to_file(cmd, T.tmac_f_bat)

    cmd_start = "START %s" % T.tmac_f_bat
    cmd_start = T.tmac_f_bat
    os.system(cmd_start)
    # wait_for_ok('done?')

    i = 0
    while True:
        i += 1
        if i > 5:
            return 0
        logger.debug("search_%s" % i)
        sleep_(15)

        # проверяем что окно вылезло
        w_title = "Technitium MAC Address Changer v6"
        w_text = "Command was executed successfully."
        _ = {
            "title": w_title,
            "text_must_be": w_text,
        }
        tasks = [
            _,
        ]
        _ = {
            "tasks": tasks,
            "close_all": T.tmac_close,
        }
        closer = close_bad_windows_class(_)
        cnt_closed = closer.close()

        done = 0  # todo - проверить
        if cnt_closed > 0:
            done = 1

        logger.debug("cnt_closed: %s" % cnt_closed)
        # wait_for_ok('todo - check, mac changed?')
        if done:
            logger.debug("!CHANGED]")
            if T.IG:
                T.IG.add1(key_changed, 1)
            return 1
        else:
            logger.error("some error]")
            continue
            return 0


def pwa_do_int_list(t0=""):
    """
        pwa как-то шифрует области. Я их перевожу в обычные целые
        u'ClientRects': [<RECT L0, T0, R574, B335>],
        'Rectangle': <RECT L160, T97, R740, B457>
    """
    t = " %s " % str(t0)
    if t.find(">") != -1:
        t = find_from_to_one("<", ">", t)
    else:
        t = find_from_to_one("(", ")", t)
    ints = []
    parts = t.split(",")
    # logger.debug('%s %s' % (t, parts))
    for part in parts:
        v = part.strip()
        v = v.split(" ")[-1]
        # v = find_from_to_one(' ', 'nahposhuk', part)
        value = int(v[1:])
        ints.append(value)
    return ints


# wait_for_ok()


def window_handle_get_properties(handle):
    """
        получить свойства окна
    """
    fun = "window_handle_get_properties"
    logger.debug("[%s %s " % (fun, handle))

    otl = 1
    otl = 0
    pwa_app = pwa_handle_to_window(handle, "app")
    w_rectangle = 0
    h_rectangle = 0

    w_clientrectangle = 0
    h_clientrectangle = 0

    window = pwa_get_window_for_app(pwa_app, handle=window_handle)
    if window is None:
        properties = {
            "w_rectangle": w_rectangle,
            "h_rectangle": h_rectangle,
            "w_clientrectangle": w_clientrectangle,
            "h_clientrectangle": h_clientrectangle,
            "status": "error",
        }
        return properties

    logger.debug("window %s %s" % (type(window), window))
    u_properties = window.GetProperties()

    properties = {}
    for k in u_properties:
        v = u_properties[k]
        k2 = str(k)
        properties[k2] = v

    t = 1
    if t or otl:
        logger.debug("GetProperties: %s" % properties)
    # GetProperties: {u'UserData': 0, u'Style': 348782592, u'ControlCount': 0, u'ClientRects': [<RECT L0, T0, R1320, B910>], u'IsEnabled': True, u'Fonts': [<LOGFONTW 'Tahoma' -11>], u'FriendlyClassName': u'OHREPLAY', u'IsUnicode': False, u'Texts': [u"Durrell II CAP - $0.05/$0.10 - $2 Cap -  EUR - No Limit Hold'em - Logged In as Inmabetor2 [000190]"], u'ContextHelpID': 0, u'ExStyle': 256, u'IsVisible': True, u'ControlID': 0, u'MenuItems': [], u'Class': u'OHREPLAY', u'Rectangle': <RECT L37, T19, R1363, B954>}

    # u'Rectangle': <RECT L37, T19, R1363, B954>} == 1326 * 935
    # u'ClientRects': [<RECT L0, T0, R1320, B910>] == 1320 * 910

    client_rects = dct_value(properties, ["ClientRects", "client_rects"])
    rectangle = dct_value(properties, ["Rectangle", "rectangle"])

    # logger.debug('ClientRects %s' % ClientRects)
    # logger.debug('Rectangle %s' % Rectangle)

    client_rects = pwa_do_int_list(client_rects)
    rectangle = pwa_do_int_list(rectangle)

    w_rectangle = rectangle[2] - rectangle[0]
    h_rectangle = rectangle[3] - rectangle[1]

    # u'ClientRects': <RECT L37, T19, R1363, B954>} == 1326 * 935
    w_clientrectangle = client_rects[2] - client_rects[0]
    h_clientrectangle = client_rects[3] - client_rects[1]

    d = {
        "rectangle": rectangle,
        "client_rects": client_rects,
        "w_rectangle": w_rectangle,
        "h_rectangle": h_rectangle,
        "w_clientrectangle": w_clientrectangle,
        "h_clientrectangle": h_clientrectangle,
    }
    if otl:
        show_dict(d)

    properties = add_defaults(d, properties)

    logger.debug("+%s]" % fun)
    return properties


def window_handle_to_zsuv(handle):
    """
        есть хендл, и я ищу главное окно его (обычно обрезаем слева-справа-внизу рамочки и сверху меню. Такая логика была у Open Scrape, приходится эмулировать)
        использовал 2018.02.01 в покер-агенте, позиции окна рабочего определять
    """
    fun = "window_handle_to_zsuv"
    otl = 0

    logger.debug("[%s %s " % (fun, handle))

    properties = window_handle_get_properties(handle)

    w_clientrectangle = properties["w_clientrectangle"]
    h_clientrectangle = properties["h_clientrectangle"]
    w_rectangle = properties["w_rectangle"]
    h_rectangle = properties["h_rectangle"]

    w = w_clientrectangle
    h = h_clientrectangle

    if otl:
        logger.debug(
            "w_clientrectangle %s, h_clientrectangle %s"
            % (w_clientrectangle, h_clientrectangle)
        )
        logger.debug(
            "w_rectangle %s, h_rectangle %s" % (w_rectangle, h_rectangle)
        )

    zsuv_left_bottom = (w_rectangle - w_clientrectangle) / 2
    zsuv_top = h_rectangle - h_clientrectangle - zsuv_left_bottom

    zsuv = [zsuv_left_bottom, zsuv_top, zsuv_left_bottom, zsuv_left_bottom]

    logger.debug("+%s w*h=%s*%s]" % (zsuv, w, h))
    return zsuv, w, h


def window_handle_to_info(handle):
    """
        получаю хендл, и по нему инфу
    """

    # title = get_window_title(handle)
    otl = 0
    fun = "window_handle_to_info"

    if otl:
        logger.debug("[%s" % fun)

    # title = ctypes.windll.user32.GetWindowTextW(handle)
    title = win32gui.GetWindowText(handle)

    title = text_to_charset(title, "utf8", "cp1251")

    threadid, pid = win32process.GetWindowThreadProcessId(
        handle
    )  # https://stackoverflow.com/questions/28068754/how-do-i-get-a-pid-from-a-window-title-in-windows-os-using-python

    # logger.debug('%s' % type(title))
    res = {
        "title": title,
        "pid": pid,
        "threadid": threadid,
        "handle": handle,
    }
    if otl:
        logger.debug("+]")

    return res


def window_handle_to_coord(handle):
    """
    есть хендл, и мне нужно узнать координаты его окна
        https://stackoverflow.com/questions/7142342/get-window-position-size-with-python
    """
    rect = win32gui.GetWindowRect(handle)
    return list(rect)


def move_mouse_smooth_to_point(task={}):
    """Smooth glides mouse from current position to point x,y with default timing and speed"""

    # высчитываем куда вести мышку
    fun = "move_mouse_smooth_to_point"

    d = {
        "x": 0,
        "y": 0,
        "seconds": 1,
        "steps": 1000 * 1,
        "x1": "cursor_position",  # от какой позиции движем?
        "y1": "cursor_position",
        "otl": 0,
        "want_plot": 0,  # хотим нарисовать путь?
    }
    task = add_defaults(task, d)
    T = Bunch(task)

    x = T.x
    y = T.y
    seconds = T.seconds
    steps = T.steps
    x1 = T.x1
    y1 = T.y1
    otl = T.otl

    if x1 == "cursor_position":
        x1, y1 = get_cursor_pos()
    # x1, y1, x2, y2 = 890, 100, 494, 200

    logger.debug("[%s %s*%s to %s*%s" % (fun, x1, y1, x, y))

    # какой путь?
    tip = "line"
    tip = "generate_random_human_path"

    if tip == "line":
        X, Y = generate_smooth_line(
            x1, y1, x, y, steps=steps
        )  # тут мы по прямой будем вести

    elif tip == "generate_random_human_path":

        # готовлю для рисования:
        dots = [[x1, x], [y1, y]]

        # logger.debug('dots %s' % dots)
        plots = [
            (dots[0], dots[1], "ro"),
        ]

        _ = {
            "AB": [x1, y1, x, y],  # точки начала и конца
            "steps": steps,
            "otl": T.otl,
            "X_to_int": 1,
            "Y_to_int": 1,
        }
        max_steps = 1  # иногда для отладки можно поставить больше и посмотреть на график
        for i in range(max_steps):
            gen = ML.generate_random_human_path(_)

            X = gen["X"]
            Y = gen["Y"]

            # и на всяк финальную точку добавляю
            if x not in X:
                X.append(x)
                Y.append(y)

            t = 0
            if otl and t and i == 1:
                logger.debug("X %s, Y %s" % (X, Y))

            plots.append((X, Y))
        # break

        t = 1
        t = 0
        if T.want_plot:
            ML.my_plot(plots)
        # wait_for_ok()

    S = generate_smooth_time(seconds, len(X))

    move_mouse_smooth_along_path(X, Y, S)

    # и точно сюда попали в конце
    move_mouse(x, y)
    logger.debug("+%s]" % fun)


def generate_smooth_time(seconds=1, steps=1000 * 1):
    """
        генерю время общее
    """
    otl = 0

    tip = "line"
    S = []

    if tip == "line":
        seconds_step = (
            seconds * 1.0 / steps
        )  # за 1 шах должно пройти столько времени
        if otl:
            logger.debug("seconds_step %s" % seconds_step)

        for n in range(steps):
            seconds_plan = n * seconds_step
            S.append(seconds_plan)
    else:
        wait_for_ok("%s error - uknown tip %s" % (fun, tip))
    return S


def move_mouse_smooth_along_path(X=[], Y=[], S=[], seconds=1):
    """Smoothly glides mouse from x1,y1, to x2,y2 in time seconds using steps amount of steps
    """

    fun = "move_mouse_smooth_along_path"

    logger.debug("[%s" % fun)

    otl = 1
    otl = 0

    t_start = time.time()

    if S == []:
        if otl:
            logger.debug("seconds %s" % seconds)
        S = generate_smooth_time(seconds, len(X))

    x_last = -1
    y_last = -1
    for n in range(len(X)):
        x_step = X[n]
        y_step = Y[n]

        # должно было пройти столько времени
        seconds_plan = S[n]
        if otl:
            logger.debug(str([n, x_step, y_step, seconds_plan]))

        # continue

        if x_last != x_step or y_last != y_step:
            move_mouse(x_step, y_step)

        # высчитываем сколько должны были прождать
        seconds_proshlo = time.time() - t_start

        to_sleep = max(0, seconds_plan - seconds_proshlo)

        if to_sleep > 0:
            if otl:
                # logger.debug('	seconds_proshlo %s, seconds_plan %s, to_sleep %s' % (seconds_proshlo, seconds_plan, to_sleep))
                pass
            time.sleep(to_sleep)

    t_end = time.time()

    seconds = t_end - t_start

    logger.debug(
        "moved to %s*%s in %.2f seconds in %s steps]"
        % (x_step, y_step, seconds, len(X))
    )


def dll_open(f_dll0):
    """
        открываем длл
    """
    fun = "dll_open"

    # f_dll = f_dll0.replace('/', r'\\')

    t = 0
    if t:
        f_dll = f_dll0
        f_dll = r"c:\money\pokeruss\dist\modules_projects\data\yeux_v1.dll"

        f_dll = "c:/money/pokeruss/dist/modules_projects/data/yeux_v1.dll"
    else:
        f_dll = f_dll0

    if file_exists(f_dll):
        mess = "file exists"
    else:
        mess = "file not exists"

    logger.debug('	%s "%s", real dll "%s" %s' % (fun, f_dll0, f_dll, mess))

    no_try = 1

    if no_try:
        dll = ctypes.CDLL(f_dll)

    else:
        try:
            dll = ctypes.CDLL(f_dll)
        # dll = cdll.LoadLibrary(f_dll)
        # dll = ctypes.WinDLL(f_dll)
        except Exception as er:
            logger.debug("ERROR %s: %s" % (fun, er))
            dll = 0
    return dll


def free_dll(dll):
    """
    free memory from dll
    #https://stackoverflow.com/questions/19547084/can-i-explicitly-close-a-ctypes-cdll
    """

    fun = "free_dll"
    logger.debug("[%s" % fun)

    if dll == "":
        logger.debug("no dll]")
        return 1

    handle = dll._handle  # obtain the DLL handle

    ctypes.windll.kernel32.FreeLibrary(handle)

    if dll:
        del dll
    else:
        logger.debug("already deleted")
    logger.debug("+]")


def make_screenshot_for_handle_one(task={}):
    """
        делаю скриншот окна - с отступом если надо
        zsuv = [слева, вверху, справа, внизу]
        zsuv = [3, 22, 3, 3]
        zsuv = [0, 0, 0, 0]
    """

    fun = "make_screenshot_for_handle_one"

    d = {
        "handle": -1,
        "zsuv": "auto",
        "f_to": "bmp.bmp",
        "want_open_img": 0,
    }
    task = add_defaults(task, d)
    T = Bunch(task)
    handle = T.handle
    zsuv = T.zsuv
    f_to = T.f_to

    logger.debug("[%s %s %s %s" % (fun, handle, zsuv, f_to))

    want_open_img = T.want_open_img
    # handle = win32gui.FindWindow(None, windowname)

    t_start = time.time()

    t = 1
    t = 0
    if t:
        app = pwa_handle_to_window(handle, "app")
        app.OHREPLAY.print_control_identifiers()
    # app.print_control_identifiers()
    # wait_for_ok()

    wDC = win32gui.GetWindowDC(handle)
    dcObj = win32ui.CreateDCFromHandle(wDC)
    cDC = dcObj.CreateCompatibleDC()
    dataBitMap = win32ui.CreateBitmap()

    # you can use this to capture only a specific window
    l, t, r, b = win32gui.GetWindowRect(handle)
    logger.debug("	GetWindowRect:", l, t, r, b)
    w0 = r - l
    h0 = b - t

    # todo: позже я могу вырезать автоматически картинку
    t = 1
    t = 0
    if t or zsuv == "auto":

        zsuv, w, h = window_handle_to_zsuv(handle)

        logger.debug("	zsuv: %s" % zsuv)

        # wait_for_ok()

        # узнать название и клас окна?
        t = 0
        if t:

            if window == 0:
                wait_for_ok("no window?")

            # logger.debug('title: %s' % window.title_re)

            texts_full = pwa_texts_full(window)

            childs = pwa_get_childs(window)
            for child in childs:
                tf = pwa_texts_full(child)
                logger.debug("child %s, tf %s" % (child, tf))
            # wait_for_ok()
    else:
        w = w0 - zsuv[0] - zsuv[2]
        h = h0 - zsuv[1] - zsuv[3]

    logger.debug("	w0*h0=%s*%s, real %s*%s" % (w0, h0, w, h))

    t = 1
    t = 0
    if t:
        # in fact: 1326 * 935
        # must_be 1320, 910
        # -3 -22 -3 -3
        zsuv = [3, 22, 3, 3]
        w_real, h_real = 1320, 910

        w = w_real
        h = h_real

        logger.debug("HACK: w*h %s*%s, zsuv %s" % (w, h, zsuv))

    dataBitMap.CreateCompatibleBitmap(dcObj, w, h)
    cDC.SelectObject(dataBitMap)

    # https://msdn.microsoft.com/en-us/library/aa293654(v=vs.60).aspx
    # http://forums.codeguru.com/showthread.php?235376-CDC-BitBlt
    # cDC.BitBlt((0,0),(w, h) , dcObj, (0,0), win32con.SRCCOPY)

    cDC.BitBlt((0, 0), (w, h), dcObj, (zsuv[0], zsuv[1]), win32con.SRCCOPY)
    dataBitMap.SaveBitmapFile(cDC, f_to)
    # Free Resources
    dcObj.DeleteDC()
    cDC.DeleteDC()
    win32gui.ReleaseDC(handle, wDC)
    win32gui.DeleteObject(dataBitMap.GetHandle())
    if file_exists(f_to):
        status = 1
    else:
        status = 0

    t = 1
    t = 0
    if t or want_open_img:
        webbrowser.open(f_to)

    seconds = time.time() - t_start
    logger.debug("%s %s seconds %s]" % (status, seconds, fun))
    return status


def make_screenshot_for_handle(task={}):
    try:
        status = make_screenshot_for_handle_one(task)
        mess = 0
    except Exception as er:
        status = 0
        mess = str(er)
    return status, mess


def find_last_id_in_directory(d):
    """
        ищем последний айди, с какого мы начнем писать
    """
    fun = "find_last_id_in_directory"
    logger.debug("[%s" % fun)
    last_id = 0
    files = get_all_file_names(d)
    for f in files:
        id = find_from_to_one("frame", ".", f)
        if id == "":
            continue
        id = int(id)
        last_id = max(id, last_id)
    logger.debug("+%s]" % last_id)
    return last_id


def make_screenshots_for_title(task={}):
    fun = "make_screenshots_for_title"
    d = {
        "title": "",
        "handle": -1,
        "d_to": "temp/screenshots",
        "sleep": 1,
        "id": -1,
        "max_steps": 1000000000,
        "zsuv": "auto",
        "fun_edit_title": "",  # умеем и править название
        "otl": 0,
    }
    task = add_defaults(task, d)
    T = Bunch(task)

    otl = T.otl

    logger.debug("[%s" % fun)

    if otl:
        show_dict(task)

    create_dir(T.d_to)

    id = T.id
    if id == -1:
        id = find_last_id_in_directory(T.d_to)

    handle = T.handle
    if handle == -1:
        handles = pwa_find_windows_simple_and_re(T.title, handle=1)
        logger.debug("found %s handles" % len(handles))
        handle = handles[0]

    step = 0
    res = {
        "status": 0,
        "reason": "",
    }
    while True:
        step += 1
        if step > T.max_steps:
            logger.debug("max_steps %s reached, exit" % T.max_steps)
            break

        logger.debug("\n" * 2 + "step %s" % step)

        active = window_activate(handle)
        if not active:
            status = 0
            res["reason"] = "window_not_actived"
            continue

        status = 1

        info = window_handle_to_info(handle)
        title = info["title"]
        if T.fun_edit_title != "":
            title = T.fun_edit_title(title)

        id = id + 1
        img_name = "frame%06d.bmp" % id
        f_img = "%s/%s" % (T.d_to, img_name)
        _ = {
            "handle": handle,
            "zsuv": T.zsuv,
            "f_to": f_img,
        }
        status, mess = make_screenshot_for_handle(_)

        if status == 1:
            # сохраняем картинку
            # и сохраняем еще хтмл
            f_html = "%s/frame%06d.htm" % (T.d_to, id)
            tpl = """[title]
<html><head><title>[title]</title></head><body><img src='[img_name]' /></body></html>"""
            repl = {
                "[title]": title,
                "[img_name]": img_name,
            }
            html = no_probely(tpl, repl)
            text_to_file(html, f_html)

            res["last_f_screenshot_img"] = f_img
            res["last_f_screenshot_html"] = f_html
            res["id"] = id

        res["reason"] = mess
        res["status"] = status

        sleep_(T.sleep)

    logger.debug("+%s]" % fun)
    return res


def pwa_get_window_for_app(pwa_app, handle=None):
    fun = "pwa_get_window_for_app"
    window = None
    want_try = False
    if handle is not None:
        want_try = False

    if want_try:
        try:
            window = pwa_app.window(handle=handle)
        except Exception as er:
            print("%s ERROR: %s" % (fun, er))
    else:
        window = pwa_app.window(handle=handle)

    return window


def get_handle_title(hwnd):
    fun = "get_handle_title"
    try:
        title = _handleprops.text(hwnd)
    except Exception as er:
        logger.error("ERROR %s for handle %s, er = %s" % (fun, hwnd, er))
        title = ""
    return title


def get_handle_process(hwnd):
    fun = "get_handle_process"
    try:
        proc = application.process_module(_handleprops.processid(hwnd))
    except Exception as er:
        logger.error("ERROR %s for handle %s, er = %s" % (fun, hwnd, er))
        proc = ""
    return proc


def explore_top_window():
    import time

    while 1:
        hwnd = _win32functions.GetForegroundWindow()
        logger.debug("\nActive title: %s" % (get_handle_title(hwnd)))
        logger.debug("Activ proc: %s" % (get_handle_process(hwnd)))
        time.sleep(2)


# print 'windows_funcs]'


def test_function_to_check_the_title(title=""):
    if title.find("windows_funcs.py") != -1:
        return 1
    return 0


def get_monitor_size():
    from win32api import GetSystemMetrics

    width, height = GetSystemMetrics(0), GetSystemMetrics(1)
    return width, height


def get_foreground_handle():
    try:
        return win32gui.GetForegroundWindow()
    except Exception as er:
        logger.warning(f"get_foreground_handle impossible (linux?), {er=}")
        return None
    # hwnd = _win32functions.GetForegroundWindow()


t = 1
t = 0
if t:
    current_user = get_current_user()
    current_user = current_user.strip()
    encoding = "utf-8"
    encoding = "latin1"
    logger.debug(str([current_user, type(current_user), len(current_user)]))
    u2 = text_to_charset(current_user, "utf8")
    logger.debug(u2)
    u3 = text_to_charset(current_user, "cp1251")
    logger.debug(u3)
    current_user2 = unicode(current_user, encoding)
    # current_user2 = current_user.encode(encoding).strip()
    logger.debug(str([current_user2, type(current_user2), len(current_user2)]))
    wait_for_ok()


def make_full_screenshot_polube(*args, **kwargs):
    fun = "make_full_screenshot_polube"
    try:
        make_full_screenshot(*args, **kwargs)
    except Exception as er:
        logger.error("ERROR %s: %s" % (fun, er))


def make_full_screenshot(f=""):
    """
    https://www.quora.com/How-can-we-take-screenshots-using-Python-in-Windows
    :param f:
    :return:
    """
    # import win32gui
    # import win32ui
    # import win32con
    # import win32api

    # grab a handle to the main desktop window
    fun = "make_full_screenshot"
    logger.debug("[%s to %s" % (fun, f))

    hdesktop = win32gui.GetDesktopWindow()

    # determine the size of all monitors in pixels
    width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
    height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
    left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
    top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)

    # create a device context
    desktop_dc = win32gui.GetWindowDC(hdesktop)
    img_dc = win32ui.CreateDCFromHandle(desktop_dc)

    # create a memory based device context
    mem_dc = img_dc.CreateCompatibleDC()

    # create a bitmap object
    screenshot = win32ui.CreateBitmap()
    screenshot.CreateCompatibleBitmap(img_dc, width, height)
    mem_dc.SelectObject(screenshot)

    # copy the screen into our memory device context
    mem_dc.BitBlt(
        (0, 0), (width, height), img_dc, (left, top), win32con.SRCCOPY
    )

    # dir must exists
    # d = os.path.abspath(os.path.dirname(f))
    mkdir(f)
    # logger.debug("dir %s exists: %s" % (d, os.path.isdir(d)))

    # save the bitmap to a file
    screenshot.SaveBitmapFile(mem_dc, f)
    # free our objects
    mem_dc.DeleteDC()
    win32gui.DeleteObject(screenshot.GetHandle())


def make_full_screenshot_pil(f=""):
    from PIL import ImageGrab

    snapshot = ImageGrab.grab()
    snapshot.save(f)


if __name__ == "__main__":
    t = 0
    t = 1
    if t:
        # kill_firefoxes()
        # os._exit(0)
        q = 'select * from Win32_Process where CommandLine like "%--chrome_with_port_6033_%"'
        search_programs(q=q, detailed=1)

        # search_programs(
        #     names=["firefox_%.exe"], q="", detailed=1, check_user=0
        # )
        os._exit(0)

        names = []
        q = 'select * from Win32_Process where CommandLine LIKE "%-marionette%" and Name LIKE "firefox_%.exe"'
        programs = search_programs(names=names, q=q, detailed=1)
        wait_for_ok()
    t = 0
    t = 1
    if t:
        make_full_screenshot("temp/screenshot.bmp")
        os._exit(0)
    # wait_for_ok(get_monitor_size())

    t = 0
    t = 1
    if t:
        geckodriver_port = 6889
        marionette_port = 57889
        r = kill_geckodriver_with_special_port(
            geckodriver_port=geckodriver_port, marionette_port=marionette_port,
        )
        logger.debug("r: %s" % r)
        os._exit(0)

    t = 1
    if t:
        t = 1
        t = 0
        if t:
            explore_top_window()
            os._exit(0)

        t = 0
        t = 1
        if t:
            title = ".*AUTOPLINK"
            title = ".*cmd.exe"
            title = "Calculator"
            # title = '.*dellatg'
            # title = '.*(inactive)'
            handle = 1
            handle = 0
            windows = pwa_find_windows_one(title, handle=handle, title_re=1)
            logger.debug("windows: %s" % windows)

            for w in windows:
                logger.debug("tip %s" % type(w))
                window_close(w)
                # handle_close(w)

                wait_for_ok("closed window?")

            handles = pwa_find_windows_one(title, handle=1, title_re=1)
            logger.debug("handles: %s" % handles)
            os._exit(0)

        _ = {
            "title": ".*cmd.exe",
            "title_re": 1,
            #'fun_check_window_title_is_good': None,
            "fun_check_window_title_is_good": test_function_to_check_the_title,
        }

        tasks = [_]

        _ = {
            "tasks": tasks,
            "close_all": 0,  # если 0 - значит просто вывести эти проги
            "return_found_windows": 1,  # вернуть найденные окна?
            "detailed": 1,
        }
        closer = close_bad_windows_class(_)
        programs = closer.close()
        logger.debug("programs: %s" % programs)
        os._exit(0)

    t = 1
    if t:
        titles = [
            "cmd.exe -",
        ]
        for title in titles:
            Show_step(title)
            t = pwa_find_windows_simple_and_re(title)
            logger.debug("%s" % t)

        os._exit(0)
    t = 1
    if t:
        q = 'select * from Win32_Process where not CommandLine LIKE "%kill_programs%" and CommandLine LIKE "%addurl_selenium.exe%"'
        q = 'select * from Win32_Process where CommandLine LIKE "%addurl_selenium.py%"'
        q = 'select * from Win32_Process where CommandLine LIKE "%spec_task%"'
        names = []
        programs = search_programs(names=names, q=q, detailed=1)
        # kill_programs([], q)
        os._exit(0)

    t = 0
    t = 1
    if t:
        kill_werfault()
        os._exit(0)

    t = 0
    t = 1
    if t:
        lst = parse_tasklist()

        pids = map(
            int,
            clear_list(
                """
					8876
					"""
            ),
        )

        for _ in lst:
            pid = _["pid"]
            if pid in pids:
                logger.info("\n" + "-" * 10)
                show_dict(_)

                t = 1
                if t:
                    wait_for_ok("kill?")
                    kill_with_id(pid)
                    wait_for_ok("killed?")

            # [parse_tasklist in 0.51 seconds]
            # 	image
            # 			"geckodriver.exe"
            # 	mem_usage
            # 			"8 984 КБ"
            # 	pid
            # 			13092
            # 	session_name
            # 			"RDP-Tcp#0"
            # 	session_num
            # 			"2"

        os._exit(0)
    t = 0
    t = 1
    if t:

        step = 0
        while True:
            step += 1
            if step > 10:
                break
            logger.info("step %s" % step)
            windows_click(200, 200)
            sleep_(5)
    t = 1
    t = 0
    if t:
        title = "- No Limit -"

        while True:
            htmlpres = randint(1, 100)
            handles = pwa_find_windows_simple_and_re(title, handle=0)
            window = handles[0]

            pwa_tvvod(htmlpres, window=window)

            sleep_(2)
        os._exit(0)

    t = 1
    t = 0
    if t:
        handle = 1641536
        title = " Poker "
        _ = {
            "title": title,
            #'handle':handle,
        }
        make_screenshots_for_title(_)

        os._exit(0)

    t = 0
    t = 1
    if t:

        titles = [
            # r'\server\usr\local\python\python',
            # r'C:\Windows\system32\cmd.exe',
            #'cmd.exe',
            #'python.exe',
            #'',
            "Proxifier Portable",
            "3proxy.exe",
        ]
        _ = {
            "titles": titles,
        }
        windows = pwa_find_windows_with_titles(_)
        show_list(windows)

        _ = {
            "windows": windows,
            "actions": ["kill"],
            "otl": 1,
        }

        r = pwa_actions_on_windows(_)
        logger.debug("r: %s" % r)

        os._exit()

    t = 1
    t = 0
    if t:
        lst = [
            "[<RECT L0, T0, R574, B335>]",
            "<RECT L160, T97, R740, B457>",
            "(L160, T97, R740, B457)",
        ]
        for l in lst:
            lst = pwa_do_int_list(l)
            logger.info("%s %s" % (l, lst))

        os._exit(0)

    t = 1
    t = 0
    if t:
        change_mac_address()

    t = 0
    t = 1
    if t:
        seconds = 3
        seconds = 1
        seconds = 10

        steps = 10
        steps = 100
        steps = 300

        x = 1125
        y = 129

        x = 100
        y = 200
        cnt = 2

        x1 = "cursor_position"

        seconds = 1.3

        x, y, x1, y1 = [830, 888, 830, 886]

        otl = 0
        want_plot = 0
        want_plot = 1

        t = 1
        if t:
            _ = {
                "x": x,
                "y": y,
                "seconds": seconds,
                "steps": steps,
                "x1": x1,  # от какой позиции движем?
                "y1": y1,
                "otl": otl,
                "want_plot": want_plot,  # хотим нарисовать путь?
            }

            move_mouse_smooth_to_point(_)
            wait_for_ok("moved?")

        sleep_(5)
        windows_click(x, y, cnt)
        os._exit(0)

    t = 0
    t = 1
    if t:
        x1, y1, x2, y2 = 100, 100, 300, 300
        window_move_along_borders(x1, y1, x2, y2)
        os._exit(0)

    t = 1
    t = 0
    if t:
        points = [
            [100, 100],
            [300, 100],
            [300, 700],
            [100, 700],
            [100, 100],
        ]
        window_move_points(points)
        os._exit(0)

    t = 0
    t = 1
    if t:
        cx, cy, mx, my, seconds = 100, 100, 200, 200, 2
        cx, cy, mx, my, seconds = 100, 100, 1000, 600, 50
        # window_cursor_line(cx, cy, mx, my, seconds=seconds)
        logger.debug("seconds: %s" % seconds)
        window_move_mouse_in_rectangle(cx, cy, mx, my, seconds=seconds)
        os._exit(0)

    os._exit(0)

    t = 1
    t = 0
    if t:
        names = ["firefox.exe"]
        names = ["dropbox.exe"]
        names = ["chrome.exe"]
        q = ""
        programs = search_programs(names=names, q=q)
        logger.debug(programs)


# РАЗНОЕ:
# 	клик в координатах:
# 		import pywinauto.application

# 		app = pywinauto.application.Application()
# 		comapp = app.connect_(path = "explorer")

# 		for i in comapp.windows_():
# 			if "Progman" == i.FriendlyClassName():
# 			i.ClickInput(coords=(900, 50))

# работа с мышкой:
# 	http://schurpf.com/python-mouse-control/
# найдено тут, и тут же много всего
# 	http://schurpf.com/python-automation/,


# потестить:
##	logger.debug("Window %s:" % win32gui.GetWindowText(handle))
