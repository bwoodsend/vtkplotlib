# -*- coding: utf-8 -*-
"""Test the contents of the vtkplotlib.image_io module."""

import numpy as np
import os, sys
from pathlib import Path

import pytest
import vtkplotlib as vpl

from tests._common import TEST_DIR

import io

pytestmark = pytest.mark.order(2)


def test_trim_image():

    fig = vpl.figure()

    # Shouldn't do anything if the figure is empty.
    assert vpl.screenshot_fig(trim_pad_width=.05).shape[:2] == fig.render_size

    vpl.quick_test_plot()
    arr = vpl.screenshot_fig()
    vpl.close()

    trimmed = vpl.image_io.trim_image(arr, fig.background_color, 10)
    background_color = np.asarray(fig.background_color) * 255

    # Check that no non-background coloured pixels have been lost.
    assert (arr[:, :, :3] != background_color).any(-1).sum() \
           == (trimmed[:, :, :3] != background_color).any(-1).sum()

    return trimmed


def test_conversions():
    vpl.quick_test_plot()
    arr = vpl.screenshot_fig()
    vpl.close()

    image_data = vpl.image_io.vtkimagedata_from_array(arr)
    arr2 = vpl.image_io.vtkimagedata_to_array(image_data)

    assert np.array_equal(arr, arr2)


def _setup_test_image(fmt):
    source = Path(vpl.data.ICONS["Right"])
    name = source.stem + "." + vpl._image_io._normalise_format(None, fmt)
    dest = TEST_DIR / name

    if not dest.exists():
        pytest.importorskip("PIL.Image").open(str(source)).save(str(dest))

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
    return np.array(pytest.importorskip("PIL.Image").open(path))


@pytest.mark.parametrize("fmt, pseudo_file", pseudos["r"] + non_pseudos)
def test_read(fmt, pseudo_file):
    if fmt == "JPEG" and sys.platform == "linux":
        pytest.xfail("PIL gives a different array with this platform/"
                     "Python-version pair.")

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
        if dest.exists():
            os.remove(str(dest))
        file = dest

    vpl.image_io.write(original, file, dest.suffix)

    if not pseudo_file:
        assert dest.exists()

    written = pillow_open(file)

    assert written.shape == original.shape
    error = np.abs(written - original.astype(float)).mean()
    assert error < 1


def read_write_opacity():
    """Test reading and writing an image with translucent parts."""
    image = np.zeros((6, 8, 4), dtype=np.uint8)
    image[1, 3] = [100, 200, 255, 89]

    file = io.BytesIO()
    vpl.image_io.write(image, file, "PNG")
    assert (pillow_open(io.BytesIO(file.getvalue())) == image).all()
    assert (vpl.image_io.read(io.BytesIO(file.getvalue())) == image).all()
