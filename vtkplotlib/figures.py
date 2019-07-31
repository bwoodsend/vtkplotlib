# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 21:21:20 2019

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


from vtkplotlib.render_window import VTKRenderer

        


class Figure(VTKRenderer):
    def __init__(self, name="vtk figure"):
        
        super().__init__(vtk.vtkRenderWindow(), vtk.vtkRenderWindowInteractor())
        self.window_name = name
        
    def show(self, block=True):
        self.start(block)
        global _figure
        if block and _figure is self:
            _figure = None
        
        
        

class QtFigure(VTKRenderer, QWidget):
    # This is actually a vtkwidget within a qt widget
    # This can be embedded into a Qt window
    # Had to fiddle randomly a bit to get it working
    # VTK is designed to work with PyQt4 not 5 (which is not backwards 
    # compatible) so quite surprising any of this actually works

    def __init__(self, name="qt vtk figure", parent=None):
        QWidget.__init__(self, parent)

        self.frame = self#QFrame

        self.vl = QVBoxLayout()
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
        self.vl.addWidget(self.vtkWidget)
        VTKRenderer.__init__(self,
                             self.vtkWidget.GetRenderWindow(),
                             self.vtkWidget.GetRenderWindow().GetInteractor())

        self.frame.setLayout(self.vl)
        
        self.window_name = name
        
    def reset_camera(self):
        reset_camera(self)
        
        
    def show(self, block=False):
        QWidget.show(self)
        self.start()
        self.setWindowTitle(self.window_name)
        
        
        
_figure = None

def gcf():
    global _figure
    if _figure is None:
        _figure = Figure()
    return _figure


def show(block=True):
    global _figure
    current_fig = gcf()
#    if clear_fig:
#        _figure = None
#    else:
#        if isinstance(current_fig, RendererQtWidget):
#            _figure = RendererQtWidget(current_fig.app)
#        else:
#            _figure = VTKRenderer()
#        [_figure.add_actor(i) for i in current_fig.render.GetActors()]
    current_fig.start(block)
    if block:
        _figure = None


def view(focal_point=None, camera_position=None, up_view=None, fig=None):
    fig = fig or gcf()
    camera = fig.render.GetActiveCamera()
    if focal_point is not None:
        camera.SetFocalPoint(*focal_point)
    if camera_position is not None:
        camera.SetPosition(*camera_position)
    if up_view is not None:
        camera.SetViewUp(*up_view)
    return camera.GetFocalPoint(), camera.GetPosition(), camera.GetViewUp()

#def view_relative(focal_point, camera_distance, camera_direction)

def reset_camera(fig=None):
    (fig or gcf()).render.ResetCamera()


def save_fig(path, scale=1, fig=None):
    if not isinstance(path, Path):
        path = Path(path)
        
    fig = fig or gcf()
    renWin = fig.renWin
    renWin.Render()
    
    # screenshot code:
    w2if = vtk.vtkWindowToImageFilter()
    w2if.SetInput(renWin)
    w2if.SetScale((scale, scale))
    w2if.Update()

    old_path = Path.cwd()
    os.chdir(path.parent)
    if path.suffix.lower() in (".jpg", ".jpeg"):
        writer = vtk.vtkJPEGWriter()
    elif path.suffix.lower() == ".png":
        writer = vtk.vtkPNGWriter()
    else:
        raise NotImplementedError(path.suffix + " is not supported")
    writer.SetFileName(path.name)
    writer.SetInputConnection(w2if.GetOutputPort())
    writer.Write()
    os.chdir(old_path)

def close(fig=None):
    global _figure
    fig = fig or gcf()
    fig.iren.GetRenderWindow().Finalize()
    fig.iren.TerminateApp()
    _figure = None


if __name__ == "__main__":
    
#    self = Figure()
    self = QtFigure(QApplication([]))
    self.show()
