# -*- coding: utf-8 -*-
# =============================================================================
# Created on Sat Jul 20 23:55:28 2019
#
# @author: Brénainn Woodsend
#
#
# MeshPlot.py plots a 3D stl (like) mesh.
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

from builtins import super

from vtkplotlib._get_vtk import vtk
import numpy as np
from pathlib2 import Path

from vtkplotlib.plots.BasePlot import ConstructedPlot
from vtkplotlib.plots.Lines import Lines

try:
    from stl.mesh import Mesh as NumpyMesh
    NUMPY_STL_AVAILABLE = True
except ImportError:
    NumpyMesh = None
    NUMPY_STL_AVAILABLE = False

MESH_DATA_TYPE_EX = lambda msg: ValueError("Invalid mesh_data argument. {}".
                                           format(msg))


def vtk_read_stl(path):
    from vtkplotlib.plots.polydata import PolyData
    from vtkplotlib.unicode_paths import PathHandler
    from vtkplotlib._vtk_errors import handler

    with PathHandler(path) as path_handler:
        reader = vtk.vtkSTLReader()
        handler.attach(reader)
        reader.SetFileName(path_handler.access_path)

        # Normally Reader doesn't do any reading until it's been plotted.
        # Update forces it to read.
        reader.Update()
        pd = PolyData(reader.GetOutput())

    # For some reason VTK just doesn't like some files. There are some vague
    # warnings in their docs - this could be what they're on about. If it
    # doesn't work ``reader.GetOutput()`` gives an empty polydata.
    if pd.vtk_polydata.GetNumberOfPoints() == 0:
        raise RuntimeError(
            "VTK's STLReader failed to read the STL file and no STL io backend "
            "is installed. VTK's STLReader is rather patchy. To read this file "
            "please ``pip install numpy-stl`` first.")

    return pd


def set_from_path(self, path, ignore_numpystl=False):

    # Ideally let numpy-stl open the file if it is installed.
    if NUMPY_STL_AVAILABLE and not ignore_numpystl:
        self.vectors = NumpyMesh.from_file(path).vectors
        return

    # Otherwise try vtk's STL reader - however it's not as reliable.
    self.polydata = vtk_read_stl(path)
    self.connect()


def set_vertices_index_pair(self, mesh_data):
    vertices, args = mesh_data
    if not isinstance(vertices, np.ndarray):
        raise MESH_DATA_TYPE_EX("First argument is of invalid type {}".format(
            type(vertices)))

    if vertices.shape[1:] != (3,):
        raise MESH_DATA_TYPE_EX("First argument has invalid shape {}. Should be"
                                " (..., 3).".format(vertices.shape))

    if not isinstance(args, np.ndarray):
        raise MESH_DATA_TYPE_EX("Second argument is of invalid type {}".format(
            type(args)))

    if args.shape[1:] != (3,):
        raise MESH_DATA_TYPE_EX(
            "Second argument has invalid shape {}. Should be"
            " (n, 3).".format(args.shape))

    if args.dtype.kind not in "iu":
        raise MESH_DATA_TYPE_EX("Second argument must be an int dtype array")

    self.vertices = vertices
    self.indices = args


def normalise_mesh_type(self, mesh_data):
    """Try to support as many of the mesh libraries out there as possible
    without having all of those libraries as dependencies.
    """
    # If string or Path then read from file.
    if isinstance(mesh_data, Path):
        mesh_data = str(mesh_data)
    if isinstance(mesh_data, str):
        set_from_path(self, mesh_data)
        return

    # If in (vertices, indices) format.
    if isinstance(mesh_data, tuple) and len(mesh_data) == 2:
        set_vertices_index_pair(self, mesh_data)
        return

    # If already an array then great.
    if isinstance(mesh_data, np.ndarray):
        vectors = mesh_data
    # If a mesh class that has the vectors in mesh.vectors as is conventional.
    elif hasattr(mesh_data, "vectors"):
        vectors = mesh_data.vectors
    else:
        raise MESH_DATA_TYPE_EX("")

    # Check shapes

    if vectors.shape[1:] != (3, 3):
        # Sometimes there are extra entries. pymesh has them. No idea why.
        vectors = vectors[:, :3, :3]

    if vectors.shape[1:] != (3, 3):
        raise MESH_DATA_TYPE_EX("mesh_data is invalid shape {}".format(
            vectors.shape))

    self.vectors = vectors


class MeshPlot(ConstructedPlot):
    """To plot STL files you will need some kind of STL reader library. If you don't
    have one then get `numpy-stl`_. Their Mesh class can be passed
    directly to :meth:`mesh_plot`.

    .. _numpy-stl: https://pypi.org/project/numpy-stl/

    :param mesh_data: The mesh to plot.
    :type mesh_data: An STL (like) object (see below)

    :param tri_scalars: Per-triangle scalar, texture-coordinates or RGB values, defaults to None.
    :type tri_scalars: np.ndarray, optional

    :param scalars: Per-vertex scalar, texture-coordinates or RGB values, defaults to None.
    :type scalars: np.ndarray, optional

    :param color: The color of the whole plot, ignored if scalars are used, defaults to white.
    :type color: str, 3-tuple, 4-tuple, optional

    :param opacity: The translucency of the plot, from `0` invisible to `1` solid, defaults to `1`.
    :type opacity: float, optional

    :param cmap: Colormap to use for scalars, defaults to `rainbow`.
    :type cmap: matplotlib cmap, `vtkLookupTable`_, or similar see :meth:`vtkplotlib.colors.as_vtk_cmap`, optional

    :param fig: The figure to plot into, can be None, defaults to :meth:`vtkplotlib.gcf`.
    :type fig: :class:`vtkplotlib.figure`, :class:`vtkplotlib.QtFigure`, optional

    :param label: Give the plot a label to use in legends, defaults to None.
    :type label: str, optional

    :return: A mesh object.
    :rtype: :class:`vtkplotlib.plots.MeshPlot.MeshPlot`


    The following example assumes you have installed `numpy-stl`_.

    .. code-block:: python

        import vtkplotlib as vpl
        from stl.mesh import Mesh

        # path = "if you have an STL file then put it's path here."
        # Otherwise vtkplotlib comes with a small STL file for demos/testing.
        path = vpl.data.get_rabbit_stl()

        # Read the STL using numpy-stl
        mesh = Mesh.from_file(path)

        # Plot the mesh
        vpl.mesh_plot(mesh)

        # Show the figure
        vpl.show()



    Unfortunately there are far too many mesh/STL libraries/classes out there to
    support them all. To overcome this as best we can, mesh_plot has a flexible
    constructor which accepts any of the following.


    1.  A filename.

    2.  Some kind of mesh class that has form `3` stored in ``mesh.vectors``.
        For example numpy-stl's stl.mesh.Mesh or pymesh's pymesh.stl.Stl


    3.   An np.array with shape (n, 3, 3) in the form:

        .. code-block:: python

           np.array([[[x, y, z],  # corner 0  \\
                      [x, y, z],  # corner 1  | triangle 0
                      [x, y, z]], # corner 2  /
                     ...
                     [[x, y, z],  # corner 0  \\
                      [x, y, z],  # corner 1  | triangle n-1
                      [x, y, z]], # corner 2  /
                    ])


        Note it's not uncommon to have arrays of shape (n, 3, 4) or (n, 4, 3)
        where the additional entries' meanings are usually irrelevant (often to
        represent scalars but as STL has no color this is always uniform). Hence
        to support mesh classes that have these, these arrays are allowed and the
        extra entries are ignored.


    4.  An np.array with shape (k, 3) of (usually unique) vertices in the form:

        .. code-block:: python

            np.array([[x, y, z],
                      [x, y, z],
                      ...
                      [x, y, z],
                      [x, y, z],
                      ])

        And a second argument of an np.array of integers with shape (n, 3) of point
        args in the form

        .. code-block:: python

            np.array([[i, j, k],  # triangle 0
                      ...
                      [i, j, k],  # triangle n-1
                      ])

        where i, j, k are the indices of the points (in the vertices array)
        representing each corner of a triangle.

        Note that this form can be (and is) easily converted to form 2) using

        .. code-block:: python

            vertices = unique_vertices[point_args]



    Hopefully this will cover most of the cases. If you are using or have written
    an STL library (or any other format) that you want supported then let me know.
    If it's numpy based then it's probably only a few extra lines to support. Or
    you can have a go at writing it yourself, either with :meth:`mesh_plot`  or
    with the :class:`vtkplotlib.PolyData` class.


    **Mesh plotting with scalars:**

    To create a heat map like image use the **scalars** or **tri_scalars** options.

    Use the **scalars** option to assign a scalar value to each point/corner:

    .. code-block:: python

        import vtkplotlib as vpl
        from stl.mesh import Mesh

        # Open an STL as before
        path = vpl.data.get_rabbit_stl()
        mesh = Mesh.from_file(path)

        # Plot it with the z values as the scalars. scalars is 'per vertex' or 1
        # value for each corner of each triangle and should have shape (n, 3).
        plot = vpl.mesh_plot(mesh, scalars=mesh.z)

        # Optionally the plot created by mesh_plot can be passed to color_bar
        vpl.color_bar(plot, "Heights")

        vpl.show()

    Use the **tri_scalars** option to assign a scalar value to each triangle:

    .. code-block:: python

        import vtkplotlib as vpl
        from stl.mesh import Mesh
        import numpy as np

        # Open an STL as before
        path = vpl.data.get_rabbit_stl()
        mesh = Mesh.from_file(path)

        # `tri_scalars` must have one value per triangle and have shape (n,) or (n, 1).
        # Create some scalars showing "how upwards facing" each triangle is.
        tri_scalars = np.inner(mesh.units, np.array([0, 0, 1]))

        vpl.mesh_plot(mesh, tri_scalars=tri_scalars)

        vpl.show()

    .. note:: **scalars** and **tri_scalars** overwrite each other and can't be used simultaneously.

    .. seealso::

        Having per-triangle-edge scalars doesn't fit well with VTK. So it got
        its own separate function :meth:`mesh_plot_with_edge_scalar`.

    """

    def __init__(self, mesh_data, tri_scalars=None, scalars=None, color=None,
                 opacity=None, cmap=None, fig="gcf", label=None):
        super().__init__(fig)
        self.connect()
        self.shape = (0, 3, 3)
        self._last_used_default_indices = False

        self.set_mesh_data(mesh_data)
        del mesh_data

        self.__setstate__(locals())

    set_mesh_data = normalise_mesh_type

    @property
    def vectors(self):
        if self._last_used_default_indices:
            return self.polydata.points.reshape(self.shape)
        else:
            return self.vertices[self.indices]

    @vectors.setter
    def vectors(self, vectors):
        vectors = np.asarray(vectors)
        self.polydata.points = vectors.reshape((-1, 3))

        # Ideally try to avoid rewriting the indices table.
        # ``self.vectors += translation`` shouldn't require a rewrite.
        # This is only safe to do if the user isn't directly playing with
        # self.indices. self._last_used_default_indices tests that.

        if vectors.shape == self.shape and self._last_used_default_indices:
            # If shape not changed, indices should be identical.
            return


#        print("rewrite indices")
        self.shape = vectors.shape

        if len(vectors) < self.shape[0] and self._last_used_default_indices:
            # If the mesh has been cropped, then the indices table can be
            # cropped.
            args = self.polydata.polygons[:len(vectors)]

        else:
            # Otherwise it has to be rewritten.
            args = np.arange(np.prod(self.shape[:-1]), dtype=self.polydata.ID_ARRAY_DTYPE)\
                        .reshape((-1, self.shape[-2]))

        self.polydata.polygons = args
        self._last_used_default_indices = True

    @property
    def vertices(self):
        return self.polydata.points

    @vertices.setter
    def vertices(self, v):
        self.polydata.points = v

    @property
    def indices(self):
        return self.polydata.polygons

    @indices.setter
    def indices(self, i):
        self.polydata.polygons = i
        self.shape = i.shape + (3,)
        self._last_used_default_indices = False

    scalars = Lines.color

    @property
    def tri_scalars(self):
        """Sets a scalar for each triangle for generating heatmaps.

        tri_scalars should be an 1D np.array of length n.

        Calls self.set_scalars. See set_scalars for implications.
        """
        return self.polydata.polygon_colors.reshape((self.shape[0], -1))

    @tri_scalars.setter
    def tri_scalars(self, tri_scalars):
        if tri_scalars is not None:
            if len(tri_scalars) != self.shape[0]:
                raise ValueError("`tri_scalars` should have the same length as "
                                 "`self.vectors` or `self.args` to be one value"
                                 " per triangle.")

            reshaped = tri_scalars.reshape((self.shape[0], -1))
            if 1 <= reshaped.shape[1] <= 3:
                tri_scalars = reshaped
            else:
                raise ValueError("`tri_scalars` should have shape ({0},), "
                                 "({0}, 1), ({0}, 2) or ({0}, 3). Received {1}"
                                 .format(self.shape[0], tri_scalars.shape)) # yapf: disable

        self.polydata.polygon_colors = tri_scalars

        if not self._freeze_scalar_range:
            self.scalar_range = Ellipsis

    @tri_scalars.deleter
    def tri_scalars(self):
        del self.polydata.polygon_colors


def mesh_plot_with_edge_scalars(mesh_data, edge_scalars, centre_scalar="mean",
                                opacity=None, cmap=None, fig="gcf", label=None):
    """Like :meth:`mesh_plot` but able to add scalars per triangle's edge. By default,
    the scalar value at centre of each triangle is taken to be the mean of the
    scalars of its edges, but it can be far more visually effective to use
    ``centre_scalar=fixed_value``.

    :param mesh_data: The mesh to plot.
    :type mesh_data: An STL (like) object (see below)

    :param edge_scalars: Per-edge scalar, texture-coordinates or RGB values.
    :type edge_scalars: np.ndarray

    :param centre_scalar: Scalar value(s) for the centre of each triangle, defaults to 'mean'.
    :type centre_scalar: str, optional

    :param opacity: The translucency of the plot, from `0` invisible to `1` solid, defaults to `1`.
    :type opacity: float, optional

    :param cmap: Colormap to use for scalars, defaults to `rainbow`.
    :type cmap: matplotlib cmap, `vtkLookupTable`_, or similar see :meth:`vtkplotlib.colors.as_vtk_cmap`, optional

    :param fig: The figure to plot into, can be None, defaults to :meth:`vtkplotlib.gcf`.
    :type fig: :class:`vtkplotlib.figure`, :class:`vtkplotlib.QtFigure`, optional

    :param label: Give the plot a label to use in legends, defaults to None.
    :type label: str, optional

    :return: A mesh plot object.
    :rtype: :class:`vtkplotlib.plots.MeshPlot.MeshPlot`


    Edge scalars are very much not the way VTK likes it. In fact VTK doesn't
    allow it. To overcome this, this function triple-ises each triangle. See
    the diagram below to see how this is done:

    .. code-block:: text

        (The diagram's tacky, I know)

                   p1

                 //|\\\\         Double lines represent the original triangle.
                // | \\\\        The single lines represent the division lines that
          l0   //  |  \\\\  l1   split the triangle into three.
              //  / \\  \\\\      The annotations show the order in which the
             // /     \\ \\\\     scalar for each edge must be provided.
            ///~~~~~~~~~\\\\\\
        p0  ~~~~~~~~~~~~~~~  p2
                  l2

        (reST doesn't like it either)

    Here is a usage example:

    .. code-block:: python

        import vtkplotlib as vpl
        from vtkplotlib import geometry
        from stl.mesh import Mesh
        import numpy as np


        path = vpl.data.get_rabbit_stl()
        mesh = Mesh.from_file(path)

        # This is the length of each side of each triangle.
        edge_scalars = geometry.distance(mesh.vectors[:, np.arange(1, 4) % 3] - mesh.vectors)

        vpl.mesh_plot_with_edge_scalars(mesh, edge_scalars, centre_scalar=0, cmap="Greens")

        vpl.show()



    I wrote this originally to visualise curvature. The calculation is ugly, but
    on the off chance someone needs it, here it is.

    .. code-block:: python

        import vtkplotlib as vpl
        from vtkplotlib import geometry
        from stl.mesh import Mesh
        import numpy as np


        path = vpl.data.get_rabbit_stl()
        mesh = Mesh.from_file(path)

        def astype(arr, dtype):
            return np.frombuffer(arr.tobytes(), dtype)

        def build_tri2tri_map(mesh):
            \"""This creates an (n, 3) array that maps each triangle to its 3
            adjacent triangles. It takes advantage of each triangles vertices
            being consistently ordered anti-clockwise. If triangle A shares an
            edge with triangle B then both A and B have the edges ends as
            vertices but in opposite order. Looking for this helps reduce the
            complexity of the problem.
            \"""

            # The most efficient way to make a pair of points hashable is to
            # take its binary representation.
            dtype = np.array(mesh.vectors[0, :2].tobytes()).dtype

            vectors_rolled = mesh.vectors[:, np.arange(1, 4) % 3]

            # Get all point pairs going one way round.
            pairs = np.concatenate((mesh.vectors, vectors_rolled), -1)

            # Get all point pairs going the other way round.
            pairs_rev = np.concatenate((vectors_rolled, mesh.vectors), -1)

            bin_pairs = astype(pairs, dtype).reshape(-1, 3)
            bin_pairs_rev = astype(pairs_rev, dtype).reshape(-1, 3)

            # Use a dictionary to find all the matching pairs.
            mapp = dict(zip(bin_pairs.ravel(), np.arange(bin_pairs.size) // 3))
            args = np.fromiter(map(mapp.get, bin_pairs_rev.flat), dtype=float, count=bin_pairs.size).reshape(-1, 3)

            # Triangles with a missing adjacent edge come out as nans.
            # Convert mapping to ints and nans to -1s.
            mask = np.isfinite(args)
            tri2tri_map = np.empty(args.shape, int)
            tri2tri_map[mask] = args[mask]
            tri2tri_map[~mask] = -1

            return tri2tri_map


        tri2tri_map = build_tri2tri_map(mesh)

        tri_centres = np.mean(mesh.vectors, axis=1)
        curves = np.cross(mesh.units[tri2tri_map], mesh.units[:, np.newaxis])
        displacements = tri_centres[tri2tri_map] - tri_centres[:, np.newaxis]
        curvatures = curves / geometry.distance(displacements, keepdims=True)

        curvature_signs = np.sign(geometry.inner_product(mesh.units[:, np.newaxis],
                                                         displacements)) * -1

        signed_curvatures = geometry.distance(curvatures) * curvature_signs

        # And finally, to plot it.
        plot = vpl.mesh_plot_with_edge_scalars(mesh, signed_curvatures)

        # Curvature must be clipped to prevent anomalies overwidening the
        # scalar range.
        plot.scalar_range = -.1, .1

        # Red represents an inside corner, blue represents an outside corner.
        plot.cmap = "coolwarm_r"

        vpl.show()

    """

    self = MeshPlot(mesh_data, fig=fig)
    vectors = self.vectors
    tri_centres = np.mean(vectors, 1)

    new_vectors = np.empty((len(vectors) * 3, 3, 3), vectors.dtype)
    # new_vectors.fill(np.nan)

    for i in range(3):
        for j in range(2):
            new_vectors[i::3, j % 3] = vectors[:, (i + j) % 3]

        new_vectors[i::3, 2 % 3] = tri_centres

    tri_scalars = edge_scalars.ravel()
    if centre_scalar == "mean":
        centre_scalars = np.mean(edge_scalars, 1)
    else:
        centre_scalars = centre_scalar

    new_scalars = np.empty((len(tri_scalars), 3), dtype=tri_scalars.dtype)
    new_scalars[:, 0] = new_scalars[:, 1] = tri_scalars
    for i in range(3):
        new_scalars[i::3, 2] = centre_scalars

    self.vectors = new_vectors
    self.scalars = new_scalars
    self.opacity = opacity
    self.fig = fig
    self.label = label
    self.cmap = cmap

    return self
