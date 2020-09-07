# -*- coding: utf-8 -*-
# =============================================================================
# Created on Sun Jul 21 15:29:19 2019
#
# @author: Brénainn Woodsend
#
#
# ScalarBar.py adds a scalar/color bar.
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

from vtkplotlib._get_vtk import vtk
import numpy as np

from vtkplotlib.plots.BasePlot import Base2DPlot


class ScalarBar(Base2DPlot):
    """Create a scalar bar. Also goes by the alias `colorbar`.

    :param plot: The plot with scalars to draw a scalarbar for.

    :param title: , defaults to ''.
    :type title: str, optional

    :param fig: The figure to plot into, can be None, defaults to :meth:`vtkplotlib.gcf`.
    :type fig: :class:`vtkplotlib.figure`, :class:`vtkplotlib.QtFigure`, optional

    :return: The scalarbar object.
    :rtype: vtkplotlib.plots.ScalarBar.ScalarBar


    The **plot** argument can be the output of any ``vtkplotlib.***`` command that takes
    `scalars` as an argument.

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
