# -*- coding: utf-8 -*-
# =============================================================================
# Created on Mon Nov 18 13:46:51 2019
#
# @author: Brénainn Woodsend
#
#
# one line to give the program's name and a brief idea of what it does.
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
"""
"""

import numpy as np
import matplotlib.pylab as plt
import sys
import os
from pathlib2 import Path

from vtkplotlib._get_vtk import vtk, numpy_to_vtk

#points = vtk_to_numpy(image_data.GetPointData().GetArray(0))
#shape = image_data.GetDimensions()[:-1]
#shape = shape[::-1] + (points.shape[-1], )


def main(colorImage):

    # colorImage = vtk.vtkImageData()
    # CreateColorImage(colorImage)

    imageMapper = vtk.vtkImageMapper()
    if vtk.VTK_MAJOR_VERSION <= 5:
        imageMapper.SetInputConnection(colorImage.GetProducerPort())
    else:
        imageMapper.SetInputData(colorImage)

    imageMapper.SetColorWindow(255)
    imageMapper.SetColorLevel(127.5)

    imageActor = vtk.vtkActor2D()
    imageActor.SetMapper(imageMapper)
    imageActor.SetPosition(20, 20)

    # Setup renderers
    renderer = vtk.vtkRenderer()

    # Setup render window
    renderWindow = vtk.vtkRenderWindow()

    renderWindow.AddRenderer(renderer)

    # Setup render window interactor
    renderWindowInteractor = vtk.vtkRenderWindowInteractor()

    style = vtk.vtkInteractorStyleImage()

    renderWindowInteractor.SetInteractorStyle(style)

    # Render and start interaction
    renderWindowInteractor.SetRenderWindow(renderWindow)

    #renderer.AddViewProp(imageActor)
    renderer.AddActor2D(imageActor)

    renderWindow.Render()
    renderWindowInteractor.Start()


from vtkplotlib import image_io
from vtkplotlib.plots.BasePlot import Base2DPlot


class Imshow(Base2DPlot):

    def __init__(self, arr, fig="gcf"):
        super().__init__(fig)

        self.image_data = image_io.vtkimagedata_from_array(arr)

        imageMapper = vtk.vtkImageMapper()
        if vtk.VTK_MAJOR_VERSION <= 5:
            imageMapper.SetInputConnection(self.image_data.GetProducerPort())
        else:
            imageMapper.SetInputData(self.image_data)

        imageMapper.SetColorWindow(255)
        imageMapper.SetColorLevel(127.5)

        imageActor = vtk.vtkActor2D()
        imageActor.SetMapper(imageMapper)
        imageActor.SetPosition(20, 20)

        self.actor = imageActor
        self.mapper = imageMapper

        self.__actor2d_init__()

        self.position = 0, 0
        self.size = (1, .1)

        self.fig.renderer.AddActor2D(imageActor)


if __name__ == "__main__":
    pass

    import vtkplotlib as vpl

    arr = plt.imread(vpl.data.ICONS["Right"])
    arr = image_io.trim_image(arr, arr[0, 0], 10)

    #image_data = vtk.vtkImageData()
    #
    #image_data.SetDimensions(arr.shape[1], arr.shape[0], arr.shape[2])
    #
    #pd = image_data.GetPointData()
    #pd.SetScalars(numpy_to_vtk(np.transpose(arr[::-1], (2, 0, 1)).ravel()))

    self = Imshow(arr)
    vpl.show()
