Figures
==================

Figures, typically abbreviated to ``fig``, are the window that you plot into.
This section outlines:

* Their creation.
* General figure management.
* Functions for controlling the camera position.
* Screenshotting the figure contents to a frozen image (file).
* Embedding a figure into PyQt5_.

Overview
--------

Some of this is handled automatically. There is a global *current working figure*.
This can be get and set using `gcf()` and `scf(fig) <scf>`. If it doesn't
exist then it is automatically created. Each plot command will add itself to the
current working figure unless explicitly told not by setting ``fig=None`` or
``fig=alternative_fig`` in the plot command. The figure is shown using
`vtkplotlib.show` or ``fig.show()``. After the shown figure is closed it ceases to
be the current working figure but you can use it by referencing it explicitly.
Figures can be reshown indefinitely and should be exactly as you left them on
close.

---------------

show
---------------

.. autofunction:: vtkplotlib.show

-----------------

figure
-----------------

.. autofunction:: vtkplotlib.figure


--------------

gcf
--------------

.. autofunction:: vtkplotlib.gcf


--------------

scf
--------------

.. autofunction:: vtkplotlib.scf


-------------------

screenshot_fig
-------------------

.. autofunction:: vtkplotlib.screenshot_fig


-------------------

save_fig
-------------------

.. autofunction:: vtkplotlib.save_fig


---------------

view
---------------

.. autofunction:: vtkplotlib.view


-----------------------

reset_camera
-----------------------

.. autofunction:: vtkplotlib.reset_camera


----------------------

zoom_to_contents
----------------------

.. autofunction:: vtkplotlib.zoom_to_contents


----------------

close
----------------

.. autofunction:: vtkplotlib.close


-------------------------

figure_history
-------------------------

.. autodata:: vtkplotlib.figure_history


----------------------

auto_figure
----------------------

.. autofunction:: vtkplotlib.auto_figure


-------------------

QtFigure
-------------------

.. autoclass:: vtkplotlib.QtFigure


--------------------

QtFigure2
--------------------

.. autoclass:: vtkplotlib.QtFigure2


