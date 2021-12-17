# -*- coding: utf-8 -*-
"""Dumping ground for random bits and bobs. I use this for several projects so
there will be a lot of irrelevant functions."""

import numpy as np
import os, sys, io


def set_to_array(s, dtype=float):
    return np.fromiter(iter(s), count=len(s), dtype=dtype)


def sep_last_ax(points):
    points = np.asarray(points)
    return tuple(points[..., i] for i in range(points.shape[-1]))


def zip_axes(*axes):
    """Convert vertex data from separate arrays for x, y, z to a single
    combined points array like most vpl functions require.

    :param axes: Each separate axis to combine.
    :type axes: numpy.ndarray

    All **axes** must have the matching or broadcastable shapes. The number of
    axes doesn't have to be 3.

    .. code-block:: python

        import vtkplotlib as vpl
        import numpy as np

        vpl.zip_axes(np.arange(10),
                     4,
                     np.arange(-5, 5))

        # Out: array([[ 0,  4, -5],
        #             [ 1,  4, -4],
        #             [ 2,  4, -3],
        #             [ 3,  4, -2],
        #             [ 4,  4, -1],
        #             [ 5,  4,  0],
        #             [ 6,  4,  1],
        #             [ 7,  4,  2],
        #             [ 8,  4,  3],
        #             [ 9,  4,  4]])

    .. seealso:: `unzip_axes()` for the reverse.

    """

    return np.concatenate(
        [i[..., np.newaxis] for i in np.broadcast_arrays(*axes)], axis=-1)


def unzip_axes(points):
    """Separate each component from an array of points.

    :param points: Some points.
    :type points: numpy.ndarray

    :return: Each axis separately as a tuple.
    :rtype: tuple

    See `zip_axes()` more information and the reverse.

    """

    return sep_last_ax(points)


def init_when_called(func):
    attr = func.__name__
    priv_attr = "_" + attr

    def getter(self):
        if not hasattr(self, priv_attr):
            setattr(self, priv_attr, func(self))
        return getattr(self, priv_attr)

    def deleter(self):
        if hasattr(self, priv_attr):
            delattr(self, priv_attr)

    return property(getter, None, deleter, func.__doc__)


def isinstance_no_import(x, module_name, type_name):
    """Test if ``isinstance(x, a_type)`` without importing **a_type** from
    wherever it came from - which would be wasteful and confuses dependency
    scanners (like PyInstaller's).
    """
    module = sys.modules.get(module_name)
    return module and isinstance(x, getattr(module, type_name))


def isinstance_PathLike(x, allow_buffers=False):
    """Test if **x** is any of the types that could contain a filename or, if
    **allow_buffers**, a pseudo file."""
    return isinstance(x, str) \
        or (hasattr(os, "PathLike") and isinstance(x, os.PathLike)) \
        or isinstance_no_import(x, "pathlib", "Path") \
        or isinstance_no_import(x, "pathlib2", "Path") \
        or (allow_buffers and isinstance(x, io.IOBase))
