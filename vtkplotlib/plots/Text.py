# -*- coding: utf-8 -*-

from vtkplotlib._get_vtk import vtk
import numpy as np

from vtkplotlib.plots.BasePlot import Base2DPlot


class Text(Base2DPlot):
    """2D text at a fixed point on the window (independent of camera
    position / orientation).

    :param text_str: The text, converts to string if not one already.
    :type text_str: str or object

    :param position: The ``(x, y)`` position in pixels on the screen, defaults to ``(0, 0)`` (left, bottom).
    :type position: tuple

    :param fontsize: Text height (ignoring tails) in pixels, defaults to 18.
    :type fontsize: int

    :param color: The color of the text, defaults to white.
    :type color: str or tuple or numpy.ndarray

    :param opacity: The translucency of the plot. Ranges from ``0.0`` (invisible) to ``1.0`` (solid).
    :type opacity: float

    :param fig: The figure to plot into, use `None` for no figure, defaults to the output of `vtkplotlib.gcf()`.
    :type fig: :class:`~vtkplotlib.figure` or :class:`~vtkplotlib.QtFigure`

    :return: The text plot object.
    :rtype: `vtkplotlib.text`


    The text doesn't resize or reposition itself when the window is resized.
    It's on the todo list.

    .. seealso:: ``vpl.text3D``

    """

    def __init__(self, text_str, position=(0, 0), fontsize=18, use_pixels=False,
                 color=(1, 1, 1), opacity=None, fig="gcf"):
        # create a text actor
        super().__init__(fig)

        self.actor = vtk.vtkTextActor()

        self.text = text_str

        self.use_pixels = use_pixels

        self.property = self.actor.GetTextProperty()

        self.property.SetFontFamilyToArial()
        self.property.SetFontSize(fontsize)
        self.color_opacity(color, opacity)

        self.actor.SetPosition(*position)

        # assign actor to the renderer
        self.fig += self

    # TODO: make this work


#    @property
#    def position(self):
#        position = self._position
#        if self.use_pixels:
#            return position
#        else:
#            return tuple(i / j for (i, j) in zip(position, self.fig.render_size))
#
#    @position.setter
#    def position(self, position):
#        if self.use_pixels:
#            self._position = position
#        else:
#            self._position = tuple(int(i * j) for (i, j) in zip(position, self.fig.render_size))

    @property
    def text(self):
        return self.actor.GetInput()

    @text.setter
    def text(self, text_str):
        if not isinstance(text_str, str):
            text_str = str(text_str)
        self.actor.SetInput(text_str)


def resize_event_cb(*args):
    # print(args)
    self.actor.SetPosition(*(i // 2 for i in fig.render_size))


if __name__ == "__main__":
    import vtkplotlib as vpl

    fig = vpl.figure()
    fig.renWin.AddObserver(vtk.vtkCommand.ModifiedEvent, resize_event_cb)
    self = vpl.text("eggs", (100, 200))
    vpl.show()
