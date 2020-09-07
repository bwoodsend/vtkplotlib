# -*- coding: utf-8 -*-
# =============================================================================
# Created on Sun Jul 21 00:51:34 2019
#
# @author: Brénainn Woodsend
#
#
# Scatter.py creates a scatter plot using spheres.
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

from vtkplotlib._get_vtk import vtk
from vtkplotlib.plots.BasePlot import SourcedPlot, _iter_colors, _iter_points, _iter_scalar


class Sphere(SourcedPlot):
    """Plot an individual sphere."""

    def __init__(self, point, color=None, opacity=None, radius=1., fig="gcf",
                 label=None):
        super().__init__(fig)

        self.source = vtk.vtkSphereSource()
        self.connect()

        self.__setstate__(locals())

    @property
    def point(self):
        return self.source.GetCenter()

    @point.setter
    def point(self, point):
        self.source.SetCenter(*point)

    @property
    def radius(self):
        return self.source.GetRadius()

    @radius.setter
    def radius(self, r):
        self.source.SetRadius(r)


class Cursor(SourcedPlot):

    def __init__(self, point, color=None, opacity=None, radius=1, fig="gcf",
                 label=None):
        super().__init__(fig)

        self.source = vtk.vtkCursor3D()
        self.source.SetTranslationMode(True)
        self.source.OutlineOff()

        self.connect()
        self.__setstate__(locals())

    @property
    def point(self):
        return self.source.GetFocalPoint()

    @point.setter
    def point(self, point):
        self.source.SetFocalPoint(*point)

    @property
    def radius(self):
        return np.array([self.source.GetModelBounds()]).reshape(
            (3, 2)).T - self.point

    @radius.setter
    def radius(self, r):
        r = np.asarray(r)

        try:
            r = r * np.array([[-1, -1, -1], [1, 1, 1]])
            assert r.size == 6
        except Exception:
            raise ValueError()

        self.source.SetModelBounds(*(r + self.point).T.flat)


def scatter(points, color=None, opacity=None, radius=1., use_cursors=False,
            fig="gcf", label=None):
    """Scatter plot using little spheres or cursor objects.

    :param points: The point(s) to place the marker(s) at.
    :type points: np.array with ``points.shape[-1] == 3``

    :param color: The color of the markers, can be singular or per marker, defaults to white.
    :type color: str, 3-tuple, 4-tuple, np.array with same shape as **points**, optional

    :param opacity: The translucency of the plot, from `0` invisible to `1` solid, defaults to `1`.
    :type opacity: float, np.array, optional

    :param radius: The radius of each marker, defaults to 1.0.
    :type radius: float, np.array, optional

    :param use_cursors: If false use spheres, if true use cursors, defaults to False.
    :type use_cursors: bool, optional

    :param fig: The figure to plot into, can be None, defaults to :meth:`vtkplotlib.gcf`.
    :type fig: :class:`vtkplotlib.figure`, :class:`vtkplotlib.QtFigure`, optional

    :param label: Give the plot a label to use in legends, defaults to None.
    :type label: str, optional

    :return: The marker or an array of markers.
    :rtype: :class:`vtkplotlib.plots.Scatter.Sphere` or :class:`vtkplotlib.plots.Scatter.Cursor` or ``np.ndarray`` or spheres or cursors.


    Coloring by directly with scalars is not supported for scatter but you can
    do it using:

    .. code-block:: python

        from matplotlib.cm import get_cmap
        vpl.scatter(points, color=get_cmap("rainbow")(scalars))

    """

    points = np.asarray(points)
    out = np.empty(points.shape[:-1], object)
    out_flat = out.ravel()
    for (i, (xyz, c, r, l)) in enumerate(
            zip(_iter_points(points), _iter_colors(color, points.shape[:-1]),
                _iter_scalar(radius, points.shape[:-1]),
                _iter_scalar(label, points.shape[:-1]))):

        if use_cursors:
            cls = Cursor
        else:
            cls = Sphere

        out_flat[i] = cls(xyz, c, opacity, r, fig, l)

    if out.ndim:
        return out
    else:
        return out_flat[0]
