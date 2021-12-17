# -*- coding: utf-8 -*-

import numpy as np
import sys
import os
from pathlib import Path

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


    :param x: The x components - a 2D array with shape ``(m, n)``.
    :type x: numpy.ndarray

    :param y: The y components - a 2D array with shape ``(m, n)``.
    :type y: numpy.ndarray

    :param z: The z components - a 2D array with shape ``(m, n)``.
    :type z: numpy.ndarray

    :param scalars: Per-point scalars, texturemap coordinates or RGB colors - an array with shape ``(m, n)``, ``(m, n, 2)`` or ``(m, n, 3)``.
    :type scalars: numpy.ndarray

    :param color: A single color (see `vtkplotlib.colors.as_rgb_a()`) for the plot, defaults to white.
    :type color: str or tuple or numpy.ndarray

    :param opacity: The translucency of the plot. Ranges from 0.0 (invisible) to 1.0 (solid).
    :type opacity: float

    :param cmap: A colormap (see `vtkplotlib.colors.as_vtk_cmap()`) to convert scalars to colors, defaults to ``'rainbow'``.

    :param fig: The figure to plot into, use `None` for no figure, defaults to the output of `vtkplotlib.gcf()`.
    :type fig: :class:`~vtkplotlib.figure` or :class:`~vtkplotlib.QtFigure`

    :param label: Give the plot a label to use in a `legend`.
    :type label: str

    :return: The surface object.
    :rtype: `vtkplotlib.surface`


    .. seealso::

        `vtkplotlib.mesh_plot()` for a surface made out of triangles or
        `vtkplotlib.polygon()` for a surface made out of polygons.

    This is the only function in `vtkplotlib` that takes it's ``(x, y, z)``
    components as separate arguments. **x**, **y** and **z** should be 2D
    arrays with matching shapes. This is typically achieved by using
    ``phi, theta = np.meshgrid(phis, thetas)`` then calculating ``x``, ``y`` and
    ``z`` from ``phi`` and ``theta``.

    Here is a rather unexciting example:

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


    .. seealso:: A parametrically constructed object plays well with a `vtkplotlib.colors.TextureMap`.

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
