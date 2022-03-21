#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging


def copy_class_attributes(class_from, class_to, only_new=True):
    """
    скопировать все атрибуты класа
    """
    fun = "copy_class_attributes"
    keys = get_all_class_attributeNames(class_from)
    for num, k in enumerate(keys, 1):
        v = getattr(class_from, k)
        logging.debug("   %s %s/%s %s" % (fun, num, len(keys), k))

        if only_new and hasattr(class_to, k):
            logging.debug("     attribute %s already exists, so skip" % k)
            continue

        class_to.__dict__[k] = v


def get_func_from_class(clas, name, default=None):
    """
    проверяем есть ли в классе ф-я, и если есть возвращаем ее
    
        # method_list = [func for func in dir(self.api_bk) if callable(getattr(self.api_bk, func)) and not func.startswith("__")]
        # print method_list

        # return name in dir(self.api_bk)


        # show_dict(self.api_bk.__dict__)
    """
    return get_class_attribute(clas, name, default=default)
    # try:
    #     return getattr(clas, name)
    # except Exception, er:
    #     return default


def get_class_attribute(clas, name, default=None):
    if name is None:
        return default

    # print 'clas=%s, name=%s' % (clas, name)
    if not hasattr(clas, name):
        return default
    return getattr(clas, name)


def get_all_class_attributeNames(class_from):
    keys = dir(class_from)
    keys.sort()
    return keys
