# -*- coding: utf-8 -*-
"""
"""

import numpy as np

import pytest
import vtkplotlib as vpl

pytestmark = pytest.mark.order(6)


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


def test_polygon():

    t = np.arange(0, 1, .1) * 2 * np.pi
    points = np.array([np.cos(t), np.sin(t), np.cos(t) * np.sin(t)]).T

    self = vpl.polygon(points, color="r")

    globals().update(locals())


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
