# -*- coding: utf-8 -*-
# =============================================================================
# Created on Sun Nov  3 19:41:11 2019
#
# @author: Brénainn Woodsend
#
#
# one line to give the program's name and a brief idea of what it does.
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
"""


from vtkplotlib.data import DATA_FOLDER as vpl_data_dir
vpl_data_dir = str(vpl_data_dir)

datas = [(vpl_data_dir, "vpl-data"),]

hiddenimports =  ['vtkmodules.vtkCommonExecutionModel',
                  'vtkmodules.vtkCommonMisc',
                  'vtkmodules.vtkCommonTransforms',
                  'vtkmodules.vtkFiltersCore',
                  'vtkmodules.vtkIOCore',
                  'vtkmodules.vtkImagingCore',
                  ]

excludedimports = ["scipy",
                   "matplotlib.pylab",
                   "matplotlib.backends",
                   "matplotlib.pyplot",
                   "PyQt4",
                   "PyQt5",
                   "tkinker",
                   ]
