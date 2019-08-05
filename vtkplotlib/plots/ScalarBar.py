# -*- coding: utf-8 -*-
"""
Created on Sun Jul 21 15:29:19 2019

@author: Brénainn Woodsend


ScalarBar.py
Adds a scalar/color bar.
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
import os
import sys
from pathlib2 import Path
from vtk.util.numpy_support import (
                                    numpy_to_vtk,
                                    numpy_to_vtkIdTypeArray,
                                    vtk_to_numpy,
                                    )

from vtkplotlib.plots.BasePlot import BasePlot



class ScalarBar(BasePlot):
    def __init__(self, plot, title="", fig=None):
    
        super().__init__(fig)
        
        self.actor = vtk.vtkScalarBarActor()
        self.actor.SetTitle(title)
    
        self.actor.SetNumberOfLabels(6)

        self.lookup_table = plot.mapper.GetLookupTable()
        self.lookup_table.ForceBuild()
        self.actor.SetLookupTable(self.lookup_table)
    
    
#        self.fig += self
        self.fig.render.AddActor2D(self.actor)
        self.fig.plots.add(self)
        



if __name__ == "__main__":
    from stl.mesh import Mesh
    import vtkplotlib as vpl
    
    mesh = Mesh.from_file(vpl.data.STLS[0])
    plot = vpl.mesh_plot(mesh.vectors, scalars=mesh.x)

    self = vpl.scalar_bar(plot)

    
    vpl.show()