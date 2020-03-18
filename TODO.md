# Stuff that needs sorting

- [ ] More DOCS
- [ ] Make `vpl.view` less useless.
- [ ] Add type and array shape checking.
- [ ] Use resize events in `vpl.text` so that it scales with the window.
- [ ] Edit `TextureMap` so that it doesn't flip the image. Or better, use VTK's.
- [ ] Fix test_optional_dependency_fallbacks.py so that it actually ignores the optional libraries. I think this requires all `LIBRARY_AVAILABLE` bool variables to become functions rather than attributes.
- [ ] Add _vtk_errors.py handling to image_io.py.
- [ ] `mesh_plot` the pycollada and meshio classes.
- [x] Fix cleanup of figures so it doen't issue the warnings on close. I think this is just `QtFigure`.
- [x] Work out why QtFigures are no longer re-showable.
- [ ] Setup a Qt/VTK abstracted timer for animation use (using a VTK timer crashes when Qt is used).
- [ ] Document accessable VTK attributes so people VTK savy users can find them.

