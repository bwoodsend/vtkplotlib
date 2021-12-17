# -*- coding: utf-8 -*-
"""
"""

import numpy as np
from vtkplotlib._get_vtk import vtk

from vtkplotlib.plots.BasePlot import Base2DPlot, BasePlot, as_rgb_a, PolyData


class Legend(Base2DPlot):
    """Creates a legend to label plots.

    :param plots_source: Plots to use in the legend. Use `None` to include nothing. Defaults to ``fig.plots``.

    :param fig: The figure to plot into, use `None` for no figure, defaults to the output of `vtkplotlib.gcf()`.
    :type fig: :class:`~vtkplotlib.figure` or :class:`~vtkplotlib.QtFigure`

    :param position: Position (relative to the size of the figure) of the bottom left corner.
    :type position: tuple

    :param size: Size (relative to the size of the figure) of the legend.
    :type size: tuple

    :param color: The background color of the legend.
    :type color: str or tuple or numpy.ndarray

    :param allow_no_label: Allow plots that have no label to have label `None`, only applicable if entries are added automatically.
    :type allow_no_label: bool

    :param allow_non_polydata_plots: Allow plots that have no polydata to represented with a box, only applicable if entries are added automatically.
    :type allow_non_polydata_plots: bool


    Elements can be added to the legend automatically or explicitly. Most plot
    commands have an optional **label** argument. If this is used then they will
    be added automatically. Multiple plots with the same label will be grouped.

    .. code-block:: python

        import vtkplotlib as vpl
        import numpy as np

        # Create some plots with labels
        vpl.scatter([0, 0, 0], color="red", label="Red Ball")
        vpl.scatter(vpl.zip_axes(5, np.arange(0, 10, 4), 0), color="yellow", label="Yellow Ball")

        # A plot without a label will not be included in the legend.
        vpl.scatter([10, 0, 0], color="green")

        # Create the legend
        vpl.legend()
        # Unless told otherwise this internally calls
        # legend.add_plots(vpl.gcf().plots)

        vpl.show()


    The legend uses a tabular format.

    +--------+------+------------+
    | Symbol | Icon | Text Label |
    +--------+------+------------+
    | Symbol | Icon | Text Label |
    +--------+------+------------+
    | Symbol | Icon | Text Label |
    +--------+------+------------+

    - A *symbol* is a 2D representation of the original plot. VTK can generate
      these flattened snapshots from a polydata object which most plots either
      have or can generate. These are accessible via ``plot.polydata``.

    - An *icon* is just a 2D image. Note that VTK only supports greyscale icons
      in legends.

    - The *text label*, as the name suggests, is just a piece of text.

    All three columns are optional. If a column is never used throughout the
    legend then the contents adjusts to close the space. Color can only be
    applied per-row. i.e the symbol, icon and text of an entry are always the
    same color.

    The following example shows how to set the entries explicitly.

    .. code-block :: python

        import vtkplotlib as vpl

        # Create a legend and don't allow it to fill itself.
        legend = vpl.legend(plots_source=None)


        # A labelled plot contains all the information it needs to add itself.
        sphere = vpl.scatter([0, 5, 10], color="g", label="Green Ball")
        # Add it like so.
        legend.set_entry(sphere)

        # Written explicitly the above is equivalent to:
        # legend.set_entry(symbol=sphere.polydata, color=sphere.color, label=sphere.label)


        # Not all plots can have a polydata. If one isn't provided then a by
        # default a square is used.
        legend.set_entry(label="Blue Square", color="blue")

        # Alternatively, if explicitly given ``symbol=None``, then the symbol
        # space is left blank.
        legend.set_entry(symbol=None, label="Just Text")


        # Most plots can be used.
        legend.set_entry(vpl.mesh_plot(vpl.data.get_rabbit_stl()), label="Rabbit")


        # To use an icon, pass a string path, array, PIL image or vtkImageData
        # to the **icon** argument. The image is converted to greyscale
        # automatically.
        legend.set_entry(None, label="Shark", icon=vpl.data.ICONS["Right"])


        vpl.show()



    ``legend.set_entry`` has an optional argument **index** which can be used to
    overwrite rows. Otherwise it defaults to appending a row.

    Some caveats / potential sources of confusion:

    - Long and thin plots such as `arrow()` tend to mess up the spacing
      which is seemingly non configurable.

    - Be careful when using `scatter()` and `quiver()` which return an
      array of plots rather than a single plot.

    - Plots based on lines such as the output of `vtkplotlib.plot()` tend not to
      show well as the lines are less than one pixel wide.

    - Automatic setting of color can only work for uniformly colored plots.
      any colors derived from scalars are ignored.


    To some extent, the text labels can be customised via
    ``legend.text_options`` which holds the vtkTextProperty (bucket class for
    settings like font). However, a lot of its methods do nothing. Most
    notably, ``legend.text_options.SetFontSize(size)`` has no effect.

    """

    def __init__(self, plots_source="fig", fig="gcf", position=(.7, .7),
                 size=(.3, .3), color="grey", opacity=None,
                 allow_non_polydata_plots=False, allow_no_label=False):

        super().__init__(fig)
        self.actor = self.legend = vtk.vtkLegendBoxActor()
        self._plots_by_label = {}

        self.__actor2d_init__()

        self.__setstate__(locals())

        self.legend.UseBackgroundOn()
        self.text_options = self.legend.GetEntryTextProperty()

        if self.fig is not None:
            self.fig += self

            if plots_source == "fig":
                plots_source = self.fig.plots

        if plots_source is not None and plots_source != "fig":
            self.add_plots(plots_source, allow_no_label=allow_no_label,
                           allow_non_polydata_plots=allow_non_polydata_plots)

    def add_plots(self, plots, allow_non_polydata_plots=False,
                  allow_no_label=False):
        by_label = self._plots_by_label
        for plot in plots:
            label = plot.label

            if label is None and not allow_no_label:
                continue

            if label in by_label:
                continue

            if isinstance(plot, Legend):
                # ignore the legend as a plot.
                continue

            elif hasattr(plot, "polydata"):
                # The symbol in the can be automatically generated from the
                # polydata if the plot has one.
                by_label[label] = plot

            elif allow_non_polydata_plots and label not in by_label:
                by_label[label] = plot

            if hasattr(plot, "polydata"):
                self.set_entry(plot)
            else:
                self.set_entry(label=label, color=plot.color)

    @property
    def color(self):
        return self.legend.GetBackgroundColor()

    @color.setter
    def color(self, color):
        color, opacity = as_rgb_a(color)
        self.legend.SetBackgroundColor(color)
        if opacity is not None:
            self.legend.SetBackgroundOpacity(opacity)

    opacity = property(lambda self: self.legend.GetBackgroundOpacity(),
                       lambda self, o: self.legend.SetBackgroundOpacity(o))

    @property
    def length(self):
        return self.legend.GetNumberOfEntries()

    @length.setter
    def length(self, length):
        self.legend.SetNumberOfEntries(length)

    __len__ = length.fget

    def set_entry(self, symbol="box", label="from plot", color=None, icon=None,
                  index="append"):
        if index == "append":
            index = self.length
            self.length += 1
        self._check_length(index)

        # isinstance check is only needed in case symbol is a numpy array.
        if isinstance(symbol, str) and symbol == "box":
            legendBox = vtk.vtkCubeSource()
            legendBox.Update()
            symbol = legendBox.GetOutput()

        elif isinstance(symbol, BasePlot):

            if label == "from plot":
                label = symbol.label

            if color is None:
                color = symbol.color
                if isinstance(color, np.ndarray):
                    # If color is actually scalars, or an array of RGBs from a
                    # PolyData based plot, ignore color.
                    color = None

        if color is not None:
            self.set_entry_color(index, color)

        if label != "from plot" and label is not None:
            self.set_entry_text(index, label)

        if symbol is not None:
            self.set_entry_symbol(index, symbol)

        if icon is not None:
            self.set_entry_icon(index, icon)

    def set_entry_icon(self, index, icon):
        self._check_length(index)
        from vtkplotlib import image_io
        # ! Icons must be greyscale !
        icon = image_io.as_vtkimagedata(icon, ndim=2)
        self.legend.SetEntryIcon(index, icon)

    def set_entry_symbol(self, index, symbol):
        self._check_length(index)

        if isinstance(symbol, np.ndarray) and symbol.dtype == object:
            # E.g. output from scatter() - just pick the 1st.
            symbol = symbol.item(0)

        polydata = symbol

        if isinstance(polydata, BasePlot):
            polydata = symbol.polydata
        if isinstance(polydata, PolyData):
            polydata = polydata.vtk_polydata

        if not isinstance(polydata, vtk.vtkPolyData):
            raise TypeError(
                "Legend symbols must be a vtkplotlib.PolyData, vtk.vtkPolyData "
                "or the output of a vtkplotlib plot method. Received type {}.".
                format(type(symbol)))

        # If the polydata is not already positioned at the origin then the
        # generated icon moves with it. This finds the polydata's position
        # and shifts a copy back to the origin if needed.

        # Find the centre of the polydata
        bounds = np.reshape(polydata.GetBounds(), (3, 2))
        centre = polydata.GetCenter()

        # Needed in case of nan points which result in 1e299s in `bounds`.
        old = np.seterr(over="ignore")

        # If not already near enough to the origin
        if np.abs(centre).max() > bounds.std(1).max() * .1:

            polydata = PolyData(polydata).copy()
            polydata.points -= np.array(centre)[np.newaxis]
            polydata = polydata.vtk_polydata

        np.seterr(**old)

        self.legend.SetEntrySymbol(index, polydata)

    def set_entry_color(self, index, color):
        self._check_length(index)
        color = as_rgb_a(color)[0]
        self.legend.SetEntryColor(index, color)

    def set_entry_text(self, index, text):
        self._check_length(index)
        self.legend.SetEntryString(index, str(text))

    def _check_length(self, index):
        if index >= self.length:
            self.length = index + 1
