# -*- coding: utf-8 -*-
# =============================================================================
# Created on 21:50
#
# @author: Brénainn
#
#
# test_imageio.py
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

from __future__ import print_function, unicode_literals, with_statement
from builtins import super

import numpy as np
import os, sys
from pathlib2 import Path

import pytest
import vtkplotlib as vpl

from tests._common import checker, TEST_DIR

import io


def test_trim_image():
    import matplotlib.pylab as plt

    fig = vpl.figure()

    # Shouldn't do anything if the figure is empty.
    assert vpl.screenshot_fig(trim_pad_width=.05).shape[:2] == fig.render_size

    vpl.quick_test_plot()
    arr = vpl.screenshot_fig()
    vpl.close()

    trimmed = vpl.image_io.trim_image(arr, fig.background_color, 10)
    background_color = np.asarray(fig.background_color) * 255

    # Check that no non-background coloured pixels have been lost.
    assert (arr != background_color).any(-1).sum() \
           == (trimmed != background_color).any(-1).sum()

    return trimmed


def test_conversions():
    vpl.quick_test_plot()
    arr = vpl.screenshot_fig()
    vpl.close()

    image_data = vpl.image_io.vtkimagedata_from_array(arr)
    arr2 = vpl.image_io.vtkimagedata_to_array(image_data)

    assert np.array_equal(arr, arr2)


needs_pillow = pytest.importorskip("PIL")


def _setup_test_image(fmt):
    source = Path(vpl.data.ICONS["Right"])
    name = source.stem + "." + vpl._image_io._normalise_format(None, fmt)
    dest = TEST_DIR / name

    if not dest.exists():
        from PIL import Image
        Image.open(str(source)).save(str(dest))

    return dest


non_pseudos = []
pseudos = {"r": [], "w": []}
for (fmt, modes) in vpl.image_io.BUFFERABLE_FORMAT_MODES:
    non_pseudos.append((fmt, False))
    for mode in "rw":
        if mode in modes:
            pseudos[mode].append((fmt, True))
        else:
            pseudos[mode].append(
                pytest.param(fmt, True, marks=pytest.mark.xfail))


def pillow_open(path):
    if not isinstance(path, io.IOBase):
        path = str(path)
    from PIL.Image import open
    return np.array(open(path))


@pytest.mark.parametrize("fmt, pseudo_file", pseudos["r"] + non_pseudos)
def test_read(fmt, pseudo_file):

    path = _setup_test_image(fmt)
    pillow_array = pillow_open(path)

    if pseudo_file:
        with open(str(path), "rb") as f:
            binary = f.read()
        file = io.BytesIO(binary)
    else:
        file = path

    vtk_array = vpl.image_io.read(file)
    assert (vtk_array == pillow_array).all()


@pytest.mark.parametrize("fmt, pseudo_file", pseudos["w"] + non_pseudos)
def test_write(fmt, pseudo_file):

    dest = TEST_DIR / ("image." + vpl._image_io._normalise_format(None, fmt))
    original = pillow_open(vpl.data.ICONS["Right"])

    if pseudo_file:
        file = io.BytesIO()
    else:
        file = dest

    vpl.image_io.write(original, file, dest.suffix)
    written = pillow_open(str(dest))

    assert written.shape == original.shape
    error = np.abs(written - original.astype(np.float)).mean()
    assert error < 1
