# -*- coding: utf-8 -*-
# =============================================================================
# Created on Thu Nov 14 14:30:15 2019
#
# @author: Brénainn Woodsend
#
#
# Legend.py creates a plot legend.
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
"""
"""


import numpy as np
import vtk

from vtkplotlib.plots.BasePlot import Actor2Base, BasePlot, process_color, PolyData


class Legend(Actor2Base):
    def __init__(self,
                 fig="gcf",
                 position=(.7, .7),
                 size=(.3, .3),
                 color="grey"):

        self.legend = vtk.vtkLegendBoxActor()
        self.color = color

        super().__init__(fig)
        self.actor = self.legend

        self.__actor2d_init__()

        self.position = position
        self.size = size


        self.legend.UseBackgroundOn()

        if self.fig is not None:
            self.fig += self


    @property
    def color(self):
        return self.legend.GetBackgroundColor()

    @color.setter
    def color(self, color):
        color, opacity = process_color(color)
        self.legend.SetBackgroundColor(color)
        if opacity is not None:
            self.legend.SetBackgroundOpacity(opacity)

    opacity = property(lambda self: self.legend.GetBackgroundOpacity()
                      ,lambda self, o: self.legend.SetBackgroundOpacity(o)
                        )


    @property
    def length(self):
        return self.legend.GetNumberOfEntries()

    @length.setter
    def length(self, length):
        self.legend.SetNumberOfEntries(length)

    __len__ = length.fget


    def set_entry(self, plot_data="box", label="from plot", color=None, icon="from plot", index="append"):
        if index == "append":
            index = self.length
            self.length += 1

        if plot_data == "box" and icon == "from plot":
            legendBox = vtk.vtkCubeSource()
            legendBox.Update()
            plot_data = legendBox.GetOutput()


        if isinstance(plot_data, BasePlot):

            if label == "from plot":
                label = plot_data.label

            if color is None:
                color = plot_data.color

            if icon == "from plot":
                plot_data = plot_data.polydata.vtk_polydata

        if isinstance(plot_data, vtk.vtkPolyData):
            icon = plot_data

            bounds = np.reshape(icon.GetBounds(), (3, 2))
            centre = bounds.mean(1)
            if np.abs(centre).max() > bounds.std(1).max() * .1:
                polydata = PolyData(icon).copy()
                polydata.points -= centre[np.newaxis]
                icon = polydata.vtk_polydata


        if color is not None:
            color = process_color(color)[0]
            self.legend.SetEntryColor(index, color)


#        self.legend.SetEntryIcon(index, color)
        if label != "from plot" and label is not None:
            self.legend.SetEntryString(index, label)

        if icon != "from plot" and icon is not None:
            print(index, repr(icon))
            self.legend.SetEntrySymbol(index, icon)


def test():
    import vtkplotlib as vpl

    self = Legend()


    self.set_entry(label="Blue Square", color="blue")

    sphere = vpl.scatter([0, 5, 10], color="g", fig=None)
    self.set_entry(sphere, "Green ball", )

    self.set_entry(vpl.mesh_plot(vpl.data.get_rabbit_stl()), "rabbit")
    self.set_entry(vpl.quiver(np.zeros(3), np.array([-1, 0, 1])), "right")

    vpl.show()
    globals().update(locals())
    return self



if __name__ == "__main__":
    self = test()

