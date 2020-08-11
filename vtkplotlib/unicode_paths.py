#encoding: utf-8
# =============================================================================
# Created on Sat Aug 31 15:38:39 2019
#
# @author: Brénainn Woodsend
#
#
# unicode_paths.py
# VTK can't handle non ascii file paths. This lets python handle all the unicode
# so that vtk is never exposed to it.
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
"""
VTK uses whatever encoding your machine's "current codepage". But you have
to explicitly string.encode(codepage) strings to bytes then hand those to VTK.
See this answer:
https://discourse.vtk.org/t/what-is-state-of-the-art-unicode-file-names-on-windows/1821/42

This module provides PathHandler - a context manager which handles this when
using VTK's file reader/writer classes.
"""

from __future__ import print_function

import numpy as np
import sys
import os
from pathlib2 import Path
# I believe it's just a Windows issue. Other OSs are more practical and use UTF-8.
# The codepage is different for different regions. This snippet should say
# what encoding to use.
# https://stackoverflow.com/questions/9226516/python-windows-console-and-encodings-cp-850-vs-cp1252
# Since VTK==9.0.0, VTK have switched to utf-8 so we can skip all this for VTK
# versions >= 9.

from vtkplotlib._get_vtk import vtk

import locale
if os.name == "nt" and vtk.VTK_MAJOR_VERSION <= 8:
    ALLOWED_ENCODING = locale.getlocale()[1] or "ascii"
else:
    ALLOWED_ENCODING = "utf-8"

if __name__ == "__main__":
    _print = print
else:
    _print = lambda *x: None

class PathHandler(object):
    """Context manager to handle unicode filenames (which VTK does poorly).
    This class will choose any combination of:

    * Temporarily changing the cwd and using relative paths for non-ascii
      folders.
    * Temporarily rename files to be read to an ascii name.
    * Direct VTK to write to an ascii name then rename it afterwards.

    """
    def __init__(self, path, mode="r", ALLOWED_ENCODING=ALLOWED_ENCODING):
        self.path = Path(path).absolute()
        del path
        self.str_path = str(self.path)
        self.ALLOWED_ENCODING = ALLOWED_ENCODING

        self.folder = self.path.parent
        self.name = self.path.name

        if mode == "r":
            if not self.path.exists():
                raise FileNotFoundError(self.str_path + " does not exist")

        elif mode == "w":
            if not self.folder.exists():
                raise FileNotFoundError("The folder {} does not exist".format(
                    self.path.parent))

        elif mode == "i":
            pass

        else:
            raise ValueError(
                "Mode must be either 'r' or 'w'. Not '{}'".format(mode))
        self.mode = mode

        # Test both the folder and the file name to see if they are safe to use.
        # Python 2.7 raises a UnicodeDecodeError for encoding rather
        # than an UnicodeEncodeError.
        try:
            self.access_folder = str(self.folder).encode(ALLOWED_ENCODING)
            self.folder_ok = True
        except (UnicodeEncodeError, UnicodeDecodeError):
            self.folder_ok = False

        try:
            self.access_name = self.path.name.encode(ALLOWED_ENCODING)
            self.name_ok = True
        except (UnicodeEncodeError, UnicodeDecodeError):
            self.name_ok = False

    @property
    def access_path(self):
        return os.path.join(self.access_folder, self.access_name)

    @property
    def py_access_path(self):
        return self.access_path.decode(self.ALLOWED_ENCODING)

    def __enter__(self):

        if not self.folder_ok:
            _print("Setting the cwd to folder")
            self.old_folder = Path.cwd()
            os.chdir(str(self.folder))
            self.access_folder = "".encode(self.ALLOWED_ENCODING)

        if not self.name_ok:
            # Test the suffix encodes OK
            suffix = self.path.suffix.encode(self.ALLOWED_ENCODING)

            while True:
                self.access_name = str(np.random.randint(1 << 31,)).encode(
                    self.ALLOWED_ENCODING) + suffix
                if not os.path.exists(self.py_access_path):
                    break

            if self.mode == "r":
                os.rename(str(self.path), self.py_access_path)

        return self

    def __exit__(self, *spam):
        #        self.access_path = Path(self.access_path)

        if not self.name_ok and os.path.exists(self.py_access_path):
            _print("Reverting name changes")
            if self.path.exists():
                # If the target path already exists then os.rename raises a
                # FileExistsError. So if the user runs the same piece of code
                # twice without deleting the output it'll fail.
                assert self.mode == "w"
                os.remove(str(self.path))
            os.rename(self.py_access_path, str(self.path))

        if not self.folder_ok:
            _print("reverting to old working dir")
            os.chdir(str(self.old_folder))


def test_path(path):
    import vtkplotlib as vpl
    from vtkplotlib._get_vtk import vtk

    path.parent.mkdir(parents=True, exist_ok=True)
    polydata = vpl.scatter([0, 0, 0]).polydata.vtk_polydata

    self = PathHandler(path, "w")
    with self:
        _print(path, "->", self.py_access_path)

        writer = vtk.vtkPolyDataWriter()
        writer.SetFileName(self.access_path)
        writer.SetInputData(polydata)
        assert writer.Write()

        assert os.path.exists(self.py_access_path)

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
        # bit weird that allclose is needed here
        assert np.all(dicts[0][key] == dicts[1][key]) or np.allclose(
            dicts[0][key], dicts[1][key])

    os.remove(str(path))
    os.removedirs(str(path.parent))

    return self


def test():
    from vtkplotlib.data import DATA_FOLDER

    NAMES = [u"name"]

    # Proper Python unicode support came in version 3.6 I think (determined
    # empirically).
    version = (sys.version_info.major, sys.version_info.minor)
    if version >= (3, 6):
        NAMES.append(u"Ñ mé")
    if version >= (3, 6):
        NAMES.append(
            np.arange(0x100, 0xd800, 0x500,
                      np.int32).tobytes().decode("utf-32"))

    import itertools
    for path in itertools.combinations_with_replacement(NAMES, 2):
        self = test_path(DATA_FOLDER / Path(*path))

    return self


if __name__ == "__main__":
    print(ALLOWED_ENCODING)
    self = test()
