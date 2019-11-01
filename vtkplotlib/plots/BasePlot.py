# -*- coding: utf-8 -*-
# =============================================================================
# Created on Sat Jul 20 23:46:41 2019
#
# @author: Brénainn Woodsend
#
#
# BasePlot.py provides some base classes for plot objects
# Copyright (C) 2019  Brénainn Woodsend
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

import vtk
import numpy as np
import os
import sys
from pathlib2 import Path

from vtkplotlib.figures import gcf
from vtkplotlib.colors import process_color
from vtkplotlib import nuts_and_bolts
from vtkplotlib.plots.polydata import PolyData



class BasePlot(object):
    """A base class for all plots in vtkplotlib. This tries to handle all the
    common steps involved in constructing and linking the vtk pipeline. Also
    setter/getters for very generic attributes like color can go here.
    """

    def __init__(self, fig="gcf"):
        if fig == "gcf":
          fig = gcf()
        self.fig = fig
        self.temp = []

        self.mapper = vtk.vtkPolyDataMapper()

        self.actor = vtk.vtkActor()


    def add_to_plot(self):
        self.actor.SetMapper(self.mapper)

        self.property = self.actor.GetProperty()
        if self.fig is not None:
            self.fig.add_plot(self)


    def color_opacity(self, color=None, opacity=None):
        prop = self.property

        color, opacity = process_color(color, opacity)

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
        self.property.SetOpacity(x)

    @property
    def visible(self):
        """Shows (=True) / hides (=False) the plot object"""
        return self.actor.GetVisibility()

    @visible.setter
    def visible(self, x):
        self.actor.SetVisibility(x)




class SourcedPlot(BasePlot):
    """Bases plots that have a source. This source is a physical object that
    must be converted/approximated into a tri-mesh surface before it can proceed
    further down the pipeline. E.g a sphere or an arrow. The source provides
    it's own conversion to triangles with source.GetOutputPort(). This class
    is just to handle the slightly different way of connecting the pipeline."""
    def add_to_plot(self):
        super().add_to_plot()
        self.mapper.SetInputConnection(self.source.GetOutputPort())


class ConstructedPlot(BasePlot):
    """Bases plots that don't have a source. Rather have to be constructed
    manually into a vtk.vtkPolyData object (generic bucket class for storing
    points/lines/surfaces ...).
    """
    def __init__(self, fig="gcf"):
        super().__init__(fig)
        self.polydata = PolyData()


    def add_to_plot(self):
        super().add_to_plot()
        if self.polydata._scalar_mode != 1:
            self.mapper.SetColorMode(vtk.VTK_COLOR_MODE_DIRECT_SCALARS)

        if vtk.VTK_MAJOR_VERSION <= 5:
            self.mapper.SetInput(self.polydata.vtk_polydata)
        else:
            self.mapper.SetInputData(self.polydata.vtk_polydata)


    def set_scalar_range(self, range=None):
        if range is None:
            range = self.polydata.point_colors
        self.mapper.SetScalarRange(np.nanmin(range), np.nanmax(range))

#    @property
#    def scalar_mode(self):
#        return self.mapper.GetScalarModeAsString()
#
#    @property
#    def color_mode(self):
#        return self.mapper.GetColorModeAsString()

#    SCALAR_MODES = {vtk.VTK_SCALAR_MODE_INDEX: "index???",
#                    vtk.VTK_SCALAR_MODE_USE_POINT_DATA: "point_scalars",
#                    vtk.VTK_SCALAR_MODE_USE_CELL_DATA: "polygon_scalars",
#                    }


#    @property
#    def point_scalars(self):
#        if self.scalar_mode == "point_scalars":
#            return self.polydata.point_scalars
#
#    @point_scalars.setter
#    def point_scalars(self, scalars):
#        self.mapper.SetScalarModeToUsePointData()
#        self.polydata.point_scalars = scalars
#
#    @property
#    def polygon_scalars(self):
#        if self.scalar_mode == "polygon_scalars":
#            return self.polydata.polygon_scalars
#
#    @polygon_scalars.setter
#    def polygon_scalars(self, scalars):
#        self.mapper.SetScalarModeToUseCellData()
#        self.polydata.polygon_scalars = scalars







def _iter_points(points):
    """Fixes the array shape to (n, 3)."""
    points = np.asarray(points)
    return nuts_and_bolts.flatten_all_but_last(points)


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
        return nuts_and_bolts.flatten_all_but_last(colors)

    else:
        raise ValueError("colors type not understood")


def _iter_scalar(s, shape):
    size = int(np.prod(shape))

    s = np.asarray(s)
    if s.shape == ():
        return (s for i in range(size))
    else:
        return s.flat




if __name__ == "__main__":
    pass
