# -*- coding: utf-8 -*-
# =============================================================================
# Created on Sun Aug  4 18:16:09 2019
#
# @author: Brénainn Woodsend
#
#
# test_plots.py tests the contents of the vtkplotlib.plots subpackage.
# Copyright (C) 2019  Brénainn Woodsend
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

import numpy as np
import vtkplotlib as vpl

import pytest

from tests._common import checker, numpy_stl


@checker()
def test_arrow():
    points = np.random.uniform(-10, 10, (2, 3))
    vpl.scatter(points)
    vpl.arrow(*points, color="g")


@checker()
def test_quiver():
    t = np.linspace(0, 2 * np.pi)
    points = np.array([np.cos(t), np.sin(t), np.cos(t) * np.sin(t)]).T
    grads = np.roll(points, 10)

    arrows = vpl.quiver(points, grads, color=grads)
    assert arrows.shape == t.shape


@checker()
def test_plot():
    t = np.arange(0, 1, .1) * 2 * np.pi
    points = np.array([np.cos(t), np.sin(t), np.cos(t) * np.sin(t)]).T
    vpl.plot(points, color="r", line_width=3, join_ends=True)


@checker()
def test_mesh():
    import time

    fig = vpl.gcf()

    path = vpl.data.get_rabbit_stl()
    _mesh = numpy_stl().Mesh.from_file(path)

    mp = vpl.mesh_plot(_mesh.vectors)

    fig.show(False)

    for i in range(10):
        mp.tri_scalars = (_mesh.x[:, 0] + 3 * i) % 20
        _mesh.rotate(np.ones(3), .1, np.mean(_mesh.vectors, (0, 1)))
        mp.vectors = _mesh.vectors
        fig.update()

        time.sleep(.01)


@checker()
def test_text():
    vpl.text("text", (100, 100), color="g")


@checker()
def test_surface():
    thi, theta = np.meshgrid(np.linspace(0, 2 * np.pi, 100),
                             np.linspace(0, np.pi, 50))

    x = np.cos(thi) * np.sin(theta)
    y = np.sin(thi) * np.sin(theta)
    z = np.cos(theta)

    vpl.surface(x, y, z, scalars=x.ravel())


@checker()
def test_scatter():
    points = np.random.uniform(-10, 10, (30, 3))

    colors = vpl.colors.normalise(points)
    radii = np.abs(points[:, 0])**.5

    vpl.scatter(points, color=colors, radius=radii, use_cursors=False)[0]
    self = vpl.scatter(points, color=colors, radius=radii, use_cursors=True)[0]
    self.point += np.array([10, 0, 0])


@checker()
def test_annotate():
    point = np.array([1, 2, 3])
    vpl.scatter(point)

    arrow, self = vpl.annotate(point, point, np.array([0, 0, 1]),
                               text_color="green", arrow_color="purple")
