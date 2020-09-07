# -*- coding: utf-8 -*-
# =============================================================================
# Created on Sun Jul 21 21:48:12 2019
#
# @author: Brénainn Woodsend
#
#
# Polygon.py creates a filled polygon.
# Copyright (C) 2019-2020  Brénainn Woodsend
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

from vtkplotlib.plots.BasePlot import ConstructedPlot


class Polygon(ConstructedPlot):
    """Creates a filled polygon(s) with **vertices** as it's corners. For a 3
    dimensional **vertices** array, each 2d array within **vertices** is a separate
    polygon.

    :param vertices: Each corner of each polygon.
    :type vertices: np.ndarray with shape ([number_of_polygons,] points_per_polygon, 3)

    :param color: The color of whole the plot, defaults to white.
    :type color: str, 3-tuple, 4-tuple, optional

    :param opacity: The translucency of the plot, from `0` invisible to `1` solid, defaults to `1`.
    :type opacity: float, optional

    :param fig: The figure to plot into, can be None, defaults to :meth:`vtkplotlib.gcf`.
    :type fig: :class:`vtkplotlib.figure`, :class:`vtkplotlib.QtFigure`, optional

    :param label: Give the plot a label to use in legends, defaults to None.
    :type label: str, optional

    :return: A polygon object.
    :rtype: :class:`vtkplotlib.plots.Polygon.Polygon`


    VTK renders everything as only triangles. Polygons with more than 3 sides
    are broken down by VTK into multiple triangles. For non-flat polygons with
    many sides, the fragmentation doesn't look too great.

    """

    def __init__(self, vertices, scalars=None, color=None, opacity=None,
                 fig="gcf", label=None):
        super().__init__(fig)

        # The implementation of this is actually exactly the same as Lines plot
        # but sets args to polydata.polygons rather than polydata.lines

        self.shape = vertices.shape[:-1]

        args = np.arange(np.prod(self.shape)).reshape(self.shape)

        self.polydata.points = vertices.reshape((-1, 3))
        self.polydata.polygons = args

        self.label = label
        self.connect()

        self.color_opacity(color, opacity)
