# -*- coding: utf-8 -*-
"""
Created on Sun Sep  1 01:23:38 2019

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

from builtins import super

import numpy as np
import matplotlib.pylab as plt
import sys
import os
from pathlib2 import Path

from vtkplotlib.plots.BasePlot import ConstructedPlot
from vtkplotlib import nuts_and_bolts





class Surface(ConstructedPlot):
    def __init__(self, x, y, z, scalars=None, color=None, opacity=None, fig="gcf"):
        super().__init__(fig)
        
        points = np.concatenate([i[..., np.newaxis] for i in (x, y, z)], axis=-1)
        flat_points = nuts_and_bolts.flatten_all_but_last(points)
        
        shape = points.shape[:-1]
        unflatten_map = np.arange(np.prod(shape)).reshape(shape)
        
        
        corners = (unflatten_map[:-1, :-1],
                   unflatten_map[1:, :-1],
                   unflatten_map[1:, 1:],
                   unflatten_map[:-1, 1:],)
            
        
        args = np.concatenate([i[..., np.newaxis] for i in corners], axis=-1)


        self.polydata.points = flat_points
        self.polydata.polygons = args
        self.scalars = scalars
        
        self.add_to_plot()
        self.color_opacity(color, opacity)
        
    
    @property
    def scalars(self):
        return self.polydata.point_scalars
    @scalars.setter
    def scalars(self, s):
        self.polydata.point_scalars = s



if __name__ == "__main__":
    import vtkplotlib as vpl
    
    thi, theta = np.meshgrid(np.linspace(0, 2 * np.pi, 100),
                             np.linspace(0, np.pi, 50))


    x = np.cos(thi) * np.sin(theta)
    y = np.sin(thi) * np.sin(theta)
    z = np.cos(theta)

    self = vpl.Surface(x, y, z, color="g")
    vpl.show()