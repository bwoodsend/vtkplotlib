# -*- coding: utf-8 -*-
# =============================================================================
# Created on Sun Jul 21 15:46:53 2019
#
# @author: Brénainn Woodsend
#
#
# Text3D.py creates a 3D floating piece of text.
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



from vtkplotlib.plots.BasePlot import SourcedPlot, _iter_colors, _iter_points, _iter_scalar
from vtkplotlib.figures import gcf, show
from vtkplotlib import geometry as geom
from vtkplotlib.plots.Arrow import Arrow


class Text3D(SourcedPlot):
    """Create floating text in 3D space. Optionally can be set to orientate
    itself to follow the camera (defaults to on) with the `follow_cam`
    argument.

    :param string: The text to be shown.
    :type string:

    :param position: The position of the start of the text, defaults to (0, 0, 0).
    :type position: tuple, optional

    :param follow_cam: Automatically rotates to follow the camera, defaults to True.
    :type follow_cam: bool, optional

    :param scale: The height of one line of text, can have 3 values, defaults to 1.0.
    :type scale: number or 3-tuple of numbers, optional

    :param color: The color of the text, defaults to white.
    :type color: str, 3-tuple, 4-tuple, optional

    :param opacity: The translucency of the text, 0 is invisible, 1 is solid, defaults to solid.
    :type opacity: float, optional

    :param fig: The figure to plot into, can be None, defaults to vpl.gcf().
    :type fig: vpl.figure, vpl.QtFigure, optional


    :return: text3D plot object
    :rtype: vtkplotlib.plots.Text3D.Text3D


    .. warning::

        This can't be passed about between figures if ``follow_cam=True``
        (the default). The figure who's camera it follows is frozen to the
        figure given to it on first construction.

    .. seealso:: ``vpl.text`` for 2D text at a fixed point on the screen.
    .. seealso:: ``vpl.annotate`` for a convenient way to label features with text and an arrow.


    """
    def __init__(self, text, position=(0, 0, 0), follow_cam=True, scale=1, color=None, opacity=None, fig="gcf"):
        super().__init__(fig)
        # Create the 3D text and the associated mapper and follower (a type of
        # actor). Position the text so it is displayed over the origin of the
        # axes.


        self.source = vtk.vtkVectorText()
        self.text = text


        # This chunk is different to how most plots objects construct
        # themselves. So super().add_to_plot() wont work unfortunately.

        self.actor = vtk.vtkFollower()
        self.scale = scale
        self.position = position

        self.mapper = vtk.vtkPolyDataMapper()
        self.actor.SetMapper(self.mapper)

        self.property = self.actor.GetProperty()
        self.mapper.SetInputConnection(self.source.GetOutputPort())


        self.fig += self
        self.color_opacity(color, opacity)

        if follow_cam:
            self.actor.SetCamera(self.fig.renderer.GetActiveCamera())

    @property
    def text(self):
        return self.source.GetText()

    @text.setter
    def text(self, text):
        if not isinstance(text, str):
            text = str(text)
        self.source.SetText(text)

    position = property(lambda self: self.actor.GetPosition(),
                        lambda self, position: self.actor.SetPosition(position))

    scale = property(lambda self: self.actor.GetScale())

    @scale.setter
    def scale(self, scale):
        if np.isscalar(scale):
            scale = (scale, ) * 3
        self.actor.SetScale(*scale)




def annotate(points, text, direction, text_color="w", arrow_color="k", distance=3., text_size=1., fig="gcf"):
    """Annotate a feature with an arrow pointing at a point and a text label
    on the reverse end of the arrow. This is just a convenience call to
    ``vpl.arrow`` and ``vpl.text3d``. See there for just one or the other.

    :param points: The position of the feature where the arrow's tip should be.
    :type points: np.ndarray

    :param text: The text to put in the label.

    :param direction: The direction from the feature to the text position as a unit vector.
    :type direction: np.ndarray with shape (3,)

    :param text_color: The color of the label, defaults to 'w'.
    :type text_color: optional

    :param arrow_color:  The color of the arrow, defaults to 'k'.
    :type arrow_color: optional

    :param distance: The distance from the feature to the label, defaults to 3.0.
    :type distance: number, optional

    :param text_size: The height of one line of text, can have 3 values, defaults to 1.0.
    :type text_size: number or 3-tuple of numbers, optional

    :param fig: The figure to plot into, can be None, defaults to vpl.gcf().
    :type fig: vpl.figure, vpl.QtFigure


    :return: (arrow, text) 2-tuple
    :rtype: (Arrow, Text3D)


    The arrow points to the highest point and the text is placed at a point
    `distance` above (where above also is determined by direction).

    If `text` is not a str then it is automatically converted to one.


    .. code-block:: python

        import vtkplotlib as vpl
        import numpy as np

        # Create a ball at a point in space.
        point = np.array([1, 2, 3])
        vpl.scatter(point)

        vpl.annotate(point,
                     "This ball is at {}".format(point),
                     np.array([0, 0, 1]))
        vpl.show()


    If multiple points are given the farthest in the direction `direction` is
    selected. The idea is to try to prevent the annotations ending up in
    amongst the plots or, when plotting meshes, inside the mesh.

    .. code-block:: python

        import vtkplotlib as vpl
        import numpy as np

        # Create several balls.
        points = np.random.uniform(-30, 30, (30, 3))
        vpl.scatter(points, color=np.random.random(points.shape))

        vpl.annotate(points,
                     "This ball is the highest",
                     np.array([0, 0, 1]),
                     text_color="k",
                     arrow_color="orange"
                     )

        vpl.annotate(points,
                     "This ball is the lowest",
                     np.array([0, 0, -1]),
                     text_color="rust",
                     arrow_color="hunter green"
                     )

        vpl.show()


    """

    point = geom.highest(points, direction)
    text_point = point + distance * direction
    return (Arrow(text_point, point,
                  color=arrow_color, fig=fig),
            Text3D(text, text_point,
                   color=text_color, scale=text_size, fig=fig))


def test():
    import vtkplotlib as vpl

#    self = vpl.text3d("some text", follow_cam=True)

    point = np.array([1, 2, 3])
    vpl.scatter(point)

    arrow, text = vpl.annotate(point, point, np.array([0, 0, 1]))

    globals().update(locals())

    vpl.show()




if __name__ == "__main__":
    test()
