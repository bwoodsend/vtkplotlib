vtkplotlib Figures
==================

Figures are the window that you plot into. This section outlines:

* Their creation.
* General figure management.
* Functions for controlling the camera position.
* Screenshotting the figure contents to a frozen image (file).
* Embedding a figure into PyQt5.

Overview
--------

Some of this is handled automatically. There is a global "current working
figure". This can be accessed using ``vpl.gcf()``. If it doesn't exist then it
is automatically created. Each plot command will add itself to the current working
figure unless explicitly told not to using the `fig` option. Either use
``fig=alternative_figure`` to plot into a different one or ``fig=None`` to not
use any. The figure is shown using ``vpl.show()`` or ``fig.show()``. After the
shown figure is closed the current working figure is deleted.



vtkplotlib.show
---------------

.. autofunction:: vtkplotlib.figures.figure_manager.show


vtkplotlib.figure
-----------------

.. autoclass:: vtkplotlib.figures.figure.Figure


vtkplotlib.gcf
--------------

.. autofunction:: vtkplotlib.figures.figure_manager.gcf


vtkplotlib.scf
--------------

.. autofunction:: vtkplotlib.figures.figure_manager.scf


vtkplotlib.reset_camera
-----------------------

.. autofunction:: vtkplotlib.figures.figure_manager.reset_camera


vtkplotlib.save_fig
-------------------

.. autofunction:: vtkplotlib.figures.figure_manager.save_fig


vtkplotlib.view
---------------

.. autofunction:: vtkplotlib.figures.figure_manager.view


vtkplotlib.close
----------------

.. autofunction:: vtkplotlib.figures.figure_manager.close


vtkplotlib.figure_history
-------------------------

.. autodata:: vtkplotlib._history.figure_history


vtkplotlib.auto_figure
-----------------------

.. autofunction:: vtkplotlib.figures.figure_manager.auto_figure


vtkplotlib.QtFigure
-------------------

.. autoclass:: vtkplotlib.figures.QtFigure.QtFigure


vtkplotlib.QtFigure2
--------------------

.. autoclass:: vtkplotlib.figures.QtGuiFigure.QtFigure2


