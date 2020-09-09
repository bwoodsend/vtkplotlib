# -*- coding: utf-8 -*-
# =============================================================================
# Created on Wed Jul 31 02:29:27 2019
#
# @author: Brénainn Woodsend
#
#
# data.__init__.py handles paths to the data folder in vtkplotlib.
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

import sys
from pathlib2 import Path

# vtkplotlib isn't zip safe and I have no intention of trying to make it so.
# Hence, using __file__ instead of (super slow) pkg_resources is fine.

from vtkplotlib import __file__ as _init_path

DATA_FOLDER = Path(_init_path).with_name("data")

MODELS_FOLDER = DATA_FOLDER / "models"


def get_rabbit_stl():
    return str(MODELS_FOLDER / "rabbit" / "rabbit.stl")


ICONS_FOLDER = DATA_FOLDER / "icons"
ICONS = {i.stem: str(i) for i in ICONS_FOLDER.glob("*.jpg")}

_HOOKS_DIR = DATA_FOLDER.with_name("__PyInstaller")


def _get_hooks_dir():
    return [str(_HOOKS_DIR)]


def assert_ok():
    assert ICONS_FOLDER.is_dir()
    assert MODELS_FOLDER.is_dir()
    assert Path(get_rabbit_stl()).exists()
    assert _HOOKS_DIR.exists()


if __name__ == "__main__":
    assert_ok()
