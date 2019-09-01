# -*- coding: utf-8 -*-

"""
Created on Sat Aug 31 02:35:37 2019

@author: Brénainn Woodsend


one line to give the program's name and a brief idea of what it does.
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


import numpy as np
import matplotlib.pylab as plt
import sys
import os
from pathlib2 import Path

import vtkplotlib as vpl
from unittest import TestCase, skipUnless, main

path = vpl.data.get_rabbit_stl(False)


class TestMeshPlot(TestCase):
    
    @skipUnless(vpl.NUMPY_STL_AVAILABLE, "Requires numpy-stl")
    def test_type_normalise(self):
        from stl.mesh import Mesh
        mesh = Mesh.from_file(path)
        vectors = mesh.vectors
        
        unique_points = set(tuple(i) for i in vectors.reshape(len(vectors) * 3, 3))
        points_enum = {point: i for (i, point) in enumerate(unique_points)}
        
        points = np.array(sorted(unique_points, key=points_enum.get))
        point_args = np.apply_along_axis(lambda x: points_enum[tuple(x)], -1, vectors)
        
        for fmt in (path, mesh, vectors, (points, point_args)):
            normalised = vpl.plots.MeshPlot.normalise_mesh_type(fmt)
            self.assertTrue(np.array_equal(normalised, vectors))
            
        for i in range(2):
            try:
                normalised = vpl.plots.MeshPlot.path_str_to_vectors(path, i)
                self.assertTrue(np.array_equal(normalised, vectors))
            except RuntimeError as ex:
                print(repr(ex))
        
    



if __name__ == "__main__":
    main()
