# -*- coding: utf-8 -*-
"""
Created on Sat Aug  3 11:31:32 2019

@author: Brénainn Woodsend


figures/__init__.py
These scripts are responsible for creating the window to plot into.
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



from .figure import Figure
from .figure_manager import (gcf,
                             scf,
                             set_auto_fig,
                             show,
                             save_fig,
                             screenshot_fig,
                             close,
                             reset_camera,
                             view)

try:
    from PyQt5 import QtWidgets, QtGui, QtCore
    PyQt5_AVAILABLE = True
    del QtWidgets, QtCore, QtGui
except ImportError:
    PyQt5_AVAILABLE = False


if PyQt5_AVAILABLE:
    from .QtFigure import QtFigure
    from .QtGuiFigure import QtFigure2

