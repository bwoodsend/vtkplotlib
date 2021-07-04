***************
Super Callbacks
***************

.. py:currentmodule:: vtkplotlib.interactive

The methods :func:`get_super_callback` and :func:`call_super_callback` get and
call VTK's original responses to user interactions which may have been
overwritten. See :ref:`Interactive:Super Callbacks?` for why you need them and
where to use them.

.. autofunction:: get_super_callback

.. autofunction:: call_super_callback

.. autoexception:: SuperError
    :show-inheritance:

.. autofunction:: null_super_callback
