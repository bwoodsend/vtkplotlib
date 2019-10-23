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
import vtk

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtkplotlib.figures.BaseFigure import BaseFigure, VTKRenderer
from vtkplotlib import nuts_and_bolts


class QtFigure(QWidget, BaseFigure):
    """The vtk render window embedded into a QWidget. This can be embedded into
    a GUI the same way all other QWidgets are used.
    """

    def __init__(self, name="qt vtk figure", parent=None):

        self.qapp = QApplication.instance() or QApplication(sys.argv)
        QWidget.__init__(self, parent)

        self.window_name = name

        self.vl = QVBoxLayout()
        self.vtkWidget = QVTKRenderWindowInteractor(self)
        self.vl.addWidget(self.vtkWidget)
        self.renWin
        iren = self.iren


        self.data_holder = []

        BaseFigure.__init__(self)
        iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())


        self.setLayout(self.vl)



    def show(self, block=None):
        QWidget.show(self)
        if block is None:
            block = self.parent() is None
        BaseFigure.show(self, block)
        self.setWindowTitle(self.window_name)

        if block:
            self.qapp.exec_()


    @nuts_and_bolts.init_when_called
    def renWin(self):
        return self.vtkWidget.GetRenderWindow()

    @nuts_and_bolts.init_when_called
    def iren(self):
        return self.vtkWidget.GetRenderWindow().GetInteractor()

    def update(self):
        BaseFigure.update(self)
        QWidget.update(self)
        self.repaint()
        self.qapp.processEvents()


    def finalise(self):
        """Very important that original finalise gets overwritten. This gets
        called imediately after self.iren.Start(). The original performs resets
        that stop the QtFigure from responding."""
        pass







if __name__ == "__main__":
    import vtkplotlib as vpl

    self = vpl.QtFigure("a qt widget figure")

    [self.render.AddActor(i.actor) for i in  vpl._quick_test_plot()]
#    self.reset_camera()
#    self.connect()

    vpl.show(fig=self)
