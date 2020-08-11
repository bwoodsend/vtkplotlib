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
        """This dummy vtk class mimics the default vtk module structure
        whilst only loading the libraries and corresponding dlls that
        vtkplotlib uses. This makes import quicker and pyinstaller builds
        smaller.
        """
        from vtkmodules.vtkCommonCore import (
            VTK_ID_TYPE, vtkCommand, VTK_COLOR_MODE_DEFAULT, vtkPoints,
            VTK_COLOR_MODE_MAP_SCALARS, VTK_MAJOR_VERSION,
            VTK_COLOR_MODE_DIRECT_SCALARS, vtkLookupTable, vtkObject)

        from vtkmodules.vtkCommonDataModel import (vtkImageData, vtkCellArray,
                                                   vtkPolyData)

        from vtkmodules.vtkCommonMath import (vtkMatrix4x4)

        from vtkmodules.vtkCommonTransforms import (vtkTransform)

        from vtkmodules.vtkFiltersGeneral import (vtkCursor3D)

        from vtkmodules.vtkFiltersSources import (
            vtkCubeSource, vtkSphereSource, vtkArrowSource)

        from vtkmodules.vtkIOGeometry import (vtkSTLReader)

        from vtkmodules.vtkIOLegacy import (vtkPolyDataReader,
                                            vtkPolyDataWriter)

        from vtkmodules.vtkInteractionStyle import (
            vtkInteractorStyleTrackballCamera,
            vtkInteractorStyleImage,
        )

        from vtkmodules.vtkRenderingAnnotation import (vtkScalarBarActor,
                                                       vtkLegendBoxActor)

        from vtkmodules.vtkRenderingCore import (
            vtkActor,
            vtkRenderer,
            vtkWindowToImageFilter,
            vtkTextActor,
            VTK_SCALAR_MODE_DEFAULT,
            VTK_SCALAR_MODE_USE_POINT_DATA,
            vtkImageMapper,
            vtkPolyDataMapper,
            vtkActor2D,
            VTK_SCALAR_MODE_USE_CELL_DATA,
            vtkRenderWindowInteractor,
            vtkRenderWindow,
            vtkFollower,
            vtkPropPicker,
            vtkActorCollection,
            vtkInteractorStyle,
        )

        from vtkmodules.vtkRenderingFreeType import (vtkVectorText)

        from vtkmodules.vtkIOImage import (
            vtkJPEGReader, vtkJPEGWriter, vtkPNGReader, vtkPNGWriter,
            vtkTIFFReader, vtkTIFFWriter, vtkBMPReader, vtkBMPWriter)

    # These aren't used directly by vtkplotlib but are by other vtk modules.
    # Explicitly importing them here is the easiest way to tell PyInstaller
    # to include them.
    if vtk.VTK_MAJOR_VERSION >= 9:
        from vtkmodules import (
            vtkCommonExecutionModel,
            vtkCommonMisc,
            vtkCommonTransforms,
            vtkFiltersCore,
            vtkIOCore,
            vtkImagingCore,
        )

    from vtkmodules.util import numpy_support

    if PyQt5_AVAILABLE:
        # QVTKRenderWindowInteractor raises an error if this isn't loaded.
        from vtkmodules.vtkRenderingOpenGL2 import vtkOpenGLRenderer

        from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

    from vtkmodules import vtkRenderingGL2PSOpenGL2

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


def _disable_numpy_complex_warning():
    """VTK's numpy_to_vtk function has a very noisy warning - disable it here."""
    import warnings
    warnings.filterwarnings("ignore", module=numpy_support.__name__)


_disable_numpy_complex_warning()
