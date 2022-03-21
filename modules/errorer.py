#!/usr/bin/python
# -*- coding: utf-8 -*-

from modules.print_functions import show_list
from modules.print_colored import *


class Errorer(object):
    def __init__(self, name=""):
        self.name = name
        self.init_parse_errors()

    def init_parse_errors(self):
        self.parse_errors = []

    def add_error(self, *args, **kwargs):
        return self.add(*args, **kwargs)

    def add(self, error="", fun=""):
        self.parse_errors.append("fun %s: %s" % (fun, error))

    def show_errors(self):
        errors = self.parse_errors
        if errors:
            print_error(
                "Errorer %s HAVE %s parse_errors:" % (self.name, len(errors))
            )
            show_list(errors)
        else:
            print_success("Errorer %s ideal - no errors" % self.name)
