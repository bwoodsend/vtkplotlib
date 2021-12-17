# -*- coding: utf-8 -*-

import numpy as np
import sys
from pathlib import Path
from itertools import zip_longest

from PyQt5 import QtWidgets, QtGui, QtCore

from vtkplotlib.figures import QtFigure, save_fig, view
from vtkplotlib.data import ICONS_FOLDER

SCREENSHOT_ICON_PATH = ICONS_FOLDER / "screenshot.png"


class QtFigure2(QtFigure):
    """This is intended to be used as/for a more sophisticated GUI when one is needed.
    By providing some common features here, hopefully this can speed up the
    tedious process of building a GUI. Any contributions here would be very
    welcome. I want to write this so that each extra feature is optional allowing
    custom GUIs can be built quickly.

    This is still under development. Currently it has:

    1. A screenshot button.
    2. A panel for preset camera views.
    3. An actor table to show / hide / color plots interactively (although it needs some way to group them).
    4. A cursor tracker displaying 3D coordinates of the mouse.

    I hope/intend to add:

    1. Suggestions welcome here...

    Use this class the same way you would use `QtFigure` (see there first.)
    Each feature is added with a ``fig.add_***()`` method.

    .. code-block:: python

        import vtkplotlib as vpl
        import numpy as np

        # Create the figure. This as-is looks like just a QtFigure.
        fig = vpl.QtFigure2()

        # Add each feature you want. Pass arguments to customise each one.
        fig.add_screenshot_button(pixels=1080)
        fig.add_preset_views()
        fig.add_show_plot_table_button()
        # Use ``fig.add_all()`` to add all them all.

        # You will likely want to dump the above into a function. Or a class
        # inheriting from ``vpl.QtFigure2``.

        # The usual, plot something super exciting.
        vpl.polygon(np.array([[1, 0, 0],
                              [1, 1, 0],
                              [0, 1, 1],
                              [0, 0, 1]]), color="grey")

        # Then either ``vpl.show()`` or
        fig.show()


    """

    def __init__(self, name="qt vtk figure", parent=None):
        super().__init__(name, parent)

        self.menu = QtWidgets.QHBoxLayout()
        self.vl.insertLayout(0, self.menu)

        self.plot_table = None

        self.save_fig_kwargs = {}

    def add_preset_views(self, names=None, view_params=None, icons=()):
        if view_params is None:
            self.view_buttons = ViewButtons.default(self)
        else:
            self.view_buttons = ViewButtons(self, names, view_params,
                                            icons=icons)

        self.menu.addLayout(self.view_buttons.to_layout())

        return self

    def add_preset_views_from_directions(self, directions, ups, mirrors=True):
        self.view_buttons = ViewButtons.from_directions(
            directions, ups, mirrors=mirrors, figure=self)
        self.menu.addLayout(self.view_buttons.to_layout())
        return self

    def add_screenshot_button(self, **save_fig_kwargs):

        self.default_screenshot_path = Path() / (self.window_name + ".jpg")

        self.screenshot_button = Button("Screenshot", self.screenshot,
                                        SCREENSHOT_ICON_PATH)
        self.menu.addWidget(self.screenshot_button)
        self.save_fig_kwargs = save_fig_kwargs
        return self

    def add_cursor_tracker(self):
        from vtkplotlib.figures.QtGuiFigure.cursor_tracker import CursorTracker
        self.cursor_tracker = CursorTracker(self)

    def screenshot(self):
        path = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save screenshot", None, "(*.jpg);;(*.png)")[0]

        if path:
            save_fig(path, fig=self, **self.save_fig_kwargs)

    def add_show_plot_table_button(self):
        self.show_plot_table_button = Button("Show plots menu",
                                             self.show_plot_table)
        self.menu.addWidget(self.show_plot_table_button)

        return self

    def show_plot_table(self):
        self.plot_table = table = PlotTable(self)
        table.show()

    def update(self):
        super().update()
        if self.plot_table is not None:
            self.plot_table.update()

    def add_all(self):
        self.add_preset_views()
        self.add_screenshot_button()
        self.add_show_plot_table_button()
        self.add_cursor_tracker()
        return self


class Button(QtWidgets.QPushButton):

    def __init__(self, name, callback=None, icon=None, parent=None):
        super().__init__(parent)

        if callback is None:
            callback = self.default_callback

        self.released.connect(callback)
        self.setIconSize(QtCore.QSize(40, 40))

        p = self.sizePolicy()
        p.setHorizontalPolicy(p.Minimum)
        p.setVerticalPolicy(p.Minimum)
        self.setSizePolicy(p)

        if icon is not None:
            self.setIcon(as_qicon(icon))
        else:
            self.setText(name)

    def default_callback(self):
        print("QButton", repr(self.text()), "was triggered")


def as_qicon(obj):
    pixmap = None

    if isinstance(obj, QtGui.QIcon):
        return obj

    from vtkplotlib.nuts_and_bolts import isinstance_PathLike, isinstance_no_import
    if isinstance_PathLike(obj):
        pixmap = QtGui.QPixmap(str(obj))

    if isinstance_no_import(obj, "PIL.Image", "Image"):
        pixmap = obj.toqpixmap()

    if pixmap is not None:
        return QtGui.QIcon(pixmap)
    else:
        raise TypeError("""Icons can be created from any of the following:
    - str
    - os.Pathlike
    - QtGui.QIcon
    - PIL.Image.Image
Received {}""".format(type(obj)))


class ViewButton(Button):

    def __init__(self, name, parent, icon=None, view_params=None):
        if view_params is None:
            view_params = {}

        super().__init__(name, self.set_view, icon, parent)

        self.args = view_params

    def set_view(self):
        view(fig=self.parent(), **self.args)

        self.parent().reset_camera()
        self.parent().update()


class ViewButtons(object):
    DEFAULT_NAMES = ("Right", "Left", "Front", "Back", "Top", "Bottom")
    DEFAULT_ICONS = tuple(ICONS_FOLDER / (i + ".jpg") for i in DEFAULT_NAMES)

    def __init__(self, fig, names=DEFAULT_NAMES, view_params=(),
                 icons=DEFAULT_ICONS):

        self.buttons = []

        for (name, args, icon) in zip_longest(names, view_params, icons):
            button = ViewButton(name, fig, icon)
            if args is not None:
                button.args = args

            self.buttons.append(button)

    @classmethod
    def default(cls, figure):

        self = cls(figure)
        self.init_default()

        return self

    def init_default(self):
        directions = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])

        ups = np.array([[0, 0, 1], [0, 1, 0]])

        self.init_from_directions(directions, ups)

    def init_from_directions(self, directions, ups, mirrors=True):

        if mirrors:
            signs = (1, -1)
        else:
            signs = (1,)

        view_params = []
        for d_ in directions:
            for sign in signs:
                d = d_ * sign
                args = {"camera_position": d}

                for up in ups:
                    if np.cross(d, up).any():
                        args["up_view"] = up
                        break
                else:
                    raise ValueError(
                        "All `up_views` are parallel to direction {}".format(d))
                view_params.append(args)

        for (button, args) in zip_longest(self.buttons, view_params):
            button.args = args

    def to_layout(self, parent=None):
        out = QtWidgets.QHBoxLayout(parent)
        [out.addWidget(i) for i in self.buttons]
        return out

    def rotate(self, M):
        for button in self.buttons:
            args = button.args
            for key in args:
                args[key] = np.matmul(args[key], M)


class PlotTable(QtWidgets.QWidget):

    def __init__(self, figure):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.figure = figure
        self.plots = self.figure.plots
        self.rows = dict()

        self.grid = QtWidgets.QGridLayout()
        self.setLayout(self.grid)

        self.timer = timer = QtCore.QTimer()
        timer.setInterval(50)
        #timer.timeout.connect(lambda: print(row.text.underMouse()))
        timer.timeout.connect(self.update)
        timer.start()

        self.update()

    def add_plot(self, plot):
        row = PlotTableRow(plot, len(self.rows))  # + 1
        row.add_to_grid(self.grid)
        self.rows[plot] = row

    def remove_plot(self, plot):
        self.rows.pop(plot)

    def update(self):
        for plot in self.plots - set(self.rows.keys()):
            self.add_plot(plot)

        for plot in set(self.rows.keys()) - self.plots:
            self.remove_plot(plot)


class PlotTableRow(object):

    def __init__(self, plot, row_num):
        self.plot = plot
        self.row_num = row_num

        self.visible_checkbox = QtWidgets.QCheckBox()
        self.visible_checkbox.setChecked(self.plot.visible)
        self.visible_checkbox.stateChanged.connect(self.chk_box_change_cb)

        if hasattr(self.plot, "name"):
            name = self.plot.name
        else:
            name = repr(self.plot)
        self.text = QLabel_alterada(name)
        self.text.released.connect(self.toggle_visible)

    def chk_box_change_cb(self):
        state = bool(self.visible_checkbox.checkState())

        self.plot.visible = bool(state)
        self.plot.fig.update()

    def toggle_visible(self):
        self.visible_checkbox.setChecked(not self.visible_checkbox.checkState())

    def add_to_grid(self, grid):
        grid.addWidget(self.visible_checkbox, self.row_num, 0)
        grid.addWidget(self.text, self.row_num, 1)


class QLabel_alterada(QtWidgets.QLabel):
    released = QtCore.pyqtSignal()

    def mouseReleaseEvent(self, ev):
        self.released.emit()


if __name__ == "__main__":
    import vtkplotlib as vpl

    app = None
    app = QtWidgets.QApplication(sys.argv)

    self = vpl.QtFigure2("Rabbits")

    plot = vpl.mesh_plot(vpl.data.get_rabbit_stl())
    # plot.name = "rabbit"
    # mesh_2 = Mesh.from_file(vpl.data.get_rabbit_stl())
    # mesh_2.translate(np.array([100, 0, 0]))
    # vpl.scatter(np.random.uniform(-100, 100, (3, 3)))

    self.add_all()
    fig, self = self, self.view_buttons

    #    M = np.roll(np.eye(3), 1, 0)
    #    self.rotate(M)

    fig.show()
#
##    self.show(False)
#
##    app.processEvents()
#    plot = vpl.mesh_plot(mesh_2, color="g")
#    plot.name = "green rabbit"
##    self.update()
#
#
#
##    app.processEvents()
##    row = table.rows[plot]
#
#    self.show()
##    app.exec_()
#
