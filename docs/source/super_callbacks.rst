***************
Super Callbacks
***************

The methods :meth:`get_super_callback` and :meth:`call_super_callback` get and
call VTK's original responses to user interactions which may have been
overwritten. See :ref:`Interactive:Super Callbacks?` for why you need them and
where to use them.

.. autofunction:: vtkplotlib.interactive.get_super_callback()

.. autofunction:: vtkplotlib.interactive.call_super_callback()

.. autoexception:: vtkplotlib.interactive.SuperError()
    :show-inheritance:

.. autofunction:: vtkplotlib.interactive.null_super_callback()
