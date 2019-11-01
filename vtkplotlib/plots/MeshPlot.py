# -*- coding: utf-8 -*-
# =============================================================================
# Created on Sat Jul 20 23:55:28 2019
#
# @author: Brénainn Woodsend
#
#
# MeshPlot.py plots a 3D stl (like) mesh.
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

from builtins import super

import vtk
import numpy as np
from pathlib2 import Path
from vtk.util.numpy_support import (
                                    numpy_to_vtk,
                                    numpy_to_vtkIdTypeArray,
                                    vtk_to_numpy,
                                    )



from vtkplotlib.plots.BasePlot import ConstructedPlot
from vtkplotlib.nuts_and_bolts import flatten_all_but_last
from vtkplotlib import _numpy_vtk


MESH_DATA_TYPE = \
"""'mesh_data' must be any of the following forms:

1)  Some kind of mesh class that has form 2) stored in mesh.vectors.
    For example numpy-stl's stl.mesh.Mesh or pymesh's pymesh.stl.Stl


2)   An np.array with shape (n, 3, 3) in the form:

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
    represent scalars but as stl has no color this is always uniform). Hence
    to support mesh classes that have these, these arrays are allowed and the
    extra entries are ignored.



3)  A tuple containing:
        An np.array with shape (k, 3) of (usually unique) vertices in the form:

            np.array([[x, y, z],
                      [x, y, z],
                      ...
                      [x, y, z],
                      [x, y, z],
                      ])

    And an np.array of integers with shape (n, 3) of point
        args in the form

            np.array([[i, j, k],  # triangle 0
                      ...
                      [i, j, k],  # triangle n-1
                      ])

        where i, j, k are the indices of the points (in the vertices array)
        representing each corner of a triangle.

    Note that this form can (and is) easily converted to form 2) using

        vertices = unique_vertices[point_args]


If you are using or have written an stl library that you want supported then
let me know. If it's numpy based then it's probably only a few extra lines to
support.

"""

try:
    from stl.mesh import Mesh as NumpyMesh
    NUMPY_STL_AVAILABLE = True
except ImportError:
    NumpyMesh = None
    NUMPY_STL_AVAILABLE = False


MESH_DATA_TYPE_EX = lambda msg :ValueError("Invalid mesh_data type\n{}\n{}"\
                                           .format(MESH_DATA_TYPE, msg))


def path_str_to_vectors(path, ignore_numpystl=False):

    # Ideally let numpy-stl open the file if it is installed.
    if NUMPY_STL_AVAILABLE and not ignore_numpystl:
        return NumpyMesh.from_file(path).vectors

    # Otherwise try vtk's STL reader - however it's far from flawless.

    # A lot of redundancy here.
    # -Read the STL using vtk's STLReader
    # -Extract the polydata
    # -Extract the vectors from the polydata
    # This can then be given to mesh_plot which will convert it straight
    # back again to a polydata.

    from vtkplotlib.plots.polydata import PolyData
    from vtkplotlib.unicode_paths import PathHandler
    from vtkplotlib._vtk_errors import handler

    with PathHandler(path) as path_handler:
        reader = vtk.vtkSTLReader()
        handler.attach(reader)
        reader.SetFileName(path_handler.access_path)

        # vtk does a really good job of point merging but it's really not
        # worth the hassle to use it just to save a bt of RAM as everything
        # else in this script assumes an (n, 3, 3) table of vectors. Disable it
        # for speed.
    #        reader.SetMerging(False)

        # Normally Reader doesn't do any reading until it's been plotted.
        # Update forces it to read.
        reader.Update()
        pd = PolyData(reader.GetOutput())

    # For some reason VTK just doesn't like some files. There are some vague
    # warnings in their docs - this could be what they're on about. If it
    # doesn't work ``reader.GetOutput()`` gives an empty polydata.
    if pd.vtk_polydata.GetNumberOfPoints() == 0:
        raise RuntimeError("VTK's STLReader failed to read the STL file and no STL io backend is installed. VTK's STLReader is rather patchy. To read this file please ``pip install numpy-stl`` first.")

    return normalise_mesh_type((pd.points, pd.polygons))



def vertices_args_pair_to_vectors(mesh_data):
    vertices, args = mesh_data
    if not isinstance(vertices, np.ndarray):
        raise MESH_DATA_TYPE_EX("First argument is of invalid type {}"\
                                .format(type(vertices)))

    if vertices.shape[1:] != (3,):
        raise MESH_DATA_TYPE_EX("First argument has invalid shape {}. Should be (..., 3)."\
                         .format(vertices.shape))

    if not isinstance(args, np.ndarray):
        raise MESH_DATA_TYPE_EX("Second argument is of invalid type {}"\
                                .format(type(args)))

    if args.shape[1:] != (3,):
        raise MESH_DATA_TYPE_EX("Second argument has invalid shape {}. Should be (n, 3)."\
                         .format(args.shape))

    if args.dtype.kind not in "iu":
        raise MESH_DATA_TYPE_EX("Second argument must be an int dtype array")

    return vertices[args]



def normalise_mesh_type(mesh_data):
    """Try to support as many of the mesh libraries out there as possible
    without having all of those libraries as dependencies.
    """
    if isinstance(mesh_data, Path):
        mesh_data = str(mesh_data)
    if isinstance(mesh_data, str):
        vectors = path_str_to_vectors(mesh_data)

    elif isinstance(mesh_data, tuple) and len(mesh_data) == 2:
        vectors = vertices_args_pair_to_vectors(mesh_data)

    else:
        if isinstance(mesh_data, np.ndarray):
            vectors = mesh_data

        elif hasattr(mesh_data, "vectors"):
            vectors = mesh_data.vectors
            if vectors.shape[1:] != (3, 3):
                vectors = vectors[:, :3, :3]

        else:
            raise MESH_DATA_TYPE_EX("")

        if vectors.shape[1:] != (3, 3):
            raise MESH_DATA_TYPE_EX("mesh_data is invalid shape {}".format(vectors.shape))

    return vectors


class MeshPlot(ConstructedPlot):
    """To plot STL files you will need some kind of STL reader library. If you don't
    have one then get this one `numpy-stl`_. Their Mesh class can be passed
    directly to vpl.mesh_plot.

    .. _numpy-stl: https://pypi.org/project/numpy-stl/

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


    1.  Some kind of mesh class that has form 2) stored in mesh.vectors.
        For example numpy-stl's stl.mesh.Mesh or pymesh's pymesh.stl.Stl


    2.   An np.array with shape (n, 3, 3) in the form:

        .. code-block:: python

           np.array([[[x, y, z],  # corner 0  \
                      [x, y, z],  # corner 1  | triangle 0
                      [x, y, z]], # corner 2  /
                     ...
                     [[x, y, z],  # corner 0  \
                      [x, y, z],  # corner 1  | triangle n-1
                      [x, y, z]], # corner 2  /
                    ])


        Note it's not uncommon to have arrays of shape (n, 3, 4) or (n, 4, 3)
        where the additional entries' meanings are usually irrelevant (often to
        represent scalars but as STL has no color this is always uniform). Hence
        to support mesh classes that have these, these arrays are allowed and the
        extra entries are ignored.


    3.  An np.array with shape (k, 3) of (usually unique) vertices in the form:

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
    you can have a go at writing it yourself, either `with mesh_plot`  or with the
    ``vpl.PolyData`` class.



    **Mesh plotting with scalars:**


    To create a heat map like image use the `scalars` or `tri_scalars` options.


    Use the `scalars` option to assign a scalar value to each point/corner:

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


    Use the `tri_scalars` option to assign a scalar value to each triangle:

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


    .. note:: `scalars` and `tri_scalars` overwrite each other and can't be used simultaneously.

    .. seealso::

        Having per-triangle-edge scalars doesn't fit well with VTK. So it got
        its own seperate function ``vpl.mesh_plot_with_edge_scalar``.


    """
    def __init__(self, mesh_data, tri_scalars=None, scalars=None, color=None, opacity=None, fig="gcf"):
        super().__init__(fig)


        self.vectors = np.ascontiguousarray(normalise_mesh_type(mesh_data))

        triangles = np.empty((len(self.vectors), 4), np.int64)
        triangles[:, 0] = 3
        for i in range(3):
            triangles[:, i+1] = np.arange(i, len(self.vectors) * 3, 3)

        triangles = triangles.ravel()

        points = self.points = vtk.vtkPoints()
        self.update_points()

        self.polydata.vtk_polydata.SetPoints(points)

        cells = vtk.vtkCellArray()
        cells.SetCells(len(triangles), numpy_to_vtkIdTypeArray(triangles))
        self.polydata.vtk_polydata.SetPolys(cells)

        self.add_to_plot()

        self.temp.append(triangles)


        self.set_scalars(scalars)
        self.set_tri_scalars(tri_scalars)
        self.color_opacity(color, opacity)

    __init__.__doc__ = (__init__.__doc__ or "") + MESH_DATA_TYPE

    def update_points(self):
        """If self.vectors has been modified (either resigned to a new array or
        the array's contents have been altered) then this be called after."""
        vertices = flatten_all_but_last(self.vectors)
        self.temp.append(vertices)

        self.points.SetData(numpy_to_vtk(vertices))


    def set_tri_scalars(self, tri_scalars, min=None, max=None):
        """Sets a scalar for each triangle for generating heatmaps.

        tri_scalars should be an 1D np.array of length n.

        Calls self.set_scalars. See set_scalars for implications.
        """
        if tri_scalars is not None:
            tri_scalars = _numpy_vtk.contiguous_safe(tri_scalars.ravel())
    #        scalars = np.array([tri_scalars, tri_scalars, tri_scalars]).T
            assert tri_scalars.size == len(self.vectors)
            scalars = np.empty((len(tri_scalars), 3))
            for i in range(3):
                scalars[:, i] = tri_scalars

            self.set_scalars(scalars, min, max)


    def set_scalars(self, scalars, min=None, max=None):
        """Sets a scalar for each corner of each triangle for generating heatmaps.

        scalars should be an array with shape (n, 3).

        self.set_scalars and self.set_tri_scalars will overwrite each other.
        If either form of scalars is used then self.color is ignored.
        """

        if scalars is not None:
    #        scalars[~np.isfinite(scalars)] = np.nanmean(scalars)
            if scalars.shape != (len(self.vectors), 3):
                raise ValueError("Expected (n, 3) shape array. Got {}".format(scalars.shape))

            scalars = _numpy_vtk.contiguous_safe(scalars)

            self.polydata.vtk_polydata.GetPointData().SetScalars(numpy_to_vtk(scalars.ravel()))
            self.temp.append(scalars)

            min = min or np.nanmin(scalars)
            max = max or np.nanmax(scalars)
            self.mapper.SetScalarRange(min, max)


def mesh_plot_with_edge_scalars(mesh_data, edge_scalars, centre_scalar="mean", opacity=None, fig="gcf"):
    r"""Like mesh_plot but able to add scalars per triangle's edge. By default,
    the scalar value at centre of each triangle is taken to be the mean of the
    scalars of its edges, but it can be far more visually effective to use the
    ``centre_scalar=`` number option.


    Edge scalars are very much not the way VTK likes it. Infact VTK doesn't
    allow it. To overcome this, this function triple-ises each triangle. See
    the diagram below to see how this is done:

    .. code-block:: text

        (The diagrams's tacky, I know)

                   p1

                 //|\\         Double lines represent the original triangle.
                // | \\        The single lines represent the division lines that
          l0   //  |  \\  l1   split the triangle into three.
              //  / \  \\      The annotations show the order in which the
             // /     \ \\     scalar for each edge must be provided.
            ///~~~~~~~~~\\\
        p0  ~~~~~~~~~~~~~~~  p2
                  l2

        (reST doesn't like it either)

    Here is a usage example:

    .. code-block:: python

        import vtkplotlib as vpl
        from stl.mesh import Mesh


        path = vpl.data.get_rabbit_stl()
        mesh = Mesh.from_file(path)

        # This is the length of each side of each triangle.
        edge_scalars = vpl.geometry.distance(mesh.vectors[:, np.arange(1, 4) % 3] - mesh.vectors)

        vpl.mesh_plot_with_edge_scalars(_mesh, edge_scalars, centre_scalar=0)

        vpl.show()




    I wrote this orginally to visualise curvature.



    """

    vectors = normalise_mesh_type(mesh_data)
    tri_centres = np.mean(vectors, 1)

    new_vectors = np.empty((len(vectors) * 3, 3, 3), vectors.dtype)
#    new_vectors.fill(np.nan)

    for i in range(3):
        for j in range(2):
            new_vectors[i::3, j % 3] = vectors[:, (i+j) % 3]

        new_vectors[i::3, 2 % 3] = tri_centres

    tri_scalars = edge_scalars.ravel()
    if centre_scalar == "mean":
        centre_scalars = np.mean(edge_scalars, 1)
    else:
        centre_scalars = centre_scalar
#
    new_scalars = np.empty((len(tri_scalars), 3), dtype=tri_scalars.dtype)
    new_scalars[:, 0] = new_scalars[:, 1] = tri_scalars
    for i in range(3):
        new_scalars[i::3, 2] = centre_scalars

    return MeshPlot(new_vectors, scalars=new_scalars, opacity=opacity, fig=fig)


if __name__ == "__main__":
    import time
    import vtkplotlib as vpl
    from stl.mesh import Mesh

    fig = vpl.gcf()

    path = vpl.data.get_rabbit_stl()
#    path = "rabbit2.stl"
    _mesh = Mesh.from_file(path)

    mesh_data = _mesh.vectors
    mesh_data = path

#    vpl.mesh_plot(mesh_data)

    edge_scalars = vpl.geometry.distance(_mesh.vectors[:, np.arange(1, 4) % 3] - _mesh.vectors)

    self = vpl.mesh_plot_with_edge_scalars(_mesh, edge_scalars, centre_scalar=0)

    mesh_data = _mesh


    fig.show()


#def test_args_based_mesh(_mesh):
#    vectors = _mesh.vectors
#
#    unique_points = set(tuple(i) for i in vectors.reshape(len(vectors) * 3, 3))
#    points_enum = {point: i for (i, point) in enumerate(unique_points)}
#
#    points = np.array(sorted(unique_points, key=points_enum.get))
#    point_args = np.apply_along_axis(lambda x: points_enum[tuple(x)], -1, vectors)
#
#    assert np.array_equal(points[point_args], vectors)
#
#    vpl.mesh_plot((points, point_args))
#    vpl.show()
