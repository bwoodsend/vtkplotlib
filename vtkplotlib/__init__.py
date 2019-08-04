# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 18:59:14 2019

@author: Brénainn


__init__.py 
Collects all the relevant parts and renames the classes to look like functions
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


from .figures import (Figure as figure,
                      gcf,
                      scf,
                      set_auto_fig,
                      show,
                      view,
                      reset_camera,
                      save_fig,
                      close,
                      PyQt5_AVAILABLE
                      )


if PyQt5_AVAILABLE:
    from .figures import QtFigure, QtFigure2
    

from .plots.Arrow import arrow, quiver
from .plots.Lines import Lines as plot
from .plots.MeshPlot import MeshPlot as mesh_plot
from .plots.Polygon import Polygon as polygon
from .plots.ScalarBar import ScalarBar as scalar_bar
from .plots.Scatter import scatter, Cursor as cursor
from .plots.Text import Text as text
from .plots.Text3D import Text3D as text3d, annotate

from . import data

color_bar = scalar_bar