# -*- coding: utf-8 -*-
# =============================================================================
# Created on Mon Jun  1 07:19:35 2020
#
# @author: Brénainn Woodsend
#
# _interactive.py
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
vtkCommands = [
    i for (i, j) in vars(vtk.vtkCommand).items() if isinstance(j, int)
]


def null_super_callback():
    """A placeholder callback for when an event doesn't have a parent callback
    which needs calling. Calling this function has no effect."""
    pass


class SuperError(RuntimeError):
    def __str__(self):
        return ("Couldn't determine the event `invoker and `event_name`. "
                "Ensure you are calling %s() from a callback which is "
                "receiving a vtkObject and str as its arguments." % self.args)


def get_super_callback(invoker=None, event_name=None):
    if invoker is None or event_name is None:
        # Try to guess the arguments that would have been provided.
        # This uses the same frame hack that future uses to mimick super() in
        # Python 2.
        _invoker, _event_name = invoker, event_name

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
            raise SuperError(caller.f_code.co_name)

        # Allow explicitly provided arguments to override those found.
        invoker, event_name = _invoker or invoker, _event_name or event_name

    # VTK has some rather loose naming rules for callbacks and event names.
    name = "On" + _re.match("(.*)Event", event_name).group(1)
    if hasattr(invoker, name):
        return getattr(invoker, name)
    name = name.replace("Press", "Down").replace("Release", "Up")
    if hasattr(invoker, name):
        return getattr(invoker, name)

    # Not all callbacks have a super event.
    return null_super_callback


def call_super_callback(invoker=None, event_name=None):
    get_super_callback(invoker, event_name)()


def _actor_collection(actors, collection=None):
    if collection is None:
        collection = vtk.vtkActorCollection()
    for actor in actors:
        collection.AddItem(getattr(actor, "actor", actor))
    return collection


class pick(object):

    def __init__(self, style):
        style = getattr(style, "style", style)
        if not isinstance(style, vtk.vtkInteractorStyle):
            raise TypeError(
                "pick requires either a figure or a or a vtkInteractorStyle")

        self.style = style
        self.picker = vtk.vtkPropPicker()
        self.update()

    def update(self):
        iren = self.style.GetInteractor()
        if iren.GetEnabled():
            # Be careful not to call GetEventPosition() when VTK's app isn't
            # running. Otherwise this will block indefinitely.
            self.point_2D = iren.GetEventPosition()

    @property
    def point_2D(self):
        """The 2D ``(horizontal, vertical)`` coordinates in pixels where the
        event happened. ``(0, 0)`` is the left lower corner of the window. """
        return self.picker.GetSelectionPoint()

    @point_2D.setter
    def point_2D(self, point):
        if len(point) == 2:
            self.picker.Pick(point[0], point[1], 0,
                             self.style.GetCurrentRenderer())
        else:
            self.picker.Pick(point[0], point[1],
                             self.style.GetCurrentRenderer())

    @property
    def point(self):
        return self.picker.GetPickPosition()

    @property
    def actor(self):
        return self.picker.GetActor()

    @property
    def actor_2D(self):
        return self.picker.GetActor2D()

    @property
    def prop_3D(self):
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

    KEYS = sorted(
        key for (key, val) in locals().items() if isinstance(val, property))


class CursorTracker(object):

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
        [
            self.labels.extend(i)
            for i in zip(self.text_labels[1:], self.coord_labels)
        ]

        [
            label.setFrameStyle(QtWidgets.QFrame.Panel
                                | QtWidgets.QFrame.Sunken)
            for label in self.coord_labels
        ]

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
        picker = pick(style)

        if picker.actor is None:
            self.set_no_cursor()
        else:
            self.set_cursor_position(picker.point)
        call_super_callback()


def _mini_vtk_repr(obj):
    if isinstance(obj, vtk.vtkObject):
        return object.__repr__(obj)
    return repr(obj)


def _default_click_event(pick):
    print(pick)


# Get all the supported mouse button types (e.g. Left, Right, Middle, ...) by
# iterating through `dir(vtkCommands)`. Note that `re.fullmatch()` doesn't
# exist in python 2 - hence the "\A...\Z" in the regex.
_mouse_buttons = set(
    i.group(1) for i in
    map(_re.compile(r"\A(\w+)ButtonPressEvent\Z").match, vtkCommands)
    if i is not None
) # yapf: disable


class OnClick(object):
    VALID_BUTTONS = _mouse_buttons

    def __init__(self, button, style, on_click=None, mouse_shift_tolerance=2):
        assert button in self.VALID_BUTTONS
        self.button = button
        self.style = getattr(style, "style", style)
        self.mouse_shift_tolerance = mouse_shift_tolerance
        self._click_location = None
        self.on_click = on_click or _default_click_event

        style.AddObserver(self.button + "ButtonPressEvent", self._press_cb)
        style.AddObserver(self.button + "ButtonReleaseEvent", self._release_cb)
        style.AddObserver("MouseMoveEvent", self._mouse_move_cb)

    def _press_cb(self, invoker, name):
        vpl.interactive.call_super_callback()
        self._click_location = invoker.GetInteractor().GetEventPosition()

    def _clicks_are_equal(self, point_0, point_1):
        shift_sqr = sum((i - j)**2 for (i, j) in zip(point_0, point_1))
        return shift_sqr <= self.mouse_shift_tolerance**2

    def _release_cb(self, invoker, name):
        vpl.interactive.call_super_callback()
        if self._click_location is None:
            return
        picker = vpl.interactive.pick(invoker)
        if picker.actor is None:
            return
        if self._clicks_are_equal(self._click_location, picker.point_2D):
            self.on_click(picker)

    def _mouse_move_cb(self, invoker, name):
        if self._click_location:
            point_2D = invoker.GetInteractor().GetEventPosition()
            if self._clicks_are_equal(self._click_location, point_2D):
                return
            self._click_location = None
        # Only calling the super event with the mouse button down (which rotates
        # the model for left click) when we are sure that this click is not
        # meant to place a marker reduces the slight jolt when you click on with
        # a sensitive mouse. Move this line to the top of this method to see
        # what I mean.
        vpl.interactive.call_super_callback()


if __name__ == "__main__":
    import vtkplotlib as vpl

    fig = vpl.QtFigure2()
    style = fig.style

    tracker = CursorTracker(fig)
    balls = vpl.quick_test_plot()
    rabbit = vpl.mesh_plot(vpl.data.get_rabbit_stl())
    rabbit.vertices -= [i.mean() for i in vpl.unzip_axes(rabbit.vertices)]
    rabbit.vertices /= 5
    text = vpl.text("text")
    collection = _actor_collection(balls)
    _actor_collection(balls, fig.iren.GetPicker().GetPickList())

    vpl.show()
