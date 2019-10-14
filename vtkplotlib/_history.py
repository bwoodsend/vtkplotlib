# -*- coding: utf-8 -*-
# =============================================================================
# Created on Thu Oct 10 21:58:54 2019
#
# @author: Brénainn Woodsend
#
#
# one line to give the program's name and a brief idea of what it does.
# Copyright (C) 2019  Brénainn Woodsend
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# =============================================================================
"""
"""


import numpy as np
import sys
import os
from pathlib2 import Path

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