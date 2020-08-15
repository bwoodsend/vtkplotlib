# -*- coding: utf-8 -*-
# =============================================================================
# Created on 22:09
#
# @author: Brénainn
#
#
# test_polydata_based.py
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

from tests._common import checker


@checker()
def test_plot():
    t = np.arange(0, 1, .001) * 2 * np.pi
    vertices = np.array(
        [np.cos(2 * t),
         np.sin(3 * t),
         np.cos(5 * t) * np.sin(7 * t)]).T
    vertices = np.array([vertices, vertices + 2])

    t = np.arange(0, 1, .125) * 2 * np.pi
    vertices = vpl.zip_axes(np.cos(t), np.sin(t), 0)

    # vertices = np.random.uniform(-30, 30, (3, 3))
    # color = np.broadcast_to(t, vertices.shape[:-1])

    self = vpl.plot(vertices, line_width=6, join_ends=True, color=t)
    # self.polydata.point_scalars = vpl.geometry.distance(vertices)
    # self.polydata.point_colors = t
    fig = vpl.gcf()
    fig.background_color = "grey"


@checker()
def test_polygon():

    t = np.arange(0, 1, .1) * 2 * np.pi
    points = np.array([np.cos(t), np.sin(t), np.cos(t) * np.sin(t)]).T

    self = vpl.polygon(points, color="r")

    globals().update(locals())


@checker()
def test_texture():

    phi, theta = np.meshgrid(np.linspace(0, 2 * np.pi, 1024),
                             np.linspace(0, np.pi, 1024))

    x = np.cos(phi) * np.sin(theta)
    y = np.sin(phi) * np.sin(theta)
    z = np.cos(theta)

    self = vpl.surface(x, y, z, fig=None)
    path = vpl.data.ICONS["Right"]
    self.polydata.texture_map = vpl.TextureMap(path, interpolate=True)
    self.colors = (vpl.zip_axes(phi * 3, theta * 5) / np.pi) % 1.

    self.connect()
    vpl.gcf().add_plot(self)


if __name__ == "__main__":
    pytest.main([__file__])
