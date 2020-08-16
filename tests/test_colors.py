# -*- coding: utf-8 -*-
# =============================================================================
# Created on 23:32
#
# @author: Brénainn
#
#
# test_colors.py
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

from __future__ import print_function, unicode_literals, with_statement, division
from builtins import super

import numpy as np
import os, sys
import re

import pytest
import vtkplotlib as vpl

from tests._common import checker

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

try:
    from PyQt5.QtGui import QColor
    parameters += [
        (QColor(*(int(i * 255) for i in RGB)), A, None),
        (QColor("#01FF06"), A, None),
    ]
except ImportError:
    pass


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


if __name__ == "__main__":
    pytest.main([__file__])
