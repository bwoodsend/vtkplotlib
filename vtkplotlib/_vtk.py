# -*- coding: utf-8 -*-
# =============================================================================
# Created on 21:16
#
# @author: Brénainn
#
#
# _vtk.py
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
"""This dummy vtk module mimics the default vtk module structure
whilst only loading the libraries and corresponding dlls that
vtkplotlib uses. This makes import quicker and PyInstaller builds
smaller.
"""

from vtkmodules.vtkCommonCore import (
    VTK_ID_TYPE, vtkCommand, VTK_COLOR_MODE_DEFAULT, vtkPoints,
    VTK_COLOR_MODE_MAP_SCALARS, VTK_MAJOR_VERSION,
    VTK_COLOR_MODE_DIRECT_SCALARS, vtkLookupTable, vtkObject, VTK_MINOR_VERSION,
    VTK_BUILD_VERSION)

from vtkmodules.vtkCommonDataModel import (vtkImageData, vtkCellArray,
                                           vtkPolyData)

from vtkmodules.vtkCommonMath import (vtkMatrix4x4)

from vtkmodules.vtkCommonTransforms import (vtkTransform)

from vtkmodules.vtkFiltersGeneral import (vtkCursor3D)

from vtkmodules.vtkFiltersSources import (vtkCubeSource, vtkSphereSource,
                                          vtkArrowSource)

from vtkmodules.vtkIOGeometry import (vtkSTLReader)

from vtkmodules.vtkIOLegacy import (vtkPolyDataReader, vtkPolyDataWriter)

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

from vtkmodules.vtkIOImage import (vtkJPEGReader, vtkJPEGWriter, vtkPNGReader,
                                   vtkPNGWriter, vtkTIFFReader, vtkTIFFWriter,
                                   vtkBMPReader, vtkBMPWriter)
