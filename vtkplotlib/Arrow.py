# -*- coding: utf-8 -*-
"""
Created on Sun Jul 21 15:54:56 2019

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


import vtk
import numpy as np
#from matplotlib import pylab as plt
from matplotlib import colors
import os
import sys
from pathlib2 import Path
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QFileDialog
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtk.util.numpy_support import (
                                    numpy_to_vtk,
                                    numpy_to_vtkIdTypeArray,
                                    vtk_to_numpy,
                                    )



from vtkplotlib.BasePlot import SourcedPlot, _iter_colors, _iter_points, _iter_scalar
from vtkplotlib.figures import gcf, show
from vtkplotlib import geometry as geom

class Arrow(SourcedPlot):
    def __init__(self, start, end, length=None, color=None, opacity=None, fig=None):
        super().__init__(fig)
        
        diff = end - start
        if length == None:
            length = geom.distance(diff)
                    
        eX, eY, eZ = geom.orthogonal_bases(diff)
        arrowSource = vtk.vtkArrowSource()
            
        matrix = vtk.vtkMatrix4x4()

        # Create the direction cosine matrix
        matrix.Identity()
        for i in range(3):
          matrix.SetElement(i, 0, eX[i])
          matrix.SetElement(i, 1, eY[i])
          matrix.SetElement(i, 2, eZ[i])
        
        # Apply the transforms
        transform = vtk.vtkTransform()
        transform.Translate(start)
        transform.Concatenate(matrix)
        transform.Scale(length, length, length)
        
        self.source = arrowSource
            
        self.add_to_plot()
        self.actor.SetUserMatrix(transform.GetMatrix())
            
        self.color_opacity(color, opacity)
                    
            


def arrow(start, end, length=None, color=None, opacity=None, fig=None):
    start = np.asarray(start)
    end = np.asarray(end)
    
    out = np.empty(start.shape[:-1], object)
    out_flat = out.ravel()
    
    for (i, s, e, l, c) in zip(range(out.size),
                                _iter_points(start),
                                _iter_points(end),
                                _iter_scalar(length, start.shape[:-1]),
                                _iter_colors(color, start.shape[:-1])):
        
        out_flat[i] = Arrow(s, e, l, c, opacity, fig)

    return out_flat
    

def quiver(point, gradient, length=None, length_scale=1, color=None, opacity=None, fig=None):
    if length is None:
        length = geom.distance(gradient)
    if length_scale != 1:
        length *= length_scale
        
    return arrow(point, point + gradient, length, color, opacity, fig)



if __name__ == "__main__":
    
    t = np.linspace(0, 2 * np.pi)
    points = np.array([np.cos(t), np.sin(t), np.cos(t) * np.sin(t)]).T
    grads = np.roll(points, 10)
    
    arrows = quiver(points, grads)
    
    show()
