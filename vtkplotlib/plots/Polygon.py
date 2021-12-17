# -*- coding: utf-8 -*-

import numpy as np

from vtkplotlib.plots.BasePlot import ConstructedPlot


class Polygon(ConstructedPlot):
    """Creates a filled polygon(s) with **vertices** as it's corners. For a 3
    dimensional **vertices** array, each 2d array within **vertices** is a separate
    polygon.

    :param vertices: Each corner of each polygon - an array with shape ``(number_of_polygons, points_per_polygon, 3)``.
    :type vertices: numpy.ndarray

    :param color: A single color for the whole the plot, defaults to white.
    :type color: str or tuple or numpy.ndarray

    :param opacity: The translucency of the plot. Ranges from ``0.0`` (invisible) to ``1.0`` (solid).
    :type opacity: float

    :param fig: The figure to plot into, use `None` for no figure, defaults to the output of `vtkplotlib.gcf()`.
    :type fig: :class:`~vtkplotlib.figure` or :class:`~vtkplotlib.QtFigure`

    :param label: Give the plot a label to use in a `legend`.
    :type label: str


    VTK renders everything as only triangles. Polygons with more than 3 sides
    are broken down by VTK into multiple triangles. For non-flat polygons with
    many sides, this *triangulation* is arbitrary.

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
