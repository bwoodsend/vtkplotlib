# -*- coding: utf-8 -*-
"""
"""

import numpy as np
import os, sys
import re

import pytest
import vtkplotlib as vpl

from matplotlib import cm

pytestmark = pytest.mark.order(0)

# Target output. Everything below should normalise to this.
RGB, A = (np.array([0.00392157, 1., 0.02745098]), .5)

parameters = [
    (RGB, A, None),
    (tuple(RGB) + (A,), None, None),
    ((RGB * 255).astype(int), int(A * 255), None),
    ("bright green", A, None),
    ("BRIGHT-GREEN", A, Warning),
    ("BRIGHT_GrEeN", A, Warning),
    ("#01FF06", A * 255, None),
    ("#01FF0680", None, None),
    ("#01FF0610", 0x80, None),
    (u"bright green", A, None),
]


@pytest.mark.parametrize(("rgb", "a", "warns"), parameters)
def test_as_rgb_a(rgb, a, warns):
    if warns:
        with pytest.warns(warns):
            rgb, a = vpl.colors.as_rgb_a(rgb, a)
    else:
        rgb, a = vpl.colors.as_rgb_a(rgb, a)
    assert pytest.approx(RGB, abs=1 / 255) == rgb
    assert pytest.approx(A, abs=1 / 255) == a


def test_as_rgb_a_misc():
    with pytest.warns(Warning):
        assert vpl.colors.as_rgb_a("not a color") == (None, None)
    with pytest.raises(ValueError):
        vpl.colors.as_rgb_a("#12312")
    assert vpl.colors.as_rgb_a() == (None, None)


@pytest.mark.parametrize("name",
                         re.findall(r"table[.](\w+)\(\)", vpl.colors.__doc__))
def test_table_in_doc(name):
    """Check all the functions listed in one of the table under `vtkLookupTable`
     in the docs actually exist.
     """
    assert hasattr(vpl.vtk.vtkLookupTable, name)


INPUTS = [
    ([(1, 0, .5), (0, 1, .5)], .2, None, None),
    ([(0, 0, 0, 1), (0, 1, 0)], None, None, 123),
    ([(1, 1, 0, 1)], None, None, 100),
    ([(0, 0, 0, 1), (0, 1, 0), (.2, .3, .4)], None, None, 123),
]


@pytest.mark.parametrize(("colors", "opacities", "scalars", "resolution"),
                         INPUTS)
def test_cmap_from_list(colors, opacities, scalars, resolution):
    cmap = vpl.colors.cmap_from_list(colors, opacities, scalars, resolution)
    assert (cmap[0][:len(colors[0])] == colors[0]).all()
    assert (cmap[-1][:len(colors[-1])] == colors[-1]).all()

    assert resolution is None or cmap.shape == (resolution, 4)


def test_cmap_from_list_scalars():
    colors = vpl.colors.cmap_from_list(["b", "w", "g"])
    scalars = np.exp(np.linspace(0, np.log(len(colors)), len(colors)))
    vpl.colors.cmap_from_list(colors, scalars=scalars)


def test_as_vtk_cmap_from_list():
    vpl.colors.as_vtk_cmap(["orange", "blue"])


cmaps = ["Blues", "Set2"]


def test_cmap_types_differ():
    assert type(cm.get_cmap(cmaps[0])) is not type(cm.get_cmap(cmaps[1]))


@pytest.mark.parametrize("cmap", cmaps)
def test_as_cmap(cmap):
    as_vtk_cmap = vpl.colors.as_vtk_cmap
    assert as_vtk_cmap(cmap) is as_vtk_cmap(cmap)
    assert as_vtk_cmap(cmap) is not as_vtk_cmap(cmap, False)

    assert as_vtk_cmap(cmap) is as_vtk_cmap(as_vtk_cmap(cmap))
    assert as_vtk_cmap(cmap) is as_vtk_cmap(cm.get_cmap(cmap))


def test_cmap_raises():
    with pytest.raises(ValueError):
        vpl.colors.as_vtk_cmap(np.arange(10))

    with pytest.raises(ValueError):
        vpl.colors.as_vtk_cmap(np.arange(10).reshape(5, 2))


if __name__ == "__main__":
    pytest.main([__file__])
