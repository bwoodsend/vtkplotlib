# -*- coding: utf-8 -*-

from vtkplotlib._get_vtk import vtk
import numpy as np

from vtkplotlib.plots.BasePlot import Base2DPlot


class ScalarBar(Base2DPlot):
    """Create a scalar bar. Also goes by the alias `color_bar`.

    :param plot: The plot with scalars to draw a scalarbar for.

    :param title: An optional heading for the scalar bar.
    :type title: str

    :param fig: The figure to plot into, use `None` for no figure, defaults to the output of `vtkplotlib.gcf()`.
    :type fig: :class:`~vtkplotlib.figure` or :class:`~vtkplotlib.QtFigure`

    :return: The scalarbar object.
    :rtype: `vtkplotlib.scalar_bar`


    The **plot** argument can be the output of any ``vtkplotlib.***`` command that takes
    **scalars** as an argument.

    """

    def __init__(self, plot, title="", fig="gcf"):

        super().__init__(fig)

        self.actor = vtk.vtkScalarBarActor()
        self.actor.SetTitle(title)

        self.actor.SetNumberOfLabels(6)

        self.__actor2d_init__()

        self.lookup_table = plot.mapper.GetLookupTable()
        if self.lookup_table.GetTable().GetNumberOfTuples() == 0:
            # ForceBuild resets it as well as building it. Thus overwriting any
            # existing colormap. Only build if it has not already been built.
            self.lookup_table.ForceBuild()
        self.actor.SetLookupTable(self.lookup_table)

        self.fig.renderer.AddActor2D(self.actor)
        self.fig.plots.add(self)

        self.set_horizontal = self.actor.SetOrientationToHorizontal
        self.set_vertical = self.actor.SetOrientationToVertical
