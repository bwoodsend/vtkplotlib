# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 21:17:35 2019

@author: Brénainn Woodsend


render_window.py
Provides the render window of a figure.
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

from vtkplotlib import _vtk_errors, nuts_and_bolts


class VTKRenderer(object):
    """This is a figure without all the extra methods attached. All Figure classes
    with inherit from this.

    This class handles creating and linking of:
        self.renWin = The outer box/window (with the close button)
        self.renderer = Shows the actual 2D image of the plot
        self.iren = The interactor is in charge of responding to clicking on the plot

    """
    window_name = ""
    def __init__(self):

        # Create a renderwindow
        # The render window can either be vtk's default window type or
        # a special PyQt compatible one
#        if window is None:
#            self.renWin = vtk.vtkRenderWindow()
#        else:
#            self.renWin = window

        # Create a renderer
        self.renderer = vtk.vtkRenderer()

        self.background_color = "light grey"#20, 50, 100


        self.camera = self.renderer.GetActiveCamera()



    @nuts_and_bolts.init_when_called
    def renWin(self):
        return vtk.vtkRenderWindow()

    @nuts_and_bolts.init_when_called
    def iren(self):
        iren = vtk.vtkRenderWindowInteractor()
        iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        return iren

    def connect(self):
        self.renWin.AddRenderer(self.renderer)

        self.iren.SetRenderWindow(self.renWin)


        _vtk_errors.handler.attach(self.renWin)
        _vtk_errors.handler.attach(self.renderer)


    def _start_interactive(self):
        # Enable user interface interactor
        # This needs to happen after any Qt show calls (if using Qt)
        self.iren.Initialize()

        self.iren.Start()
        self.finalise()

    def _show_window(self):
        self.connect()
        self.update()




    def update(self):
        self.renWin.Render()
        self.renWin.SetWindowName(self.window_name)


    def start(self,  block=True, reset_camera=True):
        self._show_window()

        if reset_camera:
            self.renderer.ResetCamera()


        if block:
            self._start_interactive()




    def finalise(self):
        self.renWin.Finalize()
        self.renWin.RemoveRenderer(self.renderer)
        del self.renWin
        del self.iren


#
#    def update(self):
#        """Redraw the plot to reflect any new/altered plots."""
#        self.start(False, False)


    def _add_actor(self, actor):
        self.renderer.AddActor(actor)

    def _remove_actor(self, actor):
        self.renderer.RemoveActor(actor)


    @property
    def background_color(self):
        return self.renderer.GetBackground()

    @background_color.setter
    def background_color(self, color):
        from vtkplotlib.colors import process_color

        color, opacity = process_color(color)
        if color is not None:
            self.renderer.SetBackground(*color)
        if opacity is not None:
            self.renderer.SetBackgroundAlpha(opacity)


    def __del__(self):
        # This prevents a vtk error dialog from popping up.
        self.renderer.RemoveAllViewProps()
        del self.renderer

        self.renWin.Finalize()
        del self.renWin




if __name__ == "__main__":
    import vtkplotlib as vpl

    self = vpl.figures.render_window.VTKRenderer()

    [self._add_actor(i.actor) for i in vpl.quick_test_plot()]
    self.start()

    self.finalise()
    self.start()