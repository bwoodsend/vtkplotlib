# -*- coding: utf-8 -*-
"""
Created on Mon May 13 15:15:26 2019

@author: Brénainn Woodsend

nuts_and_bolts.py
Dumping ground for various misc functions.
Copyright (C) 2019  Brénainn Woodsend

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""

"""Dumping ground for random bits and bobs. I use this for several projects so
there will be a lot of irrelevant functions."""

import numpy as np
import matplotlib.pylab as plt
import sys
import os




def set_to_array(s, dtype=float):
    return np.fromiter(iter(s), count=len(s), dtype=dtype)

def sep_args(args):
    print("use sep_last_ax")
    assert 0
    return sep_last_ax(args)

def sep_last_ax(points):
    points = np.asarray(points)
    return tuple(points[..., i] for i in range(points.shape[-1]))

def flatten_all_but_last(arr):
    arr = np.asarray(arr)
    return arr.reshape(int(np.prod(arr.shape[:-1])), arr.shape[-1])

def mask_union(mask, *masks):
    out = mask.copy()
    for m in masks:
        np.logical_or(out, m, out=out)
    return out

def mask_and(mask, *masks):
    out = mask.copy()
    for m in masks:
        np.logical_and(out, m, out=out)
    return out


def set_element_0(s):
    for i in s:
        return i

def arg_array_inv(args, out_len=None, default=None):
    out_len = out_len or len(args)
    out = np.empty(out_len, args.dtype)
    if default is not None:
        out.fill(default)

    out[args] = np.arange(len(args))
    return out


def random_selection(lst, size=None):
    indices = np.random.randint(0, len(lst), size)

    return np.asarray(lst)[indices]

def as_str(x):
    if isinstance(x, str):
        return x
    elif isinstance(x, bytes):
        return x.decode(errors="replace")
    else:
        return str(x)

def numpy_broadcastable(*arrs):
    arrs = (np.asarray(i) for i in arrs)
    for lens in zip(*(i.shape[::-1] for i in arrs)):
        lens = set(lens)
        if len(lens - {1}) > 1:
            return False
    return True


def init_when_called(func):
    attr = func.__name__
    priv_attr = "_" + attr
    @property
    def wrapped(self):
        if (not hasattr(self, priv_attr)):
            setattr(self, priv_attr, func(self))
        return getattr(self, priv_attr)

    @wrapped.deleter
    def wrapped(self):
        if hasattr(self, priv_attr):
            delattr(self, priv_attr)
    wrapped.__doc__ = func.__doc__
    return wrapped


#def repeat(x=None, n):
#    return (x, ) * n
#
#def difference_map(x, y):
#    x = np.asarray(x)
#    y = np.asarray(y)
#    dif = x[repeat(None, len(x.shape)), (np.newaxis, ) * len(y.shape)] - y[(np.newaxis, ) * x.shape]
#    assert dif.shape == x.shape + y.shape
#    return dif


if __name__ == "__main__":
    pass
