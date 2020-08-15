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

import pytest
import vtkplotlib as vpl

from tests._common import checker

rgb, a = (np.array([0.00392157, 1., 0.02745098]), .5)


@pytest.mark.parametrize("rgb_a", [
    (rgb, a),
    (tuple(rgb) + (a,),),
    ((rgb * 255).astype(int), int(a * 255)),
    ("bright green", a),
    ("BRIGHT-GREEN", a),
    ("BRIGHT_GrEeN", a),
    ("#01FF06", a * 255),
])
def test_as_rgb_a(rgb_a):
    _rgb, _a = vpl.colors.as_rgb_a(*rgb_a)
    assert pytest.approx(rgb, abs=1 / 255) == _rgb
    assert pytest.approx(a, abs=1 / 255) == _a


def test_as_rgb_a_warns():
    assert vpl.colors.as_rgb_a("not a color") == (None, None)


if __name__ == "__main__":
    pytest.main([__file__])
