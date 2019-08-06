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


import numpy as np
import matplotlib.pylab as plt
import sys
import os
from pathlib2 import Path


from .render_window import VTKRenderer
from .figure_manager import reset_camera, scf, gcf


class BaseFigure(VTKRenderer):
    def __init__(self, window=None, window_interactor=None):    
        super().__init__(window, window_interactor)
        scf(self)
        
        self.plots = set()

        
    _reset_camera = True

    def reset_camera(self):
        return reset_camera(self)

    
    def show(self, block=True):
        self.start(block, self._reset_camera)

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








if __name__ == "__main__":
    pass
