# -*- coding: utf-8 -*-
"""
Created on Sun Jul 21 20:32:50 2019

@author: Brénainn Woodsend


Lines.py
Plots lines through some points.
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
import os
import sys
from pathlib2 import Path
from vtk.util.numpy_support import (
                                    numpy_to_vtk,
                                    numpy_to_vtkIdTypeArray,
                                    vtk_to_numpy,
                                    )



from vtkplotlib.plots.BasePlot import ConstructedPlot, _iter_colors, _iter_points, _iter_scalar
from vtkplotlib import numpy_vtk, nuts_and_bolts
from vtkplotlib.plots.polydata import join_line_ends



class Lines(ConstructedPlot):
    """Plots a line going through an array of points. Optionally can be set to
    join the last point with the first to create a polygon."""
    def __init__(self, vertices, color=None, opacity=None, line_width=1.0, join_ends=False, fig="gcf"):
        super().__init__(fig)
        
        
        shape = vertices.shape[:-1]
        points = numpy_vtk.contiguous_safe(nuts_and_bolts.flatten_all_but_last(vertices))
        self.temp.append(points)
        
        args = nuts_and_bolts.flatten_all_but_last(np.arange(np.prod(shape)).reshape(shape))
        
        self.polydata.points = points
        if join_ends:
            self.polydata.lines = join_line_ends(args)
        else:
            self.polydata.lines = args
        
#        assert np.array_equal(points[args], vertices)
        
        
        self.add_to_plot()
        
        self.color_opacity(color, opacity)
        self.property.SetLineWidth(line_width)
    
        



if __name__ == "__main__":
    import vtkplotlib as vpl
    
    t = np.arange(0, 1, .001) * 2 * np.pi
    vertices = np.array([np.cos(2 * t),
                         np.sin(3 * t),
                         np.cos(5 * t) * np.sin(7 *t)]).T
    vertices = np.array([vertices, vertices + 2])
    
    t = np.arange(0, 1, .125) * 2 * np.pi
    vertices = np.array([np.cos(t), np.sin(t), np.zeros_like(t)]).T
    
#    vertices = np.random.uniform(-30, 30, (3, 3))
    self = vpl.plot(vertices, color="green", line_width=6, join_ends=True)
#    self.polydata.point_scalars = vpl.geometry.distance(vertices)
    self.polydata.point_scalars = t
    fig = vpl.gcf()
    fig.background_color = "grey"
    self.add_to_plot()
    vpl.show()
