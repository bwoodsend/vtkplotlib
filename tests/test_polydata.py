# -*- coding: utf-8 -*-
"""
"""

import numpy as np

import pytest

pytestmark = pytest.mark.order(5)


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

    self.quick_show()

    self.polygons, self.lines = self.lines, self.polygons
    self.quick_show()

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
