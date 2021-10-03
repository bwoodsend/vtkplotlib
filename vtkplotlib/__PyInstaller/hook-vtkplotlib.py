# -*- coding: utf-8 -*-
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
