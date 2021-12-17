# -*- coding: utf-8 -*-

# I would avoid looking in here - it's chaos.

import numpy as np
import operator

from vtkplotlib._get_vtk import (vtk, numpy_to_vtk, numpy_to_vtkIdTypeArray,
                                 vtk_to_numpy, get_vtk_to_numpy_typemap)

ID_ARRAY_DTYPE = get_vtk_to_numpy_typemap()[vtk.VTK_ID_TYPE]

from vtkplotlib import colors as vpl_colors

_numpy_to_vtk = numpy_to_vtk


def numpy_to_vtk(num_array, deep=0, array_type=None):
    assert deep or num_array.flags.contiguous
    return _numpy_to_vtk(num_array, deep, array_type)


def cell_array_handler_property(name, doc=""):
    """The cells API is identical for polygons and lines. Cells being args of
    points. E.g this line goes through points [1, 3, 4, 1] forming a closed
    triangle. Or this polygon has points [1, 3, 4] as its corners would form
    the same triangle but coloured in.
    """
    getter_getter = operator.attrgetter("vtk_polydata.Get" + name)
    setter_getter = operator.attrgetter("vtk_polydata.Set" + name)

    def getter(self):
        lines = getter_getter(self)()
        length = lines.GetNumberOfCells()
        if length:
            arr = vtk_to_numpy(lines.GetData())
            return unpack_lengths(arr)
        else:
            return []

    def setter(self, ids):
        if ids is not None and len(ids):
            ids = pack_lengths(ids)
            lines = vtk.vtkCellArray()
            ids = np.ascontiguousarray(ids, dtype=ID_ARRAY_DTYPE)
            lines.SetCells(len(ids), numpy_to_vtkIdTypeArray(ids.ravel()))
            lines._numpy_reference = ids

            setter_getter(self)(lines)
        else:
            setter_getter(self)(None)

    def deleter(self):
        setter(self, None)

    return property(getter, setter, deleter, doc)


def colors_property(vtk_name, vpl_name, doc=""):
    """The colors API is identical for per-polygon colors and per-point colors.
    Therefore this ugly mess handles both to avoid duplicity of code.

    Single colors for the entire plot is not included. That should be handled
    after the polydata has been turned into a ConstructedPlot.
    """
    getter_getter = operator.attrgetter(
        "vtk_polydata.Get{}Data".format(vtk_name))

    def getter(self):
        colors = getter_getter(self)().GetScalars()
        if colors is None:
            return
        return vtk_to_numpy(colors)

    def setter(self, colors):

        if colors is not None:

            if colors.ndim == 1:
                colors = colors[:, np.newaxis]

            if colors.ndim != 2:
                raise ValueError("`colors` must be either 1-D or 2-D")
            colors = np.ascontiguousarray(colors)

            if colors.shape[1] == 1:
                # treat colors as scalars to be passed through a colormap
                self.color_mode = vtk.VTK_COLOR_MODE_DEFAULT

            elif colors.shape[1] == 2:
                # treat colors as texture coordinates to be passed through a texturemap
                # currently texture maps haven't been properly implemented. The
                # colors are evaluated immediately here.
                if self.texture_map is None:
                    raise ValueError(
                        "A texture map must be provided in polydata.texture_map to use uv scalars."
                    )
                colors = self.texture_map(colors)
                # self.color_mode = vtk.VTK_COLOR_MODE_MAP_SCALARS
                self.color_mode = vtk.VTK_COLOR_MODE_DIRECT_SCALARS

            elif colors.shape[1] == 3:
                # treat colors as raw RGB values
                self.color_mode = vtk.VTK_COLOR_MODE_DIRECT_SCALARS

            else:
                raise ValueError("{} is an invalid shape.".format(colors.shape))

            self._colors = colors

            colors = numpy_to_vtk(colors)
            colors._numpy_ref = self._colors

        getter_getter(self)().SetScalars(colors)
        setattr(self, "color_source", vpl_name)

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


def pack_lengths(arrays):
    """Packs into VTK's compound cell array format which is designed to allow
    cells of different lengths in the same array of cells. The output format is
    a 1D array of the form
    [no of points in cell, cell_id1, cell_id2, ..., no of points in next cell, id1, id2, ...]
`
    ..doctest::

        >>> pack_lengths([[20, 21, 22],
        ...               [23, 24],
        ...               [25, 26, 27, 28]])
        array([ 3, 20, 21, 22,  2, 23, 24,  4, 25, 26, 27, 28])

    .. seealso:

        unpack_lengths for the reverse.
    """

    if isinstance(arrays, np.ndarray) and arrays.dtype != object:
        # This is just a regular numpy array with equal-lengthed rows.
        # Prepend an extra column containing the row length.

        arrays = arrays.reshape((-1, arrays.shape[-1]))

        out = np.empty((arrays.shape[0], arrays.shape[1] + 1), ID_ARRAY_DTYPE)
        out[:, 0] = arrays.shape[1]
        out[:, 1:] = arrays

        return out

    # Otherwise do it the slow way.
    flat = []
    for array in arrays:
        flat.append(len(array))
        flat.extend(array)
    return np.array(flat, dtype=ID_ARRAY_DTYPE)


def unpack_lengths(arr):
    assert len(arr.shape) == 1

    def error_msg():
        print("Warning - checksum failed. This input array will cause VTK to"
              " crash if plotted.")

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
                out.append(arr[i:j])
                if j == len(arr):
                    break
                else:
                    m = arr[j]
                    i = j + 1

        return out


SCALAR_MODES_TO_STRINGS = {
    vtk.VTK_SCALAR_MODE_DEFAULT: None,
    vtk.VTK_SCALAR_MODE_USE_CELL_DATA: "polygon_colors",
    vtk.VTK_SCALAR_MODE_USE_POINT_DATA: "point_colors"
}
SCALAR_MODES_FROM_STRINGS = {
    val: key for (key, val) in SCALAR_MODES_TO_STRINGS.items()
}

#COLOR_MODES_TO_STRINGS = {vtk.VTK_COLOR_MODE_DEFAULT:  }

############################################################################


class PolyData(object):
    """The polydata is a key building block to making customised plot objects.
    The `mesh_plot`, `plot` and `surface` methods are in fact just a thin
    wrapping layer around a `PolyData`. This class itself is a wrapper
    around VTK's `vtkPolyData`_ object.

    :param vtk_polydata: An original `vtkPolyData`_ to build on top of, defaults to constructing a new one from scratch.
    :type vtk_polydata: `vtkPolyData`_


    A polydata consists of the following 2D numpy arrays:

    +--------------------+---------+---------------+-------------------------------+
    | Attribute name     | dtype   | shape         | Meaning                       |
    +--------------------+---------+---------------+-------------------------------+
    | ``points``         | `float` | | ``(a, 3)``  | All line start and end points |
    |                    |         |               | and all polygon corners.      |
    +--------------------+---------+---------------+-------------------------------+
    | ``lines``          | `int`   | | ``(b, 3)``  | Each row of **lines**         |
    |                    |         |               | corresponds the point indices |
    |                    |         |               | a line passes through.        |
    +--------------------+---------+---------------+-------------------------------+
    | ``polygons``       | `int`   | | ``(c, 3)``  | Each row of **polygons**      |
    |                    |         |               | corresponds the point indices |
    |                    |         |               | a the corners of a polygon.   |
    +--------------------+---------+---------------+-------------------------------+
    | ``point_colors``   | `float` | | ``(a,)`` or | Per-point scalars, texture    |
    |                    |         |   ``(a, 1)``  | coordinates or RGB values,    |
    |                    |         | | ``(a, 2)``  | depending on the shape.       |
    |                    |         | | ``(a, 3)``  |                               |
    +--------------------+---------+---------------+-------------------------------+
    | ``polygon_colors`` | `float` | | ``(c,)`` or | Per-polygon scalars, texture  |
    |                    |         |   ``(c, 1)``  | coordinates or RGB values,    |
    |                    |         | | ``(c, 2)``  | depending on the shape.       |
    |                    |         | | ``(c, 3)``  |                               |
    +--------------------+---------+---------------+-------------------------------+

    Where ``a``, ``b`` and ``c`` are defined as the numbers of vertices, lines
    and polygons respectively.

    The points aren't visible themselves - to create some kind of points plot
    use `vtkplotlib.scatter()`.

    Lines and polygons can be interchanged to switch from solid surface to
    wire-frame.


    Here is an example to create a single triangle

    .. code-block:: python

        import vtkplotlib as vpl
        import numpy as np


        polydata = vpl.PolyData()

        polydata.points = np.array([[1, 0, 0],          # vertex 0
                                    [0, 1, 0],          # vertex 1
                                    [0, 0, 1]], float)  # vertex 2

        # Create a wire-frame triangle passing through vertices [0, 1, 2, 0].
        polydata.lines = np.array([[0, 1, 2, 0]])

        # Create a solid triangle with vertices [0, 1, 2] as it's corners.
        polydata.polygons = np.array([[0, 1, 2]])

        # The polydata can be quickly inspected using
        polydata.quick_show()

        # When you are happy with it, it can be turned into a proper plot
        # object like those output from other ``vpl.***()`` commands. It will be
        # automatically added to `vtkplotlib.gcf()` unless told otherwise.
        plot = polydata.to_plot()
        vpl.show()

    """

    def __init__(self, vtk_polydata=None, mapper=None):
        self.vtk_polydata = vtk_polydata or vtk.vtkPolyData()
        self.mapper = mapper or vtk.vtkPolyDataMapper()

        self.texture_map = None
        self._temp = []

    @property
    def points(self):
        points = self.vtk_polydata.GetPoints()
        if points is None:
            return None
        else:
            data = points.GetData()
            self._temp.append(data)
            return vtk_to_numpy(data)

    @points.setter
    def points(self, vertices):
        vertices = np.ascontiguousarray(vertices)
        # Store this to keep its data from being garbage collected.
        self._vertices = vertices

        if vertices is None:
            self.vtk_polydata.SetPoints(None)
        else:
            points = self.vtk_polydata.GetPoints() or vtk.vtkPoints()
            points.SetData(numpy_to_vtk(vertices))
            points._numpy_reference = vertices
            self.vtk_polydata.SetPoints(points)

    lines = cell_array_handler_property("Lines")

    polygons = cell_array_handler_property("Polys")

    ID_ARRAY_DTYPE = globals()["ID_ARRAY_DTYPE"]

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
        plot.connect()
        return plot

    point_colors = colors_property("Point", "point_colors")
    polygon_colors = colors_property("Cell", "polygon_colors")

    def __getstate__(self):
        state = {key: getattr(self, key) for key in self._keys}
        return state

    def __setstate__(self, state):
        self.__init__()
        for i in state.items():
            if i[1] is not None:
                setattr(self, *i)

    def __deepcopy__(self, memo):
        import pickle
        return pickle.loads(pickle.dumps(self))

    def copy(self):
        return self.__deepcopy__(None)

    def quick_show(self):

        plot = self.to_plot(fig=None)
        plot.quick_show()

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

    @property
    def color_source(self):
        """Use to select either point_colors or polygon_colors"""
        return SCALAR_MODES_TO_STRINGS[self.mapper.GetScalarMode()]

    @color_source.setter
    def color_source(self, mode):
        if not isinstance(mode, int):
            mode = SCALAR_MODES_FROM_STRINGS[mode]
        self.mapper.SetScalarMode(mode)

    @property
    def color_mode(self):
        """Use to select the interpretation of `self.[]_colors`.

        +-----------------------------------+-------------------+
        | int constant                      | interpretation    |
        +===================================+===================+
        | vtk.VTK_COLOR_MODE_DEFAULT        | scalars           |
        +-----------------------------------+-------------------+
        | vtk.VTK_COLOR_MODE_MAP_SCALARS    | texture coords    |
        +-----------------------------------+-------------------+
        | vtk.VTK_COLOR_MODE_DIRECT_SCALARS | direct RGB values |
        +-----------------------------------+-------------------+

        """
        return self.mapper.GetColorMode()

    @color_mode.setter
    def color_mode(self, mode):
        self.mapper.SetColorMode(mode)

    @property
    def scalar_range(self):
        return self.mapper.GetScalarRange()

    @scalar_range.setter
    def scalar_range(self, range=None):
        if range is None or range is Ellipsis:
            if self.color_source == "point_colors":
                range = self.point_colors

            elif self.color_source == "polygon_colors":
                range = self.polygon_colors

            if range is None or range is Ellipsis:
                return

        self.mapper.SetScalarRange(np.nanmin(range), np.nanmax(range))

    @property
    def cmap(self):
        return self.mapper.GetLookupTable()

    @cmap.setter
    def cmap(self, cmap):
        if cmap is not None:
            self.mapper.SetLookupTable(vpl_colors.as_vtk_cmap(cmap))

    @cmap.deleter
    def cmap(self):
        # This resets the cmap to the
        self.cmap.ForceBuild()

    _keys = [key for (key, val) in vars().items() if isinstance(val, property)]
    _keys.remove("cmap")
