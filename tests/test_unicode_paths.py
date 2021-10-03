# -*- coding: utf-8 -*-
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

if sys.version_info[0] <= 2:
    FileNotFoundError = IOError

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

    for i in range(2):
        # Do write test twice. 1 to check write and 2 to check overwriting.

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


def test_exceptions():
    with pytest.raises(FileNotFoundError):
        vpl.unicode_paths.PathHandler(TEST_DIR / "nonexistent", "r")

    with pytest.raises(FileNotFoundError):
        vpl.unicode_paths.PathHandler(TEST_DIR / "nonexistent" / "file", "w")

    with pytest.raises(ValueError):
        vpl.unicode_paths.PathHandler(__file__, mode="invalid mode")


if __name__ == "__main__":
    pytest.main([__file__])
