# -*- coding: utf-8 -*-

from vtkplotlib._get_vtk import vtk
import numpy as np

from vtkplotlib.plots.BasePlot import SourcedPlot, _iter_colors, _iter_points, _iter_scalar
from vtkplotlib import geometry as geom


class Arrow(SourcedPlot):
    """Draw a single arrow from **start** to **end**."""

    def __init__(self, start, end, length=None, width_scale=1, color=None,
                 opacity=None, fig="gcf", label=None):
        super().__init__(fig)

        diff = end - start
        if length is None:
            length = geom.distance(diff)

        # vtk needs a full set of axes to build about.
        # eX is just the direction the arrow is pointing in.
        # eY and eZ must be perpendicular to each other and eX. However beyond
        # that exact choice of eY and eZ does not matter. It only rotates the
        # arrow about eX which you can't see because it's (approximately) round.
        eX, eY, eZ = geom.orthogonal_bases(diff)
        arrowSource = vtk.vtkArrowSource()

        # This next bit puts the arrow where it's supposed to go
        matrix = vtk.vtkMatrix4x4()

        # Create the direction cosine matrix
        matrix.Identity()
        for i in range(3):
            matrix.SetElement(i, 0, eX[i])
            matrix.SetElement(i, 1, eY[i])
            matrix.SetElement(i, 2, eZ[i])

        # Apply the transforms
        transform = vtk.vtkTransform()
        transform.Translate(start)
        transform.Concatenate(matrix)
        transform.Scale(length, length * width_scale, length * width_scale)

        self.source = arrowSource

        self.connect()
        self.actor.SetUserMatrix(transform.GetMatrix())

        self.color_opacity(color, opacity)
        self.label = label


def arrow(start, end, length=None, width_scale=1., color=None, opacity=None,
          fig="gcf", label=None):
    """Draw (an) arrow(s) from **start** to **end**.

    :param start: The starting point(s) of the arrow(s).
    :type start: numpy.ndarray

    :param end: The end point(s) of the arrow(s).
    :type end:  numpy.ndarray

    :param length: The length of the arrow(s), defaults to None.
    :type length: float or numpy.ndarray

    :param width_scale: How fat to make each arrow, is relative to its length.
    :type width_scale: float or numpy.ndarray

    :param color: The color of each arrow, defaults to white.
    :type color: str or tuple or numpy.ndarray

    :param opacity: The translucency of the plot. Ranges from ``0.0`` (invisible) to ``1.0`` (solid).
    :type opacity: float

    :param fig: The figure to plot into, use `None` for no figure, defaults to the output of `vtkplotlib.gcf()`.
    :type fig: :class:`~vtkplotlib.figure` or :class:`~vtkplotlib.QtFigure`

    :param label: Give the plot a label to use in a `legend`.
    :type label: str

    :return: arrow or array of arrows


    The shapes of **start** and **end** should match. Arrow lengths are
    automatically calculated via pythagoras if not provided but can be
    overwritten by setting **length**. In this case the arrow(s) will always
    start at **start** but may not end at **end**. **length** can either be a single
    value for all arrows or an array of lengths to match the number of arrows.

    .. note::

        Arrays are supported only for convenience and just use a python for
        loop. There is no speed bonus to using numpy or trying to plot in bulk
        here.

    .. seealso:: `vtkplotlib.quiver()` for field plots.

    """

    start = np.asarray(start)
    end = np.asarray(end)

    assert start.shape == end.shape

    shape = start.shape[:-1]
    out = np.empty(shape, object)
    out_flat = out.ravel()

    for (i, s, e, l, c, lab) in zip(range(out.size), _iter_points(start),
                                    _iter_points(end),
                                    _iter_scalar(length, shape),
                                    _iter_colors(color, shape),
                                    _iter_scalar(label, shape)):

        out_flat[i] = Arrow(s, e, l, width_scale, c, opacity, fig, lab)

    if out.ndim == 0:
        return out.item()
    return out


def quiver(point, gradient, length=None, length_scale=1., width_scale=1.,
           color=None, opacity=None, fig="gcf", label=None):
    """Create arrow(s) from 'point' towards a direction given by 'gradient' to
    make field/quiver plots. Arrow lengths by default are the magnitude of
    'gradient but can be scaled with 'length_scale' or frozen with 'length'.
    See arrow's docs for more detail.

    :param point: The starting point of the arrow(s).
    :type point: numpy.ndarray

    :param gradient: The displacement / gradient vector.
    :type gradient: numpy.ndarray

    :param length: A frozen length for each arrow, defaults to unfrozen. Overrides the magnitudes of **gradient**.
    :type length: float

    :param length_scale: A scaling factor for the length of each arrow.
    :type length_scale: float

    :param width_scale: How fat to make each arrow, is relative to its length.
    :type width_scale: float

    :param color: The color of each arrow, defaults to white.
    :type color: str or tuple or numpy.ndarray

    :param opacity: The translucency of the plot. Ranges from ``0.0`` (invisible) to ``1.0`` (solid).
    :type opacity: float

    :param fig: The figure to plot into, use `None` for no figure, defaults to the output of `vtkplotlib.gcf()`.
    :type fig: :class:`~vtkplotlib.figure` or :class:`~vtkplotlib.QtFigure`

    :param label: Give the plot a label to use in a `legend`.
    :type label: str

    :return: arrow or array of arrows

    .. seealso:: `arrow` to draw arrows from a start point to an end point.

    """

    if length is None:
        length = geom.distance(gradient)
    if length_scale != 1:
        length *= length_scale

    return arrow(point, point + gradient, length, width_scale, color, opacity,
                 fig, label)


if __name__ == "__main__":

    import vtkplotlib as vpl

    t = np.linspace(0, 2 * np.pi)
    points = vpl.zip_axes([np.cos(t), np.sin(t), np.cos(t) * np.sin(t)]).T
    grads = np.roll(points, 10)

    arrows = quiver(points, grads, width_scale=.3, color=grads)

    vpl.show()
