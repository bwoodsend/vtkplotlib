# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 17:50:57 2019

@author: Brénainn Woodsend


one line to give the program's name and a brief idea of what it does.
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
from vtk.util.numpy_support import numpy_to_vtk

# try:
    # numpy_to_vtk(np.arange(4).reshape(2, 2).T)
    # ARRAYS_MUST_BE_CONTIGUOUS = False
# except:
    # ARRAYS_MUST_BE_CONTIGUOUS = True

ARRAYS_MUST_BE_CONTIGUOUS = True

if ARRAYS_MUST_BE_CONTIGUOUS:
    contiguous_safe = np.ascontiguousarray
else:
    contiguous_safe = lambda x:x





if __name__ == "__main__":
    print(ARRAYS_MUST_BE_CONTIGUOUS)
