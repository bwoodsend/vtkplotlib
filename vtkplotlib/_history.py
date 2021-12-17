# -*- coding: utf-8 -*-
"""
"""

import numpy as np
import sys
import os
from pathlib import Path

import collections


class FigureHistory(object):

    def __init__(self):
        self.deque = collections.deque(maxlen=2)

    @property
    def max_length(self):
        return self.deque.maxlen

    @max_length.setter
    def max_length(self, new):
        self.deque = collections.deque(self.deque, maxlen=new)

    def __getitem__(self, x):
        return self.deque[x]

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, self.deque)


try:
    figure_history
except NameError:
    figure_history = FigureHistory()
