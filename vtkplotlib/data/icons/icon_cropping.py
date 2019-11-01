# -*- coding: utf-8 -*-
# =============================================================================
# Created on Fri Aug  2 14:25:21 2019
#
# @author: Brénainn Woodsend
#
#
# one line to give the program's name and a brief idea of what it does.
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


import numpy as np
import matplotlib.pylab as plt
import sys
import os
from pathlib2 import Path

from PIL import Image
from vtkplotlib.data import ICONS_FOLDER

names = ["Right", "Left", "Front", "Back", "Top", "Bottom"]

BACKGROUND = np.array([[[243, 243 ,243]]], np.uint8)

CLEARANCE = 10

for name in names:


    path = ICONS_FOLDER / (name + ".jpg")

    image = Image.open(str(path))

    arr = np.array(image)

    mask = (arr == BACKGROUND).all(2)

    col_mask = mask.all(1)
    row_mask = mask.all(0)

    cols = np.argwhere(~row_mask)
    left = cols.min() - CLEARANCE
    right = cols.max() + CLEARANCE

    rows = np.argwhere(~col_mask)
    back = rows.min() - CLEARANCE
    front = rows.max() + CLEARANCE

    plt.axvline(left)
    plt.axvline(right)
    plt.axhline(front)
    plt.axhline(back)
    plt.imshow(mask)
    plt.show()

    x = (right + left) / 2
    y = (front + back) / 2

    radius = max(right - x, front - y)
#    assert 0
    left = int(x - radius)
    right = int(x + radius)
    back = int(y - radius)
    front = int(y + radius)

    size = int(radius * 2)
    cropped_arr = np.empty((size, size, 3), np.uint8)
    cropped_arr[:] = BACKGROUND

    cropped_arr[front - back + (- size): cropped_arr.shape[0] - front + back + size, \
                right - left + (- size): cropped_arr.shape[1] - right + left + size] = \
            arr[back:front, left:right]


    cropped = Image.fromarray(cropped_arr)


    cropped.save(str(path.with_suffix(".jpg")))

#    break




if __name__ == "__main__":
    pass
