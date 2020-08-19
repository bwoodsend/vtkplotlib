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

    self = vpl.legend(None, fig=None)
    assert self.fig is None
    assert self.length == 0
    vpl.gcf().add_plot(self)

    self.set_entry(label="Blue Square", color="blue")

    sphere = vpl.scatter([0, 5, 10], color="g", fig=None, label="Ball")
    self.set_entry(sphere, color="b")
    self.set_entry(
        sphere,
        "Green ball",
    )

    rabbit = vpl.mesh_plot(vpl.data.get_rabbit_stl())
    self.set_entry(rabbit, "rabbit")

    rabbit_wire = vpl.plot(rabbit.vectors, color=rabbit.vectors[:, :, 0],
                           label="octopus")
    self.set_entry(rabbit_wire)
    assert self.legend.GetEntryString(self.length - 1) == "octopus"

    # self.set_entry(vpl.quiver(np.zeros(3), np.array([-1, 0, 1])), "right")
    self.set_entry(None, label="shark", icon=vpl.data.ICONS["Right"])

    for size in ((.3, .4), (.3, .4, 0)):
        self.size = size
        assert np.array_equal(self.size, [.3, .4, 0])

    position = np.array(1) - self.size
    self.position = position
    assert np.array_equal(self.position, position)

    with pytest.raises(TypeError):
        self.set_entry(object())

    length = self.length
    for i in range(2):
        eggs = vpl.text3d("eggs", label="eggs")
        self.add_plots([eggs])
        # Re-adding labels shouldn't cause the legend to grow
        assert self.length == length + 1

    vpl.text("text")

    auto_legend = vpl.legend(position=(0, 0))
    auto_legend_no_label = vpl.legend(position=(0, .7), allow_no_label=True,
                                      allow_non_polydata_plots=True,
                                      color=(.2, .3, .4, .5))
    assert auto_legend_no_label.color == (.2, .3, .4)
    assert auto_legend_no_label.opacity == .5

    self.set_entry(vpl.scatter(np.arange(12).reshape((-1, 3)), label="scatter"),
                   label="fish", index=self.length + 3)

    self.add_plots(vpl.gcf().plots)


@checker()
def test_scalar_bar():
    plot = vpl.mesh_plot(vpl.data.get_rabbit_stl())
    plot.scalars = (plot.vertices / 5) % 1
    self = vpl.scalar_bar(plot, "criss-crossy pattern")


if __name__ == "__main__":
    pytest.main([__file__])
