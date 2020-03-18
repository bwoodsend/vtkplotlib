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

"""The image_io subpackage provides tools for working with VTK's vtkImageData
class which is used to represent 2D images and easily wins the top prize for
being the most frustration-inducing component of VTK. Unfortunately the
vtkImageData is not primarily for 2D images - rather it is for volume plots
(which are currently not implemented in vtkplotlib). Whenever vtkplotlib
works with images it converts implicitly to/from numpy arrays using methods from
here. Additionally this module provides methods for reading and writing images
through VTK's image reader/writer classes.
"""

import sys
import os
import io

import numpy as np
from pathlib2 import Path

try:
    PathLike = os.PathLike
except AttributeError:
    PathLike = Path

try:
    from PIL.Image import Image, open as pillow_open
except ImportError:
    Image = None

from vtkplotlib._get_vtk import vtk, vtk_to_numpy, numpy_to_vtk, numpy_support

from vtkplotlib.unicode_paths import PathHandler


def read(path, raw_bytes=None, format=None, convert_to_array=True):
    """Read an image from a file using one of VTK's ``vtkFormatReader`` classes
    where ``Format`` is replaced by JPEG or PNG.

    Unless specified not to using the `convert_to_array` argument, the output
    is converted to a 3D numpy array. Otherwise a vtkImageData is returned.

    .. note: `path` must be a filename and not a BytesIO or similar pseudo file object.


    """
    if isinstance(raw_bytes, bool):
        raise TypeError("The arguments for this method have changed. If you meant to set the `convert_to_array` argument, please treat it as keyword only. i.e ``convert_to_array={}``".format(raw_bytes))

    format = _normalise_format(path, format)
    try:
        Reader = getattr(vtk, "vtk{}Reader".format(format))
    except AttributeError:
        return NotImplemented

    reader = Reader()

    if isinstance(path, (str, PathLike)):
        with PathHandler(path) as path_handler:
            reader.SetFileName(path_handler.access_path)
            reader.Update()
    else:
        if isinstance(path, io.IOBase):
            raw_bytes = path.read()
        if raw_bytes is not None:
            bytes_arr = np.frombuffer(raw_bytes, dtype=np.uint8)
            vtk_bytes = numpy_to_vtk(bytes_arr)
            vtk_bytes._numpy_ref = bytes_arr
            reader.SetMemoryBuffer(vtk_bytes)
            reader.SetMemoryBufferLength(len(bytes_arr))
            reader.Update()

    im_data = reader.GetOutput()
    if convert_to_array:
        return vtkimagedata_to_array(im_data)
    return im_data


def _normalise_format(path, format):
    """Extracts ``"JPEG"``, ``"PNG"`` etc from arguments provided to image
    read write methods.
    """
    if format is None:
        try:
            format = Path(path).suffix
        except TypeError:
            raise ValueError("No ``format`` argument was given and couldn't guess the format from ``path``.")

    format = format.upper()
    if format[0] == ".":
        format = format[1:]
    if format == "JPG":
        format = "JPEG"
    if format == "TIF":
        format = "TIFF"
    return format


def write(arr, path, format=None, quality=95):
    """Write an image from a file using one of VTK's ``vtkFormatWriter`` classes
    where ``Format`` is replaced by JPEG or PNG.

    :param arr: `arr` can be a ``vtkImageData`` or a numpy array..
    :type arr:

    :param path: File path to write to.
    :type path: str, os.Pathlike, io.BytesIO,

    :param format: File format. Can be guessed based on the suffix of **path**.
    :type format: str

    :return: The raw image binary if ``path is None``, ``NotImplemented`` if the filetype is unknown Otherwise no return value.
    :rtype: bytes


    .. note::

        BytesIO and raw bytes functionality is new in vtkplotlib >= 1.3.0.
        Older versions are hardcoded to write to disk and therefore **path**
        must be a filename and not a BytesIO or similar pseudo file object.

    """
    format = _normalise_format(path, format)
    try:
        Writer = getattr(vtk, "vtk{}Writer".format(format))
    except AttributeError:
        return NotImplemented
    im_data = as_vtkimagedata(arr)
    im_data.Modified()

    writer = Writer()
    writer.SetInputDataObject(im_data)

    if Writer is vtk.vtkJPEGWriter:
        writer.SetQuality(quality)

    if isinstance(path, (str, PathLike)):
        with PathHandler(path, "w") as path_handler:
            writer.SetFileName(path_handler.access_path)
            writer.Update()
            writer.Write()
        return
    writer.WriteToMemoryOn()
    writer.Update()
    writer.Write()
    binary = vtk_to_numpy(writer.GetResult()).tobytes()

    if path is None:
        return binary
    path.write(binary)


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
#                print("Figure is empty - not cropping")
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
    if isinstance(x, PathLike):
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



from vtkplotlib.tests._figure_contents_check import checker, VTKPLOTLIB_WINDOWLESS_TEST
@checker()
def test_trim_image():
    import vtkplotlib as vpl
    import matplotlib.pylab as plt


    vpl.quick_test_plot()
    fig = vpl.gcf()
    arr = vpl.screenshot_fig()
    vpl.close()

    trimmed = trim_image(arr, fig.background_color, 10)
    background_color = np.asarray(fig.background_color) * 255

    # Check that no non-background coloured pixels have been lost.
    assert (arr != background_color).any(-1).sum() == (trimmed != background_color).any(-1).sum()

    if not VTKPLOTLIB_WINDOWLESS_TEST:
        plt.imshow(trimmed)
        plt.show()

    return trimmed




def test_conversions():
    import vtkplotlib as vpl

    # Shouldn't do anything if the figure is empty.
    assert vpl.screenshot_fig(trim_pad_width=.05).shape[:2] == vpl.gcf().render_size

    vpl.quick_test_plot()
    arr = vpl.screenshot_fig()
    vpl.close()

    image_data = vtkimagedata_from_array(arr)
    arr2 = vtkimagedata_to_array(image_data)

    assert np.array_equal(arr, arr2)

def test_reads_writes(*fmts):
    import vtkplotlib as vpl

    path = vpl.data.ICONS["Right"]
    arr = np.array(pillow_open(path))
    with open(path, "rb") as f:
        binary = f.read()

    errors = []
    for (fmt, modes) in fmts:
        for mode in modes:
            try:
                if mode == "r":
                    arr2 = read(None, binary, format=fmt)
                else:
                    arr2 = np.array(pillow_open(io.BytesIO(write(arr, None, fmt))))
                error_msg = "with_fmt={}, mode={}".format(fmt, mode)
                assert arr.shape == arr2.shape, error_msg
                error = np.abs(arr - arr2.astype(np.float)).mean()
        #            print(error, len(binary))
                assert error < 1, error_msg
            except BaseException as ex:
                errors.append((ex, fmt, mode))
                print(mode, fmt)
                raise

    return errors


BUFFERABLE_FORMAT_MODES = [
        ("jpg", "rw"),
        ("png", "w"),
        ("tif", ""),
        ("bmp", "w"),
        ]

def test():
    test_trim_image()
    test_conversions()
    test_reads_writes((".jpeg", "r"), *BUFFERABLE_FORMAT_MODES)


if __name__ == "__main__":
#    import vtkplotlib as vpl
#    from vtkplotlib import image_io
#    import matplotlib.pylab as plt
#
#    path = vpl.data.ICONS["Right"]
#
#    plt.imshow(image_io.read(path))
#    plt.show()
    test()






