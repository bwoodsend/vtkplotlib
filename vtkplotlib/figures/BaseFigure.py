# -*- coding: utf-8 -*-
"""
Created on Sat Aug  3 13:00:11 2019

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
from __future__ import print_function
from builtins import super

import numpy as np
import sys
import os
from pathlib2 import Path


from .render_window import VTKRenderer
from .figure_manager import reset_camera, scf, gcf


class BaseFigure(VTKRenderer):
    def __init__(self):
        super().__init__()
        scf(self)

        self.plots = set()


    _reset_camera = True
#    has_been_shown = False

    def reset_camera(self):
        return reset_camera(self)


    def show(self, block=True):
        # Try and force the console to finish displaying any preceeding print
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

#        if self.has_been_shown:
#            print(self, "has already been shown")
#            return

        self.start(block, self._reset_camera)

        if block and gcf() is self:
            scf(None)
#            self.has_been_shown = True


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


    def update(self):
        self.show(False)





if __name__ == "__main__":
    pass
