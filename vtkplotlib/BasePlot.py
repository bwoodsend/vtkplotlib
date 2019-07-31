# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 23:46:41 2019

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

from vtkplotlib.figures import gcf
from vtkplotlib import nuts_and_bolts


mpl_colors = {}
mpl_colors.update(colors.BASE_COLORS)
for dic in (colors.CSS4_COLORS, colors.TABLEAU_COLORS, colors.XKCD_COLORS):
    for (key, val) in dic.items():
        mpl_colors[key.split(":")[-1]] = colors.hex2color(val)
        


class BasePlot(object):
    def __init__(self, fig=None):
        self.fig = fig or gcf()
        
        
    def add_to_plot(self):
        self.mapper = vtk.vtkPolyDataMapper()
        
        self.actor = vtk.vtkActor()
        self.actor.SetMapper(self.mapper)
        
        
        self.property = self.actor.GetProperty()
        self.fig.add_actor(self.actor)

        
    def color_opacity(self, color=None, opacity=None):
        prop = self.property
    
        if opacity is not None:
            prop.SetOpacity(opacity)
        
        if color is not None:
            if isinstance(color, str):
                color = mpl_colors[color]
            
            prop.SetColor(*color[:3])
            
            if len(color) == 4:
                prop.SetOpacity(color[3])
                
    @property
    def color(self):
        return self.property.GetColor()
    
    @color.setter
    def color(self, x):
        self.color_opacity(x)
        
    @property
    def opacity(self):
        return self.property.GetOpacity()
    
    @opacity.setter
    def opacity(self, x):
        self.property.SetOpacity(x)
        
    @property
    def visable(self):
        return self.actor.GetVisibility()
    
    @visable.setter
    def visable(self, x):
        self.actor.SetVisibility(x)
        
        
        
        
class SourcedPlot(BasePlot):
    def add_to_plot(self):
        super().add_to_plot()
        self.mapper.SetInputConnection(self.source.GetOutputPort())
        
        
class ConstructedPlot(BasePlot):
    def __init__(self, fig=None):
        super().__init__(fig)
        self.poly_data = vtk.vtkPolyData()
        
    def add_to_plot(self):
        super().add_to_plot()
        self.mapper.SetInputData(self.poly_data)
        
    
        
        
        
        
def _iter_points(points):
    points = np.asarray(points)
    return nuts_and_bolts.flatten_all_but_last(points)


def _iter_colors(colors, shape):
    size = int(np.prod(shape))
    
    if colors is None:
        return (None for i in range(size))
    
    if isinstance(colors, (tuple, list, str)):
        return (colors for i in range(size))
    
    colors = np.asarray(colors)
    
    if colors.dtype == object:
        raise ValueError("colors type not understood")
    
    if colors.shape[:-1] == shape:
        return nuts_and_bolts.flatten_all_but_last(colors)
        
    else:
        raise ValueError("colors type not understood")
        
        
def _iter_scalar(s, shape):
    size = int(np.prod(shape))
    
    s = np.asarray(s)
    if s.shape == ():
        return (s for i in range(size))
    else:
        return s.flat




if __name__ == "__main__":
    pass
