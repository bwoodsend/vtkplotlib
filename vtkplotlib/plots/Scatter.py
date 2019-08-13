# -*- coding: utf-8 -*-
"""
Created on Sun Jul 21 00:51:34 2019

@author: Brénainn Woodsend


Scatter.py
Create a scatter plot using spheres.
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


class Sphere(SourcedPlot):
    """Plot an individual sphere."""
    def __init__(self, point, color=None, opacity=None, radius=1., fig="gcf"):
        super(Sphere, self).__init__(fig)
        
        self.source = vtk.vtkSphereSource()
        self.point = point
        self.source.SetRadius(radius)
        
        self.add_to_plot()        
        
        self.color_opacity(color, opacity)
        
    @property
    def point(self):
        return self.source.GetCenter()
    
    @point.setter
    def point(self, point):
        self.source.SetCenter(*point)
     
        
class Cursor(SourcedPlot):
    def __init__(self, point, color=None, opacity=None, radius=1, fig="gcf"):
        super(Cursor, self).__init__(fig)
        
        self.source = vtk.vtkCursor3D()
        self.source.SetTranslationMode(True)
        self.source.OutlineOff()
        
        
        self.add_to_plot() 
        
#        if radius != 1:
#            print("Warning - radius doesn't do anything")


        self.point = point

        
        self.color_opacity(color, opacity)

    @property
    def point(self):
        return self.source.GetFocalPoint()
    
    @point.setter
    def point(self, point):
        self.source.SetFocalPoint(*point)
        
        
def scatter(points, color=None, opacity=None, radius=1., use_cursors=False, fig="gcf"):
    points = np.asarray(points)
    out = np.empty(points.shape[:-1], object)
    out_flat = out.ravel()
    for (i, (xyz, c, r)) in enumerate(zip(_iter_points(points),
                                         _iter_colors(color, points.shape[:-1]),
                                         _iter_scalar(radius, points.shape[:-1]))):
        
        if use_cursors:
            cls = Cursor
        else:
            cls = Sphere
        
        out_flat[i] = cls(xyz, c, opacity, r, fig)
        
    return out
        
    
    
    
if __name__ == "__main__":
    import vtkplotlib as vpl
    import time
    
    points = np.random.uniform(-10, 10, (30, 3))

#    for i in range(3):
#        self = vpl.cursor(np.array([5, 0, 0]) * i, radius=4) 
        
    self = scatter(points,
                   color=points,
                   radius=np.abs(points[:, 0]) ** .5,
                   use_cursors=False
                   )[0]
    
#    vpl.show(False)
#    
#    for i in range(20):
#        self.source.SetRadius(np.random.random())
#        vpl.gcf().update()
#        time.sleep(.1)

    vpl.show()
    
    
    
    

