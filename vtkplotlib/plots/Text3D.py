# -*- coding: utf-8 -*-
"""
Created on Sun Jul 21 15:46:53 2019

@author: Brénainn Woodsend


Text3D.py
Creates a 3D text plot.
Copyright (C) 2019  Brénainn Woodsend

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from builtins import super

import vtk
import numpy as np
#from matplotlib import pylab as plt
from matplotlib import colors
import os
import sys
from pathlib2 import Path
from vtk.util.numpy_support import (
                                    numpy_to_vtk,
                                    numpy_to_vtkIdTypeArray,
                                    vtk_to_numpy,
                                    )



from vtkplotlib.plots.BasePlot import SourcedPlot, _iter_colors, _iter_points, _iter_scalar
from vtkplotlib.figures import gcf, show
from vtkplotlib import geometry as geom
from vtkplotlib.plots.Arrow import Arrow


class Text3D(SourcedPlot):
    """Create a text actor in 3D space. Optionally can be set to orientate
    itself to follow the camera (defaults to on).
    """
    def __init__(self, string, position=(0, 0, 0), follow_cam=True, scale=1, color=None, opacity=None, fig="gcf"):
        super().__init__(fig)
        # Create the 3D text and the associated mapper and follower (a type of
        # actor). Position the text so it is displayed over the origin of the
        # axes.
        if np.isscalar(scale):
            scale = (scale, ) * 3

        if not isinstance(string, str):
            string = str(string)

        self.source = vtk.vtkVectorText()
        self.source.SetText(string)


        # This chunk is different to how most plots objects construct their
        # pipeline. So super().add_to_plot() wont work unfortunately.

        self.actor = vtk.vtkFollower()
        self.actor.SetScale(*scale)
        self.actor.SetPosition(*position)

        self.mapper = vtk.vtkPolyDataMapper()
        self.actor.SetMapper(self.mapper)

        self.property = self.actor.GetProperty()
        self.mapper.SetInputConnection(self.source.GetOutputPort())


        self.fig += self
        self.color_opacity(color, opacity)

        if follow_cam:
            self.actor.SetCamera(self.fig.render.GetActiveCamera())


def annotate(points, text, direction, text_color="w", arrow_color="k", distance=3, text_size=1, fig="gcf"):
    """Annotate a feature with an arrow and a text actor.

    If multiple points are given the highest is selected where high is
    determined by 'direction' (unit vector 1D np.array with length 3).
    The arrow points to the highest point and the text is placed at a point
    'distance' above (where above also is determined by direction).
    """

    point = geom.highest(points, direction)
    text_point = point + distance * direction
    return (Arrow(text_point, point, color=arrow_color, fig=fig),
        Text3D(text, text_point, color=text_color, scale=text_size, fig=fig))


def test():
    import vtkplotlib as vpl

#    self = vpl.text3d("some text", follow_cam=True)

    point = np.array([1, 2, 3])
    vpl.scatter(point)

    arrow, text = vpl.annotate(point, point, np.array([0, 0, 1]))


    vpl.show()




if __name__ == "__main__":
    test()