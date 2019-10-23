# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 18:47:40 2019

@author: Brénainn Woodsend


one line to give the program's name and a brief idea of what it does.
Copyright (C) 2019  Brénainn Woodsend

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from __future__ import with_statement

import numpy as np
import matplotlib.pylab as plt
import sys
import os
from pathlib2 import Path

import importlib

from unittest import TestCase, main

MODULES = ("PIL", "PyQt5", "stl", )
#
#class TestOptionalDependencyFallbacks(TestCase):
#    def setUp(self):
##        del sys.modules["vtkplotlib"]
#        for i in MODULES:
#            sys.modules[i] = None
#        importlib.invalidate_caches()
#        global vpl
#        import vtkplotlib as vpl
#        importlib.reload(vpl)
##        assert not vpl.PyQt5_AVAILABLE
#        self.test_the_test()
#
#
#
#    def test_the_test(self):
#        for i in MODULES:
#            with self.assertRaises(ImportError):
#                __import__(i)
#            with self.assertRaises(AttributeError):
#                vpl.QtFigure
#
#
#    def tearDown(self):
#        for i in MODULES:
#            del sys.modules[i]
#        global vpl
#        import vtkplotlib as vpl
#        importlib.reload(vpl)
#
#
#    def test_imread(self):
#        tm = vpl.TextureMap(vpl.data.ICONS["Right"])
#        plt.imshow(tm.array)
#        plt.show()
#
#    def test_stl_reader(self):
#        vpl.mesh_plot(vpl.data.get_rabbit_stl())
##        from stl import mesh
#        vpl.show()
#
#
#if __name__ == "__main__":
#    main(TestOptionalDependencyFallbacks())
