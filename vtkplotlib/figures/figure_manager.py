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
from builtins import super

import numpy as np
import os
from pathlib2 import Path

import vtk
from vtk.util.numpy_support import vtk_to_numpy


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
    fmt = """{} requires a figure and auto_fig is disabled. Create one using
    vpl.figure() and pass it as `fig` argument. Or call vpl.set_auto_fig(True)
    and leave the `fig` argument as the defualt.""".format
    def __init__(self, name):
        super().__init__(self.fmt(name))

def gcf_check(fig, function_name):
    if fig == "gcf":
      fig = gcf()
    if fig is None:
        raise NoFigureError("save_fig")
    return fig



def show(block=True, fig="gcf"):
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

    gcf_check(fig, "show").show(block)



def view(focal_point=None, camera_position=None, camera_direction=None, up_view=None, fig="gcf"):
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

    fig = gcf_check(fig, "save_fig")

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
        camera.SetPosition(*-np.asarray(camera_direction))

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

    return dict(focal_point=camera.GetFocalPoint(),
                camera_position=camera.GetPosition(),
                up_view=camera.GetViewUp())



def reset_camera(fig="gcf"):
    """Reset the position of the camera. This does not touch the orientation.
    It pushes the camera so it whichever direction it is pointing, it is
    pointing into the middle of where all the actors are. Then it adjusts the
    zoom so that everything fits on the screen.
    """
    if fig == "gcf":
      fig = gcf()
    if fig is None:
        raise NoFigureError("reset_camera")

    fig.render.ResetCamera()


def screenshot_fig(magnification=1, pixels=None, fig="gcf"):

    if isinstance(pixels, int):
        pixels = (pixels * 16) // 9, pixels

    if isinstance(magnification, int):
        magnification = (magnification, magnification)

    if pixels is not None:
        magnification = tuple(pixels[i] // fig.render_size[i] for i in range(2))


    if fig == "gcf":
      fig = gcf()
    if fig is None:
        raise NoFigureError("save_fig")

    # figure has to be drawn
    fig.update()

    # screenshot code:
    win_to_image_filter = vtk.vtkWindowToImageFilter()
    win_to_image_filter.SetInput(fig.renWin)
    try:
        win_to_image_filter.SetScale(*magnification)
    except AttributeError:
        win_to_image_filter.SetMagnification(magnification[0])
    win_to_image_filter.Update()


    win_to_image_filter.Update()

    # Read the image as an array
    array = vtk_to_numpy(win_to_image_filter.GetOutput().
                         GetPointData().
                         GetArray(0)).reshape(fig.render_size[::-1] + (3,))

    return array[::-1]



def save_fig(path, magnification=1, pixels=None, fig="gcf"):
    """Take a screenshot and saves it to either a jpg or a png. jpg is
        recommended as it is much better at compressing these files than png.

        path:
            str or Pathlike
            Save destination

        magnification:
            An int or a (width, height) tuple of ints.
            Set the image dimensions relative to the size of the render (window).


        pixels:
            An int or a (width, height) tuple of ints.
            Set the image dimensions in pixels. If only one dimension is given
            then it is the height and an aspect ration of 16:9 is used. Overides
            `magnification` if given.


        Note that VTK can only work with integer multiples of the render size
        (given by figure.render_size). 'pixels' will be therefore be rounded to
        conform to this.

        And no I have no idea why it spins. But vtk's example in the docs does
        it as well so I think it's safe to say the problem is on their side.

    """
    from matplotlib.pylab import imsave
    imsave(str(path), screenshot_fig(magnification, pixels, fig))



def close(fig="gcf"):
    if fig == "gcf":
      fig = gcf()
    if fig is not None:
        fig.renWin.Finalize()
        fig.iren.TerminateApp()
    if fig is gcf(False):
        scf(None)



if __name__ == "__main__":
    pass
