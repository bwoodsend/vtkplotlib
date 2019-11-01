# -*- coding: utf-8 -*-
# =============================================================================
#Created on Sun Sep 29 20:17:37 2019
#
#@author: Brénainn Woodsend
#
#
# image_io.py performs image read/write operations.
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


import numpy as np
import sys
import os
from pathlib2 import Path

import vtk
from vtk.util.numpy_support import vtk_to_numpy

from vtkplotlib.unicode_paths import PathHandler


def read(path):
    ext = Path(path).suffix[1:].upper()
    if ext == "JPG":
        ext = "JPEG"
    try:
        Reader = getattr(vtk, "vtk{}Reader".format(ext))
    except AttributeError:
        return NotImplemented

    reader = Reader()
    with PathHandler(path) as path_handler:
        reader.SetFileName(path_handler.access_path)
        reader.Update()
        im_data = reader.GetOutput()
        return vtkimagedata_to_array(im_data)


def vtkimagedata_to_array(image_data):
    points = vtk_to_numpy(image_data.GetPointData().GetArray(0))
    shape = image_data.GetDimensions()[:-1]
    shape = shape[::-1] + (points.shape[-1], )
    return points.reshape(shape)[::-1]



if __name__ == "__main__":
    import vtkplotlib as vpl
    from vtkplotlib import image_io
    import matplotlib.pylab as plt

    path = vpl.data.ICONS["Right"]

    plt.imshow(image_io.read(path))
    plt.show()




