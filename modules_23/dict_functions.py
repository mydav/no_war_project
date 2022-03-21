#!/usr/bin/python
# -*- coding: utf-8 -*-


def get_nonEmpty_value_from_dicts(
    key="login", dicts=[], default=None, bad_values=[None, ""]
):
    found = default
    for dct in dicts:
        value = dct.get(key)
        if value not in bad_values:
            found = value
            break
    return found


if __name__ == "__main__":
    t = 1
    if t:
        dicts = [
            {"login": 1,},
            {"login": None},
        ]

        r = get_nonEmpty_value_from_dicts("login", dicts)
        print("found %s" % r)
        os._exit(0)
