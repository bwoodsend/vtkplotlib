# -*- coding: utf-8 -*-
# =============================================================================
# Created on 13:58
#
# @author: Brénainn
#
# interactive.py
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

# language=rst
"""
***********
Interactive
***********

The ``interactive`` submodule provides methods to handle user-interactivity such
as mouse clicking, keyboard pressing, or timer based events. This submodule is
named ``vtkplotlib.interactive`` but also goes by the alias ``vtkplotlib.i``.

This mini tutorial works from the bottom up. Starting with how raw, low-level
VTK interaction works, then progressively moving towards quicker, more
integrated vtkplotlib methods. If you're feeling lazy, you may want to read this
backwards.

.. versionadded:: 1.4.0

=========
Reference
=========

Some of the classes and methods in this submodule have their own reference pages
which can be accessed below. You are recommended, however, to read through this
page before consulting them.

.. toctree::

    pick
    super_callbacks
    OnClick
    lookup_example

=============
Events in VTK
=============

Interaction in VTK follows a similar model to those of GUI frameworks such as
`PyQt5`_ or `wxPython`_, or web frameworks. For the benefit of those who aren't
familiar with either, you define a *callback* function which may take some kind
of *event* information object as an argument:

.. code-block:: python

    def run_me_when_x_happens(event_info):
        [respond to event]

Then register the callback function along with exactly what kind of user action
you want to capture.

**In VTK**, callback functions are referred to as *observers* and always take
two arguments:

* The **invoker**, which is whichever `vtkObject`_ triggered the event.
* And the **event_name** - the type of event, such as `"KeyPressEvent"` as a string.

| The **invoker** is almost always the `vtkInteractorStyle`_, which can be found
  in vtkplotlib at :attr:`vtkplotlib.figure.style`.
| Information about the event is accessed through the
  `vtkRenderWindowInteractor`_, found at :attr:`vtkplotlib.figure.iren`.
  (The arguments to the callback function aren't particularly helpful.)
| And the registering of a new event call is done using
  ``invoker.AddObserver(event_name, callback)``.


===============
Minimal Example
===============

The following is an entry-level example which captures the user's left mouse
clicks and prints them:

.. code-block:: python

    import vtkplotlib as vpl

    # Set up a figure.
    fig = vpl.figure()
    # With some stuff in it.
    vpl.quick_test_plot()

    # Define a function to be run on left mouse click.
    def callback(invoker, event_name):
        # These will always be true. Just for demonstration purposes.
        assert invoker is fig.style
        assert event_name == "LeftButtonPressEvent"

        # Respond to the click. fig.iren.GetEventPosition() tells us where (in
        # 2D) the click happened. Converting to 3D is explained later...
        print("You clicked at", fig.iren.GetEventPosition())

        # Call the original behaviour. Otherwise left clicking will cease to do
        # what it used to do. i.e. rotate the camera. Again, explained later...
        vpl.i.call_super_callback()

    # Register the (event-type, callback) pair with `fig.style`.
    fig.style.AddObserver("LeftButtonPressEvent", callback)

    # Then show. `vpl.show()` would also work.
    fig.show()

This can be modified to print right mouse clicks, mouse releases, keyboard
presses, etc, by changing the **event_name** ``'LeftButtonPressEvent'`` to
a different event name. See `Event Types`_ for all events available.

.. note::

    IPython buffers stdout in a way that doesn't play well with VTK's event
    loop. This means that there may be a substantial delay between ``print()``
    being called and the output appearing on the screen. To get around this,
    instead run interactive VTK examples from shell.

    You can do this very lazily using ``pip install pyperclip``, then copy the
    code-block to clipboard then, run ``python -m pyperclip --paste | python``.


===========
Event Types
===========

Valid **event_name**\\ s are listed in ``vtkplotlib.interactive.vtkCommands``.
There are quite a lot of them. Rather than try to explain what each and every
one does, let me show you.

.. code-block:: python

    # Same setup as before...
    import vtkplotlib as vpl
    fig = vpl.figure()
    vpl.quick_test_plot()

    # Define a callback which prints the event_name.
    def print_event_callback(invoker, event_name):
        print(event_name, "happened at", fig.iren.GetEventPosition())
        vpl.i.call_super_callback()

    # Attach it to every available event name.
    for event_name in vpl.i.vtkCommands:
        fig.style.AddObserver(event_name, print_event_callback)

    fig.show()

If you're unsure what the event you want to capture is called, simply run this
example. You may notice that you can't get all the event names under
vtkCommands. This can be due to any of:

* The event is not applicable to the `vtkInteractorStyle`_. These events are
  not covered here.
* The event requires special hardware you don't have, such as
  *FifthButtonPressEvent* which requires a mouse with five buttons, or
  *PinchEvent* which requires a touch screen.
* The event is bizarrely specific e.g. *WindowSupportsOpenGLEvent*.


==================================
Getting Information About an Event
==================================

We know if a user clicked on something. Now you want to know where they clicked.
And what they clicked on. This is all done using :meth:`pick` (see
:ref:`pick:Pick`).

================
Super Callbacks?
================

What is this :meth:`call_super_callback` function that's in all the examples?
The answer is best explained by omitting it. Try the `Minimal Example`_ again
but remove the ``vpl.i.call_super_callback()``, then left-click-and-drag rotate
the screen.

You should see that our custom callback function still works but the original
behaviour of rotating the camera doesn't. By adding a
callback to *LeftButtonPressEvent* we have inadvertently knocked out the
pre-existing behaviour, which was ``fig.style.OnLeftButtonDown()``.

The typical way around this in other event driven frameworks like `PyQt5`_ is
overloading methods and inheriting the previous behaviour. e.g.

.. code-block:: python

    class CustomInteractionStyle(vtk.vtkInteractorStyle):
        def OnLeftClickDown(self):
            [custom behaviour here]
            # Call original behaviour using `super()`.
            super().OnLeftClickDown()

In Python you can almost always do this. But VTK is written in C++ and in C++
you must explicitly declare a method as *virtual* to allow this (which VTK
didn't). Instead we have to do it by hand. i.e. Add
``fig.style.OnLeftButtonDown()`` to our callbacks for *LeftButtonPressEvent*.

To help map event names to default callbacks, vtkplotlib provides the methods
:meth:`get_super_callback` and :meth:`call_super_callback` which respectively
find and call the original callbacks for you. Like Python's builtin
:meth:`super` function, these methods can't be called anywhere. They must be
called inside of a function taking a `vtkObject`_ and a string event name as its
arguments.


"""

from ._interactive import (
    pick, get_super_callback, call_super_callback,
    null_super_callback, SuperError, vtkCommands, OnClick
) # yapf:disable
