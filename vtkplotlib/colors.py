# -*- coding: utf-8 -*-
"""
Created on Sat Aug  3 13:01:28 2019

@author: Brénainn Woodsend


colors.py
Shamelessly steals matplotlib's color library. Functions for handling different
color types.
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

from __future__ import division
from future.utils import string_types, as_native_str

import numpy as np
from matplotlib import colors, pylab as plt
from pathlib2 import Path
import vtk
from vtk.util.numpy_support import numpy_to_vtk


try:
    from PIL import Image
except ImportError:
    Image = None

try:
    from os import PathLike
except ImportError:
    PathLike = Path


mpl_colors = {}
mpl_colors.update(colors.BASE_COLORS)
for dic in (colors.CSS4_COLORS, colors.TABLEAU_COLORS, colors.XKCD_COLORS):
    for (key, val) in dic.items():
        mpl_colors[key.split(":")[-1]] = colors.hex2color(val)


def process_color(color=None, opacity=None):
    """This is designed to handle all the different ways a color and/or
    opacity can be given.

    'color' accepts either:
        A string color name. e.g "r" or "red". This uses matplotlib's
        named color libraries. See there or vtkplotlib.colors.mpl_colors for
        a full list of names.

        Or an html hex string in the form "#RRGGBB". (An alpha here is silently ignored.)

        Or any iterable of length 3 or 4 representing
            (r, g, b) or (r, g, b, alpha)
        r, g, b, alpha can be from 0 to 1 or from 0 to 255 (inclusive).
        Conventionally if they are from 0 to 1 they should be floats and if they
        are from 0 to 255 they should be ints. But this is so often not the
        case that this rule is useless. This function divides by 255 if it sees
        anything greater than 1. Hence from 0 to 1 is the preferred format.

    'opacity':
        An scalar like the numbers for 'color'.'opacity' overides alpha
        if alpha is provided in 'color'.

"""

    color_out = None
    opacity_out = None

    if color is not None:
        if isinstance(color, str):
            if color[0] == "#":
                # allow #RRGGBB hex colors
                # mpl's hex2rgb doesn't allow opacity. Otherwise I'd just use that
                return process_color(tuple(int(color[i: 2 + i], 16) for i in range(1, len(color), 2)),
                                     opacity)
            else:
                # use matplotlib's color library
                if color in mpl_colors:
                    color = mpl_colors[color]
                else:
                    # If not in mpl's library try to correct user input and try again
                    corrected = color.lower().replace("_", " ").replace("-", " ")
                    if corrected in mpl_colors:
                        print("Auto-correcting color {!r} to {!r}.\nMatplotlib colors are all lowercase and use spaces instead of underscores.".format(color, corrected))
                        color = mpl_colors[corrected]

                    else:
                        # If still not found then cancel the whole operation (including opacity)
                        print("Color {!r} not found. Skipping color assignment. See vtkplotlib.colors.mpl_colors.keys() for a list of available colors.".format(color))
                        return None, None


        color = np.asarray(color)
        if color.dtype == int and color.max() > 1:
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


def normalise(colors, axis=None):
    colors = colors - np.nanmin(colors, axis=axis, keepdims=True)
    colors /= np.max(colors, axis=axis, keepdims=True)
    return colors



class TextureMap(object):
    def __init__(self, array, interpolate=False):

        if isinstance(array, PathLike):
            array = str(array)
        if isinstance(array, string_types):
            try:
#                raise ValueError()
                array = plt.imread(array)
            except ValueError:
                from vtkplotlib.image_io import read
                array = read(array)
            array = np.swapaxes(array, 0, 1)[:, ::-1]
        if Image and isinstance(array, Image.Image):
            array = np.array(array)
            array = np.swapaxes(array, 0, 1)[:, ::-1]

        ex = lambda x: TypeError("`array` must be an np.ndarray with shape (m, n, 3) or (m, n, 4). Got {} {}".format(x, as_native_str(array)))
        if (not isinstance(array, np.ndarray)):
            raise ex(type(array))
        if (len(array.shape) != 3):
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

            weights = np.sum(np.abs(uv_corners - uv[np.newaxis, np.newaxis]), -1)
            weights = np.max(weights, (0, 1)) - weights
            weights += np.all(weights == 0, (0, 1), keepdims=True)
            total_weights = np.sum(weights, (0, 1), keepdims=True)

            normed_weights = weights / total_weights

            return np.sum(self.array[uv_corners[..., 0], uv_corners[..., 1]] \
                          * normed_weights[..., np.newaxis],
                          (0, 1))

        else:
            uv = uv.astype(np.uint)
            return self.array[uv[..., 0], uv[..., 1]]

converted_cmaps = {}
temp = []

def vtk_cmap(cmap):
    if isinstance(cmap, str):
        if cmap in converted_cmaps:
            return converted_cmaps[cmap]
        cmap = plt.get_cmap(cmap)

    if isinstance(cmap, vtk.vtkLookupTable):
        return cmap

    if isinstance(cmap, (colors.ListedColormap, colors.LinearSegmentedColormap)):
        name = cmap.name
        if name in converted_cmaps:
            return converted_cmaps[name]
    else:
        name = None

    if isinstance(cmap, colors.ListedColormap):
        cmap = np.array(cmap.colors)

    if callable(cmap):
        cmap = cmap(np.arange(256, dtype=np.uint8))

    if not isinstance(cmap, np.ndarray):
        raise TypeError()

    if cmap.ndim == 2 and 3 <= cmap.shape[1] <= 4:
        cmap = np.ascontiguousarray((colors.to_rgba_array(cmap) * 255).astype(np.uint8))
        table = vtk.vtkLookupTable()
        table.SetTable(numpy_to_vtk(cmap))

        temp.append(cmap)
        if name is not None:
            converted_cmaps[name] = table
        return table

    else:
        raise ValueError()






if __name__ == "__main__":
    import vtkplotlib as vpl
    for args in [((.3, .4, .6), .2),
                 ([5, 8, 10], None),
                 ("red", ),
                 ("orange red", .5),
                 ("Orange_Red", ),
                 ("or33ange_rEd", ),
                 ]:
        print("process_color", args, "->", process_color(*args), "\n")

    path = Path('C:/Users/Brénainn/Downloads/3dm/duck/Bird_v1_L2.123ca5dbb1bc-8ef6-44e4-b558-3e6e2bbc7dd7/12248_Bird_v1_diff.jpg')

    self = TextureMap(path)
    self.interpolate = True

    n = 1000
    t = np.linspace(0, 1, n)
    uv = vpl.nuts_and_bolts.zip_axes(*np.meshgrid(t, t))

#    plt.figure(figsize=(n // 72,) * 2)
#    plt.imshow(self(uv))
#    plt.show()

    from PIL import Image
    im = Image.fromarray((self(uv) * 255).astype(np.uint8))
#    im.show()

#    cmap = plt.get_cmap("Blues")
#    table = vtk.vtkLookupTable()
#    table_colors = cmap(np.arange(256, dtype=np.uint8))
#    table.SetTable(numpy_to_vtk((vpl.colors.colors.to_rgba_array(table_colors) * 255).astype(np.uint8), True))
