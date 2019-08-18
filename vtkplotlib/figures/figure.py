# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 21:21:20 2019

@author: Brénainn Woodsend


figures.py
Provides/manages windows to render into.
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

from builtins import super

import vtk
import numpy as np
import os
import sys
from pathlib2 import Path


from .BaseFigure import BaseFigure


class Figure(BaseFigure):
    """The default figure class."""
    def __init__(self, name="vtk figure"):
        
        super().__init__(vtk.vtkRenderWindow(), vtk.vtkRenderWindowInteractor())
        self.window_name = name
        
        



if __name__ == "__main__":
    import vtkplotlib as vpl
    
    self = vpl.figure("a normal vtk figure")
        
        
#    vpl.plot(np.random.uniform(-10, 10, (20, 3)))
        
    direction = np.array([1, 0, 0])
    vpl.quiver(np.array([0, 0, 0]), direction)
    vpl.view(camera_direction=direction)
    vpl.reset_camera()
    
#    vpl.save_fig(Path.home() / "img.jpg", 1080)
    
    self.show()
    
    
