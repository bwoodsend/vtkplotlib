# -*- coding: utf-8 -*-
# =============================================================================
# Created on 19:58
#
# @author: Brénainn
#
#
# test_unicode_paths.py
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
"""
from __future__ import print_function, unicode_literals, with_statement
from builtins import super

import numpy as np
import os, sys
from pathlib2 import Path

import pytest
import vtkplotlib as vpl
from vtkplotlib.unicode_paths import PathHandler

from tests._common import TEST_DIR

NAMES = ["name"]

# Proper Python unicode support came in version 3.6.
if sys.version_info >= (3, 6):
    NAMES.append("Ñ mé")
    NAMES.append(np.arange(0x100, 0xd800, 0x500,np.int32)
                 .tobytes().decode("utf-32")) # yapf: disable

import itertools
PATHS = [
    TEST_DIR / Path(*i)
    for i in itertools.combinations_with_replacement(NAMES, 2)
]


@pytest.mark.parametrize("path", PATHS)
def test_read_write(path):
    path = Path(path)

    from vtkplotlib._get_vtk import vtk

    path.parent.mkdir(parents=True, exist_ok=True)
    polydata = vpl.scatter([hash(path)] * 3).polydata.vtk_polydata

    self = PathHandler(path, "w")
    with self:
        writer = vtk.vtkPolyDataWriter()
        writer.SetFileName(self.access_path)
        writer.SetInputData(polydata)
        assert writer.Write()

        assert os.path.exists(self.py_access_path)

    assert self.path.exists()

    with PathHandler(path, "r") as self:
        reader = vtk.vtkPolyDataReader()
        reader.SetFileName(self.access_path)
        reader.Update()
        read_polydata = reader.GetOutput()
        reader.CloseVTKFile()

    dicts = [
        vpl.PolyData(pd).__getstate__() for pd in (polydata, read_polydata)
    ]

    for key in dicts[0]:
        # ascii read/write isn't lossless so np.allclose() is needed here
        assert np.all(dicts[0][key] == dicts[1][key]) \
               or np.allclose(dicts[0][key], dicts[1][key])

    os.remove(str(path))

    return self


if __name__ == "__main__":
    pytest.main([__file__])
