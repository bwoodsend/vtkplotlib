# -*- coding: utf-8 -*-
# =============================================================================
#Created on Sun Sep 29 20:17:37 2019
#
#@author: Brénainn Woodsend
#
#
# image_io.py performs image read/write operations and conversions to vtkimage types.
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

"""The image_io subpackage provides tools for working 2D images. It includes methods
for:

- Converting to and from VTK's, rather awkward, vtkImageData class.
- Image reading and writing via VTK's image reader/writer classes.
- The image trimming utilised by :meth:`vtkplotlib.screenshot_fig` and :meth:`vtkplotlib.save_fig`.

For the most part, vtkplotlib converts implicitly to/from its preferred format,
which is just a numpy array of RGB values, using methods from here. But if you
are venturing into a region of VTK that vtkplotlib doesn't cover then these may
be useful.

vtkplotlib's default image format is the same as matplotlib's. i.e an (m, n, 3)
numpy array with dtype np.uint8. The most convenient way to visualise is using
matplotlib's `imshow()` method.

.. code-block::

    import matplotlib.pylab as plt
    plt.imshow(image_array)
    plt.show()


"""

from ._image_io import (read, write,
                        vtkimagedata_to_array,
                        vtkimagedata_from_array,
                        as_vtkimagedata,
                        trim_image,
                        test_bufferable_formats,
                        BUFFERABLE_FORMAT_MODES,
                        )
