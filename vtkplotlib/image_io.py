# -*- coding: utf-8 -*-
# =============================================================================
#Created on Sun Sep 29 20:17:37 2019
#
#@author: Brénainn Woodsend
#
#
# image_io.py performs image read/write operations and conversions to vtkimage types.
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

"""The image_io subpackage provides tools for working with VTK's revolting
vtkImageData class which is used to represent 2D images. Unfortunately the
vtkImageData is not primarly for 2D images - rather it is for volume plots
(which are currently not implemented in vtkplotlib) which makes it a lot more
awkward and counteruitive than you would expect it to be. Whenever vtkplotlib
works with images it converts implicitly to/from numpy arrays using methods from
here so you should only ever need these methods if you are exploring regions of
VTK that are uncovered by vtkplotlib.
"""

import numpy as np
import sys
import os
from pathlib2 import Path

try:
    PathLike = os.PathLike
except AttributeError:
    PathLike = Path

try:
    from PIL.Image import Image
except ImportError:
    Image = None

from vtkplotlib._get_vtk import vtk, vtk_to_numpy, numpy_to_vtk, numpy_support

from vtkplotlib.unicode_paths import PathHandler


def read(path, convert_to_array=True):
    """Read an image from a file using one of VTK's ``vtkFormatReader`` classes
    where ``Format`` is replaced by JPEG or PNG.

    Unless specified not to using the `convert_to_array` argument, the output
    is converted to a 3D numpy array. Otherwise a vtkImageData is returned.

    .. note: `path` must be a filename and not a BytesIO or similar psuedo file object.


    """
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
        if convert_to_array:
            return vtkimagedata_to_array(im_data)
        return im_data


def write(arr, path):
    """Write an image from a file using one of VTK's ``vtkFormatWriter`` classes
    where ``Format`` is replaced by JPEG or PNG.

    `arr` can be a ``vtkImageData`` or a numpy array.

    .. note: `path` must be a filename and not a BytesIO or similar psuedo file object.

    """
    ext = Path(path).suffix[1:].upper()
    if ext == "JPG":
        ext = "JPEG"
    try:
        Writer = getattr(vtk, "vtk{}Writer".format(ext))
    except AttributeError:
        return NotImplemented
    im_data = as_vtkimagedata(arr)
    im_data.Modified()

    writer = Writer()
    with PathHandler(path, "w") as path_handler:
        writer.SetFileName(path_handler.access_path)
        writer.SetInputDataObject(im_data)
        writer.Update()
        writer.Write()



def vtkimagedata_to_array(image_data):
    """Convert a vtkImageData to numpy array.

    .. see-also: vtkimagedata_from_array for the opposite.

    """
    points = vtk_to_numpy(image_data.GetPointData().GetScalars())
    shape = image_data.GetDimensions()
    # Be careful here. shape[2] isn't the number of values per pixel as you'd
    # expect. Rather it is a 3rd dimension as vtkImagedata is
    # supposed to hold volumes. `image_data.GetNumberOfScalarComponents()` gets
    # the right value (usually 3 for RGB).
    # Additionally vtk uses cartesian coordinates in images which isn't the
    # norm - hence the axes swapping and mirroring.
    shape = (shape[1], shape[0], image_data.GetNumberOfScalarComponents())
    return points.reshape(shape)[::-1]


def vtkimagedata_from_array(arr, image_data=None):
    """Convert a numpy array to a vtkImageData.

    .. see-also: vtkimagedata_to_array for the opposite.

    """
    assert arr.dtype == np.uint8

    if image_data is None:
        image_data = vtk.vtkImageData()

    if arr.ndim == 2:
        arr = arr[..., np.newaxis]

    image_data.SetDimensions(arr.shape[1], arr.shape[0], 1)
    image_data.SetNumberOfScalarComponents(arr.shape[2], image_data.GetInformation())

    pd = image_data.GetPointData()
    new_arr = arr[::-1].reshape((-1, arr.shape[2]))
    pd.SetScalars(numpy_to_vtk(new_arr))
    pd._numpy_reference = new_arr.data

    return image_data



def trim_image(arr, background_color, crop_padding):
    if (crop_padding is None) or crop_padding == 0:
        return arr


    background_color = np.asarray(background_color)
    if background_color.dtype.kind == "f" and arr.dtype.kind == "u":
        background_color = (background_color * 255).astype(arr.dtype)

    mask = (arr == background_color).all(-1)

    if isinstance(crop_padding, float):
        crop_padding = int(crop_padding * min(mask.shape))


    masks_1d = [mask.all(i) for i in range(2)]

    bounds = [[], []]

    for mask_1d in masks_1d:
        for (mask_1d_, bounds_) in zip((mask_1d, mask_1d[::-1]), bounds):
            arg = np.argmin(mask_1d_)
            if mask_1d_[arg]:
                print("Figure is empty - not cropping")
                return arr
            bounds_.append(arg)

    bounds = np.array(bounds)
    bounds -= crop_padding

    bounds[1] *= -1
    bounds[1] += mask.shape[::-1]
    bounds.clip(0, mask.shape[::-1], out=bounds)

#    plt.axvline(bounds[0][0])
#    plt.axhline(bounds[0][1])
#    plt.imshow(mask)
#    plt.axvline(bounds[1][0])
#    plt.axhline(bounds[1][1])
#    plt.show()

    slices = tuple(slice(*i) for i in bounds.T[::-1])

#    plt.imshow(mask[slices])
#    plt.show()

    return arr[slices]


def as_vtkimagedata(x, ndim=None):
    if isinstance(x, Path):
        x = str(x)
    if isinstance(x, str):
        try:
            from matplotlib.pylab import imread
            x = imread(x)
        except Exception:
            x = read(x)
    if Image and isinstance(x, Image):
        x = np.array(x)
    if isinstance(x, np.ndarray):
        if x.ndim == 2 and ndim == 3:
            x = x[:, :, np.newaxis]
        elif x.ndim == 3 and ndim == 2:
            x = x.mean(-1).astype(x.dtype)
        x = vtkimagedata_from_array(x)
    if isinstance(x, vtk.vtkImageData):
        return x
    raise TypeError("Unable to convert type {} to vtkImageData".format(type(x)))



def test_trim_image():
    import vtkplotlib as vpl
    import matplotlib.pylab as plt


    vpl.quick_test_plot()
    fig = vpl.gcf()
    arr = vpl.screenshot_fig()
    vpl.close()

    trimmed = trim_image(arr, fig.background_color, 10)
    background_color = np.asarray(fig.background_color) * 255

    assert (arr != background_color).any(-1).sum() == (trimmed != background_color).any(-1).sum()

    plt.imshow(trimmed)
    plt.show()


def test_conversions():
    import vtkplotlib as vpl

    vpl.quick_test_plot()
    arr = vpl.screenshot_fig()
    vpl.close()

    image_data = vtkimagedata_from_array(arr)
    arr2 = vtkimagedata_to_array(image_data)

    assert np.array_equal(arr, arr2)



if __name__ == "__main__":
#    import vtkplotlib as vpl
#    from vtkplotlib import image_io
#    import matplotlib.pylab as plt
#
#    path = vpl.data.ICONS["Right"]
#
#    plt.imshow(image_io.read(path))
#    plt.show()

    test_trim_image()
    test_conversions()




