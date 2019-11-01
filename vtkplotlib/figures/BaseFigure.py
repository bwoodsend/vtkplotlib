# -*- coding: utf-8 -*-
# =============================================================================
# Created on Sat Aug  3 13:00:11 2019
#
# @author: Brénainn Woodsend
#
#
# BaseFigure.py provides a base class for vpl figures.
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


from __future__ import print_function
from builtins import super

import numpy as np
import sys
import os
from pathlib2 import Path


from .render_window import VTKRenderer
from .figure_manager import reset_camera, scf, gcf


class BaseFigure(VTKRenderer):
    def __init__(self, name=""):
        super().__init__()
        scf(self)

        # Just for fun
        if name:
            self.window_name = name
        else:
            try:
                import namegenerator
                self.window_name = namegenerator.gen().replace("-", " ").title()
            except ImportError:
                self.window_name = "VTK figure"
        self.plots = set()


    _reset_camera = True


    def reset_camera(self):
        return reset_camera(self)


    def show(self, block=True):
        # Try and force the console to finish displaying any preceding print
        # statements before VTK start is called and blocks everything. Rather
        # limited success.
        try:
            # python 2 doesn't have flush
            print(end="", flush=True)
        except TypeError:
            pass
        sys.stdout.flush()
        for attr in ("buffer", "_buffer"):
            if hasattr(sys.stdout, attr):
                getattr(sys.stdout, attr).flush()


        self.start(block, self._reset_camera)

        # Camera only gets reset automatically the first time self.show() is
        # called.
        self._reset_camera = False

        if block and gcf() is self:
            scf(None)


    def add_plot(self, plot):
        if isinstance(plot, np.ndarray) and plot.dtype == object:
            [self.add_plot(i) for i in plot.flat]
            return
        if plot not in self.plots:
            self._add_actor(plot.actor)
            self.plots.add(plot)


    def remove_plot(self, plot):
        if isinstance(plot, np.ndarray) and plot.dtype == object:
            [self.remove_plot(i) for i in plot.flat]
            return
        if plot in self.plots:
            self._remove_actor(plot.actor)
            self.plots.remove(plot)


    def __iadd__(self, plot):
        self.add_plot(plot)
        return self

    def __isub__(self, plot):
        self.remove_plot(plot)
        return self

    @property
    def render_size(self):
        """Get the render image size (width, height) in pixels. Note that if the
        figure is a QtFigure then the setter will be constantly overridden by
        the parent widget's resizing."""
        return self.renWin.GetSize()

    @render_size.setter
    def render_size(self, size):
        self.renWin.SetSize(*size)







if __name__ == "__main__":
    pass
