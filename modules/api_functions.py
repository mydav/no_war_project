def is_api_error(obj, key="error"):
    return isinstance(obj, dict) and obj.get(key, "") != ""


def is_api_success(*args, **kwargs):
    return not is_api_error(*args, **kwargs)


def del_empty_error(obj):
    if "error" in obj and not is_api_error(obj):
        del obj["error"]


def api_success(details="", **kwargs):
    """Когда точно НЕ ошибка - такое вывожу
    удобно просматривать код на ошибке-неошибки
    """
    r = api_answer(error="", details=details, **kwargs)
    for key in ["error", "details", "error_path"]:
        value = r[key]
        if value in ["", []]:
            del r[key]
    return r


### py2
def get_api_error(obj, key="error"):
    if is_api_error(obj, key=key):
        return obj.get(key)
    return ""


def api_error(error="", details="", **kwargs):
    """При ошибке - всегда такое вывожу"""

    # для повторного использования api_error(api_error())...
    error_from = kwargs.get("error_from", None)
    if error_from is not None and isinstance(error, dict):
        error_path = error.get("error_path", [])
        error_path.append(error_from)
        error["error_path"] = error_path[:]

        if "error_from" in error:
            del error["error_from"]
        if "error_from" in kwargs:
            del kwargs["error_from"]
        kwargs.update(error)
        # print('    %s kwargs=%s' % (error_path, kwargs))
        return api_answer(**kwargs)

    return api_answer(error=error, details=details, **kwargs)


def api_answer(error="", details="", **kwargs):
    dct = locals()
    # print(dct)

    rez = {
        "error": error,
        "details": details,
    }
    for k, v in dct["kwargs"].items():
        # print ' ', k, v
        rez[k] = v

    error_path = rez.get("error_path", [])
    if "error_from" in rez:
        error_path.append(rez["error_from"])
        del rez["error_from"]
    rez["error_path"] = error_path[:]
    return rez


def demo_api_error_root():
    r = demo_api_error_1()
    print
    "1", r
    if is_api_error(r):
        r = api_error(r, error_from="demo_api_error_root")
        print
        "2", r
        return r


def demo_api_error_1():
    return api_error(demo_api_error_2(), error_from="demo_api_error_1")


def demo_api_error_2():
    return api_error("error2", error_from="demo_api_error_2")


if __name__ == "__main__":
    r = api_answer("bad", x=1, args=1)
    print(r)
    r = demo_api_error_root()
    print(r)
