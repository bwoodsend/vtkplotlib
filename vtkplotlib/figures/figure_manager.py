# -*- coding: utf-8 -*-

import numpy as np
from pathlib import Path

from vtkplotlib._get_vtk import vtk

try:
    # Doing this allows the current figure to be remembered if vtkplotlib gets
    # re-imported.
    _figure
except NameError:
    _figure = None

_auto_fig = True


def auto_figure(auto=None):
    """Enables/disables automatic figure management. If no parameters are
    provided then it returns the current state.

    :param auto: Defaults to None.
    :type auto: bool


    On by default. Disabling causes `vtkplotlib.gcf()` to always return `None`.
    Hence all plot commands will not add to a figure unless told to explicitly
    using the ``fig=a_figure`` argument. This can be useful for complex scenarios
    involving multiple figures.
    """
    global _auto_fig
    if auto is None:
        return _auto_fig
    else:
        _auto_fig = auto


def scf(figure):
    """Sets the current working figure.

    :param figure: A figure or None.
    :type figure: :class:`~vtkplotlib.figure` or :class:`~vtkplotlib.QtFigure`

    """
    global _figure
    if _figure is not None:
        from vtkplotlib._history import figure_history
        figure_history.deque.append(_figure)
    _figure = figure


def gcf(create_new=True):
    """Gets the current working figure.

    :param create_new: Allow a new one to be created if none exist, defaults to True.
    :type create_new: bool

    :return: The current figure or None.
    :rtype: :class:`vtkplotlib.figure` or :class:`vtkplotlib.QtFigure`

    If none exists then a new one gets created by `vtkplotlib.figure()` unless
    ``create_new=False`` in which case `None` is returned. This function will
    always return `None` if ``auto_figure(False)`` has been called.
    """
    global _figure

    if not _auto_fig:
        return
    if _figure is None and create_new:
        from .figure import Figure
        _figure = Figure()
    return _figure


class NoFigureError(Exception):

    fmt = """{} requires a figure and auto_fig is disabled. Create one using
    `vpl.figure()` and pass it as `fig` argument. Or call `vpl.auto_figure(True)`
    and leave the `fig` argument as the default.""".format

    def __init__(self, name):
        super().__init__(self.fmt(name))


def gcf_check(fig, function_name):
    if fig == "gcf":
        fig = gcf()
    if fig is None:
        raise NoFigureError(function_name)
    return fig


def show(block=True, fig="gcf"):
    """Shows a figure. This is analogous to matplotlib's show function. After
    your plot commands call this to open the interactive 3D viewer.

    :param block: Enter interactive mode, otherwise just open the window, defaults to True.
    :type block: bool

    :param fig: The figure to show, defaults to `vtkplotlib.gcf()`.
    :type fig: :class:`~vtkplotlib.figure` or :class:`~vtkplotlib.QtFigure`


    If **block** is True then it enters interactive mode and the program is held
    until window exit. Otherwise the window is opened but not monitored. i.e an
    image will appear on the screen but it wont respond to being clicked on. By
    editing the plot and calling ``fig.update()`` you can create an animation but
    it will be non-interactive. True interactive animation hasn't been implemented
    yet - it's on the TODO list.

    .. note::

        You might feel tempted to run show in a background thread. It
        doesn't work. If anyone does manage it then please let me know.


    .. warning::

        A window can not be closed by the close button until it is in
        interactive mode. Otherwise it'll just crash Python. Use
        `vtkplotlib.close()` to close a non interactive window.


    The current figure is reset on **exit** from interactive mode.
    """

    gcf_check(fig, "show").show(block)


def view(focal_point=None, camera_position=None, camera_direction=None,
         up_view=None, fig="gcf"):
    """Set/get the camera position/orientation.

    :param focal_point: A point the camera should point directly to.
    :type focal_point: list or tuple or numpy.ndarray

    :param camera_position: The point at which the camera is situated.
    :type camera_position: list or tuple or numpy.ndarray

    :param camera_direction: The direction in which the camera is pointing.
    :type camera_direction: list or tuple or numpy.ndarray

    :param up_view: Roll the camera so that the **up_view** vector is pointing towards the
            top of the screen.
    :type up_view: list or tuple or numpy.ndarray

    :param fig: The figure to modify, defaults to `vtkplotlib.gcf()`.
    :type fig: :class:`~vtkplotlib.figure` or :class:`~vtkplotlib.QtFigure`

    :return: A dictionary containing the new configuration.
    :rtype: dict


    .. note::

        This function's not brilliant. You may be better off manipulating the
        vtk camera directly (stored in ``fig.camera``). If you do choose this
        route, start experimenting by calling ``print(fig.camera)``. If
        anyone makes a better version of this function then please share.


    There is an unfortunate amount of implicit chaos going on here. Here are
    some hidden implications. I'm not even sure these are all true.

    1. If **forwards** is used then **focal_point** and **camera_position** are ignored.

    2. If **camera_position** is given but **focal_point** is not also given then **camera_position** is relative to where VTK determines is the middle of your plots. This is equivalent to setting ``camera_direction=-camera_position``.

    The following is well behaved:
    ::

        vpl.view(camera_direction=...,
                 up_view=...,)        # set orientations first
        vpl.reset_camera()            # auto reset the zoom

    """

    fig = gcf_check(fig, "view")

    camera = fig.camera

    if (camera_direction is not None or camera_position is not None) and \
        (focal_point is None):
        focal_point = np.zeros(3)
        reset_at_end = True
    else:
        reset_at_end = False

    # vtk's rules are if only this is specified then it
    # is used as a direction vector instead.
    if camera_direction is not None:
        camera.SetPosition(*-np.asarray(camera_direction))

    else:
        if focal_point is not None:
            camera.SetFocalPoint(*focal_point)
            # By default a figure resets it's camera position on show. This disables that.
            fig._reset_camera = False

        if camera_position is not None:
            camera.SetPosition(*camera_position)

    if up_view is not None:
        camera.SetViewUp(*up_view)

    if reset_at_end:
        fig.reset_camera()

    return dict(focal_point=camera.GetFocalPoint(),
                camera_position=camera.GetPosition(),
                up_view=camera.GetViewUp())


def reset_camera(fig="gcf"):
    """Reset the position and zoom of the camera so that all plots are visible.

    :param fig: The figure to modify, defaults to `vtkplotlib.gcf()`.
    :type fig: :class:`~vtkplotlib.figure` or :class:`~vtkplotlib.QtFigure`


    This does not touch the orientation. It pushes the camera without
    rotating it so that, whichever direction it is pointing, it is
    pointing into the middle of where all the plots are. Then it adjusts the
    zoom so that everything fits on the screen.
    """
    fig = gcf_check(fig, "reset_camera")
    fig.renderer.ResetCamera()


def screenshot_fig(magnification=1, pixels=None, trim_pad_width=None,
                   off_screen=False, fig="gcf"):
    """Take a screenshot of a figure. The image is returned as an array. To
    save a screenshot directly to a file, use `save_fig()`.

    :param magnification: Image dimensions relative to the size of the render window.
    :type magnification: int or tuple

    :param pixels: Image ``(width, height)`` or just ``height`` in pixels.
    :type pixels: int or tuple

    :param trim_pad_width: Optionally auto crop to contents, this specifies how much space to give it, defaults to no cropping. A positive int for padding in pixels, float from 0.0 - 1.0 for pad width relative to original size
    :type trim_pad_width: int or float

    :param off_screen: If true, attempt to take the screenshot without opening the figure's window.
    :type off_screen: bool

    :param fig: The figure to screenshot, defaults to `vtkplotlib.gcf()`.
    :type fig: :class:`~vtkplotlib.figure` or :class:`~vtkplotlib.QtFigure`


    Setting **pixels** overrides **magnification**. If only one dimension is given
    to **pixels** then it is the height and an aspect ration of 16:9 is used.
    This is to match with the 1080p/720p/480p/... naming convention.


    .. note::

        VTK can only work with integer multiples of the render size (given by
        ``figure.render_size``). **pixels** will be therefore be rounded to
        conform to this.

    .. note::

        I have no idea why it spins. But vtk's example in the docs does it as
        well so I think it's safe to say there's not much we can do about it.

    .. note::

        For QtFigures **off_screen** is ignored.

    """
    fig = gcf_check(fig, "screenshot_fig")

    # figure has to be drawn, including the window it goes in unless using off_screen.
    fig._prep_for_screenshot(off_screen)

    # screenshot code:
    win_to_image_filter = vtk.vtkWindowToImageFilter()
    win_to_image_filter.SetInput(fig.renWin)

    # Normalise and set user inputs for magnification.

    if isinstance(pixels, int):
        pixels = (pixels * 16) // 9, pixels

    if isinstance(magnification, int):
        magnification = (magnification, magnification)

    if pixels is not None:
        magnification = tuple(pixels[i] // fig.render_size[i] for i in range(2))

    # Dependent on VTK version.
    if hasattr(win_to_image_filter, "SetScale"):
        win_to_image_filter.SetScale(*magnification)
    else:
        if magnification[0] != magnification[1]:
            print("This version of VTK doesn't support separate magnifications "
                  "for height and width")
            magnification = (magnification[0], magnification[0])
        win_to_image_filter.SetMagnification(magnification[0])

    # Finally take the screenshot.
    win_to_image_filter.Modified()
    win_to_image_filter.Update()

    # And convert it to something a bit less awkward.
    from vtkplotlib import image_io
    arr = image_io.vtkimagedata_to_array(win_to_image_filter.GetOutput())
    arr = image_io.trim_image(arr, fig.background_color, trim_pad_width)

    return arr


def save_fig(path, magnification=1, pixels=None, trim_pad_width=None,
             off_screen=False, fig="gcf", **imsave_plotargs):
    """Take a screenshot and saves it to a file.

    :param path: The path, including extension, to save to.
    :type path: str or os.PathLike

    :param magnification: Image dimensions relative to the size of the render (window), defaults to 1.
    :type magnification: int or tuple

    :param pixels: Image ``(width, height)`` or just ``height`` in pixels.
    :type pixels: int or tuple

    :param trim_pad_width: Padding to leave when cropping to contents, see `screenshot_fig()`.
    :type trim_pad_width: int or float

    :param off_screen: If true, attempt to take the screenshot without opening the figure's window.
    :type off_screen: bool

    :param fig: The figure to save, defaults to `vtkplotlib.gcf()`.
    :type fig: :class:`~vtkplotlib.figure` or :class:`~vtkplotlib.QtFigure`


    This just calls `screenshot_fig()` then passes it to
    `matplotlib.image.imsave` function. See those for more information.

    The available file formats are determined by matplotlib's choice of
    backend. For JPEG, you will likely need to install PILLOW. JPEG has
    considerably better file size than PNG.

    """
    array = screenshot_fig(magnification=magnification, pixels=pixels, fig=fig,
                           trim_pad_width=trim_pad_width, off_screen=off_screen)

    try:
        from matplotlib.pylab import imsave
        imsave(str(path), array, **imsave_plotargs)
        return
    except ImportError:
        pass
    try:
        from PIL import Image
        Image.fromarray(array).save(str(path), **imsave_plotargs)
        return
    except ImportError:
        pass
    from vtkplotlib.image_io import write
    if write(array, path) is NotImplemented:
        raise ValueError("No writer for format '{}' could be found. Try "
                         "installing PIL for more formats.".format(
                             Path(path).ext))


def close(fig="gcf"):
    """Close a figure.

    :param fig: The figure to close, defaults to `vtkplotlib.gcf()`.
    :type fig: :class:`~vtkplotlib.figure` or :class:`~vtkplotlib.QtFigure`

    If the figure is the current figure then the current figure is reset.
    """
    if fig == "gcf":
        # Don't use gcf_check() here so close() can be called redundantly without
        # either creating a new figure just to close it again or raising a
        # NoFigureError.
        fig = gcf(create_new=False)

    if fig is not None:
        # Closing is provided by the figure classes.
        fig.close()


def zoom_to_contents(plots_to_exclude=(), padding=.05, fig="gcf"):
    """VTK, by default, leaves the camera zoomed out so that the renders contain
    a large amount of empty background. `zoom_to_contents()` zooms in so
    that the contents fill the render.

    :param plots_to_exclude: Plots that are unimportant and can be cropped out, defaults to ``()``.

    :param padding: Amount of space to leave around the contents, in pixels if integer or relative to ``min(fig.render_size)`` if float defaults to ``0.05``.
    :type padding: int or float

    :param fig: The figure zoom, defaults to `vtkplotlib.gcf()`.
    :type fig: :class:`~vtkplotlib.figure` or :class:`~vtkplotlib.QtFigure`

    This method only zooms in. If you need to zoom out to fit all your plots in
    call `vtkplotlib.reset_camera()` first then this method. Plots in
    **plots_to_exclude** are temporarily hidden (using ``plot.visible = False``)
    then restored. 2D plots such as a `legend()` or `scalar_bar()` which
    have a fixed position on the render are always excluded.

    .. note:: New in v1.3.0.

    """
    fig = gcf_check(fig, "zoom_to_contents")

    # Temporarily hide any 2D plots such as legends or scalarbars.
    from vtkplotlib.plots.BasePlot import Base2DPlot
    plots_2d_states = {
        plot: plot.visible for plot in fig.plots
        if isinstance(plot, Base2DPlot)
    }
    plots_2d_states.update((plot, plot.visible) for plot in plots_to_exclude)
    for plot in plots_2d_states:
        plot.visible = False

    for i in range(10):
        actual_shape = np.array(
            screenshot_fig(fig=fig, trim_pad_width=padding).shape[:2][::-1])
        target_shape = np.array(fig.render_size)

        zoom = (target_shape / actual_shape).min()
        if zoom > 1:
            fig.camera.Zoom(zoom)

        for (plot, state) in plots_2d_states.items():
            plot.visible = state

        if zoom < 1 + padding / 5:
            break


if __name__ == "__main__":
    pass
