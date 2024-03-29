# -*- coding: utf-8 -*-
"""
"""
import os

try:
    from vtkplotlib import _vtk as vtk
    from vtkmodules.util import numpy_support
    from vtkmodules import vtkRenderingGL2PSOpenGL2

except ImportError:
    if os.environ.get("FORCE_VTKMODULES"):
        raise
    import vtk
    from vtk.util import numpy_support

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
