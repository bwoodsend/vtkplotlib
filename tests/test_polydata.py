# -*- coding: utf-8 -*-
# =============================================================================
# Created on 22:10
#
# @author: Brénainn
#
#
# test_polydata.py
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

import pytest
import vtkplotlib as vpl

from tests._common import checker, VTKPLOTLIB_WINDOWLESS_TEST


@checker()
def test(*spam):
    import vtkplotlib as vpl
    import numpy as np

    self = vpl.PolyData()

    vectors = vpl.mesh_plot(vpl.data.get_rabbit_stl(), fig=None).vectors

    points = vectors.reshape((-1, 3))
    self.points = points
    polygons = np.arange(len(points)).reshape((-1, 3))
    self.polygons = polygons

    point_colors = vpl.colors.normalise(points, axis=0)  #[:, 0]

    self.point_colors = point_colors

    if not VTKPLOTLIB_WINDOWLESS_TEST:
        self.quick_show()
    else:
        self.to_plot(fig=None)

    self.polygons, self.lines = self.lines, self.polygons
    if not VTKPLOTLIB_WINDOWLESS_TEST:
        self.quick_show()
    else:
        self.to_plot(fig=None)

    del self.lines
    del self.polygons
    self.lines = self.polygons = polygons

    copy = self.copy()
    assert np.array_equal(self.points, copy.points)
    assert np.array_equal(self.polygons, copy.polygons)
    assert np.array_equal(self.lines, copy.lines)
    assert np.array_equal(self.point_colors, copy.point_colors)
    assert np.array_equal(self.polygon_colors, copy.polygon_colors)

    copy.points += [100, 0, 0]

    (self + copy).to_plot()
    repr(self)

    globals().update(locals())


def test_packing():
    from vtkplotlib.plots.polydata import pack_lengths, unpack_lengths
    randint = np.random.randint

    x = [randint(0, 10, i) for i in randint(0, 10, 10)]

    packed = pack_lengths(x)
    unpacked = unpack_lengths(packed)

    assert len(x) == len(unpacked)
    assert all(map(np.array_equal, x, unpacked))


if __name__ == "__main__":
    pytest.main([__file__])
