# -*- coding: utf-8 -*-
from ._version import __version__, __version_info__
from ._history import figure_history

from .figures import (
    Figure as figure,
    gcf,
    scf,
    auto_figure,
    show,
    view,
    reset_camera,
    save_fig,
    screenshot_fig,
    close,
    zoom_to_contents,
)

from .plots.Arrow import arrow, quiver
from .plots.Lines import Lines as plot
from .plots.MeshPlot import MeshPlot as mesh_plot, mesh_plot_with_edge_scalars, NUMPY_STL_AVAILABLE
from .plots.Polygon import Polygon as polygon
from .plots.ScalarBar import ScalarBar as scalar_bar
from .plots.Scatter import scatter
from .plots.Surface import Surface as surface
from .plots.Text import Text as text
from .plots.Text3D import Text3D as text3d, annotate
from .plots.Legend import Legend as legend

from .plots import BasePlot
from .plots.polydata import PolyData

from . import data, image_io, interactive, colors, geometry, nuts_and_bolts

i = interactive

color_bar = scalar_bar


def quick_test_plot(fig="gcf"):
    """A quick laziness function to create 30 random spheres.

    :param fig: The figure to plot into, use `None` for no figure, defaults to the output of `vtkplotlib.gcf()`.
    :type fig: :class:`~vtkplotlib.figure` or :class:`~vtkplotlib.QtFigure`

    .. code-block:: python

        import vtkplotlib as vpl

        vpl.quick_test_plot()
        vpl.show()

    """
    import numpy as np
    return scatter(np.random.uniform(-30, 30, (30, 3)),
                   color=np.random.rand(30, 3), fig=fig) # yapf: disable


from .nuts_and_bolts import zip_axes, unzip_axes
from .colors import TextureMap
from ._get_vtk import vtk

# Explicitly importing these can improve IDE autocompletion.
from . import _interactive, _image_io


def __getattr__(name):
    global QtFigure, QtFigure2
    if name in ("QtFigure", "QtFigure2"):
        from .figures.QtFigure import QtFigure
        from .figures.QtGuiFigure import QtFigure2
    try:
        return globals()[name]
    except KeyError:
        raise AttributeError(name) from None
