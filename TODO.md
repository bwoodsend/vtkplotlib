# Stuff that needs sorting

- DOCS
- Make `vpl.view` less useless.
- Multi-colors for `vpl.plot`.
- Add type and array shape checking.
- Use resize events in `vpl.text` so that it scales with the window.
- Edit `TextureMap` so that it doesn't flip the image. Or better, use VTK's.
- Move the mapper to the `PolyData` class.
- Add a `quick_show()` method to `BasePlot`.
- Sort the `mapper.SetScalarMode` hoohah.
- Implement a `write` in image_io.py.
- Fix test_optional_dependency_fallbacks.py so that it actually ignores the optional libraries. I think this requires all `LIBRARY_AVAILABLE` bool variables to become functions rather than attributes.
- Make `PolyData` not use  `deepcopy` in `numpy_to_vtk`.
- Add _vtk_errors.py handling to image_io.py.
- Add `cmap` as a `property` of `BasePlot`.
- `mesh_plot` the pycollada and meshio classes.
- Change `plot.set_scalar_range` to a `property`.
- Fix cleanup of figures so it doen't issue the warnings on close. I think this is just `QtFigure`.

