# -*- coding: utf-8 -*-
"""
Created on Sun Dec 30 16:20:42 2018

@author: Brénainn Woodsend

geometry.py
For functions with anything to do with geometry
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

import numpy as np
import matplotlib.pylab as plt


def distance(points):
    return np.sqrt(np.sum(points ** 2, axis=-1))

def inner_product(a, b):
    return np.sum(a * b, axis=-1)

def distance_sqr(points):
    return np.sum(points ** 2, axis=-1)


def components_perpendicular_to_direction(vectors, normalised_direction):
    return vectors - inner_product(vectors, normalised_direction)[..., np.newaxis] * normalised_direction

    
def highest(points, up=np.array([0, 0, 1]), include_hight=False):
    
    heights = inner_product(points, up)
    arg = np.unravel_index(np.argmax(heights), heights.shape)
    
    if include_hight:
        return points[arg], heights[arg]
    else:
        return points[arg]

def stagger(points, depth=1):
    ijs = [(i, len(points) - depth + i) for i in range(depth + 1)]
    return tuple(points[i:j] for (i, j) in ijs)
    

def separate_path_components(path, direction):
    direction_mag = distance(direction)
    direction = direction / direction_mag
    
    parallel_components = inner_product(path, direction)
    
    perpendicular_components_vects = components_perpendicular_to_direction(path, direction)
    
    return perpendicular_components_vects, parallel_components


def flatten_components(components):
    local_displacements = components[1:] - components[:-1]
    local_distances = distance(local_displacements)
    
    distances = np.empty(len(components), components.dtype)
    distances[0] = 0
    distances[1:] = np.cumsum(local_distances)
    
    return distances
    

def separate_paths_concatenate(*paths, direction):
    perp_total = 0
    perps = []
    parrs = []
    for path in paths:
        if path is not None:
            perp, parr= separate_path_components(path, direction)
            perp = flatten_components(perp)
            perps.append(perp + perp_total)
            parrs.append(parr)
            perp_total += perp[-1]
        else:
            print("Warning. A path was None")
            perp_total += 1
    return perps, parrs
    
    
def plot_path_separated(*paths, direction, **plotargs):
    for (perp, parr) in zip(*separate_paths_concatenate(*paths, direction=direction)):
        plt.plot(perp, parr, **plotargs)


def from_xz(xz, y=0):
    shape_xz = xz.shape
    shape_xyz = shape_xz[:-1] + (shape_xz[-1] + 1,)
    
    xyz = np.empty(shape_xyz, xz.dtype)
    xyz[..., 0] = xz[..., 0]
    xyz[..., 1] = y
    xyz[..., 2] = xz[..., 1]
    return xyz

def to_xz(xyz):
    return xyz[..., [0, 2]]
    

def rotation_matrix(theta_rad):
    return np.array([[np.cos(theta_rad), np.sin(theta_rad)],
                     [-np.sin(theta_rad), np.cos(theta_rad)]])
    
    
def rotate(points, theta_deg):
    if points.shape[-1] != 2:
        raise ValueError("points last axis must have length 2")

    if theta_deg == 0:
        return points
    
    elif theta_deg == 90:
        out = np.empty_like(points)
        out[..., 0] = -points[..., 1]
        out[..., 1] = points[..., 0]
        return out
    
    elif theta_deg == 180:
        return -points
    
    elif theta_deg == 270:
        return -rotate(points, 90)
        
    else:
        theta_rad = np.deg2rad(theta_deg)
        m = rotation_matrix(theta_rad)        
        return np.dot(points, m)
    

def real_and_bounded(x, lb=0, ub=1):
    mask = x.imag == 0
    mask &= x.real >= lb
    mask &= x.real <= ub
    return x.real[mask]


def deg_to_vect(x):
    theta = np.deg2rad(x)
    if isinstance(x, np.ndarray):
        shape = x.shape + (2, )
    else:
        shape = (2, )
    out = np.empty(shape, float)
    out[..., 0] = np.cos(theta)
    out[..., 1] = np.sin(theta)
    return out

def cumsum(a, initial=0, dtype=None):
    dtype = dtype or a.dtype
    shape = list(a.shape)
    shape[0] += 1
    out = np.empty(tuple(shape), dtype)
    out[:] = np.asarray(initial)[..., np.newaxis]
    out[1:] += np.cumsum(a, 0, dtype=dtype)
    return out


def vect_to_deg(xy, avoid_jumps=False):
    out = np.rad2deg(np.arctan2(xy[..., 1], xy[..., 0]))
    if avoid_jumps:
        diff = np.empty_like(out)
        diff[0] = out[0]
        diff[1:] = np.diff(out)
#        diff[0] += out[0]
        without_jumps = (diff + 180) % 360 - 180
#        diff[0] -= out[0]
        out = np.cumsum(without_jumps)
    return out


def normalise(vects):
    vects /= distance(vects)[..., np.newaxis]
    
def normalised(vects):
    return vects / distance(vects)[..., np.newaxis]

def get_components(points, *unit_vectors):
    return tuple(inner_product(points, uv) for uv in unit_vectors)

def tri_centres(mesh):
    return np.mean(mesh.vectors, axis=1)


def spherical(vects):
    r = distance(vects)
    vects = vects / r
    theta = np.rad2deg(np.arccos(vects[..., 2]))
    thi = np.rad2deg(np.arctan2(vects[..., 1], vects[..., 0]))
    return r, thi, theta


def orthogonal_bases(vector0):
    vector0 = np.asarray(vector0)
    import nuts_and_bolts
    old_shape = vector0.shape
    vector0 = nuts_and_bolts.flatten_all_but_last(vector0)
    vector0 = normalised(vector0)
    if not np.isfinite(vector0).all():
        raise ValueError("vector0 must have non zero magnitude")
        
    to_do_mask = np.ones(vector0.shape[:-1], bool)
    vector1 = np.empty_like(vector0)
    vector2 = np.empty_like(vector0)
    
    while to_do_mask.any():
        temp = np.random.uniform(-1, 1, 3)
        
        vector1[to_do_mask] = np.cross(temp, vector0[to_do_mask])
        vector1[to_do_mask] /= distance(vector1)[..., np.newaxis]
        
        vector2[to_do_mask] = np.cross(vector0[to_do_mask], vector1[to_do_mask])
        vector2[to_do_mask] /= distance(vector2)[..., np.newaxis]
        
        to_do_mask &= np.logical_not(np.isfinite(vector2).all(-1))
    
    return vector0.reshape(old_shape), vector1.reshape(old_shape), vector2.reshape(old_shape)



class UnitVector(object):
    def __init__(self, vector):
        vector = normalised(np.array(vector))
        self.vector = vector
        
        
    def __repr__(self):
        return self.__class__.__name__ + "({})".format(self.vector)
    
    def __call__(self, vec):
        if isinstance(vec, UnitVector):
            vec = vec.vector
        return inner_product(self.vector, vec)
    
    def matched_sign(self, vector):
        return vector * np.sign(self(vector))
    
    def __neg__(self):
        return type(self)(-self.vector)
    
    
#def orthogonal_bases(vector0):
#    if distance(vector0) == 0:
#        raise ValueError("vector0 must have non zero magnitude")
#    vector0 = normalised(vector0)
#    
#    while True:
#        temp = np.random.uniform(-1, 1, 3)
#        vector1 = np.cross(temp, vector0)
#        
#        if distance(vector1):
#            normalise(vector1)
#            
#            vector2 = np.cross(vector0, vector1)
#            if distance(vector2):
#                normalise(vector2)
#                break
#            
#    return vector0, vector1, vector2

    
    
def wrap(attr):
    def f(self, *args):
#        args2 = []
#        for arg in args:
##            if isinstance(arg, UnitVector):
##                arg = arg.vector
#            args2.append(args)
##        print(attr, args2)
        return getattr(self.vector, attr)(*args)
    return f

for attr in ['__abs__',
             '__add__',
             '__and__',
             '__array__',
#             '__array_finalize__',
#             '__array_function__',
#             '__array_interface__',
#             '__array_prepare__',
#             '__array_priority__',
#             '__array_struct__',
#             '__array_ufunc__', 
#             '__array_wrap__', 
             '__bool__', 
             '__complex__', 
             '__contains__', 
             '__divmod__',
             '__eq__',
             '__float__',
             '__floordiv__', 
             '__ge__',
             '__getitem__', 
             '__gt__', 
             '__hash__', 
             '__iadd__', 
             '__iand__', 
             '__ifloordiv__', 
             '__ilshift__', 
             '__imatmul__', 
             '__imod__', 
             '__imul__', 
             '__index__', 
             '__int__', 
             '__invert__', 
             '__ior__', 
             '__ipow__', 
             '__irshift__', 
             '__isub__', 
             '__iter__', 
             '__itruediv__', 
             '__ixor__', 
             '__le__', 
             '__len__', 
             '__lshift__', 
             '__lt__', 
             '__matmul__', 
             '__mod__', 
             '__mul__', 
             '__ne__', 
#             '__neg__', 
             '__or__', 
             '__pos__', 
             '__pow__',
             '__radd__', 
             '__rand__', 
             '__rdivmod__', 
#             '__reduce__', 
             '__rfloordiv__', 
             '__rlshift__', 
             '__rmatmul__', 
             '__rmod__', 
             '__rmul__', 
             '__ror__', 
             '__rpow__', 
             '__rrshift__', 
             '__rshift__', 
             '__rsub__', 
             '__rtruediv__', 
             '__rxor__', 
             '__setitem__',
             '__sub__',
             '__truediv__', 
             '__xor__',]:
    setattr(UnitVector, attr, wrap(attr))
    

#    
#
#    def __neg__(self):
#        return self.__class__(-self.vector)
#    def __array__(self):
#        return self.vector.__array__()
#
#    def __add__(self, x):
#        return self.vector + x
#    def __radd__(self, x):
#        return self.vector + x
#    def __mul__(self, x):
#        return self.vector * x
#    def __rmul__(self, x):
#        return self.vector * x
#    def __sub__(self, x):
#        return self.vector - x
#    def __rsub__(self, x):
#        return x - self.vector
#    def __pow__(self, x):
#        return self.vector ** x
    
#class UnitVector(np.ndarray):    
#    
#    @classmethod
#    def from_np_array(cls, arr):
#        print("from numpy new")
#        arr = normalised(arr)
#        out = cls._uv_new(cls, arr.shape)
#        out[:] = arr
#        return out
#        
#    @classmethod
#    def _np_new(self, arr):
#        print("numpy new")
#        return self.__new__(np.ndarray, arr.shape)
#    
#    @classmethod
#    def __new__(cls, *args, **kargs):
#        print("__new__", cls, *args, **kargs)
#        return super().__new__(*args, **kargs)
#
#        
#UnitVector._uv_new = UnitVector.__new__
#UnitVector.__new__ = np.ndarray.__new__#UnitVector._np_new
    
    
    
#    def __getattribute__(self, name):
#        print(name)
#        return super().__getattribute__(name)
    
#class UnitVector(np.ndarray):
#    def __init__(self, vect):
#        
#    pass
#        self.__class__ = np.ndarray

def set_angle_range(x, lb=0, 
                    strict_ub=True, one_rotation=360):
    
    
    y = ((x - lb) % one_rotation) + lb
    if strict_ub:
        pass
    else:
        y[y == lb] += one_rotation
        
    return y
    
    
def row_to_3cols(arr):
    out_shape = arr.shape + (3,)
    out = np.empty(out_shape, arr.dtype)
    for i in range(3):
        out[..., i] = arr
    return out



    
if __name__ == "__main__":
#    path = np.array([[1, 2, 3]])
#    x1 = np.array([0, 1, 0])
#    x2 = np.array([.5, 0, .6])
    
#    print(separate_path_multi_components(path, x1, x2))
    vector = [1, 0, 0]
    vector = normalised(np.array(vector))
    self = UnitVector(vector)
