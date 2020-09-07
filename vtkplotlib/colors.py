# -*- coding: utf-8 -*-
# =============================================================================
# Created on Sat Aug  3 13:01:28 2019
#
# @author: Brénainn Woodsend
#
#
# colors.py "borrows" matplotlib's color library and contains functions for handling different
# color types.
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
Colors
======

The :mod:`vtkplotlib.colors` module provides methods for:

- Converting the various color types and matplotlib's named colors to RGB(A)
  using :meth:`as_rgb_a`.
- Creating and converting colormaps (usually abbreviated to cmap) to VTK's
  equivalent ``vtkLookupTable`` class.
- Texture mapping.

For the most part, these methods are used implicitly whenever you set the
**color** or **cmap** arguments of any of vtkplotlib's classes/methods/attributes.
But if you're doing something unusual then these may help.

.. note:: This submodule was introduced in `v1.3.0`.

------------------------------------------------

Individual Colors
-----------------

as_rgb_a
^^^^^^^^

.. autofunction:: vtkplotlib.colors.as_rgb_a

---------------------------------------------

Colormaps
---------

Colormaps are used to visualize scalar data as heatmaps. The color map
determines which color represents each scalar value. In VTK, colormaps are
called lookup tables and are of type ``vtk.vtkLookupTable``.

Any vtkplotlib method that takes  **cmap** argument can utilise a colormap.

.. code-block:: python

    import vtkplotlib as vpl
    from stl.mesh import Mesh

    # Load the usual rabbit.
    mesh = Mesh.from_file(vpl.data.get_rabbit_stl())

    fig = vpl.figure()

    # Use the x values as scalars. Use matplotlib's "rainbow" colormap.
    plot = vpl.mesh_plot(mesh, scalars=mesh.x, cmap="rainbow")
    fig.show()

    # The cmap is accessed as a vtkLookupTable via the cmap attribute.
    plot.cmap
    # (vtkCommonCorePython.vtkLookupTable)0000003C06D06F40

    # Create and set a new cmap from a list of colors.
    plot.cmap = ["red", "white", "green"]
    fig.show()

    # Explicitly set the scalar range
    plot.scalar_range = -20, 20
    fig.show()

    # Set the scalar range back to automatic
    plot.scalar_range = ...

Note that in Python 2.7 you can't use ``...`` except when indexing. Use
``Ellipsis`` instead.


---------------------------------------------


as_vtk_cmap
^^^^^^^^^^^

.. autofunction:: vtkplotlib.colors.as_vtk_cmap

---------------------------------------------

cmap_from_list
^^^^^^^^^^^^^^

.. autofunction:: vtkplotlib.colors.cmap_from_list


---------------------------------------------

vtkLookupTable
^^^^^^^^^^^^^^

VTK's ``vtkLookupTable`` provides some useful functionality that you can't access
any other way. Assuming you have a lookup table called ``table`` you can use the
following:

+-----------------------------------+------------------------------------------+
| Methods                           | Meaning                                  |
+===================================+==========================================+
| | table.GetBelowRangeColor()      | | Choose a color to use when given       |
| | table.SetBelowRangeColor()      | | a scalar below the scalar range.       |
| | table.GetUseBelowRangeColor()   | | This must be enabled explicitly to     |
| | table.SetUseBelowRangeColor()   | | use.                                   |
+-----------------------------------+------------------------------------------+
| | table.GetAboveRangeColor()      | | Choose a color to use when given       |
| | table.SetAboveRangeColor()      | | a scalar above the scalar range.       |
| | table.GetUseAboveRangeColor()   | | This must be enabled explicitly to     |
| | table.SetUseAboveRangeColor()   | | use.                                   |
+-----------------------------------+------------------------------------------+
| | table.GetNanColor()             | | Choose a color to use when given       |
| | table.SetNanColor()             | | a NaN scalar.                          |
+-----------------------------------+------------------------------------------+


.. note::

    The scalar range is not controlled by the lookup table.


---------------------------------------------------------

Texture Maps
------------

Texture maps are like colormaps but two dimensional. i.e Rather than feeding it
a scalar and getting a color, you give it an `x` and `y` coordinate and get a
color. Texture maps allow you to color surfaces realistically to look like fur or
grass or brickwork by using a texture map containing a 2D image of that texture.

TextureMap
^^^^^^^^^^

.. autoclass:: vtkplotlib.colors.TextureMap

---------------------------------------------------------

Misc
------

normalise
^^^^^^^^^

.. autofunction:: vtkplotlib.colors.normalise

"""

from __future__ import division
from future import utils as _future_utils

import numpy as np
from matplotlib import colors, cm
from vtkplotlib._get_vtk import vtk, numpy_to_vtk, vtk_to_numpy

from vtkplotlib._matplotlib_colors import matplotlib_colors as mpl_colors


def as_rgb_a(color=None, opacity=None):
    """This method converts all the different ways a single color and opacity
    can be specified into the form ``(np.array([red, green, blue]), opacity)``.

    The **color** argument can be:

    #. A string named color such as "r" or "red". This uses matplotlib's
       named color libraries. For a full list of available colors see the dicts
       `BASE_COLORS`, `CSS4_COLORS` and `XKCD_COLORS` from `matplotlib.colors` or
       `vtkplotlib.colors.mpl_colors.keys()`.

    #. A tuple or list of `3` or `4` scalars representing (r, g, b) or
       (r, g, b, alpha). r, g, b, alpha can be from `0` to `1` or from `0` to
       `255` (inclusive).

    #. An html hex string in the form "#RRGGBB" or "#RRGGBBAA" where ``"RR"``,
       ``"GG"``, ``"BB"`` and ``"AA"`` are hexadecimal numbers from `00` to `FF`.

    #. A ``PyQt5.QtGui.QColor()``.

    The **opacity** argument should be a scalar like those for the (r, g, b)
    from form 2 above values.

    If an opacity if specified in both arguments then **opacity** argument
    overrides alpha values in **color**.

    .. note::

        Conventionally the values if they are from 0.0 to 1.0 they should be
        floats and if they are from 0 to 255 they should be ints. But this is so
        often not the case that this rule is unusable. This function divides by
        255 if the scalars are integers and it sees anything greater than 1.
"""

    color_out = None
    opacity_out = None

    if color is not None:
        if isinstance(color, _future_utils.string_types):
            if _future_utils.PY2 and isinstance(color, unicode):
                color = color.encode()

            if color[0] == "#":
                return as_rgb_a(_hex_to_rgba(color), opacity)

            return as_rgb_a(_named_matplotlib_color(color), opacity)

        # QColors
        from vtkplotlib.nuts_and_bolts import isinstance_no_import
        if isinstance_no_import(color, "PyQt5.QtGui", "QColor"):
            return as_rgb_a(color.getRgbF(), opacity)

        color = np.asarray(color)
        if color.dtype.kind in "ui" and color.max() > 1:
            # convert 0 <= x < 256 colors to 0 <= x <= 1
            color = color / 255.
            if opacity is not None:
                opacity /= 255

        if len(color) == 4:
            opacity_out = color[3]
            color = np.array(color[:3])

        color_out = color

    if opacity is not None:
        opacity_out = opacity

    return color_out, opacity_out


def _hex_to_rgba(color):
    """
    Convert #RRGGBB hex colors to (R, G, B) tuple of ints.
    Or #RRGGBBAA to (R, G, B, A).

    matplotlib's hex2rgb doesn't allow opacity. Otherwise I'd just use that.
    """
    if len(color) not in (7, 9):
        raise ValueError("Invalid length HTML Hex string color \"%s\"." % color)
    try:
        return tuple(int(color[i:i + 2], 16) for i in range(1, len(color), 2))
    except ValueError:
        raise ValueError("Invalid HTML Hex string color \"%s\"." % color)


def _named_matplotlib_color(color):
    if color in mpl_colors:
        return mpl_colors[color]

    # If not in mpl's library try to correct user input and try again
    corrected = color.lower().replace("_", " ").replace("-", " ")
    import warnings

    if corrected in mpl_colors:
        warnings.warn(
            "Auto-correcting color {!r} to {!r}.\nMatplotlib "
            "colors are all lowercase and use spaces instead of"
            " underscores.".format(color, corrected),
            UserWarning
        )  # yapf: disable
        return mpl_colors[corrected]

    # If still not found then skip color assignment.
    warnings.warn(
        "Color {!r} not found. Skipping color assignment. "
        "See vtkplotlib.colors.mpl_colors.keys() for a list"
        " of available colors.".format(color),
        UserWarning
    )  # yapf: disable
    return None


def normalise(colors, axis=None):
    """Scale and translate RBG(A) values so that they are all between 0 and 1.

    :param colors: Array of colors.
    :type colors: np.ndarray

    :param axis: Axis to reduce over, normally either ``-1`` or ``None`` are sensible, defaults to ``None``.
    :type axis: int, optional

    :return: Normalised colors.
    :rtype: np.ndarray

    The output should have the properties ``np.min(out, axis) == 0`` and
    ``np.max(out, axis) == 1``.

    .. code-block:: python

        import vtkplotlib as vpl
        import numpy as np

        points = np.random.uniform(-30, 30, (300, 3))

        # This would be an invalid way to color by position.
        # vpl.scatter(points, color=points)

        # A better way to color by position.
        vpl.scatter(points, color=vpl.colors.normalise(points))
        vpl.show()

    """
    colors = colors - np.nanmin(colors, axis=axis, keepdims=True)
    colors /= np.nanmax(colors, axis=axis, keepdims=True)
    return colors


class TextureMap(object):
    """Use a 2D image as a color lookup table.

    .. warning::

        This is still very much under development and requires a bit of
        monkey-wrenching to use. Currently only ``vpl.surface`` and
        ``vpl.PolyData`` have any support for it.


    :param array: The image data. It is converted to an array if it isn't one already.
    :type array: filename, np.ndarray with shape (m, n, 3 or 4), PIL Image

    :param interpolate: Allow interpolation between pixels, defaults to False.
    :type interpolate: bool, optional

    :return: A callable texturemap object.
    :rtype: :class:`vtkplotlib.TextureMap`


    The TextureMap object can be called to look up the color at a coordinate(s).
    Like everything else in vtkplotlib, texture coordinates should be zipped
    into a single array of the form:

    .. code-block:: python

        np.array([[x0, y0],
                  [x1, y1],
                  ...,
                  [xn, yn]])

    Unlike typical images, texture-map coordinates traditionally use the
    conventional (x, y) axes. i.e Right is x-increasing and up is y-increasing.
    Indices are always between 0 and 1 and are independent of the size of the
    image. To use texture-coordinates, pass an array with
    ``array.shape[-1] == 2`` as the scalar argument to a plot command.


    Typically texture-maps are found in some 3D file formats but integrating
    those is still under development. Texture-maps also play very well with
    parametric plots, namely ``vpl.surface`` using the 2 independent variables
    as the texture coordinates.

    .. code-block:: python

        import vtkplotlib as vpl
        import numpy as np

        # Define the 2 independent variables
        phi, theta = np.meshgrid(np.linspace(0, 2 * np.pi, 1024),
                                 np.linspace(0, np.pi, 1024))

        # Calculate the x, y, z values to form a sphere
        x = np.cos(phi) * np.sin(theta)
        y = np.sin(phi) * np.sin(theta)
        z = np.cos(theta)

        # You can play around with this. The coordinates must be zipped
        # together into one array with ``shape[-1] == 2``, hence the
        # ``vpl.zip_axes``. And must be between 0 and 1, hence the ``% 1.0``.
        texture_coords = (vpl.zip_axes(phi * 3, theta * 5) / np.pi) % 1.0

        # Pick an image to use. There is a picture of a shark here if you
        # don't have one available.
        path = vpl.data.ICONS["Right"]
        texture_map = vpl.TextureMap(path, interpolate=True)


        # You could convert `texture_coords` to `colors` now using.
        # colors = texture_map(texture_coords)
        # then pass ``colors`` as the `scalars` argument instead.

        vpl.surface(x, y, z,
                    scalars=texture_coords,
                    texture_map=texture_map)

        vpl.show()


    """

    def __init__(self, array, interpolate=False):
        from vtkplotlib.nuts_and_bolts import isinstance_PathLike
        if isinstance_PathLike(array):
            array = str(array)
        if isinstance(array, str):
            path = array
            from vtkplotlib.image_io import read
            array = read(path)
            if array is NotImplemented:
                try:
                    from matplotlib.pylab import imread
                    array = imread(path)
                except Exception as ex:
                    _future_utils.raise_from(
                        NotImplementedError(
                            "Could not find a suitable VTKImageReader for \"{}\" "
                            "and matplotlib's search failed with the following:"
                        ), ex)

            array = np.swapaxes(array, 0, 1)[:, ::-1]
        from vtkplotlib.nuts_and_bolts import isinstance_no_import
        if isinstance_no_import(array, "PIL.Image", "Image"):
            array = np.array(array)
            array = np.swapaxes(array, 0, 1)[:, ::-1]

        ex = lambda x: TypeError("`array` must be an np.ndarray with shape"
                                 " (m, n, 3) or (m, n, 4). Got {} {}".format(
                                     x, repr(array)))
        if not isinstance(array, np.ndarray):
            raise ex(type(array))
        if len(array.shape) != 3:
            raise ex(array.shape)
        if not (3 <= array.shape[2] <= 4):
            raise ex(array.shape)

        if array.dtype.kind in "ui":
            array = array / ((1 << (8 * array.dtype.itemsize)) - 1)

        self.array = array
        self.interpolate = interpolate

        self.shape = np.array(self.array.shape[:2])

    def __call__(self, uv):
        uv = (uv * (self.shape - 1))
        if self.interpolate:
            uv_bottom_left = np.floor(uv).astype(np.uint)
            u_left = uv_bottom_left[..., 0].astype(np.uint)
            v_bottom = uv_bottom_left[..., 1]

            uv_top_right = np.ceil(uv)
            u_right = uv_top_right[..., 0]
            v_top = uv_top_right[..., 1]

            uv_corners = np.empty((2, 2) + uv.shape, np.uint)
            uv_corners[0, :, ..., 0] = u_left
            uv_corners[:, 1, ..., 1] = v_top
            uv_corners[1, :, ..., 0] = u_right
            uv_corners[:, 0, ..., 1] = v_bottom

            weights = np.sum(np.abs(uv_corners - uv[np.newaxis, np.newaxis]),
                             -1)
            weights = np.max(weights, (0, 1)) - weights
            weights += np.all(weights == 0, (0, 1), keepdims=True)
            total_weights = np.sum(weights, (0, 1), keepdims=True)

            normed_weights = weights / total_weights

            return np.sum(
                self.array[uv_corners[..., 0], uv_corners[..., 1]] *
                normed_weights[..., np.newaxis], (0, 1))

        else:
            uv = uv.astype(np.uint)
            return self.array[uv[..., 0], uv[..., 1]]


converted_cmaps = {}
_temp = []


def as_vtk_cmap(cmap, cache=True):
    """Colormaps are generally converted implicitly from any valid format to a
    ``vtk.vtkLookupTable`` using this method. `Any valid format` is defined as
    the following:

    #. A string matplotlib colormap name such as ``'RdYlGn'``.
    #. Anything out of the ``matplotlib.cm`` package.
    #. A list of named colors such as ``["red", "white", "blue"]``. See
       :meth:`cmap_from_list` for more details and flexibility.
    #. An ``(n, 3)`` or ``(n, 4)`` numpy array of RGB(A) int or float values.
    #. A callable that takes an array of scalars and returns an array of form **4**.

    Unless specified otherwise using ``cache=False``, named colormaps of form
    **1** are cached in ``vtkplotlib.colors.converted_cmaps``. If you intend to
    modify the vtkLookupTable then it's best not to allow caching.

    .. note::

        VTK doesn't interpolate between colors. i.e if you use form **4** and
        only provide a short list of colors then the resulting heatmap will be
        block colors rather than a smooth gradient.

    .. note::

        Whilst VTK appears to support opacity gradients in the colormaps, it
        doesn't actually use them. If your colormap says opacity should vary
        with scalars then the opacity is averaged for the plot.


    """

    if isinstance(cmap, _future_utils.string_types):
        if cache and cmap in converted_cmaps:
            return converted_cmaps[cmap]
        cmap = cm.get_cmap(cmap)

    if isinstance(cmap, vtk.vtkLookupTable):
        return cmap

    if cache and isinstance(
            cmap, (colors.ListedColormap, colors.LinearSegmentedColormap)):
        name = cmap.name
        if name in converted_cmaps:
            return converted_cmaps[name]
    else:
        name = None

    if isinstance(cmap, colors.ListedColormap):
        cmap = np.array(cmap.colors)

    if callable(cmap):
        cmap = cmap(np.arange(256, dtype=np.uint8))

    if isinstance(cmap, list):
        cmap = cmap_from_list(cmap)

    if not isinstance(cmap, np.ndarray):
        raise TypeError("cmap is of an invalid type {}.".format(type(cmap)))

    if cmap.ndim == 2 and 3 <= cmap.shape[1] <= 4:
        cmap = np.ascontiguousarray(
            (colors.to_rgba_array(cmap) * 255).astype(np.uint8))
        table = vtk.vtkLookupTable()
        table.SetTable(numpy_to_vtk(cmap))
        table._numpy_ref = cmap

        _temp.append(cmap)
        if name is not None:
            converted_cmaps[name] = table
        return table

    else:
        raise ValueError(
            "`cmap` should have shape (n, 3) or (n, 4). Received {}.".format(
                cmap.shape))


def cmap_from_list(colors, opacities=None, scalars=None, resolution=None):
    """Create a colormap from a list of colors. Unlike matplotlib's
    ``ListedColormap``, this method will interpolate between the input
    **colors** to give a smooth map.

    :param colors: A list colors.
    :type colors: list of valid colors as defined by :meth:`as_rgb_a`

    :param opacities: Translucency or translucencies, defaults to ``None``.
    :type opacities: Scalar from 0 to 1 or array-like of scalars, optional

    :param scalars: Control scalars to correspond exact colors from **color**, defaults to ``np.arange(len(colors))``.
    :type scalars: array-like with same length as **colors**, optional

    :param resolution: Number of colors in output, defaults to ``(len(colors) - 1) * 255 + 1``.
    :type resolution: int, optional

    :return: An array of RGBA values.
    :rtype: ``np.ndarray`` with shape ``(n, 4)`` and dtype ``np.uint8``

    The output can be fed either to :meth:`as_vtk_cmap` or passed directly as a
    **cmap** argument to any vtkplotlib method that takes one.

    """
    from vtkplotlib.plots.BasePlot import _iter_scalar
    from vtkplotlib.nuts_and_bolts import zip_axes, unzip_axes
    n = len(colors)

    rgbas = np.empty((len(colors), 4))

    for (i, color, opacity) in zip(range(n), colors, _iter_scalar(opacities,
                                                                  n)):
        color, opacity = as_rgb_a(color, opacity)
        rgbas[i, :3], rgbas[i:, 3] = color, (1. if opacity is None else opacity)

    if scalars is None:
        scalars = np.arange(n)

    if resolution is None:
        resolution = (n - 1) * 255 + 1

    ts = np.linspace(scalars[0], scalars[-1], resolution)

    arr = zip_axes(*(np.interp(ts, scalars, i) for i in unzip_axes(rgbas)))

    return arr


#plt.imshow(np.broadcast_to(arr[:, np.newaxis], (len(arr), 100, 4)))

#if __name__ == "__main__":
#    import vtkplotlib as vpl
#    for args in [((.3, .4, .6), .2),
#                 ([5, 8, 10], None),
#                 ("red", ),
#                 ("orange red", .5),
#                 ("Orange_Red", ),
#                 ("or33ange_rEd", ),
#                 ]:
#        print("as_rgb_a", args, "->", as_rgb_a(*args), "\n")
#
#    path = Path('C:/Users/Brénainn/Downloads/3dm/duck/Bird_v1_L2.123ca5dbb1bc-8ef6-44e4-b558-3e6e2bbc7dd7/12248_Bird_v1_diff.jpg')
#
#    self = TextureMap(path)
#    self.interpolate = True
#
#    n = 1000
#    t = np.linspace(0, 1, n)
#    uv = vpl.nuts_and_bolts.zip_axes(*np.meshgrid(t, t))
#
##    plt.figure(figsize=(n // 72,) * 2)
##    plt.imshow(self(uv))
##    plt.show()
#
#    from PIL import Image
#    im = Image.fromarray((self(uv) * 255).astype(np.uint8))
#    im.show()

#    cmap = plt.get_cmap("Blues")
#    table = vtk.vtkLookupTable()
#    table_colors = cmap(np.arange(256, dtype=np.uint8))
#    table.SetTable(numpy_to_vtk((vpl.colors.colors.to_rgba_array(table_colors) * 255).astype(np.uint8), True))
