# -*- coding: utf-8 -*-

import numpy as np

from vtkplotlib.plots.BasePlot import ConstructedPlot
from vtkplotlib.plots.polydata import join_line_ends


class Lines(ConstructedPlot):
    """Plots a line passing through an array of points.

    :param vertices: The points to plot through.
    :type vertices: numpy.ndarray

    :param color: The color(s) of the lines, defaults to white.
    :type color: str or tuple or numpy.ndarray

    :param opacity: The translucency of the plot. Ranges from ``0.0`` (invisible) to ``1.0`` (solid).
    :type opacity: float

    :param line_width: The thickness of the lines, defaults to 1.0.
    :type line_width: float

    :param join_ends: If true, join the 1st and last points to form a closed loop, defaults to False.
    :type join_ends: bool

    :param cmap: A colormap (see `vtkplotlib.colors.as_vtk_cmap()`) to convert scalars to colors, defaults to ``rainbow``.

    :param fig: The figure to plot into, can be `None`, defaults to `vtkplotlib.gcf()`.
    :type fig: :class:`~vtkplotlib.figure` or :class:`~vtkplotlib.QtFigure`

    :param label: Give the plot a label to use in a `legend`.
    :type label: str

    :return: A lines object. Always a single object - even when plotting multiple lines.
    :rtype: `vtkplotlib.plot`

    If **vertices** is 3D then multiple separate lines are plotted. This can be
    used to plot meshes as wireframes.

    .. code-block:: python

        import vtkplotlib as vpl
        from stl.mesh import Mesh

        mesh = Mesh.from_file(vpl.data.get_rabbit_stl())
        vertices = mesh.vectors

        vpl.plot(vertices, join_ends=True, color="dark red")
        vpl.show()

    If **color** is an `numpy.ndarray` then a color per vertex is implied. The shape
    of **color** relative to the shape of **vertices** determines whether the
    colors should be interpreted as scalars, texture coordinates or RGB values.
    If **color** is either a `list`, `tuple`, or `str` then it is one color for
    the whole plot.


    .. code-block:: python

        import vtkplotlib as vpl
        import numpy as np

        # Create an octagon, using `t` as scalar values.

        t = np.arange(0, 1, .125) * 2 * np.pi
        vertices = vpl.zip_axes(np.cos(t),
                                np.sin(t),
                                0)

        # Plot the octagon.
        vpl.plot(vertices,
                 line_width=6,   # use a chunky (6pt) line
                 join_ends=True, # join the first and last points
                 color=t,        # use `t` as scalar values to color it
                 )

        # use a dark background for contrast
        fig = vpl.gcf()
        fig.background_color = "grey"

        vpl.show()

    """

    def __init__(self, vertices, color=None, opacity=None, line_width=1.0,
                 join_ends=False, cmap=None, fig="gcf", label=None):
        super().__init__(fig)
        self.connect()

        self.shape = ()
        self.join_ends = join_ends
        self.vertices = vertices
        # self.opacity = opacity
        # self.color = color
        # self.line_width = line_width
        del vertices
        self.__setstate__(locals())

    @property
    def line_width(self):
        return self.property.GetLineWidth()

    @line_width.setter
    def line_width(self, width):
        self.property.SetLineWidth(width)

    @property
    def vertices(self):
        return self.polydata.points.reshape(self.shape)

    @vertices.setter
    def vertices(self, vertices):
        vertices = np.asarray(vertices)
        self.polydata.points = vertices.reshape((-1, 3))

        if vertices.shape == self.shape:
            return

        self.shape = vertices.shape
        args = np.arange(np.prod(self.shape[:-1]), dtype=self.polydata.ID_ARRAY_DTYPE)\
                    .reshape((-1, self.shape[-2]))

        if self.join_ends:
            self.polydata.lines = join_line_ends(args)
        else:
            self.polydata.lines = args

    @property
    def color(self):
        colors = self.polydata.point_colors
        if colors is not None:
            return colors.reshape(self.shape[:-1] + (-1,))

        # TODO: fix this for MeshPlot.
        return ConstructedPlot.color.fget(self)

    @color.setter
    def color(self, c):
        if isinstance(c, np.ndarray):
            if c.shape == self.shape[:-1]:
                c = c[..., np.newaxis]
            # TODO: put a proper failsafe in here

            if c.ndim == 1:
                c = c[:, np.newaxis]

            # assert self.shape[:-1] == c.shape[:-1]
            self.polydata.point_colors = c.reshape((-1, c.shape[-1]))

            if not self._freeze_scalar_range:
                self.scalar_range = Ellipsis

        else:
            ConstructedPlot.color.fset(self, c)
            self.polydata.point_colors = None
