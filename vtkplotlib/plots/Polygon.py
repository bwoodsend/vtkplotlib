# -*- coding: utf-8 -*-
"""
Created on Sun Jul 21 21:48:12 2019

@author: Brénainn Woodsend


Polygon.py
Creates a filled polygon.
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

import vtk
import numpy as np
#from matplotlib import pylab as plt
import os
import sys
from pathlib2 import Path
from vtk.util.numpy_support import (
                                    numpy_to_vtk,
                                    numpy_to_vtkIdTypeArray,
                                    vtk_to_numpy,
                                    )



from vtkplotlib.plots.BasePlot import ConstructedPlot, _iter_colors, _iter_points, _iter_scalar
from vtkplotlib import nuts_and_bolts, numpy_vtk




class Polygon(ConstructedPlot):
    """Creates a filled polygon with 'vertices' as it's corners. For a 3
    dimensional `vertices` array, each 2d array within vertices is a polygon.
    """
    def __init__(self, vertices, color=None, opacity=None, fig="gcf"):
        super().__init__(fig)
    
        # The implementation of this is actually exactly the same as Lines plot
        # but sets args to polydata.polygons rather than polydata.lines
        shape = vertices.shape[:-1]
        points = numpy_vtk.contiguous_safe(nuts_and_bolts.flatten_all_but_last(vertices))
        self.temp.append(points)
        
        args = nuts_and_bolts.flatten_all_but_last(np.arange(np.prod(shape)).reshape(shape))
        
        self.polydata.points = points
        self.polydata.polygons = args
            
        
        
        
        self.add_to_plot()

        self.color_opacity(color, opacity)
        



if __name__ == "__main__":
    import vtkplotlib as vpl
    
    t = np.arange(0, 1, .1) * 2 * np.pi
    points = np.array([np.cos(t), np.sin(t), np.cos(t) * np.sin(t)]).T
    
    self = vpl.polygon(points, color="r")
    
    vpl.show()

