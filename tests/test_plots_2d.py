# -*- coding: utf-8 -*-
# =============================================================================
# Created on 22:05
#
# @author: Brénainn
#
#
# test_plots_2d.py
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
"""

from __future__ import print_function, unicode_literals, with_statement
from builtins import super

import numpy as np
import os, sys

import pytest
import vtkplotlib as vpl

from tests._common import checker


@checker()
def test_legend():
    import vtkplotlib as vpl

    self = vpl.legend(None)

    self.set_entry(label="Blue Square", color="blue")

    sphere = vpl.scatter([0, 5, 10], color="g", fig=None, label="Ball")
    self.set_entry(sphere, color="b")
    self.set_entry(
        sphere,
        "Green ball",
    )

    self.set_entry(vpl.mesh_plot(vpl.data.get_rabbit_stl()), "rabbit")
    # self.set_entry(vpl.quiver(np.zeros(3), np.array([-1, 0, 1])), "right")
    self.set_entry(None, label="shark", icon=vpl.data.ICONS["Right"])
    self.size = (.3, .3)
    self.position = np.array(1) - self.size


@checker()
def test_scalar_bar():
    plot = vpl.mesh_plot(vpl.data.get_rabbit_stl())
    plot.scalars = (plot.vertices / 5) % 1
    self = vpl.scalar_bar(plot, "criss-crossy pattern")


if __name__ == "__main__":
    pytest.main([__file__])
