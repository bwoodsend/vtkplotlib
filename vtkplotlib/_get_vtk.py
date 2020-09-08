# -*- coding: utf-8 -*-
# =============================================================================
# Created on Wed Jan 15 15:44:54 2020
#
# @author: Brénainn Woodsend
#
#
# one line to give the program's name and a brief idea of what it does.
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
import os

try:
    from PyQt5 import QtWidgets, QtGui, QtCore
    PyQt5_AVAILABLE = True
    del QtWidgets, QtCore, QtGui
except ImportError:
    PyQt5_AVAILABLE = False

try:
    from vtkplotlib import _vtk as vtk
    from vtkmodules.util import numpy_support
    if PyQt5_AVAILABLE:
        from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

        # QVTKRenderWindowInteractor raises an error if this isn't loaded.
        from vtkmodules.vtkRenderingOpenGL2 import vtkOpenGLRenderer

    from vtkmodules import vtkRenderingGL2PSOpenGL2

except ImportError:
    if os.environ.get("FORCE_VTKMODULES"):
        raise
    import vtk
    from vtk.util import numpy_support
    if PyQt5_AVAILABLE:
        from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

if vtk.VTK_MAJOR_VERSION >= 9:
    from vtkmodules import (
        vtkCommonExecutionModel,
        vtkCommonMisc,
        vtkCommonTransforms,
        vtkFiltersCore,
        vtkIOCore,
        vtkImagingCore,
    )

numpy_to_vtk = numpy_support.numpy_to_vtk
get_vtk_array_type = numpy_support.get_vtk_array_type
vtk_to_numpy = numpy_support.vtk_to_numpy
get_vtk_to_numpy_typemap = numpy_support.get_vtk_to_numpy_typemap
numpy_to_vtkIdTypeArray = numpy_support.numpy_to_vtkIdTypeArray


def _disable_numpy_complex_warning():
    """VTK's numpy_to_vtk function has a very noisy warning - disable it here."""
    import warnings
    warnings.filterwarnings("ignore", module=numpy_support.__name__)


_disable_numpy_complex_warning()

VTK_VERSION_INFO = (vtk.VTK_MAJOR_VERSION, vtk.VTK_MINOR_VERSION,
                    vtk.VTK_BUILD_VERSION)
