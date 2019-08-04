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
import sys
import os
from pathlib2 import Path

from itertools import zip_longest
from PIL import Image
from PyQt5 import QtWidgets, QtGui, QtCore


from vtkplotlib.figures import QtFigure, save_fig, view
from vtkplotlib.data import ICONS_FOLDER

SCREENSHOT_ICON_PATH = ICONS_FOLDER / "screenshot.png"


class QtFigure2(QtFigure):
    """This is intended to be used as/for a more sophisticated GUI when one is needed.
    By providing some common features here, hopefully this can speed up the 
    tedious process of building a GUI. Any contributions here would be very
    welcome. I want to write this so that each extra feature is optional allowing
    custom GUIs can be built quickly.
    
    This is still under development. Currently it has:
        1) A screenshot button
        2) A panel for preset camera views
    
    I hope/intend to add:
        1) An actor table to show / hide / color plots interactively.
    
    """
    def __init__(self, name="qt vtk figure", parent=None):
        super().__init__(name, parent)


        self.menu = QtWidgets.QHBoxLayout()
        self.vl.insertLayout(0, self.menu)
        
#        self.menu.setFixedHeight(100)
#        self.setStyle(Style())
    
#        self.views = Views(["up"],
#                           [{"camera_direction": np.array([1, 0, 0])}],
#                           self,
#                           ).views
        self.view_buttons = ViewButtons.default(self)
                           
        self.menu.addLayout(self.view_buttons.to_layout())
        
        self.right_menu = self.menu#QtWidgets.QMenuBar()
#        self.menu.addWidget(self.right_menu)
       
        self.default_screenshot_path = Path.home() / (name + ".jpg")
        self.screenshot_button = Button("Screenshot",
                                        self.screenshot,
                                        SCREENSHOT_ICON_PATH)
        self.right_menu.addWidget(self.screenshot_button)
        
        
    
    def screenshot(self):
        path = QtWidgets.QFileDialog.getSaveFileName(self, 
                                                     "Save screenshot",
                                                     str(self.default_screenshot_path),
                                                     "(*.jpg);;(*.png)")[0]
        
        if path:
            save_fig(path, 10, self)
        
        
    def show(self, block=False):
#        self.menu.adjustSize()
#        size = self.menu.sizeHint()
#        size.setHeight(size.height() * 2)
#        self.menu.resize(size)

        super().show()
#        self.menu.resize(size)
        
        
        
class Button(QtWidgets.QPushButton):
    def __init__(self, name, callback=None, icon=None, parent=None):
        super().__init__(parent)

        if callback is None:
            callback = self.default_callback
                
        self.released.connect(callback)
        self.setIconSize(QtCore.QSize(40, 40))
        
        p = self.sizePolicy()
        p.setHorizontalPolicy(p.Minimum)
        p.setVerticalPolicy(p.Minimum)
        self.setSizePolicy(p)
        
        if icon is not None:
            self.setIcon(as_qicon(icon))
        else:
            self.setText(name)
            
            
    def default_callback(self):
        print("QButton", repr(self.text()), "was triggered")
        
        
        
def as_qicon(obj):
    pixmap = None
    
    if isinstance(obj, QtGui.QIcon):
        return obj
    
    if isinstance(obj, str):
        obj = Path(obj)
        
    if isinstance(obj, os.PathLike):
#                if obj.is_file():
            pixmap = QtGui.QPixmap(str(obj))
            
    if isinstance(obj, Image.Image):
        pixmap = obj.toqpixmap()
            
        
    if pixmap is not None:
        return QtGui.QIcon(pixmap)#.scaled(00, 100))
    else:
        raise TypeError("""Icons can be created from any of the following:
    - str
    - os.Pathlike 
    - QtGui.QIcon
    - PIL.Image.Image
Received {}""".format(type(obj)))
                    

        

class ViewButton(Button):
    def __init__(self, name, parent, icon=None,
                 view_args={}):

        super().__init__(name, self.set_view, icon, parent)
        
        self.args = view_args
    
    
    def set_view(self):
        view(**self.args, fig=self.parent())
        
        self.parent().reset_camera()
        self.parent().update()
        


class ViewButtons(object):
    def __init__(self, names, view_args, fig, icons=()):
        self.buttons = []
        
        for (name, args, icon) in zip_longest(names, view_args, icons):
            button = ViewButton(name, fig, icon, args)
            self.buttons.append(button)
            
    @classmethod            
    def default(cls, figure):

        names = ["Right", "Left", "Front", "Back", "Top", "Bottom"]
    
        directions = np.array([[1, 0, 0],
                               [-1, 0, 0],
                               [0, 1, 0],
                               [0, -1, 0],
                               [0, 0, 1],
                               [0, 0, -1]])
    
        ups = np.array([[0, 0, 1],
                        [0, 1, 0]])
    
        view_args = []
        for d in directions:
                args = {"camera_position": d}
                
                for up in ups:
                    if not (d & up).any():
                        args["up_view"] = up
                        break
                view_args.append(args)
        
        paths = [ICONS_FOLDER / (i + ".jpg") for i in names]
    
        return cls(names, view_args, figure, icons=paths)
    
    
    def to_layout(self, parent=None):
        out = QtWidgets.QHBoxLayout(parent)
        [out.addWidget(i) for i in self.buttons]
        return out
    



if __name__ == "__main__":
    import vtkplotlib as vpl
    from stl.mesh import Mesh
    
    app = None
    app = QtWidgets.QApplication(sys.argv)
    
    self = vpl.QtFigure2("Some Dots")
#    vpl.scatter(np.random.uniform(-5, 5, (5, 3)), fig=self)
#    vpl.quiver(np.zeros((3, 3)), np.eye(3) * 5, color=np.eye(3))
    
    vpl.mesh_plot(Mesh.from_file(vpl.data.STLS[0]))
    
        
    
    self.show()
    
    app.exec_()
    
