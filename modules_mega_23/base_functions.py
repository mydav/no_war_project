#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys

#!без этого не получается использовать подмодули с этой папки в modules_mega
t = 0
t = 1
if t:
    d_current = os.path.join(os.path.dirname(os.path.realpath(__file__)))
    sys.path += [d_current]
    # sys.path.insert(0, d_current)
    # print('        add to path "%s " (file %s)' % (d_current, __file__))

# from modules_mega_23.center_koordinator import *
