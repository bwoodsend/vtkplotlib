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

from unittest import TestCase, main, skipUnless
import numpy as np

import vtkplotlib as vpl
from vtkplotlib.tests.base import BaseTestCase

try:
    from stl.mesh import Mesh
except ImportError:
    Mesh = None


class TestPlots(BaseTestCase):

    @vpl.tests._figure_contents_check.checker()
    def test_arrow(self):
        points = np.random.uniform(-10, 10, (2, 3))
        vpl.scatter(points)
        vpl.arrow(*points, color="g")

    @vpl.tests._figure_contents_check.checker()
    def test_quiver(self):
        t = np.linspace(0, 2 * np.pi)
        points = np.array([np.cos(t), np.sin(t), np.cos(t) * np.sin(t)]).T
        grads = np.roll(points, 10)

        arrows = vpl.quiver(points, grads, color=grads)
        self.assertEqual(arrows.shape, t.shape)

    @vpl.tests._figure_contents_check.checker()
    def test_plot(self):
        t = np.arange(0, 1, .1) * 2 * np.pi
        points = np.array([np.cos(t), np.sin(t), np.cos(t) * np.sin(t)]).T
        vpl.plot(points, color="r", line_width=3, join_ends=True)

    @vpl.tests._figure_contents_check.checker()
    @skipUnless(Mesh, "numpy-stl is not installed")
    def test_mesh(self):
        import time

        fig = vpl.gcf()

        path = vpl.data.get_rabbit_stl()
        _mesh = Mesh.from_file(path)

        self = vpl.mesh_plot(_mesh.vectors)

        fig.show(False)

        for i in range(10):
            self.tri_scalars = (_mesh.x[:, 0] + 3 * i) % 20
            _mesh.rotate(np.ones(3), .1, np.mean(_mesh.vectors, (0, 1)))
            self.vectors = _mesh.vectors
            fig.update()

            time.sleep(.01)

    def test_polygon(self):
        vpl.plots.Polygon.test()
        vpl.plots.Lines.test()

    @skipUnless(Mesh, "numpy-stl is not installed")
    def test_scalar_bar(self):
        vpl.plots.ScalarBar.test()

    def test_scatter(self):
        vpl.plots.Scatter.test()

    @vpl.tests._figure_contents_check.checker()
    def test_text(self):
        vpl.text("text", (100, 100), color="g")

    def test_annotate(self):
        vpl.text3d
        vpl.plots.Text3D.test()

    @vpl.tests._figure_contents_check.checker()
    def test_surface(self):
        thi, theta = np.meshgrid(np.linspace(0, 2 * np.pi, 100),
                                 np.linspace(0, np.pi, 50))

        x = np.cos(thi) * np.sin(theta)
        y = np.sin(thi) * np.sin(theta)
        z = np.cos(theta)

        vpl.surface(x, y, z, scalars=x.ravel())

    def test_surface_and_texturemap(self):
        vpl.plots.Surface.test()

    def test_polydata(self):
        vpl.plots.polydata.test()
        vpl.plots.polydata.test_packing()

    def test_legend(self):
        vpl.plots.Legend.test()
