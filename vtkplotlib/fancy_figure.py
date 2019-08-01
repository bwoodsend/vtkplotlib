# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 20:09:13 2019

@author: Brénainn Woodsend


fancy_figure.py
Create a more sophisticated render window for plotting into.
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
from vtkplotlib.data import ICONS_FOLDER

SCREENSHOT_ICON_PATH = ICONS_FOLDER / "screenshot.png"


class QtFigure2(QtFigure):
    """This is intended to be used as/for a sophistcated GUI when one is needed.
    By providing some common features here, hopefully we can speed up the 
    tedious process of building a GUI. Any contributions here would be very
    welcome. I want to write this so each extra feature is optional so that
    custom GUIs can be built quickly.
    
    This is still under development. Currently it has:
        1) A screenshot button
    
    I hope/intend to add:
        1) An actor table to show / hide / color plots interactively.
    
    """
    def __init__(self, name="qt vtk figure", parent=None):
        super().__init__(name, parent)


        self.menu = QtWidgets.QMenuBar()
        self.vl.insertWidget(0, self.menu)
        
        self.right_menu = QtWidgets.QMenuBar()
        self.menu.setCornerWidget(self.right_menu)
        
        if SCREENSHOT_ICON_PATH.is_file():
            icon = QtGui.QIcon(str(SCREENSHOT_ICON_PATH))
            self.screenshot_button = QtWidgets.QAction(icon, "Screenshot")
        else:
            self.screenshot_button = QtWidgets.QAction("Screenshot")
            
        self.screenshot_button.triggered.connect(self.screenshot)
        
        self.right_menu.addAction(self.screenshot_button)
        
    
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
    
    self = vpl.QtFigure2("Some Dots")
    vpl.scatter(np.random.uniform(-5, 5, (5, 3)), fig=self)
    
    self.show()
    
    app.exec_()
    
