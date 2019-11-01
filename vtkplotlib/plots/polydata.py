# -*- coding: utf-8 -*-
# =============================================================================
# Created on Tue Aug 27 17:44:33 2019
#
# @author: Brénainn Woodsend
#
#
# polydata.py exposes the PolyData wrapper class.
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
import os
from pathlib2 import Path
from matplotlib.cm import get_cmap
import vtk
from vtk.util.numpy_support import (
    numpy_to_vtk,
    numpy_to_vtkIdTypeArray,
    vtk_to_numpy,
    get_vtk_to_numpy_typemap
)
import itertools

ID_ARRAY_NUMPY_DTYPE = get_vtk_to_numpy_typemap()[vtk.VTK_ID_TYPE]

# def unpack_id_array(arr, max_size):
#
from vtkplotlib import colors as vpl_colors

_numpy_to_vtk = numpy_to_vtk


def numpy_to_vtk(num_array, deep=0, array_type=None):
    assert deep or num_array.flags.contiguous
    return _numpy_to_vtk(np.ascontiguousarray(num_array), deep, array_type)


def cell_array_handler_property(name, doc=""):
    def getter(self):
        lines = getattr(self.vtk_polydata, "Get{}".format(name))()
        length = lines.GetNumberOfCells()
        if length:
            arr = vtk_to_numpy(lines.GetData())
            return unpack_lengths(arr)
        else:
            return []

    def setter(self, ids):
        if len(ids):
            ids = pack_lengths(ids)
            lines = vtk.vtkCellArray()
            lines.SetCells(len(ids), numpy_to_vtkIdTypeArray(
                ids.astype(ID_ARRAY_NUMPY_DTYPE).ravel(), deep=True))
            getattr(self.vtk_polydata, "Set{}".format(name))(lines)
        else:
            getattr(self.vtk_polydata, "Set{}".format(name))(None)

    def deleter(self):
        setter(self, [])

    return property(getter, setter, deleter, doc)


def colors_property(vtk_name, vpl_name, doc=""):
    def getter(self):
        colors = getattr(self.vtk_polydata, "Get{}Data".format(vtk_name))().GetScalars()
        if colors is None:
            return
        return vtk_to_numpy(colors)


    def setter(self, colors):

        if colors is not None:


            if colors.ndim == 1:
                colors = colors[:, np.newaxis]

            assert colors.ndim == 2

            self._colors = colors
            self._scalar_mode = colors.shape[1]

            if colors.shape[1] == 1:
#                colors = self.cmap(vpl_colors.normalise(colors))
                pass

            elif colors.shape[1] == 2:
                if self.texture_map is None:
                    raise ValueError("A texture map must be provided in polydata.texture_map to use uv scalars.")
                colors = self.texture_map(colors)

            elif colors.shape[1] == 3:
                pass

            else:
                assert 0

            colors = numpy_to_vtk(np.ascontiguousarray(
                                    colors), deep=True)
        getattr(self.vtk_polydata, "Get{}Data".format(vtk_name))().SetScalars(colors)
        setattr(self, "color_mode", vpl_name)

    def deleter(self):
        setattr(self, vpl_name, None)

    return property(getter, setter, deleter, doc)


def join_line_ends(lines):
    lines = np.asarray(lines)

    if lines.dtype == object:
        out = np.empty(lines.size, object)
        for (i, line) in enumerate(lines.flat):
            out[i] = line[np.arange(max(-1, -len(line)), len(line))]
        return out

    else:
        n, m = lines.shape
        return lines[:, np.arange(max(-1, -m), m)]


def pack_lengths(itr_of_arrays):
    if not isinstance(itr_of_arrays, (list, np.ndarray)):
        itr_of_arrays = list(itr_of_arrays)
    itr_of_arrays = np.asarray(itr_of_arrays)

    if itr_of_arrays.dtype == object:
        parts = itertools.chain(*[([len(i)], i) for i in itr_of_arrays.flat])
        return np.concatenate(list(parts))

    else:
        from vtkplotlib.nuts_and_bolts import flatten_all_but_last

        itr_of_arrays = flatten_all_but_last(itr_of_arrays)
        n, m = itr_of_arrays.shape
        lengths = np.empty((n, 1), int)
        lengths[:] = m
        return np.concatenate([lengths, itr_of_arrays], axis=1)


def unpack_lengths(arr):
    assert len(arr.shape) == 1

    def error_msg():
        print("Warning - checksum failed. This input array will cause VTK to crash if plotted.")

    if len(arr) == 0:
        return []

    m = arr[0]
    if (m == arr[::m + 1]).all():
        if len(arr) % (m + 1):
            error_msg()
        return arr.reshape((len(arr) // (m + 1), m + 1))[:, 1:]

    else:
        i = 1
        out = []
        while True:
            j = i + m
            if j > len(arr):
                error_msg()
                break
            else:
                out.append(arr[i: j])
                if j == len(arr):
                    break
                else:
                    m = arr[j]
                    i = j + 1

        return out


############################################################################


class PolyData(object):
    """The polydata is a key building block to making customised plot objects. A
    lot of vtkplotlib plot commands use one of these under the hood.

    :param vtk_polydata: An original vtkPolyData to build on top of, defaults to None.
    :type vtk_polydata: vtk.vtkPolyData, optional

    This is a wrapper around VTK's vtkPolyData object. This class is
    incomplete. I still need to sort colors/scalars properly. And I want to add
    functions to build from vtkSource objects.

    A polydata consists of:

    1. points
    2. lines
    3. polygons
    4. scalar, texturemap coordinates or direct color information

    or combinations of the four.

    :param self.points: All the vertices used for all points, lines and polygons. These points aren't visible. To create some kind of points plot use vpl.scatter.
    :type self.points: np.ndarray of floats with shape (`number_of_vertices`, `3`)

    :param self.lines: The arg of each vertex from `self.points` the line should pass through. Each row represents a seperate line.
    :type self.lines: np.ndarray of ints with shape (`number_of_lines`, `points_per_line`)

    :param self.polygons: Each row represents a polygon. Each cell contains the arg of a vertex from `self.points` that is to be a corner of that polygon.
    :type self.polygons: np.ndarray of ints with shape (`number_of_polygons`, `corners_per_polygon`)

    Lines and polyons can be interchanged to switch from solid surface to
    wire-frame.


    Here is an example to create a single triangle

    .. code-block:: python

        import vtkplotlib as vpl
        import numpy as np


        polydata = vpl.PolyData()

        polydata.points = np.array([[1, 0, 0],
                                    [0, 1, 0],
                                    [0, 0, 1]], float)

        # Create a wire-frame triangle passing points [0, 1, 2, 0].
        polydata.lines = np.array([[0, 1, 2, 0]])

        # Create a solid triangle with points [0, 1, 2] as it's corners.
        polydata.polygons = np.array([[0, 1, 2]])

        # The polydata can be quickly inspected using
        polydata.quick_show()

        # When you are happy with it, it can be turned into a proper plot
        # object like those output from other ``vpl.***()`` commands. It will be
        # automatically added to ``vpl.gcf()`` unless told otherwise.
        plot = polydata.to_plot()
        vpl.show()




    The original vtkPolyData object is difficult to use, can't directly work
    with numpy and is full of pot-holes that can cause unexplained crashes if
    not carefully avoided. This wrapper class seeks to solve those issues by
    acting as an intermediate layer between you and VTK. This class consists
    mainly of properties that

    - handle the numpy-vtk conversions
    - ensure proper shape checking
    - hides VTK's rather awkward compound array structures
    - automatically sets scalar mode/range parameters in the mapper

    A `vpl.PolyData` can be constructed from scratch or from an existing
    `vtkPolyData` object.

    It also provides convenience methods ``self.to_plot()`` and
    ``self.quick_show()`` for quick one-line visualising the current state.





    """
    def __init__(self, vtk_polydata=None):
        self.vtk_polydata = vtk_polydata or vtk.vtkPolyData()

        self.cmap = get_cmap()
        self.texture_map = None
#        self.color_mode = ""
        self._scalar_mode = 1


#        self.points = []
#        self.lines = []

    @property
    def points(self):
        points = self.vtk_polydata.GetPoints()
        if points is None:
            return None
        else:
            return vtk_to_numpy(points.GetData())

    @points.setter
    def points(self, vertices):
        vertices = np.ascontiguousarray(vertices)

        if vertices is None:
            self.vtk_polydata.SetPoints(None)
        else:
            points = vtk.vtkPoints()
            points.SetData(numpy_to_vtk(vertices, deep=True))
            self.vtk_polydata.SetPoints(points)

    lines = cell_array_handler_property("Lines")

    polygons = cell_array_handler_property("Polys")

    def __repr__(self):
        out = ["%s {\n" % self.__class__.__name__]
        for i in "points lines polygons".split():
            x = getattr(self, i)
            if x is not None:
                x = len(x)
            out.append("    {} {}{}\n".format(x, i[:-1], ("", "s")[x != 1]))
        out.append("}\n")

        return "".join(out)

    def to_plot(self, fig="gcf"):
        from vtkplotlib.plots.BasePlot import ConstructedPlot
        plot = ConstructedPlot(fig)
        plot.polydata = self
        plot.add_to_plot()
        return plot


    point_colors = colors_property("Point", "point_colors")
    polygon_colors = colors_property("Cell", "polygon_colors")

    _keys = {key for (key, val) in vars().items() if isinstance(val, property)}

    def __getstate__(self):
        state = {key: getattr(self, key) for key in self._keys}
#        del state["vtk_polydata"]
        return state

    def __setstate__(self, state):
        self.__init__()
        for i in state.items():
            setattr(self, *i)

    def __deepcopy__(self, memo):
        import pickle
        return pickle.loads(pickle.dumps(self))

    def quick_show(self):
        import vtkplotlib as vpl
        old_fig = vpl.gcf(create_new=False)

        fig = vpl.figure(repr(self))
        plot = self.to_plot(fig)
        vpl.show(fig)

        vpl.scf(old_fig)
        return plot

    def __add__(self, other):
        assert isinstance(other, self.__class__)
        new = self.__class__()
        points = [self.points, other.points]
        points[1] = points[1].astype(points[0].dtype)
        new.points = np.concatenate(points)

        for attr in ("polygons", "lines"):
            lines = [getattr(self, attr), getattr(other, attr)]
            try:
                lines[1] = lines[1] + len(points[0])
            except BaseException:
                for i in lines[1]:
                    i += len(points[0])

            try:
                lines = np.concatenate(lines)
            except ValueError:
                lines = list(lines[0]) + list(lines[1])

            setattr(new, attr, lines)

        colors = [self.point_colors, other.point_colors]
        for i in range(2):
            if colors[i] is None:
                colors[i] = np.zeros(len(points[i]))
        new.point_colors = np.concatenate(colors)

        return new


if __name__ == "__main__":
    import vtkplotlib as vpl

    t = np.arange(0, 1, .01) * 2 * np.pi
    points = np.array([np.cos(t), np.sin(t), np.cos(t)
                       * np.sin(t)], dtype=np.float32).T

    path = Path(vpl.data.get_rabbit_stl())

    vpl.QtFigure2().add_screenshot_button()

#    other = vpl.plot(points, color="r").polydata
    self = PolyData()
##    self.points = points
###
###    n, m = 10, 50
###    itr_of_arrays = np.random.randint(0, len(points), (n, m))
####    lines = np.concatenate((np.ones((n, 1), int) * m, lines), axis=1)
###
#    lines = [np.random.randint(0, len(t), np.random.randint(3, 5)) for i in range(10)]
#    self = vpl.plots.polydata.PolyData()
#    self.points = points
#    self.lines = join_line_ends(lines)
#    self.to_plot()

    from stl.mesh import Mesh
    vectors = Mesh.from_file(vpl.data.get_rabbit_stl()).vectors

    points = vpl.nuts_and_bolts.flatten_all_but_last(vectors)
    self.points = points
    polygons = np.arange(len(points)).reshape((len(points) // 3, 3))
    self.polygons = polygons

#    point_colors = points[:, np.newaxis, 0]
#    self.point_colors = point_colors

    point_colors = vpl.colors.normalise(points, axis=0)#[:, 0]

    self.point_colors = point_colors

    plot = self.to_plot()
#    plot.set_scalar_range((0, 1))
#    plot.mapper.SetScalarModeToUsePointData()
#    plot.mapper.SetColorMode(vtk.VTK_COLOR_MODE_DIRECT_SCALARS)
    vpl.show()
