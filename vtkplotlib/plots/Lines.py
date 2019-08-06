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
from vtkplotlib import geometry as geom



class Lines(ConstructedPlot):
    """Plots a line going through an array of points. Optionally can be set to
    join the last point with the first to create a polygon."""
    def __init__(self, vertices, color=None, opacity=None, line_width=1.0, join_ends=False, fig=None):
        super().__init__(fig)
        
        points = vtk.vtkPoints()
        points.SetData(numpy_to_vtk(vertices))
        
        # vtkCellArray is a supporting object that explicitly represents cell connectivity.
        # The cell array structure is a raw integer list of the form:
        # (n,id1,id2,...,idn, n,id1,id2,...,idn, ...) where n is the number of points in
        # the cell, and id is a zero-offset index into an associated point list.
        
        point_args = np.empty(1 + len(vertices) + join_ends, np.int64)
        point_args[0] = len(vertices) + join_ends
        point_args[1: 1+len(vertices)] = np.arange(len(vertices))
        if join_ends:
            point_args[-1] = 0
        lines = vtk.vtkCellArray()
        lines.SetCells(len(point_args), numpy_to_vtkIdTypeArray(point_args.ravel()))
        
        
        # vtkPolyData is a data object that is a concrete implementation of vtkDataSet.
        # vtkPolyData represents a geometric structure consisting of vertices, lines,
        # polygons, and/or triangle strips
        polygon = self.poly_data
        polygon.SetPoints(points)
        polygon.SetLines(lines)
        
        
        # Create an actor to represent the polygon. The actor orchestrates rendering of
        # the mapper's graphics primitives. An actor also refers to properties via a
        # vtkProperty instance, and includes an internal transformation matrix. We
        # set this actor's mapper to be polygonMapper which we created above.
        self.actor = vtk.vtkActor()
        
        self.add_to_plot()
        
        self.color_opacity(color, opacity)
        self.property.SetLineWidth(line_width)
    
        





if __name__ == "__main__":
    import vtkplotlib as vpl
    
    t = np.arange(0, 1, .001) * 2 * np.pi
    points = np.array([np.cos(2 * t),
                       np.sin(3 * t),
                       np.cos(5 * t) * np.sin(7 *t)]).T
    
#    vertices = np.random.uniform(-30, 30, (3, 3))
    self = vpl.plot(points, color="green", line_width=3, join_ends=True)
    
    vpl.show()
