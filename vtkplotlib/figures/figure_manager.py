# -*- coding: utf-8 -*-
"""
Created on Sat Aug  3 14:09:25 2019

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

import numpy as np
import os
from pathlib2 import Path

import vtk



_figure = None

_auto_fig = True


def set_auto_fig(auto=True):
    global _auto_fig
    _auto_fig = auto
    
    
def scf(figure):
    """Sets the current working figure."""
    global _figure
    _figure = figure
    

def gcf(create_new=True):
    """Gets the current working figure. If there isn't one it creates one
    unless 'create_new' is set to False in which case returns None. The new
    figure is always a regular Figure type (not a QtFigure). Returns None
    if set_auto_fig(False) has been called.
    """
    global _figure

#    print(_auto_fig)
#    print(_figure)
    if not _auto_fig:
        return
    if _figure is None and create_new:
        from .figure import Figure
        _figure = Figure()
    return _figure


class NoFigureError(Exception):
    fmt = """{} requires a figure. Create one using vpl.figure() and pass it as
    'fig' argument.""".format
    def __init__(self, name):
        super().__init__(self.fmt(name))
        


def show(block=True, fig=None):
    """Shows the figure.
    For regular figures:
        If 'block' is True then it enters interactive mode and the program
        is held until window exit.
        Otherwise the window is opened but not monitored. i.e an image 
        will appear on the screen but it wont respond to being clicked on.
        By editing the plot and calling fig.update() you can create an
        animation but it will be non-interactive. True interactive hasn't
        been implemented yet - use the vtk example to build on top of this.
        And no you can't just run show in a background thread. It just
        doesn't work. If anyone does manage it then please let me know.
            
    For QtFigures:
        'block' is ignored. A QtFigure will become interactive when qapp.exec_()
        is called (which also blocks). Otherwise you get the same unresponsive
        window as you do above.
        
    Important - A window can not be closed by the close button until it is in
                interactive mode. Otherwise it'll just crash python. Use
                vtkplotlib.close() to kill a non interactive window.
                
    For either figure type 'block' == True will reset the figure given by gcf().
    """
    
    global _figure
    current_fig = fig or gcf()
    
    if current_fig is None:
        raise NoFigureError("show")

    
    current_fig.show(block)
    if block:
        _figure = None



def view(focal_point=None, camera_position=None, camera_direction=None, up_view=None, fig=None):
    """Set the camera view. If forwards is used then focal_point and
        camera_position are ignored. 
    
        focal_point:
            np.array([x, y, z]) of the point you are looking at.
            
        camera_position:
            np.array([x, y, z]) of the point you are looking from. If 
            'focal_point' is not also given then 'camera_position' is relative
            to where VTK determines is the middle of your plots. This is 
            equivalent to setting 'camera_direction' as -camera_direction.
            
        camera_direction:
            np.array([eX, eY, eZ]) 
            The direction the camera is pointing.
            
        up_view:
            np.array([eX, eY, eZ])
            roll the camera so that the up_view vector is pointing towards the 
            top of the screen.
            
            
        This needs some serious work. It'll likely be better to manipulate the
        vtk camera directly (stored in fig.camera). You also might want to call
        vpl.reset_camera() afterwards as it seems to be the only way to reset
        the zoom automatically. An absolutely worst case scenario would be to
        use the following:
            
            vpl.view(camera_direction=...,
                     up_view=...,)        # set orientations first
            vpl.reset_camera()            # auto reset the zoom
            vpl.view(focal_point=middle_of_plot) # optionally shift the camera to where you want it.
            
    """
        
    fig = fig or gcf()
    if fig is None:
        raise NoFigureError("save_fig")

    camera = fig.camera
    
    if (camera_direction is not None or camera_position is not None) and \
        (focal_point is None):
            focal_point = np.zeros(3)
            reset_at_end = True
    else:
        reset_at_end = False
    
    # vtk's rules are if only this is specified then it 
    # is used as a direction vector instead.
    if camera_direction is not None:
        camera.SetPosition(*-camera_direction)
    
    else:
        if focal_point is not None:
            camera.SetFocalPoint(*focal_point)
            # By default a figure resets it's camera position on show. This disables that.
            fig._reset_camera = False
    
        if camera_position is not None:
            camera.SetPosition(*camera_position)
        
    if up_view is not None:
        camera.SetViewUp(*up_view)
        
    if reset_at_end:
        fig.reset_camera()
        
    return camera.GetFocalPoint(), camera.GetPosition(), camera.GetViewUp()



def reset_camera(fig=None):
    """Reset the position of the camera. This does not touch the orientation.
    It pushes the camera so it whichever direction it is pointing, it is 
    pointing into the middle of where all the actors are. Then it adjusts the
    zoom so that everything fits on the screen.
    """
    fig = (fig or gcf())
    if fig is None:
        raise NoFigureError("reset_camera")
    
    fig.render.ResetCamera()




def save_fig(path, size=720, fig=None):
    """Take a screenshot and saves it to either a jpg or a png. jpg is
        recommended as it is much better at compressing these files than png.
    
        path:
            str or Pathlike
            Save destination
            
        scale:
            An int or a (width, height) tuple of ints.
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
    if fig is None:
        raise NoFigureError("save_fig")
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
    fig = fig or gcf()
    if fig is not None:
        fig.iren.GetRenderWindow().Finalize()
        fig.iren.TerminateApp()
        scf(None)



if __name__ == "__main__":
    pass
