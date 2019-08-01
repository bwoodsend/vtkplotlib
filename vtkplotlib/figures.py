# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 21:21:20 2019

@author: Brénainn Woodsend


figures.py
Provides/manages windows to render into.
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
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


from vtkplotlib.render_window import VTKRenderer


class BaseFigure(VTKRenderer):
    
    _reset_camera = True

    def reset_camera(self):
        return reset_camera(self)

    
    def show(self, block=True):
        self.start(block, self._reset_camera)

        global _figure
        if block and _figure is self:
            _figure = None
            
    def __iadd__(self, plot):
        self.add_actor(plot.actor)
        return self
        
    def __isub__(self, plot):
        self.remove_actor(plot.actor)
        return self



class Figure(BaseFigure):
    """The default figure class."""
    def __init__(self, name="vtk figure"):
        
        super().__init__(vtk.vtkRenderWindow(), vtk.vtkRenderWindowInteractor())
        self.window_name = name
        
        global _figure
        _figure = self
        
        

class QtFigure(BaseFigure, QWidget):
    """The vtk render window embedded into a QWidget. This can be embedded into
    a GUI the same way all other QWidgets are used.
    """

    def __init__(self, name="qt vtk figure", parent=None):
        QWidget.__init__(self, parent)


        self.vl = QVBoxLayout()
        self.vtkWidget = QVTKRenderWindowInteractor(self)
        self.vl.addWidget(self.vtkWidget)
        VTKRenderer.__init__(self,
                             self.vtkWidget.GetRenderWindow(),
                             self.vtkWidget.GetRenderWindow().GetInteractor())

        self.setLayout(self.vl)
        
        self.window_name = name
        
        global _figure
        _figure = self

        
        
    def show(self, block=False):
        QWidget.show(self)
        BaseFigure.show(self, block)
        self.setWindowTitle(self.window_name)

        global _figure
        if block and _figure is self:
            _figure = None
        
        
        
_figure = None

def gcf():
    """Gets the current working figure. If there isn't one it creates one. The
    new figure is always a regular Figure type (not Qt).
    """
    global _figure
    if _figure is None:
        _figure = Figure()
    return _figure


def show(block=True, fig=None):
    """Shows the figure.
    For regular figures:
        If 'block' is True then it enters interactive mode and the program
        is held until window exit.
        Otherwise the window is opened but not monitored. i.e an image 
        will appear on the screen but it wont respond to being clicked on.
        By editting the plot and calling fig.update() you can create an
        animiation but it will be non-interactive. True interactive hasn't
        been implemented yet - use the vtk example to build on top of this.
        And no you can't just run show in a background thread. It just
        doesn't work. If anyone does manage it then please let me know.
            
    For QtFigures:
        'block' is ignored. A QtFigure will become interactive when qapp.exec_()
        is called (which also blocks). Otherwise you get the same unresponsive
        window as you do above.
        
    Important - A window can not be closed by the close button until it is in
                interactive mode. Otherwise it'll just crash python. Use
                vkplotlib.close() to kill a non interactive window.
                
    For either figure type 'block' == True will reset the figure given by gcf().
    """
    
    global _figure
    current_fig = fig or gcf()
    
    current_fig.show(block)
    if block:
        _figure = None


def view(focal_point=None, camera_position=None, forwards=None, up_view=None, fig=None):
    """Set the camera view. If forwards is used then focal_point and
        camera_position are ignored.
    
        focal_point:
            np.array([x, y, z]) of the point you are looking at.
            
        camera_position:
            np.array([x, y, z]) of the point you are looking from.
            
        forwards:
            np.array([eX, eY, eZ]) 
            The direction the camera is pointing.
            
        up_view:
            np.array([eX, eY, eZ])
            roll the camera so that the up_view vector is pointing towards the 
            top of the screen.
    """
        
    fig = fig or gcf()
    camera = fig.render.GetActiveCamera()
    
    # vtk has a strange feature where if only this is specified then it 
    # is used as a direction vector instead.
    if forwards is not None:
        camera.SetPosition(*-forwards)
    
    else:
        if focal_point is not None:
            camera.SetFocalPoint(*focal_point)
            # By default a figure resets it's camera position on show. This disables that.
            fig._reset_camera = False
    
        if camera_position is not None:
            camera.SetPosition(*camera_position)
        
    if up_view is not None:
        camera.SetViewUp(*up_view)
        
        
    return camera.GetFocalPoint(), camera.GetPosition(), camera.GetViewUp()


def reset_camera(fig=None):
    """Reset the position of the camera. This does not touch the orientation.
    It pushes the camera so it whichever direction it is pointing, it is 
    pointing into the middle of where all the actors are. Then it adjusts the
    zoom so that everything fits on the screen.
    """
    (fig or gcf()).render.ResetCamera()

BaseFigure.reset_camera.__doc__ = reset_camera.__doc__
BaseFigure.show.__doc__ = show.__doc__


def save_fig(path, size=720, fig=None):
    """Take a screenshot and saves it to either a jpg or a png. jpg is
        much better suited for compressing these files than png.
    
        path:
            str or Pathlike
            Save destination
            
        scale:
            An int or a (width, hight) tuple of ints.
            Set the image dimensions in pixels. If only one dimension is given
            then it is the height and an aspect ration of 16:9 is used.
            
            
        Note that for some reason vtk can only work with multiples of 300
        pixels. 'size' will be therefore be rounded to conform to this.
            
        And no I have no idea why it spins. But vtk's example in the docks 
        does it as well so I think it's safe to say it's their problem.
    
    """
    if not isinstance(path, Path):
        path = Path(path)
        
        
    if isinstance(size, int):
        size = (size * 16) // 9, size
        
    size = tuple(round(i / 300) for i in size)
        
    fig = fig or gcf()
    renWin = fig.renWin
    # figure has to be drawn
    renWin.Render()
    
    # screenshot code:
    w2if = vtk.vtkWindowToImageFilter()
    w2if.SetInput(renWin)
    w2if.SetScale(*size) 
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
    import vtkplotlib as vpl
    
    QT = False
        
    if QT:
        app = None
        app = QApplication([])
        self = vpl.QtFigure("a qt widget figure")
        
    else:    
        self = vpl.figure("a normal vtk figure")
        
        
#    vpl.plot(np.random.uniform(-10, 10, (20, 3)))
        
    direction = np.array([1, 0, 0])
    vpl.quiver(np.array([0, 0, 0]), direction)
    vpl.view(forwards=direction)
    vpl.reset_camera()
    
#    vpl.save_fig(Path.home() / "img.jpg", 1080)
    
    self.show()
    
    
    if QT:
        app.exec_()
