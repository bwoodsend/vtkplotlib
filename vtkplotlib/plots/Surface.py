# -*- coding: utf-8 -*-
# =============================================================================
# Created on Sun Sep  1 01:23:38 2019
#
# @author: Brénainn Woodsend
#
#
# Surface.py plot a 3D parametrically described surface.
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
import sys
import os
from pathlib2 import Path

from vtkplotlib.plots.BasePlot import ConstructedPlot
from vtkplotlib import nuts_and_bolts


class Surface(ConstructedPlot):
    """Create a parametrically defined surface. This is intended for
    visualising mathematical functions of the form

    .. math::

        z = f(x, y)

    or

    .. math::

        x = f(\\phi, \\theta) \\quad
        y = g(\\phi, \\theta) \\quad
        z = h(\\phi, \\theta) \\quad


    :param x: x components.
    :type x: 2D np.ndarray with shape (m, n)

    :param y: y components.
    :type y: 2D np.ndarray with shape (m, n)

    :param z: z components.
    :type z: 2D np.ndarray with shape (m, n)

    :param scalars: per-point scalars / texturemap coordinates / RGB colors, defaults to None.
    :type scalars: np.ndarray with shape (m, n [, 1 or 2 or 3]), optional

    :param color: The color of the plot, defaults to white.
    :type color: str, 3-tuple, 4-tuple, optional

    :param opacity: The translucency of the plot, from `0` invisible to `1` solid, defaults to `1`.
    :type opacity: float, optional

    :param cmap: Colormap to use for scalars, defaults to `rainbow`.
    :type cmap: matplotlib cmap, `vtkLookupTable`_, or similar see :meth:`vtkplotlib.colors.as_vtk_cmap`, optional

    :param fig: The figure to plot into, can be None, defaults to :meth:`vtkplotlib.gcf`.
    :type fig: :class:`vtkplotlib.figure`, :class:`vtkplotlib.QtFigure`, optional

    :param label: Give the plot a label to use in legends, defaults to None.
    :type label: str, optional

    :return: The surface object.
    :rtype: :class:`vtkplotlib.surface`


    .. seealso::

        :meth:`vtkplotlib.mesh_plot` for a surface made out of triangles or
        :meth:`vtkplotlib.polygon` for a surface made out of polygons.

    This is the only function in `vtkplotlib` that takes it's (x, y, z)
    components as separate arguments. **x**, **y** and **z** should be 2D
    arrays with matching shapes. This is typically achieved by using
    ``phi, theta = np.meshgrid(phis, thetas)`` then calculating x, y and z
    from ``phi`` and ``theta``. Here is a rather unexciting example.

    .. code-block:: python

        import vtkplotlib as vpl
        import numpy as np

        phi, theta = np.meshgrid(np.linspace(0, 2 * np.pi, 1024),
                             np.linspace(0, np.pi, 1024))


        x = np.cos(phi) * np.sin(theta)
        y = np.sin(phi) * np.sin(theta)
        z = np.cos(theta)

        vpl.surface(x, y, z)

        vpl.show()


    .. seealso:: A parametrically constructed object plays well with a :class:`vtkplotlib.colors.TextureMap`.

    """

    def __init__(self, x, y, z, scalars=None, color=None, opacity=None,
                 texture_map=None, cmap=None, fig="gcf", label=None):
        super().__init__(fig)

        points = nuts_and_bolts.zip_axes(x, y, z)
        flat_points = points.reshape((-1, 3))

        shape = points.shape[:-1]
        unflatten_map = np.arange(
            np.prod(shape), dtype=self.polydata.ID_ARRAY_DTYPE).reshape(shape)

        corners = (
            unflatten_map[:-1, :-1],
            unflatten_map[1:, :-1],
            unflatten_map[1:, 1:],
            unflatten_map[:-1, 1:],
        )

        args = np.concatenate([i[..., np.newaxis] for i in corners], axis=-1)

        self.polydata.points = flat_points
        self.polydata.polygons = args
        self.polydata.texture_map = texture_map
        self.colors = scalars
        self.cmap = cmap

        self.connect()
        self.color_opacity(color, opacity)
        self.label = label
        self.scalar_range = Ellipsis

    @property
    def colors(self):
        return self.polydata.point_colors

    @colors.setter
    def colors(self, s):
        if s is not None:
            s = np.asarray(s)
            if s.ndim < 3:
                s = s[..., np.newaxis]
            s = s.reshape((-1, s.shape[-1]))
        self.polydata.point_colors = s
