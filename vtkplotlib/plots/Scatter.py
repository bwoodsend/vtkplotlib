# -*- coding: utf-8 -*-

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
    :type points: numpy.ndarray

    :param color: The color of the markers, can be singular or per marker, defaults to white.
    :type color: str or tuple or numpy.ndarray

    :param opacity: The translucency of the plot. Ranges from ``0.0`` (invisible) to ``1.0`` (solid).
    :type opacity: float or numpy.ndarray

    :param radius: The radius of each marker.
    :type radius: float or numpy.ndarray

    :param use_cursors: If false use spheres, if true use cursors, defaults to False.
    :type use_cursors: bool

    :param fig: The figure to plot into, use `None` for no figure, defaults to the output of `vtkplotlib.gcf()`.
    :type fig: :class:`~vtkplotlib.figure` or :class:`~vtkplotlib.QtFigure`

    :param label: Give the plot a label to use in a `legend`.
    :type label: str

    :return: The marker or a `numpy.ndarray` of markers.

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
