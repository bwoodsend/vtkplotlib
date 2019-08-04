# -*- coding: utf-8 -*-
"""
Created on Sat Aug  3 16:51:42 2019

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
import sys
import os
from pathlib2 import Path


from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from .BaseFigure import BaseFigure
from .render_window import VTKRenderer


class QtFigure(BaseFigure, QWidget):
    """The vtk render window embedded into a QWidget. This can be embedded into
    a GUI the same way all other QWidgets are used.
    """

    def __init__(self, name="qt vtk figure", parent=None):
        QWidget.__init__(self, parent)


        self.vl = QVBoxLayout()
        self.vtkWidget = QVTKRenderWindowInteractor(self)
        self.vl.addWidget(self.vtkWidget)
        BaseFigure.__init__(self,
                            self.vtkWidget.GetRenderWindow(),
                            self.vtkWidget.GetRenderWindow().GetInteractor())

        self.setLayout(self.vl)
        
        self.window_name = name
        

    def show(self, block=False):
        QWidget.show(self)
        BaseFigure.show(self, block)
        self.setWindowTitle(self.window_name)





if __name__ == "__main__":
    import vtkplotlib as vpl

    app = None
    app = QApplication([])
    self = vpl.QtFigure("a qt widget figure")

    direction = np.array([1, 0, 0])
    vpl.quiver(np.array([0, 0, 0]), direction)
    vpl.view(camera_direction=direction)
    vpl.reset_camera()

    self.show()
    app.exec_()
