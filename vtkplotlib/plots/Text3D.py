# -*- coding: utf-8 -*-

from vtkplotlib._get_vtk import vtk
import numpy as np

from vtkplotlib.plots.BasePlot import SourcedPlot
from vtkplotlib import geometry as geom
from vtkplotlib.plots.Arrow import Arrow


class Text3D(SourcedPlot):
    """Create floating text in 3D space. Optionally can be set to orientate
    itself to follow the camera (defaults to on) with the **follow_cam**
    argument.

    :param text: The text to be shown.

    :param position: The position of the start of the text, defaults to (0, 0, 0).
    :type position: tuple

    :param follow_cam: Automatically rotates to follow the camera, defaults to True.
    :type follow_cam: bool

    :param scale: The height in world coordinates of one line of text. Use a 3-tuple of values to stretch or squash it.
    :type scale: float or tuple

    :param color: The color of the text, defaults to white.
    :type color: str or tuple or numpy.ndarray

    :param opacity: The translucency of the plot. Ranges from ``0.0`` (invisible) to ``1.0`` (solid).
    :type opacity: float

    :param fig: The figure to plot into, use `None` for no figure, defaults to the output of `vtkplotlib.gcf()`.
    :type fig: :class:`~vtkplotlib.figure` or :class:`~vtkplotlib.QtFigure`

    :param label: Give the plot a label to use in a `legend`.
    :type label: str

    :return: text3D plot object
    :rtype: `vtkplotlib.text3d`


    .. warning::

        This can't be passed about between figures if ``follow_cam=True``
        (the default). The figure who's camera it follows is frozen to the
        figure given to it on first construction.

    .. seealso:: ``vpl.text`` for 2D text at a fixed point on the screen.
    .. seealso:: ``vpl.annotate`` for a convenient way to label features with text and an arrow.


    """

    def __init__(self, text, position=(0, 0, 0), follow_cam=True, scale=1,
                 color=None, opacity=None, fig="gcf", label=None):
        super().__init__(fig)
        # Create the 3D text and the associated mapper and follower (a type of
        # actor). Position the text so it is displayed over the origin of the
        # axes.

        self.source = vtk.vtkVectorText()
        # This chunk is different to how most plots objects construct
        # themselves. So super().connect() wont work unfortunately.
        self.actor = vtk.vtkFollower()
        self.actor.SetMapper(self.mapper)
        self.property = self.actor.GetProperty()
        self.mapper.SetInputConnection(self.source.GetOutputPort())

        self.__setstate__(locals())

        self.fig += self

        if follow_cam:
            self.actor.SetCamera(self.fig.renderer.GetActiveCamera())

    @property
    def text(self):
        return self.source.GetText()

    @text.setter
    def text(self, text):
        if not isinstance(text, str):
            text = str(text)
        self.source.SetText(text)

    position = property(lambda self: self.actor.GetPosition(),
                        lambda self, position: self.actor.SetPosition(position))

    scale = property(lambda self: self.actor.GetScale())

    @scale.setter
    def scale(self, scale):
        if np.isscalar(scale):
            scale = (scale,) * 3
        self.actor.SetScale(*scale)


def annotate(points, text, direction, text_color="w", arrow_color="k",
             distance=3., text_size=1., fig="gcf"):
    """Annotate a feature with an arrow pointing at a point and a text label
    on the reverse end of the arrow. This is just a convenience call to
    `arrow()` and `text3d()`. See there for just one or the other.

    :param points: The position of the feature where the arrow's tip should be.
    :type points: numpy.ndarray

    :param text: The text to put in the label.

    :param direction: The direction from the feature to the text position as a unit vector.
    :type direction: numpy.ndarray

    :param text_color: The color of the label, defaults to 'w'.

    :param arrow_color:  The color of the arrow, defaults to 'k'.

    :param distance: The distance from the feature to the label.

    :param text_size: The height of one line of text, can have 3 values, defaults to 1.0.
    :type text_size: float or tuple

    :param fig: The figure to plot into, use `None` for no figure, defaults to the output of `vtkplotlib.gcf()`.
    :type fig: :class:`~vtkplotlib.figure` or :class:`~vtkplotlib.QtFigure`

    :return: An (`arrow`, `text3d`)  pair.


    The arrow points to the highest point and the text is placed at a point
    **distance** above (where above also is determined by direction).

    If **text** is not a `str` then it is automatically converted to one.


    .. code-block:: python

        import vtkplotlib as vpl
        import numpy as np

        # Create a ball at a point in space.
        point = np.array([1, 2, 3])
        vpl.scatter(point)

        vpl.annotate(point,
                     "This ball is at {}".format(point),
                     np.array([0, 0, 1]))
        vpl.show()


    If multiple points are given the farthest in the direction **direction** is
    selected. The idea is to try to prevent the annotations ending up in
    amongst the plots or, when plotting meshes, inside the mesh.

    .. code-block:: python

        import vtkplotlib as vpl
        import numpy as np

        # Create several balls.
        points = np.random.uniform(-30, 30, (30, 3))
        vpl.scatter(points, color=np.random.random(points.shape))

        vpl.annotate(points,
                     "This ball is the highest",
                     np.array([0, 0, 1]),
                     text_color="k",
                     arrow_color="orange"
                     )

        vpl.annotate(points,
                     "This ball is the lowest",
                     np.array([0, 0, -1]),
                     text_color="rust",
                     arrow_color="hunter green"
                     )

        vpl.show()


    """

    point = geom.highest(points, direction)

    arrow = Arrow(point + (distance - .5 * text_size) * direction, point,
                  color=arrow_color, fig=fig)

    text = Text3D(text, point + distance * direction, color=text_color,
                  scale=text_size, fig=fig)

    return arrow, text
