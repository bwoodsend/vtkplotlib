# -*- coding: utf-8 -*-
# =============================================================================
# Created on Mon Jun  1 07:19:35 2020
#
# @author: Brénainn Woodsend
#
# template.py
# What does this file do.
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

#import os, sys
import sys as _sys
#import numpy as np
#from pathlib2 import Path
import re as _re
from vtkplotlib._get_vtk import vtk
vtkCommands = [i for (i, j) in vars(vtk.vtkCommand).items() if isinstance(j, int)]

def null_callback():
    pass

def get_super_callback(invoker=None, event_name=None):
    if invoker is None or event_name is None:
        # Try to guess the arguments that would have been provided.
        # This uses the same frame hack that future uses to mimick super() in
        # Python 2.

        # Find the frame that called either this method or call_super_callback().
        caller = _sys._getframe(0)
        cb_frame = caller.f_back
        if cb_frame.f_code.co_name == "call_super_callback":
            caller = cb_frame
            cb_frame = cb_frame.f_back

        # Guess the arguments by type rather than name.
        names = cb_frame.f_code.co_varnames[:cb_frame.f_code.co_argcount]
        f_args = (cb_frame.f_locals[i] for i in names)
        invoker = None
        for event_name in f_args:
            # This loop is just to bypass any `self` or `cls` 1st arguments.
            if hasattr(invoker, "AddObserver") and isinstance(event_name, str):
                break
            invoker = event_name
        else:
            raise TypeError("Couldn't determine the event `invoker and `event_name`. Ensure you are calling {}() from a callback which is recieving a vtkObject and str as its arguments.".format(caller.f_code.co_name))

    # VTK has some rather loose naming rules for callbacks and event names.
    name = "On" + _re.match("(.*)Event", event_name).group(1)
    if hasattr(invoker, name):
        return getattr(invoker, name)
    name = name.replace("Press", "Down").replace("Release", "Up")
    if hasattr(invoker, name):
        return getattr(invoker, name)

    # Not all callbacks have a super event.
    return null_callback


def call_super_callback(invoker=None, event_name=None):
    get_super_callback(invoker, event_name)()


def _actor_collection(actors, collection=None):
    if collection is None:
        collection = vtk.vtkActorCollection()
    for actor in actors:
        collection.AddItem(getattr(actor, "actor", actor))
    return collection


class pick_point(object):
    def __init__(self, style_or_iren):
        if isinstance(style_or_iren, vtk.vtkRenderWindowInteractor):
            iren = style_or_iren
            style = iren.GetInteractionStyle()
        elif isinstance(style_or_iren, vtk.vtkInteractorStyle):
            style = style_or_iren
            iren = style.GetInteractor()
        else:
            raise TypeError()

        self.style = style
        self.iren = iren
        self.picker = iren.GetPicker()
        self.update()

    def update(self):
        self.point_2d = self.iren.GetEventPosition()

    @property
    def point_2d(self):
        return self.picker.GetSelectionPoint()

    @point_2d.setter
    def point_2d(self, point):
        if len(point) == 2:
            self.picker.Pick(*point, 0, self.style.GetCurrentRenderer())
        else:
            self.picker.Pick(*point, self.style.GetCurrentRenderer())

    @property
    def point(self):
        return self.picker.GetPickPosition()
    @property
    def actor(self):
        return self.picker.GetActor()
    @property
    def actor_2d(self):
        return self.picker.GetActor2D()
    @property
    def prop_3d(self):
        return self.picker.GetProp3D()
    @property
    def view_prop(self):
        return self.picker.GetViewProp()
    @property
    def volume(self):
        return self.picker.GetVolume()

    def __repr__(self):
        return type(self).__name__ + " {\n" +\
            "\n".join("  {}: {}".format(key, _mini_vtk_repr(getattr(self, key))) for key in self.KEYS) +\
            "\n}\n"

    KEYS = sorted(key for (key, val) in locals().items() if isinstance(val, property))


class CursorTrackor(object):
    def __init__(self, fig):
        self.fig = fig
        self.init_labels()

        self.fig.style.AddObserver("MouseMoveEvent", self.mouse_move_cb)

        self.set_no_cursor()

    def init_labels(self):
        from PyQt5 import QtWidgets
        self.text_labels = [QtWidgets.QLabel(i) for i in "Cursor X Y Z".split()]
        self.coord_labels = [QtWidgets.QLabel() for i in range(3)]

        self.labels = [self.text_labels[0]]
        [self.labels.extend(i) for i in zip(self.text_labels[1:], self.coord_labels)]

        [label.setFrameStyle(QtWidgets.QFrame.Panel | QtWidgets.QFrame.Sunken) for label in self.coord_labels]

        layout = QtWidgets.QHBoxLayout()
        layout.addStretch()
        [layout.addWidget(i) for i in self.labels]

        self.fig.vl.addLayout(layout)


    def set_cursor_position(self, position):
        for (label, axis) in zip(self.coord_labels, position):
            label.setText(format(axis, "6.2f"))

    def set_no_cursor(self):
        for label in self.coord_labels:
            label.setText("  --  ")

    def mouse_move_cb(self, style, event_name):
        picker = pick_point(style)

        if picker.actor is None:
            self.set_no_cursor()
        else:
            self.set_cursor_position(picker.point)
        call_super_callback()


def _mini_vtk_repr(obj):
    if isinstance(obj, vtk.vtkObject):
        return type(obj).__name__ + " " + hex(id(obj))
    return repr(obj)


if __name__ == "__main__":
    import vtkplotlib as vpl

    fig = vpl.QtFigure2()
    style = fig.style

    tracker = CursorTrackor(fig)
    balls = vpl.quick_test_plot()
    rabbit = vpl.mesh_plot(vpl.data.get_rabbit_stl())
    rabbit.vertices -= [i.mean() for i in vpl.unzip_axes(rabbit.vertices)]
    rabbit.vertices /= 5
    text = vpl.text("text")
    collection = _actor_collection(balls)
    _actor_collection(balls, fig.iren.GetPicker().GetPickList())

    vpl.show()





