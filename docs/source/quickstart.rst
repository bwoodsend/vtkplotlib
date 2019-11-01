Introduction
======================================



.. image:: python_versions.svg


A simple library to make 3D graphics using easy. Built on top of VTK. Whilst
VTK is a very versatile library, it still only has a rather low level API. Even the
simplest examples require the construction and linking of a large number of
complicated internal components. This and other factors make writing in it slow
and painful. This library seeks to overcome that by wrapping the all ugliness
into numpy friendly functions to create a 3D equivalent of matplotlib. All the
VTK components/functionality are still accessible but by default are already
setup for you.

Key features
------------

* Clean and easy to install.
* Takes advantage of VTK's lesser known numpy support so that data can be efficiently copied by reference between numpy and VTK making it much faster than most of the VTK examples you'll find online.
* Has direct support for STL plotting.
* Can be embedded seamlessly into `PyQt5`_ applications.
* Is freezable with `pyinstaller`_.


Requirements for installing:
------------------------------------------------------------------------------

 - `numpy`_
 - `pathlib2`_
 - `matplotlib`_
 - `vtk`_
 - `future`_

There is no VTK version for Windows users with python 2.7 on PyPi. But you can
get a .whl from `here <https://www.lfd.uci.edu/~gohlke/pythonlibs/#vtk>`_.



Installation:
------------------------------------------------------------------------------

To install run the following into shell/bash/terminal. The mandatory dependencies
will installed automatically.

.. code-block:: shell

    pip install git+https://github.com/bwoodsend/vtkplotlib.git



Optional requirements:
------------------------------------------------------------------------------

Some features require you to install the following:

 - `numpy-stl`_ or any other STL library if you want to plot STL files. `numpy-stl`_ is my STL library of choice.
 - `PyQt5`_ if you want to include your plots in a larger Qt GUI.
 - `namegenerator`_ for fun.


.. _numpy: http://numpy.org/
.. _matplotlib: http://matplotlib.org/
.. _pathlib2: https://pypi.org/project/pathlib2/
.. _vtk: https://pypi.org/project/vtk/
.. _PyQt5: https://pypi.org/project/PyQt5/
.. _numpy-stl: https://pypi.org/project/numpy-stl/
.. _future: https://pypi.org/project/future/
.. _pyinstaller: https://www.pyinstaller.org/
.. _namegenerator: https://pypi.org/project/namegenerator/



Quickstart:
------------------------------------------------------------------------------




Scatter plots:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


.. code-block:: python

    import vtkplotlib as vpl
    import numpy as np

    # In vtkplotlib coordinates are always expressed as numpy arrays with shape
    # (3,) or (n, 3) or (..., 3).
    # Create 30 random points.
    points = np.random.uniform(-10, 10, (30, 3))

    # Plot the points as spheres.
    vpl.scatter(points)

    # Show the plot.
    vpl.show()

A window should open with lots of white sphere's in it.

You can add some color using the color argument.

Colors can be assigned to all the balls using rgb

.. code-block:: python

    vpl.scatter(points, color=(.3, .8, .8))
    vpl.show()


or rgba

.. code-block:: python

    vpl.scatter(points, color=(.3, .8, .8, .2))
    vpl.show()


or using any of matplotlib's named colors using strings.

.. code-block:: python

    vpl.scatter(points, color="r")
    vpl.show()

See matplotlib or ``vpl.colors.mpl_colors`` for a full list of available colors.


Or colors can be given per point

.. code-block:: python

    colors = np.random.random(points.shape)
    vpl.scatter(points, color=colors)
    vpl.show()




Line plots:
^^^^^^^^^^^^^^^^^^^^^^^^


.. code-block:: python

    import vtkplotlib as vpl
    import numpy as np

    # Create some kind of wiggly shape
    # use ``vpl.zip_axes`` to combine (x, y, z) axes
    t = np.linspace(0, 2 * np.pi, 300)
    points = vpl.zip_axes(np.cos(2 * t),
                          np.sin(3 * t),
                          np.cos(5 * t) * np.sin(7 *t))

    # Plot a line
    vpl.plot(points,
             color="green",
             line_width=3)

    vpl.show()


For plotting a polygon you can use join_ends=True to join the last point with
the first.

.. code-block:: python

    # Create the corners of an octagon
    t = np.arange(0, 1, 1 / 8) *  2 * np.pi
    points = vpl.zip_axes(np.cos(t), np.sin(t), 0)

    # Plot them
    vpl.plot(points,
             join_ends=True)

    vpl.show()




Mesh plots:
^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: vtkplotlib.plots.MeshPlot.MeshPlot
    :noindex:


...............................
Figure managing:
...............................


There are two main basic types in vtkplotlib.

 - Figures are the window you plot into.
 - Plots are the physical objects that go in the figures.

In all the previous examples the figure has been handled automatically. For more
complex scenarios you may need to handle the figures yourself. The following
demonstrates the figure handling functions.

.. code-block:: python

    import vtkplotlib as vpl
    import numpy as np

    # You can create a figure explicitly using figure()
    fig = vpl.figure("Your Figure Title Here")

    # Creating a figure automatically sets it as the current working figure
    # You can get the current figure using gcf()
    vpl.gcf() is fig # Should be True

    # If a figure hadn't been explicitly created using figure() then gcf()
    # would have created one. If gcf() had also not been called here then
    # the plotting further down will have internally called gcf().

    # A figure's properties can be edited directly
    fig.background_color = "dark green"
    fig.window_name = "A New Window Title"


    points = np.random.uniform(-10, 10, (2, 3))

    # To add to a figure you can either:

    # 1) Let it automatically add to the whichever figure gcf() returns
    vpl.scatter(points[0], color="r")

    # 2) Explicitly give it a figure to add to
    vpl.scatter(points[1], radius=2, fig=fig)

    # 3) Or pass fig=None to prevent it being added then add it later
    arrow = vpl.arrow(points[0], points[1], color="g", fig=None)
    fig += arrow
    # fig.add_plot(arrow) also does the same thing


    # Finally when your ready to view the plot call show. Like before you can
    # do this one of several ways
    # 1) fig.show()
    # 2) vpl.show() # equivalent to gcf().show()
    # 3) vpl.show(fig=fig)

    fig.show() # The program will wait here until the user closes the window.


    # Once a figure is shown it is gets placed in `vpl.figure_history` which
    # stores recent figures. The default maximum number of figures is two. For
    # convenience whilst console bashing, you can retrieve the last figure.
    # But it will no longer be the current working figure.

    vpl.figure_history[-1] is fig # Should be True
    fig is vpl.gcf() # Should be False

    # A figure can be reshown indefinitely and should be exactly as you left it
    # when it was closed.
    fig.show()



..
    ...............................
    Using multiple figures:
    ...............................

    If you need multiple figures open at once you can do this.

    .. code-block:: python

        import vtkplotlib as vpl

        # The auto figure setting is just going to get in the way. To counter this
        # just switch it off.
        vpl.auto_figure(False)

        # Now gcf() will not create new figures and always return None. New plots
        # will not automatically add themselves to figures.

        # Create 3 labelled figures
        figures = []
        for i in range(1, 4):
            figures.append(vpl.figure("Figure {}".format(i)))


        # A plot can be added to multiple figures
        ball = vpl.scatter([0, 0, 0])
        for figure in figures:
            figure += ball


        # Or a different plot for each figure
        for figure in figures:
            vpl.scatter(np.ones(3), color=np.random.random(3), fig=figure)


        # Show all plots
        for figure in figures:
            # By default show() blocks until the window has been closed again. This
            # can be overridden using the following.
            figure.show(block=False)

        # Calling show(block=False) doesn't enable user interactivity. If you try
        # to click on the windows now they won't respond. To make the windows
        # responsive call show once more without using block=False.
        figure = figures[-1]
            # This causes the program to block here whilst it monitors the windows.
            # VTK's 'monitor windows' function is global i.e it doesn't matter which
            # figure calls it and it affects any and all windows that are open.
        print("showing", figure.window_name)
        figure.show()




