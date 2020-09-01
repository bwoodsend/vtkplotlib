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

import sys as _sys
import re as _re

if _sys.version_info >= (3, 3, 0):
    from collections.abc import Mapping
else:
    from collections import Mapping

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
    """Finds the original VTK callback function for a given event. Like the
    builtin ``super()`` in Python 3.x, this method should be able to find its
    own arguments.

    :param invoker: The `vtkObject`_ you used in ``invoker.AddObserver(..)``, defaults to ``None``.
    :type invoker: `vtkObject`_, optional

    :param event_name: The name of the interaction, defaults to ``None``.
    :type event_name: str, optional

    :return: A method of **invoker** or a dummy :meth:`null_callback` function.
    :rtype: callable

    :raises: :class:`SuperError` if called without (an) argument(s) and the argument(s) couldn't be determined automatically.

    The original callback (if there is one) is always a method of the
    *invoker**. VTK has some rather loose naming rules which make this
    deceptively fiddly.

    If called inside function which takes a `vtkObject`_ and a ``str`` as its
    first two arguments, then :meth:`get_super_callback` will use the values of
    those two arguments as its own arguments. Or, if you provide those
    arguments explicitly, you can call this function anywhere. e.g.

        >>> vpl.i.get_super_callback(fig.style, "MouseMoveEvent")
        <built-in method OnMouseMove of vtkmodules.vtkInteractionStyle.vtkInteractorStyleTrackballCamera object at 0x000000C0AB4B1E88>

    Not all events have parent events. In these cases a dummy function is
    returned. This is also the case for non-existant event types.

        >>> vpl.i.get_super_callback(fig.style, "WindowIsCurrentEvent")
        <function null_super_callback at 0x000000C0AB4ABA68>
        >>> vpl.i.get_super_callback(fig.style, "BlueMoonEvent")
        <function null_super_callback at 0x000000C0AB4ABA68>

    Should you want to, you can also overide the one or both arguments. The
    following will swap the left and right mouse-click functionallities.

    .. code-block:: python

        import vtkplotlib as vpl
        fig = vpl.figure()
        vpl.quick_test_plot()

        def callback(invoker, event_name):
            # Swap left for right and vice-versa.
            if "Left" in event_name:
                swapped = event_name.replace("Left", "Right")
            else:
                swapped = event_name.replace("Right", "Left")

            # Call the callback for the switched event_name.
            vpl.i.call_super_callback(event_name=swapped)

        for event_name in ["LeftButtonPressEvent", "LeftButtonReleaseEvent",
                           "RightButtonPressEvent", "RightButtonReleaseEvent"]:
            fig.style.AddObserver(event_name, callback)

        fig.show()

    """
    if invoker is None or event_name is None:
        # Try to guess the arguments that would have been provided.
        # This uses the same frame hack that future uses to mimic super() in
        # Python 2.
        _invoker, _event_name = invoker, event_name

        # Find the frame that called either this method or call_super_callback().
        # noinspection PyUnresolvedReferences
        caller = _sys._getframe(0)
        cb_frame = caller.f_back

        # If this function has been called by call_super_callback():
        if cb_frame.f_code.co_name == "call_super_callback":
            # Go up another frame to skip the get_super_callback() frame.
            caller = cb_frame
            cb_frame = cb_frame.f_back

        # Guess the arguments by type rather than name.
        names = cb_frame.f_code.co_varnames[:cb_frame.f_code.co_argcount]
        f_args = (cb_frame.f_locals[i] for i in names)
        invoker = None
        for event_name in f_args:
            # This loop is just to bypass any `self` or `cls` 1st arguments.
            # It should break on its 1st or 2nd iteration.
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
    """
    Just runs ``get_super_callback(invoker, event_name)()``. See
    :meth:`get_super_callback`.
    """
    get_super_callback(invoker, event_name)()


def _actor_collection(actors, collection=None):
    if collection is None:
        collection = vtk.vtkActorCollection()
    for actor in actors:
        collection.AddItem(getattr(actor, "actor", actor))
    return collection


class pick(object):
    # language=rst
    """Pick collects information about user interactions into a handy bucket
    class.

    .. code-block:: python

        import vtkplotlib as vpl
        import numpy as np

        # Create a figure.
        fig = vpl.figure()

        # With something semi-interesting in it.
        u, v = np.meshgrid(np.linspace(-10, 10), np.linspace(-10, 10))
        vpl.surface(np.sin(u) * np.sin(v), np.cos(u) * np.sin(v), v, scalars=v)

        def callback(invoker, event_name):
            vpl.i.call_super_callback()

            # Optional, if you're using Python in interactive mode then you can
            # play around with the pick afterwards.
            global pick

            # pick this current event to get a pick object. A pick contains
            # everything VTK has to tell you about the event.
            pick = vpl.i.pick(invoker)

            # To see everything pick has to say, just print it.
            print(pick)

            if pick.actor is None:
                print("Mouse is hovering over background.")
            else:
                print("Mouse is hovering over {} at (x, y, z) = {}."
                      .format(repr(pick.actor), pick.point))

        fig.style.AddObserver("MouseMoveEvent", callback)

        vpl.show()

    The most important properties of a :meth:`pick` are :attr:`pick.point` which
    tells you the 3D coordinates of the event and :attr:`pick.actor` which tells
    you the `vtkActor`_ of the plot under which the event took place.

    """

    def __init__(self, style, from_=None):
        self.style = style
        self.picker = vtk.vtkPropPicker()
        self.update()
        self.from_ = from_

    @property
    def style(self):
        return self._style

    @style.setter
    def style(self, style):
        style = getattr(style, "style", style)
        if not isinstance(style, vtk.vtkInteractorStyle):
            raise TypeError("pick.style should be either a figure or a or a "
                            "vtkInteractorStyle. Got a {}.".format(type(style)))
        self._style = style

    @property
    def from_(self):
        """Limit the :attr:`actor` results to only a set of actors.

        The (writeable) :attr:`from_` attribute allows you restrict the actors
        that can be picked. This can be useful, when placing markers on an
        object, to avoid placing a marker on top of another marker.

        You can set this attribute to an iterable of vtkplotlib plots, an
        iterable of `vtkActor`_\\ s, or a mapping with either plots or actors as
        its keys. On setting this attribute is normalised into the mapping form.
        To disable filtering use either ``del pick.from_`` or ``pick.from_ =
        None``.

        .. code-block:: python

            import vtkplotlib as vpl
            import numpy as np

            fig = vpl.figure()
            ball = vpl.scatter([0, 0, 0], radius=10, color="green")
            text = vpl.text("Click on the green ball", color="black")

            # Create a restricted pick that will only treat clicks on anything
            # other than the ball as it would with clicks on the background.
            pick = vpl.i.pick(fig, from_=[ball])

            def callback(pick):
                if pick.actor is not None:
                    vpl.scatter(pick.point, color="r", fig=fig)
                    text.text = "Now try to click on one of the red balls"

            vpl.i.OnClick("Left", fig, callback, pick=pick)

            fig.show()

        If its not immediately clear what the difference is then remove the
        ``from_=[ball]`` try clicking on a red ball a few times, then rotate the
        camera slightly. You should see that each click creates a new red ball
        on top of the last, creating a tower of balls.

         """
        return self._from_map

    @from_.setter
    def from_(self, from_):
        if from_ is None:
            del self.from_
        else:
            if not isinstance(from_, Mapping):
                from_ = {getattr(i, "actor", i): i for i in from_}
            self.picker.GetPickList().RemoveAllItems()
            _actor_collection(from_, self.picker.GetPickList())
            self._from_map = from_
            self.picker.PickFromListOn()

    @from_.deleter
    def from_(self):
        self._from_map = None
        self.picker.GetPickList().RemoveAllItems()
        self.picker.PickFromListOff()

    @property
    def picked(self):
        """Contains the plot where the event happened. This can be thought of as
         equivalent to ``pick.from_[pick.actor]``. If the :attr:`from_` has not
         been set or the event happened over empty space or over an actor which
         isn't in ``pick.from_`` then the output is None.

         .. code-block:: python

            import vtkplotlib as vpl
            import numpy as np

            fig = vpl.figure()
            spheres = vpl.scatter(np.random.uniform(-30, 30, (50, 3)))
            vpl.text("Click on the spheres")

            def callback(pick):
                sphere = pick.picked
                if sphere is not None:
                    sphere.color = np.random.random(3)

            vpl.i.OnClick("Left", fig, callback, pick=vpl.i.pick(fig, from_=spheres))

            fig.show()

        """
        if (self.actor is not None) and (self._from_map is not None):
            return self._from_map[self.actor]

    def update(self):
        iren = self.style.GetInteractor()
        if iren and iren.GetEnabled():
            # Be careful not to call GetEventPosition() when VTK's app isn't
            # running. Otherwise this will block indefinitely.
            self.point_2D = iren.GetEventPosition()
        return self

    @property
    def point_2D(self):
        """The 2D ``(horizontal, vertical)`` coordinates in pixels where the
        event happened. ``(0, 0)`` is the left lower corner of the window. """
        # For some strange reason GetSelectionPoint() includes a 3rd dimension
        # which is always zero. Get rid of it as it's confusing.
        return self.picker.GetSelectionPoint()[:2]

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
        """The `vtkActor`_ of the plot where the event took place. This
        corresponds to ``plot.actor`` where ``plot`` is the output of any
        vtkplotlib plotting function.

        .. code-block:: python

            import vtkplotlib as vpl
            import numpy as np

            fig = vpl.figure()
            spheres = vpl.scatter(np.random.uniform(-10, 10, (30, 3)))
            vpl.text("Hover the mouse over a sphere")

            def callback(invoker, event_name):
                actor = vpl.i.pick(invoker).actor
                for sphere in spheres:
                    if sphere.actor is actor:
                        sphere.color = "blue"
                    else:
                        sphere.color = "white"
                vpl.i.call_super_callback()
                fig.update()

            fig.style.AddObserver("MouseMoveEvent", callback)

            fig.show()

        """
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
        out = type(self).__name__ + " {\n"
        for key in self.KEYS:
            if key == "from_":
                value = ("NULL - pick.from_ is not set" if self.from_ is None
                         else "%i items" % len(self.from_))
            else:
                value = _mini_vtk_repr(getattr(self, key))
            out += "  %s: %s\n" % (key, value)
        return out + "}\n"

    KEYS = sorted(
        key for (key, val) in locals().items() if isinstance(val, property))


def _mini_vtk_repr(obj):
    """The ``__str__`` method of `vtkObject`_ and its descendants tells you
    everything about it, often recursing to child objects, making it very long.
    This is helpful sometimes but not always. Use Python's default ``__str__``
    in cases where every detail is not desired."""
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

    def __init__(self, button, style, on_click=None, mouse_shift_tolerance=2,
                 pick=None):
        assert button in self.VALID_BUTTONS
        self.button = button
        style = self.style = getattr(style, "style", style)
        self.mouse_shift_tolerance = mouse_shift_tolerance
        self._click_location = None
        self.on_click = on_click or _default_click_event
        self.pick = pick or globals()["pick"](self.style)

        # Only call style.OnMouseMove() if another callback isn't already
        # doing it. This isn't an ideal work around.
        self._super_on_mouse_move = not style.HasObserver("MouseMoveEvent")

        style.AddObserver(self.button + "ButtonPressEvent", self._press_cb)
        style.AddObserver(self.button + "ButtonReleaseEvent", self._release_cb)
        style.AddObserver("MouseMoveEvent", self._mouse_move_cb)

    def _press_cb(self, invoker, name):
        call_super_callback()
        self.pick.update()
        self._click_location = self.pick.point_2D

    def _clicks_are_equal(self, point_0, point_1):
        shift_sqr = sum((i - j)**2 for (i, j) in zip(point_0, point_1))
        return shift_sqr <= self.mouse_shift_tolerance**2

    def _release_cb(self, invoker, name):
        if (self._click_location is not None
                and self.pick.update().actor is not None and
                self._clicks_are_equal(self._click_location, self.pick.point_2D)
                and self.on_click(self.pick)):
            call_super_callback()

    def _mouse_move_cb(self, invoker, name):
        if self._click_location:
            self.pick.update()
            if self._clicks_are_equal(self._click_location, self.pick.point_2D):
                return
            self._click_location = None
        # Only calling the super event with the mouse button down (which rotates
        # the model for left click) when we are sure that this click is not
        # meant to place a marker reduces the slight jolt when you click on with
        # a sensitive mouse. Move the lines below to the top of this method to
        # see what I mean.
        if self._super_on_mouse_move:
            call_super_callback()


if __name__ == "__main__":
    import vtkplotlib as vpl

    fig = vpl.QtFigure2()
    style = fig.style

    balls = vpl.quick_test_plot()
    rabbit = vpl.mesh_plot(vpl.data.get_rabbit_stl())
    rabbit.vertices -= [i.mean() for i in vpl.unzip_axes(rabbit.vertices)]
    rabbit.vertices /= 5
    text = vpl.text("text")

    vpl.show()
