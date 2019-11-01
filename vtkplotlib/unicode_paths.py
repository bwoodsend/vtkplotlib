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


import numpy as np
import sys
import os
from pathlib2 import Path


class PathHandler(object):
    def __init__(self, path, mode="r", ALLOWED_ENCODING="ascii"):
        self.str_path = str(path)
        self.path = Path(path)
        self.ALLOWED_ENCODING = ALLOWED_ENCODING


        self.folder = self.path.parent
        self.name = self.path.name

        self.access_path = self.path

        if mode == "r":
            if not self.path.exists():
                raise FileNotFoundError(self.str_path + " does not exist")

        elif mode == "w":
            if not self.folder.exists():
                raise FileNotFoundError("The folder {} does not exist".format(self.path.parent))

        elif mode == "i":
            pass

        else:
            raise ValueError("Mode must be either 'r' or 'w'. Not '{}'".format(mode))
        self.mode = mode

        # Test both the folder and the file name to see if they are safe to use.
        # Strangely Python 2.7 raises a UnicodeDecodeError for encoding rather
        # than an UnicodeEncodeError.
        try:
            str(self.folder).encode(ALLOWED_ENCODING)
            self.folder_ok = True
        except (UnicodeEncodeError, UnicodeDecodeError):
            self.folder_ok = False

        try:
            self.path.name.encode(ALLOWED_ENCODING)
            self.name_ok = True
        except (UnicodeEncodeError, UnicodeDecodeError):
            self.name_ok = False



    def __enter__(self):

        if not self.folder_ok:
#            print("Warning - non-ascii folder", self.folder)
            print("Setting the cwd to folder")
            self.old_folder = Path.cwd()
            os.chdir(str(self.folder))
            self.access_path = Path(self.access_path.name)


        if not self.name_ok:
#            print("Warning - non-ascii file name '{}'. Will give file a temporary name then change back afterwards."\
#                  .format(self.name))

            self.access_path.suffix.encode(self.ALLOWED_ENCODING)

            while True:
                self.access_path = self.access_path.with_name(str(np.random.randint(1 << 31,)) + self.access_path.suffix)
                if not self.access_path.exists():
                    break

            if self.mode == "r":
                os.rename(self.path, self.access_path)

        self.access_path = str(self.access_path)

        return self



    def __exit__(self, *spam):
        self.access_path = Path(self.access_path)

        if not self.name_ok and self.access_path.exists():
            print("Reverting name changes")
            if self.path.exists():
                # If the target path already exists then os.rename raises a
                # FileExistsError. So if the user runs the same piece of code
                # twice without deleting the output it'll fail.
                assert self.mode == "w"
                os.remove(self.path)
            os.rename(self.access_path, self.path.name)

        if not self.folder_ok:
            print("reverting to old working dir")
            os.chdir(str(self.old_folder))



def test():
    from vtkplotlib.unicode_paths import PathHandler
    #    path = "C:\\" + "\\".join(np.random.randint(128, 0x1000, 10, np.int32).tobytes().decode("utf-32") for i in range(5)) + ".jpg"
    path = Path(__file__).parent / 'ԗݨྪࢩѸ\u0590ഃׅƂ' / 'ಫܴ\u0a92ȕՆؐཛྷറƃತ' / 'ෂҢघԝઌƔࢳܢˀાՀએࡓ\u061cཪЈतயଯ\u0886.txt'
    path.parent.mkdir(parents=True, exist_ok=True)

    with PathHandler(path, "w") as self:
        Path(self.access_path).write_text(u"eggs")
        str(self.access_path).encode(self.ALLOWED_ENCODING)


    with PathHandler(path, "r") as self:
        assert Path(self.access_path).read_text() == u"eggs"
        str(self.access_path).encode(self.ALLOWED_ENCODING)

    os.remove(str(path))
    os.removedirs(str(path.parent))

    return self




if __name__ == "__main__":
    self = test()
