# -*- coding: utf-8 -*-
# =============================================================================
# Created on Thu Mar 19 19:01:59 2020
#
# @author: Brénainn Woodsend
#
# _image_io.py
# Workhorse for image_io.py
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

"""This module defines everything that goes in vtkplotlib.image_io.
"""


import sys
import os
import io

import numpy as np
from pathlib2 import Path


from vtkplotlib._get_vtk import vtk, vtk_to_numpy, numpy_to_vtk, numpy_support

from vtkplotlib.unicode_paths import PathHandler
from vtkplotlib import nuts_and_bolts
from vtkplotlib._vtk_errors import VTKErrorRaiser


def read(path, raw_bytes=None, format=None, convert_to_array=True):
    """Read an image from a file using one of VTK's ``vtkFormatReader`` classes
    where ``Format`` is replaced by JPEG, PNG, BMP or TIFF.

    :param path: Filename or file handle or ``None`` if using the **raw_bytes** argument.
    :type path: str, os.PathLike, io.BytesIO

    :param raw_bytes: Image compressed binary data, defaults to ``None``.
    :type raw_bytes: bytes, optional

    :param format: Image format extension (e.g. jpg), not needed if format can be determined from **path**, defaults to ``None``.
    :type format: str, optional

    :param convert_to_array: If true, convert to numpy, otherwise leave as vtkImageData, defaults to ``True``.
    :type convert_to_array: bool, optional

    :return: Read image.
    :rtype: np.ndarray or `vtkImageData`_

    The file format can be determined automatically from the **path** suffix or the beginning
    of **raw_bytes**. **format** can be any of JPEG, PNG, TIFF, BMP. It is case
    insensitive, tolerant to preceding '.'s e.g. ``format=".jpg"`` and
    understands the aliases JPG \u21d4 JPEG and TIF \u21d4 TIFF.

    The following demonstrates how to use pseudo file objects to avoid temporary
    files when reading an image from the web.

    .. code-block:: python

        import vtkplotlib as vpl

        # Link you're image url here
        url = "https://raw.githubusercontent.com/bwoodsend/vtkplotlib/master/vtkplotlib/data/icons/Right.jpg"

        # You can make the url request with either:
        from urllib import request
        raw_bytes = request.urlopen(url).read()

        # Or if you have the more modern requests library installed:
        # import requests
        # raw_bytes = requests.get(url).content

        # Pass the bytes to :meth:`read` using:
        image = vpl.image_io.read(path=None, raw_bytes=raw_bytes)

        # Visualize using matplotlib.
        from matplotlib import pyplot
        pyplot.imshow(image)
        pyplot.show()


    .. warning::

        Some formats only support reading from disk. See
        ``vtkplotlib.image_io.BUFFERABLE_FORMAT_MODES`` or for which these are.

    .. note::

        BytesIO and raw bytes functionality is new in vtkplotlib >= 1.3.0.
        Older versions are hardcoded to write to disk and therefore **path**
        must be a filename and not a BytesIO or similar pseudo file object.


    """
    if isinstance(raw_bytes, bool):
        raise TypeError("The arguments for this method have changed. If you meant to set the `convert_to_array` argument, please treat it as keyword only. i.e ``convert_to_array={}``".format(raw_bytes))

    if (path is None) == (raw_bytes is None):
        raise TypeError("Exactly one of `path` and `raw_bytes` should be specified.")

    if isinstance(path, io.IOBase):
        raw_bytes = path.read()

    format = _normalise_format(path, format, raw_bytes)
    try:
        Reader = getattr(vtk, "vtk{}Reader".format(format))
    except AttributeError:
        return NotImplemented

    reader = Reader()

    with VTKErrorRaiser(reader):

        if nuts_and_bolts.isinstance_PathLike(path):
            with PathHandler(path) as path_handler:
                reader.SetFileName(path_handler.access_path)
                reader.Update()
        else:
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


def _normalise_format(path, format, header=None):
    """Extracts ``"JPEG"``, ``"PNG"`` etc from arguments provided to image
    read write methods. Implements the hierarchy for multiple arguments given.

    - User explicitly gives format.
    - Format read from header.
    - Format read from filename suffix.

    """
    if format is None:
        if header is not None:
            format = format_from_header(header)

    if format is None:
        try:
            format = Path(path).suffix
        except TypeError:
            raise ValueError("No `format` argument was given and couldn't guess the format from `path`.")

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

    :param arr: **arr** can be a `vtkImageData`_ or a numpy array.
    :type arr: np.ndarray

    :param path: File path to write to.
    :type path: str, os.Pathlike, io.BytesIO,

    :param format: Image format extension (e.g. jpg), not needed if format can be determined from **path**, defaults to ``None``.
    :type format: str, optional

    :param quality: Lossy compression quality, only applicable to JPEGs, defaults to 95.
    :type quality: int from 0 to 100, optional

    :return: The raw image binary if ``path is None``, ``NotImplemented`` if the filetype is unknown. Otherwise no return value.
    :rtype: bytes

    See :meth:`read` for more information.

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

    if nuts_and_bolts.isinstance_PathLike(path):
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

    .. seealso:: :meth:`vtkimagedata_from_array` for the reverse.

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

    :param arr: Array of colors.
    :type arr: np.ndarray with dtype ``np.uint8``

    :param image_data: An image data to write into, a new one is created if not specified, defaults to ``None``.
    :type image_data: `vtkImageData`_, optional

    :return: A VTK image.
    :rtype: `vtkImageData`_

    Grayscale images are allowed. ``arr.shape`` can be any of ``(m, n)`` or
    ``(m, n, 1)`` for greyscale, ``(m, n, 3)`` for RGB, or ``(m, n, 4)`` for
    RGBA.

    .. seealso:: :meth:`vtkimagedata_to_array` for the reverse.

    .. seealso:: :meth:`as_vtkimagedata` for converting from other types.

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
    """Crop an image to its contents so that there aren't large amounts of empty
    background.

    :param arr: An image array.
    :type arr: 3D np.ndarray

    :param background_color: The color of the portions to crop away.
    :type background_color: Strictly an (r, g, b) tuple.

    :param crop_padding: Space to leave, in pixels if int, or relative to image size if float.
    :type crop_padding: int or float

    :return: Smaller image array.
    :rtype: 3D np.ndarray


    If you don't want your files smaller you can instead use
    :meth:`vtkplotlib.zoom`.

    """
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
    """Convert **x** to a vtkImageData.

    **x** can be any of the following:

    - A vtkImageData.
    - A 2D or 3D numpy array.
    - A file or filename to be read.
    - A Pillow image.

    Some VTK methods require a greyscale image. Using ``ndim=2`` will convert to
    greyscale.

    """
    assert (ndim is None) or (2 <= ndim <= 3)

    # From file.
    if nuts_and_bolts.isinstance_PathLike(x):
        x = str(x)
    if nuts_and_bolts.isinstance_PathLike(x, allow_buffers=True):
        try:
            from matplotlib.pylab import imread
            x = imread(x)
        except Exception:
            x = read(x)

    # From PILLOW.
    if nuts_and_bolts.isinstance_no_import(x, "PIL.Image", "Image"):
        x = np.array(x)

    # From array.
    if isinstance(x, np.ndarray):
        if x.ndim == 2 and ndim == 3:
            x = x[:, :, np.newaxis]
        elif x.ndim == 3 and ndim == 2:
            x = x.mean(-1).astype(x.dtype)
        x = vtkimagedata_from_array(x)

    # From vtk.
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
        try:
            plt.imshow(trimmed)
            plt.show()
        except UnicodeDecodeError:
            # There's an issue with the tk backend in python 2.
            pass

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

def test_bufferable_formats(*fmts):
    import vtkplotlib as vpl
    from PIL.Image import open as pillow_open

    path = vpl.data.ICONS["Right"]
    arr = np.array(pillow_open(path))
    with open(path, "rb") as f:
        binary = f.read()

    errors = []
    for (fmt, modes) in fmts:
        for mode in modes:
            try:
                if mode == "r":
                    arr2 = read(None, binary)
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
        ("JPEG", "rw"),
        ("PNG", "w"),
        ("TIFF", ""),
        ("BMP", "w"),
        ]

def test():
    test_trim_image()
    test_conversions()
    try:
        __import__("PIL")
    except ImportError:
        pass
    else:
        test_bufferable_formats((".jpg", "r"), *BUFFERABLE_FORMAT_MODES)

import re

# https://en.wikipedia.org/wiki/List_of_file_signatures

FORMAT_CODES = {
    "JPEG": """
        FF D8 FF ??
        FF D8 FF E0 00 10 4A 46 49 46 00 01
        FF D8 FF EE
        FF D8 FF E1 ?? ?? 45 78 69 66 00 00
        """,
    "PNG": """
        89 50 4E 47 0D 0A 1A 0A
        """,
    "BMP": """
        42 4D
        """,
    "TIFF": """
        49 49 2A 00
        4D 4D 00 2A
        """
}

def _code_to_regex(code):
    return re.compile(b"".join(b"." if i == "??" else re.escape(bytes([int(i, 16)]))\
                               for i in code.strip(" \n").split()), re.DOTALL)

def _codes_to_regexes(codes_block):
    return [_code_to_regex(i) for i in codes_block.strip(" \n").split("\n")]

FORMAT_REGEXS = [(key, _codes_to_regexes(val)) for (key, val) in FORMAT_CODES.items()]

def format_from_header(header):
    """Guess image type based on the first few bytes. This is a bit useless
    seeing as JPEG is the only format that can be read from RAM."""
    for (fmt, patterns) in FORMAT_REGEXS:
        for pattern in patterns:
            if pattern.match(header):
                return fmt
    raise ValueError("Unrecognised header " + repr(header[:16]))



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
