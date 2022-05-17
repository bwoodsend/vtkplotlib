# -*- coding: utf-8 -*-
"""This module defines everything that goes in vtkplotlib.image_io.
"""

import sys
import os
import io

import numpy as np
from pathlib import Path

from vtkplotlib._get_vtk import (vtk, vtk_to_numpy, numpy_to_vtk, numpy_support,
                                 VTK_VERSION_INFO)

from vtkplotlib.unicode_paths import PathHandler
from vtkplotlib import nuts_and_bolts
from vtkplotlib._vtk_errors import VTKErrorRaiser


def read(path, raw_bytes=None, format=None, convert_to_array=True):
    """Read an image from a file using one of VTK's ``vtkFormatReader`` classes
    where ``Format`` is replaced by JPEG, PNG, BMP or TIFF.

    :param path: Filename or file handle or `None` if using the **raw_bytes** argument.
    :type path: str, os.PathLike, io.BytesIO

    :param raw_bytes: Image compressed binary data.
    :type raw_bytes: bytes

    :param format: Image format extension (e.g. jpg). This should never be needed.
    :type format: str

    :param convert_to_array: If true, convert to `numpy.ndarray`, otherwise leave as vtkImageData_.
    :type convert_to_array: bool

    :return: Read image.
    :rtype: `numpy.ndarray` or `vtkImageData`_

    The file format can be determined automatically from the **path** suffix or the beginning
    of **raw_bytes**. **format** can be any of JPEG, PNG, TIFF, BMP. It is case
    insensitive, tolerant to preceding ``'.'`` e.g. ``format=".jpg"`` and
    understands the aliases JPG \u21d4 JPEG and TIF \u21d4 TIFF.

    The following demonstrates how to use pseudo file objects to avoid temporary
    files when reading an image from the web.

    .. code-block:: python

        import vtkplotlib as vpl

        # Link your image url here
        url = "https://raw.githubusercontent.com/bwoodsend/vtkplotlib/master/vtkplotlib/data/icons/Right.jpg"

        # You can make the url request with either:
        from urllib import request
        raw_bytes = request.urlopen(url).read()

        # Or if you have the more modern requests library installed:
        # import requests
        # raw_bytes = requests.get(url).content

        # Pass the bytes to `read()` using:
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

    .. note::

        There is a bug in VTK==9.0.0


    """
    if isinstance(raw_bytes, bool):
        raise TypeError(
            "The arguments for this method have changed. If you meant to set the `convert_to_array` argument, please treat it as keyword only. i.e ``convert_to_array={}``"
            .format(raw_bytes))

    if (path is None) == (raw_bytes is None):
        raise TypeError(
            "Exactly one of `path` and `raw_bytes` should be specified.")

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

    if format == "TIFF" and VTK_VERSION_INFO >= (9, 0, 0):
        # There's a bug in VTK 9 that reads TIFFs upside-down.
        im_data = vtkimagedata_to_array(im_data)[::-1]
        return im_data if convert_to_array else vtkimagedata_from_array(im_data)

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
            raise ValueError(
                "No `format` argument was given and couldn't guess the format from `path`."
            )

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

    :param arr: An image array.
    :type arr: `numpy.ndarray` or `vtkImageData`_

    :param path: File path to write to.
    :type path: str or os.PathLike or io.BytesIO

    :param format: Image format extension (e.g. jpg), not needed if format can be determined from **path**.
    :type format: str

    :param quality: Lossy compression quality (only applicable to JPEGs) between 0 to 100.
    :type quality: int

    :return: The raw image binary if ``path is None``, `NotImplemented` if the filetype is unknown. Otherwise no return value.
    :rtype: bytes

    See `read` for more information.

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

    .. seealso:: `vtkimagedata_from_array` for the reverse.

    """
    points = vtk_to_numpy(image_data.GetPointData().GetScalars())
    shape = image_data.GetDimensions()
    # Be careful here. shape[2] isn't the number of values per pixel as you'd
    # expect. Rather it is a 3rd dimension as vtkImageData is
    # supposed to hold volumes. `image_data.GetNumberOfScalarComponents()` gets
    # the right value (usually 3 for RGB).
    # Additionally vtk uses cartesian coordinates in images which isn't the
    # norm - hence the axes swapping and mirroring.
    shape = (shape[1], shape[0], image_data.GetNumberOfScalarComponents())
    return np.ascontiguousarray(points.reshape(shape)[::-1])


def vtkimagedata_from_array(arr, image_data=None):
    """Convert a numpy array to a vtkImageData.

    :param arr: An ``uint8`` array of colors.
    :type arr: numpy.ndarray

    :param image_data: An image data to write into, a new one is created if not specified.
    :type image_data: `vtkImageData`_

    :return: A VTK image.
    :rtype: `vtkImageData`_

    Grayscale images are allowed. ``arr.shape`` can be any of ``(m, n)`` or
    ``(m, n, 1)`` for greyscale, ``(m, n, 3)`` for RGB, or ``(m, n, 4)`` for
    RGBA.

    .. seealso:: `vtkimagedata_to_array` for the reverse.

    .. seealso:: `as_vtkimagedata` for converting from other types.

    """
    assert arr.dtype == np.uint8

    if image_data is None:
        image_data = vtk.vtkImageData()

    if arr.ndim == 2:
        arr = arr[..., np.newaxis]

    image_data.SetDimensions(arr.shape[1], arr.shape[0], 1)
    image_data.SetNumberOfScalarComponents(arr.shape[2],
                                           image_data.GetInformation())

    pd = image_data.GetPointData()
    new_arr = arr[::-1].reshape((-1, arr.shape[2]))
    pd.SetScalars(numpy_to_vtk(new_arr))
    pd._numpy_reference = new_arr.data

    return image_data


def trim_image(arr, background_color, crop_padding):
    """Crop an image to its contents so that there aren't large amounts of empty
    background.

    :param arr: An image array.
    :type arr: numpy.ndarray

    :param background_color: The color of the portions to crop away.
    :type background_color: tuple

    :param crop_padding: Space to leave, in pixels if `int`, or relative to image size if `float`.
    :type crop_padding: int or float

    :return: A smaller image array.
    :rtype: numpy.ndarray


    If you don't want your files smaller you can instead use
    `vtkplotlib.zoom_to_contents`.

    """
    if (crop_padding is None) or crop_padding == 0:
        return arr

    background_color = np.asarray(background_color)
    if background_color.dtype.kind == "f" and arr.dtype.kind == "u":
        background_color = (background_color * 255).astype(arr.dtype)

    mask = (arr[:, :, :len(background_color)] == background_color).all(-1)

    if isinstance(crop_padding, float):
        crop_padding = int(crop_padding * min(mask.shape))

    masks_1d = [mask.all(i) for i in range(2)]

    bounds = [[], []]

    for mask_1d in masks_1d:
        for (mask_1d_, bounds_) in zip((mask_1d, mask_1d[::-1]), bounds):
            arg = np.argmin(mask_1d_)
            if mask_1d_[arg]:
                return arr
            bounds_.append(arg)

    bounds = np.array(bounds)
    bounds -= crop_padding

    bounds[1] *= -1
    bounds[1] += mask.shape[::-1]
    bounds.clip(0, mask.shape[::-1], out=bounds)

    slices = tuple(slice(*i) for i in bounds.T[::-1])
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


BUFFERABLE_FORMAT_MODES = [
    ("JPEG", "rw"),
    ("PNG", "w" if VTK_VERSION_INFO < (9, 0, 0) else "rw"),
    ("TIFF", ""),
    ("BMP", "" if VTK_VERSION_INFO < (8, 1, 0) else "w"),
]

import re

# https://en.wikipedia.org/wiki/List_of_file_signatures

FORMAT_CODES = {
    "JPEG":
        """
        FF D8 FF ??
        FF D8 FF E0 00 10 4A 46 49 46 00 01
        FF D8 FF EE
        FF D8 FF E1 ?? ?? 45 78 69 66 00 00
        """,
    "PNG":
        """
        89 50 4E 47 0D 0A 1A 0A
        """,
    "BMP":
        """
        42 4D
        """,
    "TIFF":
        """
        49 49 2A 00
        4D 4D 00 2A
        """
}


def _hex_to_byte(string):
    if string == "??":
        return b"."
    value = int(string, 16)
    return value.to_bytes(1, "little")


def _code_to_regex(code):
    parts = (_hex_to_byte(i) for i in code.strip(" \n").split())
    return re.compile(b"".join(parts), re.DOTALL)


def _codes_to_regexes(codes_block):
    return [_code_to_regex(i) for i in codes_block.strip(" \n").split("\n")]


FORMAT_REGEXS = [
    (key, _codes_to_regexes(val)) for (key, val) in FORMAT_CODES.items()
]


def format_from_header(header):
    """Guess image type based on the first few bytes. This is a bit useless
    seeing as JPEG is the only format that can be read from RAM."""
    for (fmt, patterns) in FORMAT_REGEXS:
        for pattern in patterns:
            if pattern.match(header):
                return fmt
    raise ValueError("Unrecognised header " + repr(header[:16]))
