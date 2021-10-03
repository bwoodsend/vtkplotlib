# -*- coding: utf-8 -*-
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
