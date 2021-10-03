# -*- coding: utf-8 -*-
"""Test most of the contents of the vtkplotlib.plots module."""

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
    text = vpl.text("spaghetti", (100, 150), color="g")
    assert text.text == "spaghetti"
    assert np.all(text.position[:2] == (100, 150))
    assert np.all(text.color == vpl.colors.as_rgb_a("g")[0])
    text.text = "not spaghetti"
    assert text.actor.GetInput() == text.text == "not spaghetti"


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
    assert np.all(self.color == vpl.colors.as_rgb_a("green")[0])
    assert self.text == str(point)
    assert (self.position - point == (0, 0, 3)).all()
    assert np.all(arrow.color == vpl.colors.as_rgb_a("purple")[0])
