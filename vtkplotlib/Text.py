# -*- coding: utf-8 -*-
"""
Created on Sun Jul 21 15:47:18 2019

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


import vtk
import numpy as np
#from matplotlib import pylab as plt
from matplotlib import colors
import os
import sys
from pathlib2 import Path
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QFileDialog
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtk.util.numpy_support import (
                                    numpy_to_vtk,
                                    numpy_to_vtkIdTypeArray,
                                    vtk_to_numpy,
                                    )



from vtkplotlib.BasePlot import BasePlot
from vtkplotlib.figures import gcf, show
from vtkplotlib.nuts_and_bolts import flatten_all_but_last

class Text(BasePlot):
    def __init__(self, text_str, position=(0, 0), fontsize=18, color=(1, 1, 1), fig=None):
        # create a text actor
        super().__init__(fig)
        
        self.actor = vtk.vtkTextActor()
        self.actor.SetInput(text_str)

        self.property = self.actor.GetTextProperty()
        
        self.property.SetFontFamilyToArial()
        self.property.SetFontSize(fontsize)
        self.property.SetColor(*color)


        self.actor.SetPosition(*position)
        
        # assign actor to the renderer
        self.fig.add_actor(self.actor)




if __name__ == "__main__":
    
    
    self = Text("eggs")
    show()
