# -*- coding: utf-8 -*-
# =============================================================================
# Created on Sun Jul 21 15:47:18 2019
#
# @author: Brénainn Woodsend
#
#
# Text.py puts text onto the render-window.
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

import vtk
import numpy as np
from matplotlib import colors
import os
import sys
from pathlib2 import Path
from vtk.util.numpy_support import (
                                    numpy_to_vtk,
                                    numpy_to_vtkIdTypeArray,
                                    vtk_to_numpy,
                                    )



from vtkplotlib.plots.BasePlot import BasePlot

class Text(BasePlot):
    """2D text at a fixed point on the window (independent of camera
    position / orientation).

    :param text_str: The text, converts to string if not one already.
    :type text_str: str, object

    :param position: The ``(x, y)`` position in pixels on the screen, defaults to ``(0, 0)`` (left, bottom).
    :type position: 2-tuple of ints, optional

    :param fontsize: Text height (ignoring tails) in pixels, defaults to 18.
    :type fontsize: int, optional

    :param color: The color of the text, defaults to white.
    :type color: str, 3-tuple, 4-tuple, optional

    :param opacity: The translucency of the text, 0 is invisible, 1 is solid, defaults to solid.
    :type opacity: float, optional

    :param fig: The figure to plot into, can be None, defaults to vpl.gcf().
    :type fig: vpl.figure, vpl.QtFigure, optional


    :return: The text plot object.
    :rtype: vtkplotlib.plots.Text.Text


    The text doesn't resize or reposition itself when the window is resized.
    It's on the todo list.

    .. seealso:: ``vpl.text3D``

    """
    def __init__(self, text_str, position=(0, 0), fontsize=18, use_pixels=False,
                 color=(1, 1, 1), opacity=None, fig="gcf"):
        # create a text actor
        super().__init__(fig)

        self.actor = vtk.vtkTextActor()

        self.text = text_str

        self.use_pixels = use_pixels

        self.property = self.actor.GetTextProperty()

        self.property.SetFontFamilyToArial()
        self.property.SetFontSize(fontsize)
        self.color_opacity(color, opacity)

        self.actor.SetPosition(*position)

        # assign actor to the renderer
        self.fig += self

    # TODO: make this work
#    @property
#    def position(self):
#        position = self._position
#        if self.use_pixels:
#            return position
#        else:
#            return tuple(i / j for (i, j) in zip(position, self.fig.render_size))
#
#    @position.setter
#    def position(self, position):
#        if self.use_pixels:
#            self._position = position
#        else:
#            self._position = tuple(int(i * j) for (i, j) in zip(position, self.fig.render_size))

    @property
    def text(self):
        self.actor.GetInput()

    @text.setter
    def text(self, text_str):
        if not isinstance(text_str, str):
            text_str = str(text_str)
        self.actor.SetInput(text_str)


def resize_event_cb(*args):
    print(args)
    self.actor.SetPosition(*(i // 2 for i in fig.render_size))


if __name__ == "__main__":
    import vtkplotlib as vpl
    import vtk

    fig = vpl.figure()
    fig.renWin.AddObserver(vtk.vtkCommand.ModifiedEvent, resize_event_cb)
    self = vpl.text("eggs", (100, 200))
    vpl.show()
