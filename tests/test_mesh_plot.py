# -*- coding: utf-8 -*-
"""Test mesh plotting."""

from __future__ import print_function, unicode_literals, with_statement
from builtins import super

import numpy as np
import os, sys
from pathlib2 import Path

import pytest
import vtkplotlib as vpl

from tests._common import checker, numpy_stl

path = vpl.data.get_rabbit_stl()


def test_type_normalise():
    mesh = numpy_stl().Mesh.from_file(path)
    vectors = mesh.vectors

    unique_points = set(tuple(i) for i in vectors.reshape(len(vectors) * 3, 3))
    points_enum = {point: i for (i, point) in enumerate(unique_points)}

    points = np.array(sorted(unique_points, key=points_enum.get))
    point_args = np.apply_along_axis(lambda x: points_enum[tuple(x)], -1,
                                     vectors)

    vpl.plots.MeshPlot.NUMPY_STL_AVAILABLE = False

    for fmt in (path, mesh, vectors, (points, point_args)):
        normalised = vpl.mesh_plot(fmt).vectors
        assert np.array_equal(normalised, vectors)

    vpl.plots.MeshPlot.NUMPY_STL_AVAILABLE = True

    vpl.close()


@checker()
def test_edge_scalars():

    fig = vpl.gcf()

    _mesh = numpy_stl().Mesh.from_file(path)

    mesh_data = _mesh.vectors
    mesh_data = path

    edge_scalars = vpl.geometry.distance(
        _mesh.vectors[:,np.arange(1, 4) % 3] - _mesh.vectors) # yapf: disable

    self = vpl.mesh_plot_with_edge_scalars(_mesh, edge_scalars, centre_scalar=0)
    self.cmap = "Reds"


if __name__ == "__main__":
    pytest.main([__file__])
