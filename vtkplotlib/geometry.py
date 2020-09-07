# -*- coding: utf-8 -*-
# =============================================================================
# Created on Sun Dec 30 16:20:42 2018
#
# @author: Brénainn Woodsend
#
# geometry.py contains functions that have anything to do with geometry.
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
#
# =============================================================================
"""
Anything geometry related goes in here. I use this file for multiple projects
so there will be unused functions in here.
"""
from __future__ import division

import numpy as np

from vtkplotlib import nuts_and_bolts


def distance(points, keepdims=False):
    return np.sqrt(np.sum(points**2, axis=-1, keepdims=keepdims))


def inner_product(a, b):
    return np.sum(a * b, axis=-1)


#def distance_sqr(points):
#    return np.sum(points ** 2, axis=-1)


def highest(points, up=np.array([0, 0, 1]), include_height=False):
    points = np.asarray(points)

    heights = inner_product(points, up)
    arg = np.unravel_index(np.argmax(heights), heights.shape)

    if include_height:
        return points[arg], heights[arg]
    else:
        return points[arg]


def normalise(vectors):
    vectors /= distance(vectors)[..., np.newaxis]


def normalised(vectors):
    return vectors / distance(vectors)[..., np.newaxis]


def orthogonal_bases(vector0):
    vector0 = np.asarray(vector0)

    old_shape = vector0.shape
    vector0 = vector0.reshape((-1, vector0.shape[-1]))
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

    return vector0.reshape(old_shape), vector1.reshape(
        old_shape), vector2.reshape(old_shape)
