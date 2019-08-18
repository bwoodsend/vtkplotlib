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
from vtkplotlib import geometry as geom, numpy_vtk




class Polygon(ConstructedPlot):
    """Creates a filled polygon with 'vertices' as it's corners."""
    def __init__(self, vertices, color=None, opacity=None, fig="gcf"):
        super().__init__(fig)
    
        polygon = self.poly_data
        
        vertices = numpy_vtk.contiguous_safe(vertices)
        self.temp.append(vertices)
        
        points = vtk.vtkPoints()
        points.SetData(numpy_to_vtk(vertices))        
        polygon.SetPoints(points)
        
        
        # vtkCellArray is a supporting object that explicitly represents cell connectivity.
        # The cell array structure is a raw integer list of the form:
        # (n,id1,id2,...,idn, n,id1,id2,...,idn, ...) where n is the number of points in
        # the cell, and id is a zero-offset index into an associated point list.
        
        point_args = np.empty(1 + len(vertices), np.int64)
        point_args[0] = len(vertices)
        point_args[1: 1+len(vertices)] = np.arange(len(vertices))
        polys = vtk.vtkCellArray()
        polys.SetCells(1, numpy_to_vtkIdTypeArray(point_args.ravel()))
        
        lines = vtk.vtkCellArray()
        lines.SetCells(len(point_args), numpy_to_vtkIdTypeArray(point_args.ravel()))
        
        
        polygon.SetPolys(polys)
        polygon.SetLines(lines)
        
        
        self.add_to_plot()

        self.color_opacity(color, opacity)
        



if __name__ == "__main__":
    import vtkplotlib as vpl
    
    t = np.arange(0, 1, .1) * 2 * np.pi
    points = np.array([np.cos(t), np.sin(t), np.cos(t) * np.sin(t)]).T
    
    self = vpl.polygon(points, color="r")
    
    vpl.show()

