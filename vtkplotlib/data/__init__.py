# -*- coding: utf-8 -*-
# =============================================================================
# Created on Wed Jul 31 02:29:27 2019
#
# @author: Brénainn Woodsend
#
#
# data.__init__.py handles paths to the data folder in vtkplotlib.
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


import sys
from pathlib2 import Path

import pkg_resources


if getattr( sys, 'frozen', False ) :
    # running in a pyinstaller bundle
    DATA_FOLDER = Path(pkg_resources.resource_filename("vtkplotlib", "")).parent / "vpl-data"
else :
    # running normally
    DATA_FOLDER = Path(pkg_resources.resource_filename("vtkplotlib", "")) / "data"

ROOT = DATA_FOLDER.parent


MODELS_FOLDER = DATA_FOLDER / "models"

def get_rabbit_stl():
#    print("This is not my rabbit file. See README.txt and LICENSE.txt in\n{}\nfor details.".format(folder))
    return str(MODELS_FOLDER / "rabbit" / "rabbit.stl")

ICONS_FOLDER = DATA_FOLDER / "icons"

ICONS = {i.stem: str(i) for i in ICONS_FOLDER.glob("*")}




def assert_ok():
    assert ICONS_FOLDER.is_dir()
    assert MODELS_FOLDER.is_dir()
    assert Path(get_rabbit_stl()).exists()

if __name__ == "__main__":
    assert_ok()