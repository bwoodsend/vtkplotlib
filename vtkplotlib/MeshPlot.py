# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 23:55:28 2019

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

from stl.mesh import Mesh


from vtkplotlib.BasePlot import ConstructedPlot
from vtkplotlib.figures import gcf
from vtkplotlib.nuts_and_bolts import flatten_all_but_last

class MeshPlot(ConstructedPlot):
    def __init__(self, mesh, tri_scalars=None, scalars=None, color=None, opacity=None, fig=None):
        super().__init__(fig)
        
        self.mesh = mesh
        triangles = np.empty((len(mesh), 4), np.int64)
        triangles[:, 0] = 3
        for i in range(3):
            triangles[:, i+1] = np.arange(i, len(mesh) * 3, 3)
            
        triangles = triangles.ravel()

        points = self.points = vtk.vtkPoints()
        self.update_points()

        self.poly_data.SetPoints(points)
        
        cells = vtk.vtkCellArray()
        cells.SetCells(len(triangles), numpy_to_vtkIdTypeArray(triangles))
        self.poly_data.SetPolys(cells)
        
        self.add_to_plot()
        
        self.fig.temp.append(triangles)
        
        
        self.set_scalars(scalars)
        self.set_tri_scalars(tri_scalars)
        self.color_opacity(color, opacity)
    

    def update_points(self):
        vertices = flatten_all_but_last(self.mesh.vectors)
        self.fig.temp.append(vertices)
        
        self.points.SetData(numpy_to_vtk(vertices))        

    
    def set_tri_scalars(self, tri_scalars):
        if tri_scalars is not None:
    #        scalars = np.array([tri_scalars, tri_scalars, tri_scalars]).T
            assert tri_scalars.shape == (len(self.mesh), )
            scalars = np.empty((len(tri_scalars), 3))
            for i in range(3):
                scalars[:, i] = tri_scalars
                
            self.set_scalars(scalars)
    
            
    def set_scalars(self, scalars):
        if scalars is not None:
    #        scalars[~np.isfinite(scalars)] = np.nanmean(scalars)
            if scalars.shape != (len(self.mesh), 3):
                raise ValueError("Expected (n, 3) shape array. Got {}".format(scalars.shape))
    
            self.poly_data.GetPointData().SetScalars(numpy_to_vtk(scalars.ravel()))
            self.fig.temp.append(scalars)
            
            self.mapper.SetScalarRange(np.nanmin(scalars), np.nanmax(scalars))
            
        
     
    


if __name__ == "__main__":
    import time
    import vtkplotlib as vpl

    
    fig = vpl.gcf()
    mesh = Mesh.from_file("C:/Users/Brénainn/Documents/uni/project/stl/1_mandibular.stl")
    self = vpl.mesh_plot(mesh)
    

#    self.property.SetEdgeVisibility(True)
    
#    fig.show(False)
#    
##    t0 = time.perf_counter()
#    for i in range(7):
##        self.color = np.random.random(3)
##        print(self.color)
#        self.set_tri_scalars((mesh.x[:, 0] + i) % 15 )
##        mesh.rotate(np.ones(3), .1)
#        fig.update()
#        self.update_points()
#        time.sleep(1)
#    print(time.perf_counter() - t0)
    
#    fig.show(False)
#    time.sleep(3)
#    self.color_opacity((1, 0, 0))
#    fig.renWin.Render()
#    time.sleep(3)
#    self.color_opacity((0, 1, 0))
#    [vpl.plot(i, join_ends=True, color="k") for i in mesh.vectors[-5000:]]
    
    edges = vtk.vtkExtractEdges()
    edges.SetInputData(self.poly_data)
    
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(edges.GetOutput())
    
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    
    actor.GetProperty().SetColor(1,0,0)

    
#    fig.add_actor(actor)
    fig.render.AddActor(actor)
    
    
    fig.show()
    
