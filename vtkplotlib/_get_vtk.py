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

try:
    from PyQt5 import QtWidgets, QtGui, QtCore
    PyQt5_AVAILABLE = True
    del QtWidgets, QtCore, QtGui
except ImportError:
    PyQt5_AVAILABLE = False


try:

    class vtk(object):
        """This dummpy vtk class mimicks the default vtk module structure
        whilst only loading the libraries and corresponding dlls that
        vtkplotlib uses. This makes import quicker and pyinstaller builds
        smaller.
        """
        from vtkmodules.vtkRenderingCorePython import vtkActor
        from vtkmodules.vtkRenderingCorePython import vtkRenderer
        from vtkmodules.vtkRenderingCorePython import vtkWindowToImageFilter
        from vtkmodules.vtkFiltersSourcesPython import vtkCubeSource
        from vtkmodules.vtkCommonCorePython import VTK_ID_TYPE
        from vtkmodules.vtkCommonCorePython import vtkCommand
        from vtkmodules.vtkRenderingCorePython import vtkTextActor
        from vtkmodules.vtkInteractionStylePython import vtkInteractorStyleTrackballCamera
        from vtkmodules.vtkCommonCorePython import VTK_COLOR_MODE_DEFAULT
        from vtkmodules.vtkCommonDataModelPython import vtkImageData
        from vtkmodules.vtkInteractionStylePython import vtkInteractorStyleImage
        from vtkmodules.vtkFiltersSourcesPython import vtkSphereSource
        from vtkmodules.vtkCommonCorePython import vtkPoints
        from vtkmodules.vtkRenderingCorePython import VTK_SCALAR_MODE_DEFAULT
        from vtkmodules.vtkCommonMathPython import vtkMatrix4x4
        from vtkmodules.vtkRenderingAnnotationPython import vtkScalarBarActor
        from vtkmodules.vtkCommonCorePython import VTK_COLOR_MODE_MAP_SCALARS
        from vtkmodules.vtkRenderingCorePython import VTK_SCALAR_MODE_USE_POINT_DATA
        from vtkmodules.vtkIOLegacyPython import vtkPolyDataReader
        from vtkmodules.vtkRenderingCorePython import vtkImageMapper
        from vtkmodules.vtkRenderingAnnotationPython import vtkLegendBoxActor
        from vtkmodules.vtkRenderingCorePython import vtkPolyDataMapper
        from vtkmodules.vtkCommonCorePython import VTK_MAJOR_VERSION
        from vtkmodules.vtkIOLegacyPython import vtkPolyDataWriter
        from vtkmodules.vtkCommonCorePython import VTK_COLOR_MODE_DIRECT_SCALARS
        from vtkmodules.vtkCommonCorePython import vtkLookupTable
        from vtkmodules.vtkCommonTransformsPython import vtkTransform
        from vtkmodules.vtkRenderingCorePython import vtkActor2D
        from vtkmodules.vtkRenderingCorePython import VTK_SCALAR_MODE_USE_CELL_DATA
        from vtkmodules.vtkFiltersSourcesPython import vtkArrowSource
        from vtkmodules.vtkRenderingCorePython import vtkRenderWindowInteractor
        from vtkmodules.vtkCommonDataModelPython import vtkCellArray
        from vtkmodules.vtkRenderingFreeTypePython import vtkVectorText
        from vtkmodules.vtkRenderingCorePython import vtkRenderWindow
        from vtkmodules.vtkIOGeometryPython import vtkSTLReader
        from vtkmodules.vtkCommonDataModelPython import vtkPolyData
        from vtkmodules.vtkFiltersGeneralPython import vtkCursor3D
        from vtkmodules.vtkRenderingCorePython import vtkFollower

    from vtkmodules.vtkRenderingOpenGL2Python import vtkOpenGLRenderer

    from vtkmodules.util import numpy_support

    if PyQt5_AVAILABLE:
        from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


except ImportError:
#    pass
    import vtk
    from vtk.util import numpy_support

    if PyQt5_AVAILABLE:
        from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


numpy_to_vtk = numpy_support.numpy_to_vtk
get_vtk_array_type = numpy_support.get_vtk_array_type
vtk_to_numpy = numpy_support.vtk_to_numpy
get_vtk_to_numpy_typemap = numpy_support.get_vtk_to_numpy_typemap
numpy_to_vtkIdTypeArray = numpy_support.numpy_to_vtkIdTypeArray
