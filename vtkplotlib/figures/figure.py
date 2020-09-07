# -*- coding: utf-8 -*-
# =============================================================================
# Created on Sat Jul 20 21:21:20 2019
#
# @author: Brénainn Woodsend
#
#
# figures.py provides windows to render into.
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

from builtins import super

from vtkplotlib._get_vtk import vtk
import numpy as np
import os
import sys
from pathlib2 import Path

from vtkplotlib.figures.BaseFigure import BaseFigure, nuts_and_bolts, vtk


class Figure(BaseFigure):
    """Create a new figure. This will automatically be set as the current
    working figure (returned by ``vpl.gcf()``).

    :param name: The window title, defaults to 'vtk figure'.
    :type name: str, optional

    """

    def __init__(self, name=""):
        super().__init__(name)

    def show(self, block=True):
        if self.renWin.GetOffScreenRendering():
            # Showing a renWin with off screen rendering will hang indefinitely.
            # Bizarrely, turning it off isn't enough - the renWin must be
            # completely replaced.
            self.on_close()
        self._connect_renderer()
        self.iren.SetRenderWindow(self.renWin)
        self.iren.Initialize()
        self.iren.SetInteractorStyle(self.style)
        # The iren stuff resets the window name - this puts it back.
        self.window_name = self._window_name
        self.renWin.Render()
        if block:
            self._start_interactive()
        super().show(block)

    def render(self):
        self._connect_renderer()
        self.renWin.Render()

    def _start_interactive(self):
        self._flush_stdout()
        self.iren.Start()
        self.on_close()

    @nuts_and_bolts.init_when_called
    def renWin(self):
        renWin = vtk.vtkRenderWindow()
        renWin.SetWindowName(self._window_name)
        return renWin

    @nuts_and_bolts.init_when_called
    def iren(self):
        iren = vtk.vtkRenderWindowInteractor()
        iren.SetInteractorStyle(self.style)
        return iren

    def close(self):
        if hasattr(self, "renWin"):
            self.renWin.Finalize()
        super().close()
        self.on_close()

    def on_close(self):
        self._disconnect_renderer()
        if hasattr(self, "_iren"):
            self.iren.SetRenderWindow(None)
        del self.renWin
        del self.iren

    def _prep_for_screenshot(self, off_screen=False):
        BaseFigure._prep_for_screenshot(self, off_screen)
        self.renWin.SetOffScreenRendering(off_screen)
        self.render()

    _window_name = ""

    @property
    def window_name(self):
        if hasattr(self, "_renWin"):
            return self.renWin.GetWindowName()
        return self._window_name

    @window_name.setter
    def window_name(self, window_name):
        if hasattr(self, "_renWin"):
            self.renWin.SetWindowName(window_name)
        self._window_name = window_name


if __name__ == "__main__":
    Figure._abc_assert_no_abstract_methods()
    import vtkplotlib as vpl

    self = vpl.figure("a normal vtk figure")

    # vpl.plot(np.random.uniform(-10, 10, (20, 3)))

    direction = np.array([1, 0, 0])
    vpl.quiver(np.array([0, 0, 0]), direction)
    vpl.view(camera_direction=direction)
    vpl.reset_camera()

    # vpl.save_fig(Path.home() / "img.jpg", 1080)

    self.show()
