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
from builtins import super

import numpy as np
import sys
import os
from pathlib2 import Path

from itertools import zip_longest
from PyQt5 import QtWidgets, QtGui, QtCore

try:
    from PIL import Image
except ImportError:
    Image = None


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

        self.plot_table = None



    def add_preset_views(self, names=None, view_params=None, icons=()):
        if view_params is None:
            self.view_buttons = ViewButtons.default(self)
        else:
            self.view_buttons = ViewButtons(names, view_params, self, icons=())
#
        self.menu.addLayout(self.view_buttons.to_layout())

        return self



    def add_screenshot_button(self):

        self.default_screenshot_path = Path() / (self.window_name + ".jpg")

        self.screenshot_button = Button("Screenshot",
                                        self.screenshot,
                                        SCREENSHOT_ICON_PATH)
        self.menu.addWidget(self.screenshot_button)



    def screenshot(self):
        path = QtWidgets.QFileDialog.getSaveFileName(self,
                                                     "Save screenshot",
                                                     str(self.default_screenshot_path),
                                                     "(*.jpg);;(*.png)")[0]

        if path:
            save_fig(path, fig=self)


    def add_show_plot_table_button(self):
        self.show_plot_table_button = Button("Show plots menu",
                                             self.show_plot_table)
        self.menu.addWidget(self.show_plot_table_button)

        return self


    def show_plot_table(self):
        self.plot_table = table = PlotTable(self)
        table.show()



#    def show(self, block=False):
#        super().show(block)

    def update(self):
        self.setWindowModified(True)
        super().update()
        if self.plot_table is not None:
            self.plot_table.update()


#    def close(self):
#        super().close()


    def add_all(self):
        self.add_preset_views()
        self.add_screenshot_button()
        self.add_show_plot_table_button()




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

    try:
        PathLike = os.PathLike
    except AttributeError:
        PathLike = Path

    if isinstance(obj, PathLike):
#                if obj.is_file():
            pixmap = QtGui.QPixmap(str(obj))

    if (Image is not None) and isinstance(obj, Image.Image):
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
                 view_params={}):

        super().__init__(name, self.set_view, icon, parent)

        self.args = view_params


    def set_view(self):
        view(**self.args, fig=self.parent())

        self.parent().reset_camera()
        self.parent().update()



class ViewButtons(object):
    def __init__(self, names, view_params, fig, icons=()):
        self.buttons = []

        for (name, args, icon) in zip_longest(names, view_params, icons):
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

        view_params = []
        for d in directions:
                args = {"camera_position": d}

                for up in ups:
                    if not (d & up).any():
                        args["up_view"] = up
                        break
                view_params.append(args)

        paths = [ICONS_FOLDER / (i + ".jpg") for i in names]

        return cls(names, view_params, figure, icons=paths)


    def to_layout(self, parent=None):
        out = QtWidgets.QHBoxLayout(parent)
        [out.addWidget(i) for i in self.buttons]
        return out



class PlotTable(QtWidgets.QWidget):
    def __init__(self, figure):
        super().__init__()
        self.figure = figure
        self.plots = self.figure.plots
        self.rows = dict()

        self.grid = QtWidgets.QGridLayout()
        self.setLayout(self.grid)

        self.timer = timer = QtCore.QTimer()
        timer.setInterval(50)
#        timer.timeout.connect(lambda: print(row.text.underMouse()))
        timer.timeout.connect(self.update)
        timer.start()


        self.update()


    def add_plot(self, plot):
#        print("add", plot)
        row = PlotTableRow(plot, len(self.rows))# + 1
        row.add_to_grid(self.grid)
        self.rows[plot] = row


    def remove_plot(self, plot):
#        print("remove", plot)
        self.rows.pop(plot)


    def update(self):
        for plot in (self.plots - self.rows.keys()):
            self.add_plot(plot)

        for plot in (self.rows.keys() - self.plots):
            self.remove_plot(plot)


class PlotTableRow(object):
    def __init__(self, plot, row_num):
        self.plot = plot
        self.row_num = row_num

        self.visible_ckbox = QtWidgets.QCheckBox()
        self.visible_ckbox.setChecked(self.plot.visible)
        self.visible_ckbox.stateChanged.connect(self.chk_box_change_cb)

        if hasattr(self.plot, "name"):
            name = self.plot.name
        else:
            name = repr(self.plot)
        self.text = QLabel_alterada(name)
        self.text.released.connect(self.toggle_visible)



    def chk_box_change_cb(self):
        state = bool(self.visible_ckbox.checkState())
#        print("setting", self.plot, "visibility to", state)

        self.plot.visible = bool(state)
        self.plot.fig.update()


    def toggle_visible(self):
        self.visible_ckbox.setChecked(not self.visible_ckbox.checkState())


    def add_to_grid(self, grid):
        grid.addWidget(self.visible_ckbox, self.row_num, 0)
        grid.addWidget(self.text, self.row_num, 1)



class QLabel_alterada(QtWidgets.QLabel):
    released = QtCore.pyqtSignal()

    def mouseReleaseEvent(self, ev):
        self.released.emit()


#if __name__ == "__main__":
#    import vtkplotlib as vpl
#    from stl.mesh import Mesh
#
#    app = None
#    app = QtWidgets.QApplication(sys.argv)
#
#    self = vpl.QtFigure2("Rabbits")
##    vpl.scatter(np.random.uniform(-5, 5, (5, 3)), fig=self)
##    vpl.quiver(np.zeros((3, 3)), np.eye(3) * 5, color=np.eye(3))
#
#    plot = vpl.mesh_plot(Mesh.from_file(vpl.data.get_rabbit_stl()))
#    plot.name = "rabbit"
#    mesh_2 = Mesh.from_file(vpl.data.get_rabbit_stl())
#    mesh_2.translate(np.array([100, 0, 0]))
##    vpl.scatter(np.random.uniform(-100, 100, (3, 3)))
#
#    self.add_all()
#
##    self.show(False)
#
##    app.processEvents()
#    plot = vpl.mesh_plot(mesh_2, color="g")
#    plot.name = "green rabbit"
##    self.update()
#
#
#
##    app.processEvents()
##    row = table.rows[plot]
#
#    self.show()
##    app.exec_()
#
