=========
Changelog
=========

Release history for `vtkplotlib`.

v1.4.1
------

* Fix PyInstaller hook location.

v1.4.0
------

* Speed up initialisation by replacing loading of matplotlib's colors with a
  literal `dict`.

* Fix the ``text`` property to `text` returning `None`.

* Fix the **colors** attribute of `surface` mishandling 2D array of
  scalars.

* Fix `TypeError` tripped by ``as_vtk_cmap("string", False)``.

* Create the `interactive` submodule with the alias `i`.

* Fix `legend`\ 's ``key: entry`` mapping being reset.

* Fix ``legend.set_entry(array)`` calling bool on an array

* Fix VTK version dependent `image_io.read` for TIFF, BMP and PNG.

* Move the tests module outside of the distributed `vtkplotlib` package.

* Fix unicode support for ``VTK>=9.0.0``.

* Add cursor tracker to fancy `QtFigure2`.

* Fix handling of a `PolyData` containing NaNs in a `legend`.

v1.3.5
------

* Import new VTK==9.0.0 dependencies explicitly to make them more PyInstaller
  friendly.

v1.3.4
------

* Support VTK 9.0.0.

v1.3.3
------

* Restore compatibility with Python 2.7.

* Elimiate importing ``pkg_resources`` which has a very slow startup time.

v1.3.2
------

* Fix the **off_screen** argument to `save_fig` having no effect.

v1.3.1
------

* Remeber to increment the version this time...

v1.3.0
------

* Catch VTK file reading errors and raise them as Python exceptions, replacing
  the pop-up error dialogs VTK uses by default.

* `QtFigure` now supports being re-shown.

* Fix spurious VTK error dialogs from messy garbage collection of figures.

* Allow a `pathlib.Path` to be used in functions where a filename is expected.

* Support TIFF and bitmap image formats using VTK's image reading/writing
  machinery.

* Add patchy support for `io.BytesIO` image files. This is heavily dependent
  on VTK allows it.

* Add a `zoom_to_contents` method.

* Add support for off screen rendering (screenshotting without drawing a
  window).

* Fix the **label** parameter to `quiver` and `arrow` having no effect.

v1.2.1
------

* Take advantage of the new modular structure of ``VTK >= 8.2.0`` so that
  `vtkplotlib` only imports the parts of VTK that it needs. This makes
  ``import vtkplotlib`` faster and PyInstaller applications smaller. Older
  versions of VTK are still supported and behave unchanged.

v1.2.0
------

* Add a `vtkplotlib.legend` whose contents are determined by a new ``label``
  parameter to each `vtkplotlib` plot command.

* Add colormaps support to `mesh_plot`

* Add an option to `save_fig` and `screenshot_fig` to automatically crop
  away blank regions of the image.

* Add a ``quick_show()`` method to all plots.

v1.1.0
------

* Made a clumsy mistake in screenshot_fig. Forgot that the window needs to be
  open for it to work. Updated now and added to its test so it doesn't slip by
  again

* Catch and raise an exception raise if unable to open a given image type.

* Add a figure history (`vtkplotlib.figure_history`) to store the most
  recent figure(s).

* Allow cursors (given by `vtkplotlib.scatter` with ``use_cursors=True``) to
  be resized.

* Alias `zip_axes` and `unzip_axes` to the top level package.

*  Fix non-Qt figures not being re `show` able.

* Add a `PolyData` wrapper class for VTK's ``vtkPolyData`` allowing easy
  construction of custom mesh-like objects.

* Encourage a `sys.stdout` flush before starting the interactive renderer.
  This reduces (but does not fix) a race condition between VTK's event loop
  and IPython's console if a figure is shown soon after a `print` statement.

* Add support for non ASCII characters in paths which VTK doesn't handle by
  default.

v1.0.0
------

* Initial release on PyPI.
