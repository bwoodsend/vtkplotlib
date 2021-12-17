# -*- coding: utf-8 -*-

from vtkplotlib._get_vtk import vtk
import numpy as np

from vtkplotlib.figures import gcf
from vtkplotlib.colors import as_rgb_a
from vtkplotlib.plots.polydata import PolyData
from vtkplotlib.nuts_and_bolts import init_when_called


class BasePlot(object):
    """A base class for all plots in vtkplotlib. This tries to handle all the
    common steps involved in constructing and linking the vtk pipeline. Also
    setter/getters for very generic attributes like color can go here.
    """

    def __init__(self, fig="gcf"):
        self.fig = fig
        self.label = None

        self.actor = vtk.vtkActor()

    @property
    def fig(self):
        return self._fig

    @fig.setter
    def fig(self, fig):
        if fig == "gcf":
            fig = gcf()
        self._fig = fig

    def __setstate__(self, state):
        [setattr(self, key, val) for (key, val) in state.items()
         if key != "self" and val is not None] # yapf: disable

    @init_when_called
    def mapper(self):
        return vtk.vtkPolyDataMapper()

    def connect(self):
        self.actor.SetMapper(self.mapper)

        self.property = self.actor.GetProperty()
        if self.fig is not None:
            self.fig.add_plot(self)

    def color_opacity(self, color=None, opacity=None):
        prop = self.property

        color, opacity = as_rgb_a(color, opacity)

        if opacity is not None:
            prop.SetOpacity(opacity)

        if color is not None:
            prop.SetColor(color)

    def __hash__(self):
        return hash(id(self))

    @property
    def color(self):
        return self.property.GetColor()

    @color.setter
    def color(self, x):
        self.color_opacity(x)

    @property
    def opacity(self):
        """Set / get the translucency. 0 is invisible, 1 is solid."""
        return self.property.GetOpacity()

    @opacity.setter
    def opacity(self, x):
        if x is None:
            x = 1
        self.property.SetOpacity(x)

    @property
    def visible(self):
        """Shows (=True) / hides (=False) the plot object"""
        return self.actor.GetVisibility()

    @visible.setter
    def visible(self, x):
        self.actor.SetVisibility(x)

    def quick_show(self):
        from vtkplotlib import gcf, scf, figure
        old_gcf = gcf(False)
        fig = figure(name=repr(self))
        fig += self
        fig.show()
        scf(old_gcf)


#    @property
#    def polydata(self):
#        raise TypeError("{} type objects can't produce a polydata object.".format(type(self)))


class SourcedPlot(BasePlot):
    """Bases plots that have a source. This source is a physical object that
    must be converted/approximated into a tri-mesh surface before it can proceed
    further down the pipeline. E.g a sphere or an arrow. The source provides
    it's own conversion to triangles with source.GetOutputPort(). This class
    is just to handle the slightly different way of connecting the pipeline."""

    def connect(self):
        super().connect()
        self.mapper.SetInputConnection(self.source.GetOutputPort())

    @property
    def polydata(self):
        self.source.Update()
        return PolyData(self.source.GetOutput())


class ConstructedPlot(BasePlot):
    """Bases plots that don't have a source. Rather have to be constructed
    manually into a vtk.vtkPolyData object (generic bucket class for storing
    points/lines/surfaces ...).
    """

    def __init__(self, fig="gcf"):
        super().__init__(fig)
        self.polydata = PolyData()
        self._freeze_scalar_range = False

    def connect(self):
        super().connect()

        if vtk.VTK_MAJOR_VERSION <= 5:
            self.mapper.SetInput(self.polydata.vtk_polydata)
        else:
            self.mapper.SetInputData(self.polydata.vtk_polydata)

    @property
    def mapper(self):
        return self.polydata.mapper

    @property
    def scalar_range(self):
        return self.polydata.scalar_range

    @scalar_range.setter
    def scalar_range(self, range):
        self.polydata.scalar_range = range
        if range is not None or range is not Ellipsis:
            self._freeze_scalar_range = True

    cmap = PolyData.cmap


class Base2DPlot(BasePlot):

    def __actor2d_init__(self):

        self.actor.GetPositionCoordinate(
        ).SetCoordinateSystemToNormalizedDisplay()
        self.actor.GetPosition2Coordinate(
        ).SetCoordinateSystemToNormalizedDisplay()

    @property
    def position(self):
        """The 2D position of the left bottom corner."""
        return np.array(self.actor.GetPositionCoordinate().GetValue())

    @position.setter
    def position(self, position):
        self.actor.GetPositionCoordinate().SetValue(*position)

    @property
    def size(self):
        """The 2D position of the left bottom corner."""
        return np.array(self.actor.GetPosition2Coordinate().GetValue())

    @size.setter
    def size(self, size):
        self.actor.GetPosition2Coordinate().SetValue(*size)


def _iter_points(points):
    """Fixes the array shape to (n, 3)."""
    points = np.asarray(points)
    return points.reshape((-1, 3))


def _iter_colors(colors, shape):
    """Check if colors is a single value or is to be iterated over. If it is
    single then creates a generator that yields that value repeatedly."""
    size = int(np.prod(shape))

    if colors is None:
        return (None for i in range(size))

    if isinstance(colors, (tuple, list, str)):
        return (colors for i in range(size))

    colors = np.asarray(colors)

    if colors.dtype == object:
        raise ValueError("colors type not understood")

    if colors.shape[:-1] == shape:
        return colors.reshape((-1, colors.shape[-1]))
    else:
        print(colors, shape)
        raise ValueError("colors type not understood")


def _iter_scalar(s, shape):
    size = int(np.prod(shape))

    arr = np.asarray(s)
    if arr.shape == ():
        return (s for i in range(size))
    else:
        return arr.flat


if __name__ == "__main__":
    pass
