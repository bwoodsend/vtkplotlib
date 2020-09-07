# -*- coding: utf-8 -*-
# =============================================================================
#Created on Sun Sep 29 20:17:37 2019
#
#@author: Brénainn Woodsend
#
#
# image_io.py
# Performs image read/write operations and conversions to vtkImage types.
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
========
Images
========

The :mod:`image_io` subpackage provides tools for working 2D images. It includes
methods for:

- Converting to and from VTK's `vtkImageData`_ class.
- Image reading and writing via VTK's image reader/writer classes.
- The image trimming utilised by :meth:`vtkplotlib.screenshot_fig` and
  :meth:`vtkplotlib.save_fig`.

For the most part, vtkplotlib converts implicitly to/from its preferred format,
which is just a numpy array of RGB values, using methods from here. But if you
are venturing into a region of VTK that vtkplotlib doesn't cover then these may
be useful.

vtkplotlib's default image format is the same as matplotlib's. i.e an ``(m, n,
3)`` numpy array with dtype ``np.uint8``. The most convenient way to visualise
is using matplotlib's `imshow`_ method.

.. code-block::

    import matplotlib.pylab as plt
    plt.imshow(image_array)
    plt.show()

.. note:: This submodule was introduced in `v1.3.0`.

-------------------------

Conversions
-----------

Converting numpy to `vtkImageData`_ and back is ugly. These methods do this for
you.

-------------------------

vtkimagedata_from_array
^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: vtkplotlib.image_io.vtkimagedata_from_array

-------------------------

vtkimagedata_to_array
^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: vtkplotlib.image_io.vtkimagedata_to_array

-------------------------

as_vtkimagedata
^^^^^^^^^^^^^^^

.. autofunction:: vtkplotlib.image_io.as_vtkimagedata

-------------------------

Read and Write
--------------

VTK provides classes for reading and writing images to disk. These are somewhat
superseded by `Pillow`_ (Python image library) which does the same thing. But
these methods are included anyway just in case you don't want to use Pillow.

-------------------------

read
^^^^

.. autofunction:: vtkplotlib.image_io.read

-------------------------

write
^^^^^

.. autofunction:: vtkplotlib.image_io.write

-------------------------

Formats allowing pseudo files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Some formats allow reading and writing from RAM whereas others must use the disk.
The following table summarises which are allowed. This table is accessible via
``vtkplotlib.image_io.BUFFERABLE_FORMAT_MODES``.

====  ==============
Name  Allowed modes
====  ==============
JPEG  Read and Write
PNG   Write
TIFF
BMP   Write
====  ==============


-------------------------

Misc
----------

trim_image
^^^^^^^^^^

.. autofunction:: vtkplotlib.image_io.trim_image



.. _vtkImageData: https://vtk.org/doc/nightly/html/classvtkImageData.html#details

.. _imshow: https://matplotlib.org/api/_as_gen/matplotlib.pyplot.imshow.html

.. _Pillow: https://pillow.readthedocs.io/en/stable/

"""

from ._image_io import (
    read,
    write,
    vtkimagedata_to_array,
    vtkimagedata_from_array,
    as_vtkimagedata,
    trim_image,
    BUFFERABLE_FORMAT_MODES,
)
