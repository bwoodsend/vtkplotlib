# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 21:17:35 2019

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
from vtk.util.numpy_support import (
                                    numpy_to_vtk,
                                    numpy_to_vtkIdTypeArray,
                                    vtk_to_numpy,
                                    )




class VTKRenderer(object):
    def __init__(self, window=None, window_interactor=None):

        # Create a renderwindow
        # The render window can either be vtk's default window type or 
        # a special PyQt compatible one
        if window is None:
            self.renWin = vtk.vtkRenderWindow()
        else:
            self.renWin = window
        
        # Create a renderer
        self.render = vtk.vtkRenderer()
        # And add it to the render window
        self.renWin.AddRenderer(self.render)
        self.render.SetBackground(tuple(np.array([20, 50, 100]) / 256))
        
        # Create a renderwindowinteractor
        # The render window interactor can either be vtk's default window type or 
        # a special PyQt compatible one
        if window_interactor is None:
            iren = vtk.vtkRenderWindowInteractor()
        else:
            iren = window_interactor
            
#        print(iren)
        iren.SetRenderWindow(self.renWin)
        iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())

        
        self.iren = iren
        self.window_name = ""
        
        self.temp = []
        
        
    def start(self, block=True):
        # Enable user interface interactor
        # This needs to happen after some of the Qt stuff is done
        self.iren.Initialize()
        self.renWin.Render()
        self.renWin.SetWindowName(self.window_name)
        if block:
            self.iren.Start()
            
    def update(self):
        self.renWin.Render()
        

        
    def add_actor(self, actor):
        self.render.AddActor(actor)
        
    def remove_actor(self, actor):
        self.render.RemoveActor(actor)
        
        





if __name__ == "__main__":

    self = VTKRenderer()
    self.start()
