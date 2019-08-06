# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 23:55:28 2019

@author: Brénainn Woodsend


MeshPlot.py 
Plot a 3D stl (like) mesh.
Copyright (C) 2019  Brénainn Woodsend

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""


import vtk
import numpy as np
#from matplotlib import pylab as plt
from matplotlib import colors
import os
import sys
from pathlib2 import Path
from vtk.util.numpy_support import (
                                    numpy_to_vtk,
                                    numpy_to_vtkIdTypeArray,
                                    vtk_to_numpy,
                                    )



from vtkplotlib.plots.BasePlot import ConstructedPlot
from vtkplotlib.nuts_and_bolts import flatten_all_but_last



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
        

    
3)  An np.array with shape (k, 3) of (usually unique) vertices in the form:
        
        np.array([[x, y, z],
                  [x, y, z],
                  ...
                  [x, y, z],
                  [x, y, z],
                  ])
    
    And a second argument of an np.array of integers with shape (n, 3) of point
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


MESH_DATA_TYPE_EX = lambda msg :ValueError("Invalid mesh_data type\n{}\n{}"\
                                           .format(MESH_DATA_TYPE, msg))


class MeshPlot(ConstructedPlot):
    """Plot an STL (like) surface composed of lots of little triangles. Accepts
    mesh types from various 3rd party libraries. This was primarily written for
    the numpy-stl library. Failing that can also take other more generic formats.
    See __init__ for more info.
    """
    def __init__(self, *mesh_data, tri_scalars=None, scalars=None, color=None, opacity=None, fig=None):
        super().__init__(fig)
        
        # Try to support as many of the mesh libraries out there as possible
        # without having all of those libraries as dependencies
        
        if len(mesh_data) == 1:
            mesh_data = mesh_data[0]
            
            if isinstance(mesh_data, np.ndarray):
                self.vectors = mesh_data
                
            elif hasattr(mesh_data, "vectors"):
                self.vectors = mesh_data.vectors
                if self.vectors.shape[1:] != (3, 3):
                    self.vectors = self.vectors[:, :3, :3]
                
            else:
                raise MESH_DATA_TYPE_EX("")
            
            if self.vectors.shape[1:] != (3, 3):
                raise MESH_DATA_TYPE_EX("mesh_data is invalid shape {}".format(self.vectors.shape))
            
                
        elif len(mesh_data) == 2:
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
                
            if args.dtype != int:
                raise MESH_DATA_TYPE_EX("Second argument must be an int dtype array")
                
            self.vectors = vertices[args]
            
        else:
            raise MESH_DATA_TYPE_EX("")
                                 
            
        triangles = np.empty((len(self.vectors), 4), np.int64)
        triangles[:, 0] = 3
        for i in range(3):
            triangles[:, i+1] = np.arange(i, len(self.vectors) * 3, 3)
            
        triangles = triangles.ravel()

        points = self.points = vtk.vtkPoints()
        self.update_points()

        self.poly_data.SetPoints(points)
        
        cells = vtk.vtkCellArray()
        cells.SetCells(len(triangles), numpy_to_vtkIdTypeArray(triangles))
        self.poly_data.SetPolys(cells)
        
        self.add_to_plot()
        
        self.fig.temp.append(triangles)
        
        
        self.set_scalars(scalars)
        self.set_tri_scalars(tri_scalars)
        self.color_opacity(color, opacity)

    __init__.__doc__ = (__init__.__doc__ or "") + MESH_DATA_TYPE    

    def update_points(self):
        """If self.vectors has been modified (either resigned to a new array or
        the array's contents have been altered) then this be called after."""
        vertices = flatten_all_but_last(self.vectors)
        self.fig.temp.append(vertices)
        
        self.points.SetData(numpy_to_vtk(vertices))        

    
    def set_tri_scalars(self, tri_scalars, min=None, max=None):
        """Sets a scalar for each triangle for generating heatmaps. 
        
        tri_scalars should be an 1D np.array of length n. 
        
        Calls self.set_scalars. See set_scalars for implications.
        """
        if tri_scalars is not None:
    #        scalars = np.array([tri_scalars, tri_scalars, tri_scalars]).T
            assert tri_scalars.shape == (len(self.vectors), )
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
    
            self.poly_data.GetPointData().SetScalars(numpy_to_vtk(scalars.ravel()))
            self.fig.temp.append(scalars)
            
            min = min or np.nanmin(scalars)
            max = max or np.nanmax(scalars)
            self.mapper.SetScalarRange(min, max)
            
    
     
    


if __name__ == "__main__":
    import time
    import vtkplotlib as vpl
    from stl.mesh import Mesh
    
    
    
    fig = vpl.gcf()
    
    path = vpl.data.get_rabbit_stl()
    _mesh = Mesh.from_file(path)
    
    self = vpl.mesh_plot(_mesh.vectors)
    

    fig.show(False)
    
    t0 = time.perf_counter()
    for i in range(100):
#        self.color = np.random.random(3)
#        print(self.color)
        self.set_tri_scalars((_mesh.x[:, 0] + 3 * i) % 20 )
        _mesh.rotate(np.ones(3), .1, np.mean(_mesh.vectors, (0, 1)))
        fig.update()
        self.update_points()
#        time.sleep(.01)
        if (time.perf_counter() - t0) > 2:
            break
    
    
    fig.show()
    
