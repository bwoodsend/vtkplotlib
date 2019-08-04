# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 02:29:27 2019

@author: Brénainn Woodsend


data.py handles paths to the data folder in this package
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


import pkg_resources

DATA_FOLDER = Path(pkg_resources.resource_filename("vtkplotlib", "")) / "data"

STL_FOLDER = DATA_FOLDER / "models"

STLS = [i for i in STL_FOLDER.rglob("*.stl") if i.is_file()]

ICONS_FOLDER = DATA_FOLDER / "icons"

ICONS = {i.stem: str(i) for i in ICONS_FOLDER.glob("*")}

#assert ICONS_FOLDER.is_dir()
#assert STL_FOLDER.is_dir()



if __name__ == "__main__":
    pass
