.. vtkplotlib documentation master file, created by
   sphinx-quickstart on Tue Aug  6 00:07:07 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to vtkplotlib's documentation!
======================================

..
    .. toctree::
       :maxdepth: 2
       :caption: Contents:




A simple library to make 3D graphics using VTK easy. VTK is a very versatile 
library but you have to do a lot of the construction yourself. This and many 
other factors make writing in it very slow and frustrating. This library seeks
to overcome that by wrapping the all ugly bits into numpy friendly functions to
create a 3D equivalent of matplotlib. It also takes advantage of VTK's lesser 
known numpy support so that data can be more efficiently passed between numpy
and VTK than most of the VTK examples you'll find online.


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

 `pip install git+https://github.com/bwoodsend/vtkplotlib.git`



Optional requirements:
------------------------------------------------------------------------------

Some features require you to install the following:

 - `numpy-stl`_ or any other STL library if you want to plot STL files. `numpy-stl`_ is my STL library of choice.
 - `PyQt5`_ if you want to include your plots in a GUI.
 

.. _numpy: http://numpy.org/
.. _matplotlib: http://matplotlib.org/
.. _pathlib2: https://pypi.org/project/pathlib2/
.. _vtk: https://pypi.org/project/vtk/
.. _PyQt5: https://pypi.org/project/PyQt5/
.. _numpy-stl: https://pypi.org/project/numpy-stl/
.. _future: https://pypi.org/project/future/



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
    
See matplotlib or vpl.colors.mpl_colors for a full list of available colors.


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
    t = np.linspace(0, 2 * np.pi, 300)
    points = np.array([np.cos(2 * t),
                       np.sin(3 * t),
                       np.cos(5 * t) * np.sin(7 *t)]).T
    
    # Plot a line 
    vpl.plot(points,
             color="green",
             line_width=3)
    
    vpl.show()


For plotting a polygon you can use join_ends=True to join the last point with
the first.

.. code-block:: python

    # Create the corners of an octogon
    t = np.arange(0, 1, 1 / 8) *  2 * np.pi
    points = np.array([np.cos(t),
                       np.sin(t),
                       np.zeros_like(t)]).T
    
    # Plot them
    vpl.plot(points,
             join_ends=True)
    
    vpl.show()




Mesh plots:
^^^^^^^^^^^^^^^^^^^^^^^

To plot STL files you will need some kind of STL reader library. If you don't 
have one then get this one `numpy-stl`_. Their Mesh class can be passed 
directly to vpl.mesh_plot.

The following example assumes you have installed `numpy-stl`_. 

.. code-block:: python
    
    import vtkplotlib as vpl
    from stl.mesh import Mesh

    # path = "if you have an STL file then put it's path here."
    # Otherwise vtkplotlib comes with a small STL file for demos/testing.
    path = vpl.data.get_rabbit_stl()
    
    # Read the STL using numpy-stl
    mesh = Mesh.from_file(path)
        
    # Plot the mesh
    vpl.mesh_plot(mesh)

    # Show the figure
    vpl.show()



Unfortunately there are far too many mesh/STL libraries/classes out there to
support them all. To overcome this as best we can, mesh_plot has a flexible
constructor which accepts any of the following.


1.  Some kind of mesh class that has form 2) stored in mesh.vectors. 
    For example numpy-stl's stl.mesh.Mesh or pymesh's pymesh.stl.Stl

    
2.   An np.array with shape (n, 3, 3) in the form:

    .. code-block:: python
    
       np.array([[[x, y, z],  # corner 0  \
                  [x, y, z],  # corner 1  | triangle 0
                  [x, y, z]], # corner 2  /
                 ...
                 [[x, y, z],  # corner 0  \
                  [x, y, z],  # corner 1  | triangle n-1
                  [x, y, z]], # corner 2  /
                ])
    
    
    Note it's not uncommon to have arrays of shape (n, 3, 4) or (n, 4, 3) 
    where the additional entries' meanings are usually irrelevant (often to
    represent scalars but as STL has no color this is always uniform). Hence
    to support mesh classes that have these, these arrays are allowed and the
    extra entries are ignored.
        
    
3.  An np.array with shape (k, 3) of (usually unique) vertices in the form:
    
    .. code-block:: python
        
        np.array([[x, y, z],
                  [x, y, z],
                  ...
                  [x, y, z],
                  [x, y, z],
                  ])
    
    And a second argument of an np.array of integers with shape (n, 3) of point
    args in the form
    
    .. code-block:: python
    
        np.array([[i, j, k],  # triangle 0
                  ...
                  [i, j, k],  # triangle n-1
                  ])
    
    where i, j, k are the indices of the points (in the vertices array) 
    representing each corner of a triangle.
    
    Note that this form can be (and is) easily converted to form 2) using
    
    .. code-block:: python
    
        vertices = unique_vertices[point_args]



Hopefully this will cover most of the cases. If you are using or have written
an STL library that you want supported then let me know. If it's numpy based
then it's probably only a few extra lines to support.



.............................
Mesh plotting with scalars:
.............................


To create a heat map like image use the 'scalars' or 'tri_scalars' options.


To use 'scalars':

.. code-block:: python

    import vtkplotlib as vpl
    from stl.mesh import Mesh

    # Open an STL as before
    path = vpl.data.get_rabbit_stl()
    mesh = Mesh.from_file(path)
    
    # Plot it with the z values as the scalars. scalars is 'per vertex' or 1
    # value for each corner of each triangle and should have shape (n, 3).
    plot = vpl.mesh_plot(mesh, scalars=mesh.z)
    
    # Optionally the plot created by mesh_plot can be passed to color_bar
    vpl.color_bar(plot, "Heights")
    
    vpl.show()
    

To use 'tri_scalars':

.. code-block:: python

    import vtkplotlib as vpl
    from stl.mesh import Mesh
    import numpy as np

    # Open an STL as before
    path = vpl.data.get_rabbit_stl()
    mesh = Mesh.from_file(path)

    # tri_scalars is one value per triangle
    # Create some scalars showing "how far upwards" each triangle is facing
    tri_scalars = np.inner(mesh.units, np.array([0, 0, 1]))
    
    vpl.mesh_plot(mesh, tri_scalars=tri_scalars)
    
    vpl.show()



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
    
    # Creating a figure automatcally sets it as the current working figure
    # You can get the current figure using gcf()
    vpl.gcf() is fig # Should be True
    
    # If a figure hadn't been explicitly created using figure() then gcf()
    # would have created one. If gcf() had also not been called here then
    # the plotting further down will have called gcf().
    
    # A figure's properties can be editted directly
    fig.background_color = "orange"
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
    
    fig.show() # The program will wait here until th user closes the window.
    
    
Once a figure is shown it is deleted. A new figure must be used for future
plots. Note that calling show on a figure that has already been shown 
causes a crash. I've tried to overcome this but with no success. Until 
someone finds a way round this we'll just have to accept figures are 
single use.

..
    ...............................
    Using multiple figures:
    ...............................
    
    If you need multiple figures open at once you can do this.
    
    .. code-block:: python
        
        import vtkplotlib as vpl
        
        # The auto figure setting is just going to get in the way. To counter this
        # just switch it off.
        vpl.set_auto_fig(False)
        
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
            # can be overidden using the following.
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
        
        
        