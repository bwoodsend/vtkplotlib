# -*- coding: utf-8 -*-
# =============================================================================
# Created on Tue Sep 08 23:19:14 2020
#
# @author: Brénainn
#
# hook-vtkplotlib.py
# Copyright (C) 2019-2020  Brénainn Woodsend
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
"""
Hook for PyInstaller.
"""

from PyInstaller.utils.hooks import collect_data_files

datas = []

# These lines can be removed to skip specific unwanted data files.

# Icon used by QtFigure2.add_screenshot_button().
datas += collect_data_files("vtkplotlib", includes=["**/screenshot.png"])

# Icons used by QtFigure2.add_preset_views().
datas += collect_data_files("vtkplotlib", includes=["**/*.jpg"])

# The rabbit STL. Only used for demonstrating.
# datas += collect_data_files("vtkplotlib", includes=["**/rabbit/"])

excludes = [
    "matplotlib.backends",
    "vtkmodules.all",
    "matplotlib.pylab",
    "matplotlib.pyplot",
    "scipy",
]
