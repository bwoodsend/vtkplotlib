# -*- coding: utf-8 -*-
"""
Created on Sun Jul 21 15:46:53 2019

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
from vtkplotlib.Arrow import Arrow


class Text3D(SourcedPlot):
    def __init__(self, string, position=(0, 0, 0), follow_cam=True, scale=1, color=None, opacity=None, fig=None):
        super().__init__(fig)
        # Create the 3D text and the associated mapper and follower (a type of
        # actor). Position the text so it is displayed over the origin of the
        # axes.
        if np.isscalar(scale):
            scale = (scale, ) * 3
            
        if not isinstance(string, str):
            string = str(string)
        
        self.source = vtk.vtkVectorText()
        self.source.SetText(string)
        
        
        self.actor = vtk.vtkFollower()
        self.actor.SetScale(*scale)
        self.actor.SetPosition(*position)
        
        self.mapper = vtk.vtkPolyDataMapper()
        
        self.actor.SetMapper(self.mapper)
        
        self.property = self.actor.GetProperty()
        self.fig.add_actor(self.actor)
        self.mapper.SetInputConnection(self.source.GetOutputPort())

        
        self.color_opacity(color, opacity)
        
        if follow_cam:
            self.actor.SetCamera(self.fig.render.GetActiveCamera())
    
        
def annotate(points, text, direction, text_color="w", arrow_color="k", distance=3, text_size=1, fig=None):
    point = geom.highest(points, direction)
    text_point = point + distance * direction
    return (Arrow(text_point, point, colors=arrow_color, fig=fig), 
        Text3D(text, text_point, color=text_color, scale=text_size, fig=fig))



if __name__ == "__main__":
    
    self = Text3D("ugg", follow_cam=True)
    
    show()
    
    
