def get_value_from_list_for_key(objects=[], key="name", default=None):
    for obj in objects:
        value = obj.get(key)
        if value is not None:
            break

    if value is None:
        value = default

    return value


def plist(lst=[], limit=0):
    if lst is None:
        lst = []
    new_list = []
    if limit:
        for element in lst:
            try:
                t = "%s..." % str(element)[:limit]
            except Exception as er:
                t = element
            new_list.append(t)
    else:
        new_list = lst[:]
    try:
        return "[%s]" % ", ".join(new_list)
    except Exception as er:
        return lst


if __name__ == "__main__":
    print(plist([1, 2, 3]))
