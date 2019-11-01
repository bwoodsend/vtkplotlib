# -*- coding: utf-8 -*-
# =============================================================================
# Created on Sat Aug  3 16:51:42 2019
#
# @author: Brénainn Woodsend
#
#
# QtFigure.py provides a figure that doubles as a QWidget.
# Copyright (C) 2019  Brénainn Woodsend
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# =============================================================================


import numpy as np
import sys
import os
from pathlib2 import Path
import vtk

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtkplotlib.figures.BaseFigure import BaseFigure, VTKRenderer
from vtkplotlib import nuts_and_bolts


class QtFigure(BaseFigure, QWidget):
    """The VTK render window embedded into a PyQt5 QWidget. This can be
    embedded into a GUI the same way all other QWidgets are used.

    :param name: The window title of the figure, only applicable is parent is None, defaults to 'qt vtk figure'.
    :type name: str, optional

    :param parent: Parent window, defaults to None.
    :type parent: NoneType, optional


    .. note::

        If you are new to Qt then this is a rather poor place to start. Whilst
        many libraries in Python are intuitive enough to be able to just dive
        straight in, Qt is not one of them. Preferably familiarise yourself
        with some basic Qt before coming here.


    This class inherits both from QWidget and a vtkplotlib BaseFigure class.
    Therefore it can be used exactly the same as you would normally use either
    a `QWidget` or a `vpl.figure`.

    Care must be taken when using Qt to ensure you have **exactly one**
    QApplication. To make this class quicker to use the qapp is created
    automatically but is wrapped in a

    .. code-block:: python

        if QApplication.instance() is None:
            self.qapp = QApplication(sys.argv)
        else:
            self.qapp = QApplication.instance()

    This prevents multiple QApplication instances from being created (which
    causes an instant crash) whilst also preventing a QWidget from being
    created without a qapp (which also causes a crash).


    On ``self.show()``, ``self.qapp.exec_()`` is called automatically if
    ``self.parent() is None`` (unless specified otherwise). If the QFigure is part
    of a larger window then ``larger_window.show()`` must also show
    the figure. It won't begin interactive mode until ``qapp.exec_()`` is
    called.


    If the figure is not to be part of a larger window then it behaves exactly
    like a regular figure. You just need to explicitly create it first.

    .. code-block:: python

        import vtkplotlib as vpl

        # Create the figure. This automatically sets itself as the current
        # working figure. The qapp is created automatically if one doesn't
        # already exist.
        vpl.QtFigure("Exciting Window Title")

        # Everything from here on should be exactly the same as normal.

        vpl.quick_test_plot()

        # Automatically calls ``qapp.exec_()``. If you don't want it to then
        # use ``vpl.show(False)``.
        vpl.show()


    However this isn't particularly helpful. A more realistic example would
    require the figure be part of a larger window. In this case, treat the
    figure as you would any other QWidget. You must explicitly call
    ``figure.show()`` however. (Not sure why.)

    .. code-block:: python

        import vtkplotlib as vpl
        from PyQt5 import QtWidgets

        # python 2 compatibility
        from builtins import super


        class FigureAndButton(QtWidgets.QWidget):
            def __init__(self):
                super().__init__()

                # Go for a vertical stack layout.
                vbox = QtWidgets.QVBoxLayout()
                self.setLayout(vbox)

                # Create the figure
                self.figure = vpl.QtFigure()

                # Create a button and attach a callback.
                self.button = QtWidgets.QPushButton("Make a Ball")
                self.button.released.connect(self.button_pressed_cb)

                # QtFigures are QWidgets and are added to layouts with `addWidget`
                vbox.addWidget(self.figure)
                vbox.addWidget(self.button)


            def button_pressed_cb(self):
                # Plot commands can be called in callbacks. The current working
                # figure is still self.figure and will remain so until a new
                # figure is created explicitly. So the ``fig=self.figure``
                # arguments below aren't necessary but are recommended for
                # larger, more complex scenarios.

                # Randomly place a ball.
                vpl.scatter(np.random.uniform(-30, 30, 3),
                            color=np.random.rand(3),
                            fig=self.figure)

                # Reposition the camera to better fit to the balls.
                vpl.reset_camera(self.figure)

                # Without this the figure will not redraw unless you click on it.
                self.figure.update()


            def show(self):
                # The order of these two are interchangeable.
                super().show()
                self.figure.show()




        qapp = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)

        window = FigureAndButton()
        window.show()
        qapp.exec_()


    .. seealso:: QtFigure2 is an extension of this to provide some standard GUI elements, ready-made.


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
#        Very important that original finalise gets overwritten. This gets
#        called immediately after self.iren.Start(). The original performs resets
#        that stop the QtFigure from responding.
        pass





if __name__ == "__main__":
    pass

