# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 20:09:13 2019

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

from PyQt5 import QtWidgets, QtGui, QtCore

from vtkplotlib.figures import QtFigure, save_fig

SCREENSHOT_ICON_PATH = Path(__file__).with_name("screenshot.png")


class QtFigure2(QtFigure):
    def __init__(self, name="qt vtk figure", parent=None):
        super().__init__(name, parent)



        self.menu = QtWidgets.QMenuBar()
        self.vl.insertWidget(0, self.menu)
        
        if SCREENSHOT_ICON_PATH.is_file():
            icon = QtGui.QIcon(str(SCREENSHOT_ICON_PATH))
            self.screenshot_button = QtWidgets.QAction(icon, "Screenshot")
        else:
            self.screenshot_button = QtWidgets.QAction("Screenshot")
            
        self.screenshot_button.triggered.connect(self.screenshot)
        
        self.menu.addAction(self.screenshot_button)
        
    
    def screenshot(self):
        path = QtWidgets.QFileDialog.getSaveFileName(self, 
                                                     "Save screenshot",
                                                     self.window_name,
                                                     "(*.jpg);;(*.png)")[0]
        
        if path:
            save_fig(path, 10, self)
        
        






if __name__ == "__main__":
    import vtkplotlib as vpl
    
    app = None
    app = QtWidgets.QApplication(sys.argv)
    
    self = vpl.figure_qt2("thing")
    vpl.scatter(np.random.uniform(-5, 5, (5, 3)), fig=self)
    
    self.show()
    
    app.exec_()
    
