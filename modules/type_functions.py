def change_variable_type_to_most_suitable(v=""):
    """
        меняем тип к самому подходящему
    """
    if is_int(v):
        v = convert_to_int(v)
    elif is_float(v):
        v = convert_to_float(v)
    else:
        pass
    return v


#       is float?
def is_float(item=""):
    # https://stackoverflow.com/questions/736043/checking-if-a-string-can-be-converted-to-float-in-python
    try:
        convert_to_float(item)
        return 1
    except Exception as er:
        # print "Not a float"
        return 0


def is_int(item=""):
    # https://stackoverflow.com/questions/736043/checking-if-a-string-can-be-converted-to-float-in-python
    try:
        convert_to_int(item)
        return 1
    except Exception as er:
        # print "Not a int"
        return 0


def convert_to_int(item=""):
    return int(str(item).strip())


def convert_to_float(item=""):
    return float(str(item).replace(",", ".").strip())


if __name__ == "__main__":
    t = 1
    if t:
        values = [
            1,
            " 1",
            "1. ",
            "1.0",
            "1.1",
            "1,1",
        ]
        for value in values:
            t = 1
            t = 0
            if t:
                print(value, is_int(value))
                continue

            changed = change_variable_type_to_most_suitable(value)
            m = f"value `{value}`       `{type(value)}`, new value {changed} with type `{type(changed)}`"
            print(m)
