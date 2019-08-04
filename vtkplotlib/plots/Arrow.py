# -*- coding: utf-8 -*-
"""
Created on Sun Jul 21 15:54:56 2019

@author: Brénainn Woodsend


Arrow.py creates an arrow / quiver plot.
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
from vtk.util.numpy_support import (
                                    numpy_to_vtk,
                                    numpy_to_vtkIdTypeArray,
                                    vtk_to_numpy,
                                    )

from vtkplotlib.plots.BasePlot import SourcedPlot, _iter_colors, _iter_points, _iter_scalar
from vtkplotlib import geometry as geom


class Arrow(SourcedPlot):
    def __init__(self, start, end, length=None, color=None, opacity=None, fig=None):
        super().__init__(fig)
        
        diff = end - start
        if length == None:
            length = geom.distance(diff)
                    
        # vtk needs a full set of axes to build about.
        # eX is just the direction the arrow is pointing in.
        # eY and eZ must be perpendicular to each other and eX. However beyond 
        # that exact choice of eY and eZ does not matter. It only rotates the 
        # arrow about eX which you don't see because it's (approximately) round.
        eX, eY, eZ = geom.orthogonal_bases(diff)
        arrowSource = vtk.vtkArrowSource()


        # This next bit puts the arrow where it's supposed to go
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
    """Draw an arrow / arrows from 'start' to 'end'. 'start' and 'end' should
    have matching shapes. Arrow lengths are automatically calculated by 
    pythagoras but can be overwritten by setting 'length'. 'length' can either 
    be a single value for all arrows or an array of lengths to match the number
    of arrows. Note arrays are supported only for convenience and just use a
    python for loop. There is no speed bonus for using numpy or trying to plot
    in bulk here. Returns an array of stand-alone Arrow objects with same shape
    as the input."""
    
    start = np.asarray(start)
    end = np.asarray(end)
    
    assert start.shape == end.shape
    
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
    """Create an arrow from 'point' towards a direction given by 'gradient'. 
    Lengths by default are the magnitude of 'gradient but can be scaled with
    'length_scale' or overwritten with 'length'. See arrow's docs for more 
    detail.
    """
    
    if length is None:
        length = geom.distance(gradient)
    if length_scale != 1:
        length *= length_scale
        
    return arrow(point, point + gradient, length, color, opacity, fig)



if __name__ == "__main__":
    
    import vtkplotlib as vpl
    
    t = np.linspace(0, 2 * np.pi)
    points = np.array([np.cos(t), np.sin(t), np.cos(t) * np.sin(t)]).T
    grads = np.roll(points, 10)
    
    arrows = quiver(points, grads, color=grads)
    
    vpl.show()
