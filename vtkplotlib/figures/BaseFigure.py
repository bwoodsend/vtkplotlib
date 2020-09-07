# -*- coding: utf-8 -*-
# =============================================================================
# Created on Sat Aug  3 13:00:11 2019
#
# @author: Brénainn Woodsend
#
#
# BaseFigure.py provides a base class for vpl figures.
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

from __future__ import print_function
from builtins import super

import numpy as np
import sys
import abc

from .figure_manager import reset_camera, scf, gcf
from vtkplotlib._get_vtk import vtk
from vtkplotlib import _vtk_errors, nuts_and_bolts


def abstract_property(func):
    if sys.version_info > (3, 3):
        return property(abc.abstractmethod(func))
    else:
        return abc.abstractproperty(func)


def _abc_assert_not_abstract_method(name, method):
    if isinstance(method, property):
        _abc_assert_not_abstract_method(name + " getter", method.fget)
        _abc_assert_not_abstract_method(name + " setter", method.fset)
        _abc_assert_not_abstract_method(name + " deleter", method.fdel)
        return

    if getattr(method, "__isabstractmethod__", False):
        raise Exception(name + " is abstract and has not been re-implemented.")


class BaseFigure(object):

    def __init__(self, name=""):
        scf(self)

        self.renderer = vtk.vtkRenderer()

        # Just for fun
        if name:
            self.window_name = name
        else:
            try:
                import namegenerator
                self.window_name = namegenerator.gen().replace("-", " ").title()
            except ImportError:
                self.window_name = "VTK figure"
        self.plots = set()

        self.background_color = "light grey"

    #################  Create core VTK components  ############################

    @property
    def camera(self):
        return self.renderer.GetActiveCamera()

    @camera.setter
    def camera(self, camera):
        self.renderer.SetActiveCamera(camera)

    @abstract_property
    def iren(self):
        pass

    @abstract_property
    def renWin(self):
        pass

    @nuts_and_bolts.init_when_called
    def style(self):
        return vtk.vtkInteractorStyleTrackballCamera()

    @style.setter
    def style(self, style):
        self._style = style
        if hasattr(self, "_iren"):
            self.iren.SetInteractorStyle(style)

    ##########  Connecting core VTK components  ################################

    def _connect_renderer(self):
        self.renWin.AddRenderer(self.renderer)
        self.style.SetCurrentRenderer(self.renderer)
        _vtk_errors.handler.attach(self.renderer)

    def _disconnect_renderer(self):
        if self.renderer.GetRenderWindow():
            self.renWin.RemoveRenderer(self.renderer)
        self.style.SetCurrentRenderer(None)

    ########## Opening, closing, updating the figure  ##########################

    @abc.abstractmethod
    def show(self, block=True):
        # Camera only gets reset automatically the first time self.show() is
        # called.
        self._reset_camera = False

        if block and gcf() is self:
            scf(None)

    @abc.abstractmethod
    def close(self):
        if self is gcf(False):
            scf(None)

    def update(self):
        self._connect_renderer()
        self.renWin.Render()

    ########  Adding and removing plot elements to the figure  #################

    def _add_actor(self, actor):
        self.renderer.AddActor(actor)

    def _remove_actor(self, actor):
        """vtk automatically checks if the actor is there and silently skips it
        if it isn't. No need to check it beforehand.
        """
        self.renderer.RemoveActor(actor)

    def add_plot(self, plot):
        if isinstance(plot, np.ndarray) and plot.dtype == object:
            [self.add_plot(i) for i in plot.flat]
            return
        if isinstance(plot, vtk.vtkActor):
            self._add_actor(plot)
            return
        if plot not in self.plots:
            self.plots.add(plot)
        self._add_actor(plot.actor)

    def remove_plot(self, plot):
        if isinstance(plot, np.ndarray) and plot.dtype == object:
            [self.remove_plot(i) for i in plot.flat]
            return
        if isinstance(plot, vtk.vtkActor):
            self._remove_actor(plot)
        if plot in self.plots:
            self.plots.remove(plot)
        self._remove_actor(plot.actor)

    def __iadd__(self, plot):
        self.add_plot(plot)
        return self

    def __isub__(self, plot):
        self.remove_plot(plot)
        return self

    #########  Configuring the figure  #########################################

    @property
    def render_size(self):
        """Get the render image size (width, height) in pixels. Note that if the
        figure is a QtFigure then the setter will be constantly overridden by
        the parent widget's resizing."""
        return self.renWin.GetSize()

    @render_size.setter
    def render_size(self, size):
        self.renWin.SetSize(*size)

    @property
    def background_color(self):
        return self.renderer.GetBackground()

    @background_color.setter
    def background_color(self, color):
        from vtkplotlib.colors import as_rgb_a

        color, opacity = as_rgb_a(color)
        if color is not None:
            self.renderer.SetBackground(*color)
        if opacity is not None:
            self.renderer.SetBackgroundAlpha(opacity)

    #########  figure_manager.py methods  #####################################

    _reset_camera = True

    def reset_camera(self):
        return reset_camera(self)

    @abc.abstractmethod
    def _prep_for_screenshot(self, off_screen=False):
        if self._reset_camera:
            self.reset_camera()
            self._reset_camera = False

    ############  some other bits  #############################################

    @classmethod
    def _abc_assert_no_abstract_methods(cls):
        """Ideally this class would be an `abc.ABC` but in order for multiple
        inheritance to work (used by the QFigure which also inherits QWidget)
        we can't use metaclasses.
        """
        # Don't use `vars(cls)` here as inherited methods are only in the
        # parent class dict. i.e this test would be useless.
        for name in dir(cls):
            _abc_assert_not_abstract_method(name, getattr(cls, name))

    @staticmethod
    def _flush_stdout():
        """Try and force the console to finish displaying any preceding print
        statements before VTK start is called and blocks everything. Rather
        limited success."""
        try:
            # python 2 doesn't have flush
            print(end="", flush=True)
        except TypeError:
            pass
        sys.stdout.flush()
        for attr in ("buffer", "_buffer"):
            if hasattr(sys.stdout, attr):
                getattr(sys.stdout, attr).flush()


if __name__ == "__main__":
    pass
