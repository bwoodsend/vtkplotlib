# -*- coding: utf-8 -*-
# =============================================================================
# Created on Sun Jul 21 15:54:56 2019
#
# @author: Brénainn Woodsend
#
#
# Arrow.py creates an arrow / quiver plot.
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
from vtk.util.numpy_support import (
                                    numpy_to_vtk,
                                    numpy_to_vtkIdTypeArray,
                                    vtk_to_numpy,
                                    )

from vtkplotlib.plots.BasePlot import SourcedPlot, _iter_colors, _iter_points, _iter_scalar
from vtkplotlib import geometry as geom


class Arrow(SourcedPlot):
    def __init__(self, start, end, length=None, width_scale=1, color=None, opacity=None, fig="gcf"):
        super().__init__(fig)

        diff = end - start
        if length == None:
            length = geom.distance(diff)

        # vtk needs a full set of axes to build about.
        # eX is just the direction the arrow is pointing in.
        # eY and eZ must be perpendicular to each other and eX. However beyond
        # that exact choice of eY and eZ does not matter. It only rotates the
        # arrow about eX which you can't see because it's (approximately) round.
        eX, eY, eZ = geom.orthogonal_bases(diff)
        arrowSource = vtk.vtkArrowSource()


        # This next bit puts the arrow where it's supposed to go
        matrix = vtk.vtkMatrix4x4()

        # Create the direction cosine matrix
        matrix.Identity()
        for i in range(3):
          matrix.SetElement(i, 0, eX[i])
          matrix.SetElement(i, 1, eY[i])
          matrix.SetElement(i, 2, eZ[i])

        # Apply the transforms
        transform = vtk.vtkTransform()
        transform.Translate(start)
        transform.Concatenate(matrix)
        transform.Scale(length, length * width_scale, length * width_scale)


        self.source = arrowSource

        self.add_to_plot()
        self.actor.SetUserMatrix(transform.GetMatrix())

        self.color_opacity(color, opacity)



def arrow(start, end, length=None, width_scale=1., color=None, opacity=None, fig="gcf"):
    """Draw (an) arrow(s) from `start` to `end`.

    :param start: The starting point(s) of the arrow(s).
    :type start: np.ndarray

    :param end: The end point(s) of the arrow(s).
    :type end:  np.ndarray

    :param length: The length of the arrow(s), defaults to None.
    :type length: number, np.ndarray, optional

    :param width_scale: How fat to make each arrow, is relative to its length, defaults to 1.0.
    :type width_scale: number, np.ndarray, optional

    :param color: The color of each arrow, defaults to white.
    :type color: str, 3-tuple, 4-tuple, np.ndarray of shape(n, 3)

    :param opacity: The translucency of each arrow, 0 is invisible, 1 is solid, defaults to solid.
    :type opacity: float

    :param fig: The figure to plot into, can be None, defaults to vpl.gcf().
    :type fig: vpl.figure, vpl.QtFigure


    :return: arrow or array of arrows
    :rtype: vtkplotlib.plots.Arrow.Arrow, np.array of Arrows


    The shapes of `start` and `end` should match. Arrow lengths are
    automatically calculated via pythagoras if not provided but can be
    overwritten by setting `length`. In this case the arrow(s) will always
    start at `start` but may not end at `end`. `length` can either be a single
    value for all arrows or an array of lengths to match the number of arrows.

    .. note::

        arrays are supported only for convenience and just use a python for
        loop. There is no speed bonus to using numpy or trying to plot in bulk
        here.

    .. seealso:: ``vpl.quiver`` for field plots.

    """

    start = np.asarray(start)
    end = np.asarray(end)

    assert start.shape == end.shape

    out = np.empty(start.shape[:-1], object)
    out_flat = out.ravel()

    for (i, s, e, l, c) in zip(range(out.size),
                                _iter_points(start),
                                _iter_points(end),
                                _iter_scalar(length, start.shape[:-1]),
                                _iter_colors(color, start.shape[:-1])):

        out_flat[i] = Arrow(s, e, l, width_scale, c, opacity, fig)

    return out_flat


def quiver(point, gradient, length=None, length_scale=1., width_scale=1., color=None, opacity=None, fig="gcf"):
    """Create an arrow from 'point' towards a direction given by 'gradient'.
    This is intended to make field/quiver plots. Arrow lengths by default are
    the magnitude of 'gradient but can be scaled with 'length_scale' or
    frozen with 'length'. See arrow's docs for more detail.

    :param point: The starting point of the arrow(s).
    :type point: np.ndarray

    :param gradient: The displacement / gradient vector.
    :type gradient: np.ndarray

    :param length: A frozen length for each arrow, defaults to None.
    :type length: NoneType, optional

    :param length_scale: A scaling factor for the length of each arrow, defaults to 1.0.
    :type length_scale: int, optional

    :param width_scale: How fat to make each arrow, is relative to its length, defaults to 1.0.
    :type width_scale: int, optional

    :param color: The color of each arrow, defaults to white.
    :type color: str, 3-tuple, 4-tuple, np.ndarray of shape(n, 3)

    :param opacity: The translucency of each arrow, 0 is invisible, 1 is solid, defaults to solid.
    :type opacity: float

    :param fig: The figure to plot into, can be None, defaults to vpl.gcf().
    :type fig: vpl.figure, vpl.QtFigure


    :return: arrow or array of arrows
    :rtype: vtkplotlib.plots.Arrow.Arrow, np.array of Arrows

    """

    if length is None:
        length = geom.distance(gradient)
    if length_scale != 1:
        length *= length_scale

    return arrow(point, point + gradient, length, width_scale, color, opacity, fig)



if __name__ == "__main__":

    import vtkplotlib as vpl

    t = np.linspace(0, 2 * np.pi)
    points = np.array([np.cos(t), np.sin(t), np.cos(t) * np.sin(t)]).T
    grads = np.roll(points, 10)

    arrows = quiver(points, grads, width_scale=.3, color=grads)

    vpl.show()
