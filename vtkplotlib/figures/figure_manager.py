# -*- coding: utf-8 -*-
# =============================================================================
# Created on Sat Aug  3 14:09:25 2019
#
# @author: Brénainn Woodsend
#
#
# figure_manager.py provides some general figure io operations.
# Copyright (C) 2019  Brénainn Woodsend
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# =============================================================================


from builtins import super

import numpy as np
import os
from pathlib2 import Path

import vtk
from vtk.util.numpy_support import vtk_to_numpy

try:
    # Doing this allows the current figure to be remembered if vtkplotlib get's
    # re-imported.
    _figure
except NameError:
    _figure = None

_auto_fig = True


def auto_figure(auto=None):
    """Enables/disables automatic figure management. If no parameters are
    provided then it returns the current state.

    :param auto: Defaults to None.
    :type auto: bool, optional


    On by default. Disabling causes ``vpl.gcf()`` to always return None. Meaning
    that all plot commands will not add to a figure unless told to explicitly
    using the ``fig=a_figure`` argument. This can be useful for complex scenarios
    involving multiple figures.
    """
    global _auto_fig
    if auto is None:
        return _auto_fig
    else:
        _auto_fig = auto


def scf(figure):
    """Sets the current working figure.

    :param figure: The figure or None.
    :type figure: vpl.figure, vpl.QtFigure

    """
    global _figure
    if _figure is not None:
        from vtkplotlib._history import figure_history
        figure_history.deque.append(_figure)
    _figure = figure


def gcf(create_new=True):
    """Gets the current working figure.

    :param create_new: Allow a new one to be created if none exist, defaults to True.
    :type create_new: bool, optional


    :return: The current figure or None.
    :rtype: vpl.figure, vpl.QtFigure

    If none exists then a new one gets created by ``vpl.figure()`` unless
    ``create_new=False`` in which case None is returned. Will always return None
    if ``auto_figure(False)`` has been called.
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
    """"""

    fmt = """{} requires a figure and auto_fig is disabled. Create one using
    vpl.figure() and pass it as `fig` argument. Or call vpl.auto_figure(True)
    and leave the `fig` argument as the default.""".format
    def __init__(self, name):
        super().__init__(self.fmt(name))

def gcf_check(fig, function_name):
    if fig == "gcf":
      fig = gcf()
    if fig is None:
        raise NoFigureError(function_name)
    return fig



def show(block=True, fig="gcf"):
    """Shows a figure. This is analogous to matplotlib's show function. After
    your plot commands call this to open the interactive 3D image viewer.

    :param block: , defaults to True.
    :type block: bool, optional

    :param fig: The figure to show, defaults to vpl.gcf().
    :type fig: vpl.figure, vpl.QtFigure


    If 'block' is True then it enters interactive mode and the program
    is held until window exit.
    Otherwise the window is opened but not monitored. i.e an image
    will appear on the screen but it wont respond to being clicked on.
    By editing the plot and calling fig.update() you can create an
    animation but it will be non-interactive. True interactive animation hasn't
    been implemented yet - it's on the TODO list.


    .. note::

        You might feel tempted to run show in a background thread. It
        doesn't work. If anyone does manage it then please let me know.


    .. warning::

        A window can not be closed by the close button until it is in
        interactive mode. Otherwise it'll just crash python. Use
        vtkplotlib.close() to kill a non interactive window.


    The current figure is reset on **exit** from interactive mode.
    """

    gcf_check(fig, "show").show(block)



def view(focal_point=None, camera_position=None, camera_direction=None, up_view=None, fig="gcf"):
    """Set/get the camera position/orientation.

    :param focal_point: A point the camera should point directly to, defaults to None.
    :type focal_point: np.array([x, y, z]), optional

    :param camera_position: The point the camera is situated, defaults to None.
    :type camera_position: np.array([x, y, z]), optional

    :param camera_direction: The direction the camera is pointing, defaults to None.
    :type camera_direction: np.array([eX, eY, eZ]), optional

    :param up_view: Roll the camera so that the `up_view` vector is pointing towards the
            top of the screen, defaults to None.
    :type up_view: np.array([eX, eY, eZ]), optional

    :param fig: The figure to plot into, can be None, defaults to vpl.gcf().
    :type fig: vpl.figure, vpl.QtFigure


    :return: A dictionary containing the current configuration.
    :rtype: dict


    .. note::

        This function sucks. You may be better off manipulating the
        vtk camera directly (stored in fig.camera). If you do choose this
        route, start experimenting by calling ``print(fig.camera)``. If
        anyone makes a better version of this function then please share.


    There is an unfortunate amount of implicit chaos going on here. Here are
    some hidden implications. I'm not even sure these are all true.

    1. If `forwards` is used then `focal_point` and `camera_position` are ignored.

    2. If `camera_position` is given but `focal_point` is not also given then `camera_position` is relative to where VTK determines is the middle of your plots. This is equivalent to setting `camera_direction` as ``-camera_position``.

    The following is well behaved:
    ::

        vpl.view(camera_direction=...,
                 up_view=...,)        # set orientations first
        vpl.reset_camera()            # auto reset the zoom

    """

    fig = gcf_check(fig, "view")

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
    """Reset the position and zoom of the camera so that all plots are visible.

    :param fig: The figure, defaults to vpl.gcf().
    :type fig: vpl.figure, vpl.QtFigure


    This does not touch the orientation. It pushes the camera without
    rotating it so that, whichever direction it is pointing, it is
    pointing into the middle of where all the plots are. Then it adjusts the
    zoom so that everything fits on the screen.
    """
    if fig == "gcf":
      fig = gcf()
    if fig is None:
        raise NoFigureError("reset_camera")

    fig.renderer.ResetCamera()


def screenshot_fig(magnification=1, pixels=None, fig="gcf"):
    """Take a screenshot of a figure. The image is returned as an array. To
    save a screenshot directly to a file, see vpl.save_fig.

    :param path: The path, including extension, to save to.
    :type path: str or Pathlike

    :param magnification: Image dimensions relative to the size of the render (window), defaults to 1.
    :type magnification: int or a (width, height) tuple of ints, optional

    :param pixels: Image dimensions in pixels, defaults to None.
    :type pixels: int or a (width, height) tuple of ints, optional

    :param fig: The figure screenshot, defaults to vpl.gcf().
    :type fig: vpl.figure, vpl.QtFigure


    Setting `pixels` overrides `magnification`. If only one dimension is given
    to `pixels` then it is the height and an aspect ration of 16:9 is used.
    This is to match with the 1080p/720p/480p/... naming convention.


    .. note::

        VTK can only work with integer multiples of the render size (given by
        `figure.render_size`). `pixels` will be therefore be rounded to
        conform to this.

    .. note::

        And no I have no idea why it spins. But vtk's example in the docs does
        it as well so I think it's safe to say the problem is on their side.

    """
    fig = gcf_check(fig, "screenshot_fig")

    # figure has to be drawn, including the window it goes in.
    fig.show(block=False)

    # screenshot code:
    win_to_image_filter = vtk.vtkWindowToImageFilter()
    win_to_image_filter.SetInput(fig.renWin)


    if isinstance(pixels, int):
        pixels = (pixels * 16) // 9, pixels

    if isinstance(magnification, int):
        magnification = (magnification, magnification)

    if pixels is not None:
        magnification = tuple(pixels[i] // fig.render_size[i] for i in range(2))

    try:
        win_to_image_filter.SetScale(*magnification)
    except AttributeError:
        if magnification[0] != magnification[1]:
            print("This version of VTK doesn't support seperate magnifications for height and width")
            magnification = (magnification[0], magnification[0])
        win_to_image_filter.SetMagnification(magnification[0])

    win_to_image_filter.Update()

    # Read the image as an array
    from vtkplotlib import image_io
    return image_io.vtkimagedata_to_array(win_to_image_filter.GetOutput())



def save_fig(path, magnification=1, pixels=None, fig="gcf"):
    """Take a screenshot and saves it to a file.

    :param path: The path, including extension, to save to.
    :type path: str or Pathlike

    :param magnification: Image dimensions relative to the size of the render (window), defaults to 1.
    :type magnification: int or a (width, height) tuple of ints, optional

    :param pixels: Image dimensions in pixels, defaults to None.
    :type pixels: int or a (width, height) tuple of ints, optional

    :param fig: The figure screenshot, defaults to vpl.gcf().
    :type fig: vpl.figure, vpl.QtFigure


    This just calls ``vpl.screenshot_fig`` then passes it to matplotlib's
    imsave function. See those for more information.

    The available file formats are determined by matplotlib's choice of
    backend. For JPEG, you will likely need to install PILLOW. JPEG has
    considerably better file size than PNG.

    """
    from matplotlib.pylab import imsave
    imsave(str(path), screenshot_fig(magnification, pixels, fig))



def close(fig="gcf"):
    """Close a figure.

    :param fig: The figure to close, defaults to vpl.gcf().
    :type fig: vpl.figure, vpl.QtFigure

    If the figure is the current figure then the current figure is reset.
    """
    if fig == "gcf":
      fig = gcf()

    if fig is not None:
        # This is important if the figure is ever reshown. Otherwise VTK will
        # crash.
        fig.finalise()

    if fig is gcf(False):
        scf(None)



if __name__ == "__main__":
    pass
