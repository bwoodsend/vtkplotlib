# -*- coding: utf-8 -*-
# =============================================================================
# Created on 21:58
#
# @author: Brénainn
#
#
# test_qt.py
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

import time
from builtins import super

import numpy as np
import os, sys

import pytest
import vtkplotlib as vpl

from tests._common import checker, VTKPLOTLIB_WINDOWLESS_TEST

pytestmark = pytest.mark.skipif(not vpl.PyQt5_AVAILABLE, reason="Requires Qt")


@checker()
def test_qfigure():
    vpl.QtFigure._abc_assert_no_abstract_methods()

    self = vpl.QtFigure("a Qt widget figure")

    assert self is vpl.gcf()

    direction = np.array([1, 0, 0])
    vpl.quiver(np.array([0, 0, 0]), direction)
    vpl.view(camera_direction=direction)
    vpl.reset_camera()

    self.show(block=False)
    self.close()

    self.showMaximized(block=not VTKPLOTLIB_WINDOWLESS_TEST)
    out = vpl.screenshot_fig(fig=self)
    vpl.close(fig=self)

    globals().update(locals())
    return out


@checker()
def test_qfigure2():
    fig = vpl.QtFigure2("a QWidget figure")
    fig.setWindowTitle(fig.window_name)
    assert fig is vpl.gcf()

    plot = vpl.scatter(np.arange(9).reshape((3, 3)).T)[0]
    vpl.quick_test_plot()

    fig.add_all()

    fig.show(block=False)
    fig.qapp.processEvents()

    for i in fig.view_buttons.buttons:
        i.released.emit()
        fig.qapp.processEvents()
        time.sleep(.1)

    if not VTKPLOTLIB_WINDOWLESS_TEST:
        fig.screenshot_button.released.emit()
    fig.show_plot_table_button.released.emit()

    fig.show(block=False)

    for plot in fig.plot_table.rows:
        fig.plot_table.rows[plot].text.released.emit()
        fig.qapp.processEvents()
        assert not plot.visible

    assert np.allclose(vpl.screenshot_fig(fig=fig),
                       np.array(255) * fig.background_color)

    for plot in fig.plot_table.rows:
        fig.plot_table.rows[plot].text.released.emit()
        fig.qapp.processEvents()
        assert plot.visible

    fig.plot_table.close()


if __name__ == "__main__":
    pytest.main([__file__])
