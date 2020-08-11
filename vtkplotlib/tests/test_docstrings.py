# -*- coding: utf-8 -*-
# =============================================================================
# Created on Sun Dec  8 21:49:50 2019
#
# @author: Brénainn Woodsend
#
#
# one line to give the program's name and a brief idea of what it does.
# Copyright (C) 2019  Brénainn Woodsend
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# =============================================================================
"""
"""

from unittest import TestCase, skipUnless

from vtkplotlib import PyQt5_AVAILABLE, NUMPY_STL_AVAILABLE

from vtkplotlib.tests._figure_contents_check import checker, VTKPLOTLIB_WINDOWLESS_TEST
from vtkplotlib.tests.base import BaseTestCase

if PyQt5_AVAILABLE:
    from PyQt5 import QtWidgets, QtCore, QtGui
import vtkplotlib as vpl


class TestDocs(BaseTestCase):
    """These are automatically extracted from the docstrings."""

    @checker()
    @skipUnless(PyQt5_AVAILABLE, "PyQt5 not installed")
    def test_doc_00(self):
        # Create the figure. This automatically sets itself as the current
        # working figure. The qapp is created automatically if one doesn't
        # already exist.
        vpl.QtFigure("Exciting Window Title")

        # Everything from here on should be exactly the same as normal.

        vpl.quick_test_plot()

        # Automatically calls ``qapp.exec_()``. If you don't want it to then
        # use ``vpl.show(False)``.

    @checker()
    @skipUnless(PyQt5_AVAILABLE, "PyQt5 not installed")
    def test_doc_01(self):
        import vtkplotlib as vpl
        from PyQt5 import QtWidgets
        import numpy as np
        import sys

        # python 2 compatibility
        from builtins import super

        class FigureAndButton(QtWidgets.QWidget):

            def __init__(self):
                super().__init__()

                # Go for a vertical stack layout.
                vbox = QtWidgets.QVBoxLayout()
                self.setLayout(vbox)

                # Create the figure
                self.figure = vpl.QtFigure(parent=self)

                # Create a button and attach a callback.
                self.button = QtWidgets.QPushButton("Make a Ball")
                self.button.released.connect(self.button_pressed_cb)

                # QtFigures are QWidgets and are added to layouts with `addWidget`
                vbox.addWidget(self.figure)
                vbox.addWidget(self.button)

            def button_pressed_cb(self):
                """Plot commands can be called in callbacks. The current working
                figure is still self.figure and will remain so until a new
                figure is created explicitly. So the ``fig=self.figure``
                arguments below aren't necessary but are recommended for
                larger, more complex scenarios.
                """

                # Randomly place a ball.
                vpl.scatter(np.random.uniform(-30, 30, 3),
                            color=np.random.rand(3), fig=self.figure)

                # Reposition the camera to better fit to the balls.
                vpl.reset_camera(self.figure)

                # Without this the figure will not redraw unless you click on it.
                self.figure.update()

            def show(self):
                # The order of these two are interchangeable.
                super().show()
                self.figure.show()

            def closeEvent(self, event):
                """This isn't essential. VTK, OpenGL, Qt and Python's garbage
                collect all get in the way of each other so that VTK can't
                clean up properly which causes an annoying VTK error window to
                pop up. Explicitly calling QtFigure's `closeEvent()` ensures
                everything gets deleted in the right order.
                """
                self.figure.closeEvent(event)

        qapp = QtWidgets.QApplication.instance() or QtWidgets.QApplication(
            sys.argv)

        window = FigureAndButton()
        window.show()

        qapp.processEvents()
        for i in range(5):
            window.button.released.emit()
            qapp.processEvents()
        output_to_verify = checker().reduce_fig(window.figure)

        if VTKPLOTLIB_WINDOWLESS_TEST:
            window.close()

        self._do_not_delete_yet = window

        return output_to_verify

#    @checker()
#    @skipUnless(PyQt5_AVAILABLE, "PyQt5 not installed")
#    def test_doc_02(self):
#        import vtkplotlib as vpl
#        import numpy as np
#        from PyQt5.QtWidgets import QApplication
#
#        # Create the figure. This as-is looks like just a QtFigure.
#        fig = vpl.QtFigure2()
#
#        # Add each feature you want. Pass arguments to customise each one.
#        fig.add_screenshot_button(pixels=1080)
#        fig.add_preset_views()
#        fig.add_show_plot_table_button()
#        # Use ``fig.add_all()`` to add all them all.
#
#        # You will likely want to dump the above into a function. Or a class
#        # inheriting from ``vpl.QtFigure2``.
#
#        # The usual, plot something super exciting.
#        vpl.polygon(np.array([[1, 0, 0],
#                              [1, 1, 0],
#                              [0, 1, 1],
#                              [0, 0, 1]]), color="grey")
#
#        # Then either ``vpl.show()`` or
##        fig.show()

    @checker()
    @skipUnless(NUMPY_STL_AVAILABLE, "numpy-stl not installed")
    def test_doc_03(self):
        import vtkplotlib as vpl
        from stl.mesh import Mesh

        mesh = Mesh.from_file(vpl.data.get_rabbit_stl())
        vertices = mesh.vectors

        vpl.plot(vertices, join_ends=True, color="dark red")
#        vpl.show()

    @checker()
    def test_doc_04(self):
        import vtkplotlib as vpl
        import numpy as np

        # Create an octagon, using `t` as scalar values.
        t = np.arange(0, 1, .125) * 2 * np.pi
        vertices = vpl.zip_axes(np.cos(t), np.sin(t), 0)

        # Plot the octagon.
        vpl.plot(
            vertices,
            line_width=6,  # use a chunky (6pt) line
            join_ends=True,  # join the first and last points
            color=t,  # use `t` as scalar values to color it
        )

        # use a dark background for contrast
        fig = vpl.gcf()
        fig.background_color = "grey"

    @checker()
    @skipUnless(NUMPY_STL_AVAILABLE, "numpy-stl not installed")
    def test_doc_05(self):
        import vtkplotlib as vpl
        from stl.mesh import Mesh

        # path = "if you have an STL file then put it's path here."
        # Otherwise vtkplotlib comes with a small STL file for demos/testing.
        path = vpl.data.get_rabbit_stl()

        # Read the STL using numpy-stl
        mesh = Mesh.from_file(path)

        # Plot the mesh
        vpl.mesh_plot(mesh)

        # Show the figure

    @skipUnless(NUMPY_STL_AVAILABLE, "numpy-stl not installed")
    def test_doc_06(self):
        import vtkplotlib as vpl
        from stl.mesh import Mesh

        # Open an STL as before
        path = vpl.data.get_rabbit_stl()
        mesh = Mesh.from_file(path)

        # Plot it with the z values as the scalars. scalars is 'per vertex' or 1
        # value for each corner of each triangle and should have shape (n, 3).
        plot = vpl.mesh_plot(mesh, scalars=mesh.z)

        # Optionally the plot created by mesh_plot can be passed to color_bar
        vpl.color_bar(plot, "Heights")

    @checker()
    @skipUnless(NUMPY_STL_AVAILABLE, "numpy-stl not installed")
    def test_doc_07(self):
        import vtkplotlib as vpl
        from stl.mesh import Mesh
        import numpy as np

        # Open an STL as before
        path = vpl.data.get_rabbit_stl()
        mesh = Mesh.from_file(path)

        # `tri_scalars` must have one value per triangle and have shape (n,) or (n, 1).
        # Create some scalars showing "how upwards facing" each triangle is.
        tri_scalars = np.inner(mesh.units, np.array([0, 0, 1]))

        vpl.mesh_plot(mesh, tri_scalars=tri_scalars)

    @skipUnless(NUMPY_STL_AVAILABLE, "numpy-stl not installed")
    def test_doc_08(self):
        import vtkplotlib as vpl
        from stl.mesh import Mesh
        import numpy as np

        path = vpl.data.get_rabbit_stl()
        mesh = Mesh.from_file(path)

        # This is the length of each side of each triangle.
        edge_scalars = vpl.geometry.distance(mesh.vectors[:,
                                                          np.arange(1, 4) % 3] -
                                             mesh.vectors)

        vpl.mesh_plot_with_edge_scalars(mesh, edge_scalars, centre_scalar=0,
                                        cmap="Greens")

#        vpl.show()

    @checker()
    def test_doc_09(self):
        import vtkplotlib as vpl
        import numpy as np

        phi, theta = np.meshgrid(np.linspace(0, 2 * np.pi, 1024),
                                 np.linspace(0, np.pi, 1024))

        x = np.cos(phi) * np.sin(theta)
        y = np.sin(phi) * np.sin(theta)
        z = np.cos(theta)

        vpl.surface(x, y, z)

#        vpl.show()

    @checker()
    def test_doc_10(self):
        import vtkplotlib as vpl
        import numpy as np

        # Create a ball at a point in space.
        point = np.array([1, 2, 3])
        vpl.scatter(point)

        vpl.annotate(point, "This ball is at {}".format(point),
                     np.array([0, 0, 1]))
#        vpl.show()

    @checker()
    def test_doc_11(self):
        import vtkplotlib as vpl
        import numpy as np

        # Create several balls.
        points = np.random.uniform(-30, 30, (30, 3))
        vpl.scatter(points, color=np.random.random(points.shape))

        vpl.annotate(points, "This ball is the highest", np.array([0, 0, 1]),
                     text_color="k", arrow_color="orange")

        vpl.annotate(points, "This ball is the lowest", np.array([0, 0, -1]),
                     text_color="rust", arrow_color="hunter green")


#        vpl.show()

    @checker()
    def test_doc_12(self):
        import numpy as np

        polydata = vpl.PolyData()

        polydata.points = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], float)

        # Create a wire-frame triangle passing points [0, 1, 2, 0].
        polydata.lines = np.array([[0, 1, 2, 0]])

        # Create a solid triangle with points [0, 1, 2] as it's corners.
        polydata.polygons = np.array([[0, 1, 2]])

        # The polydata can be quickly inspected using
        if not VTKPLOTLIB_WINDOWLESS_TEST:
            polydata.quick_show()

        # When you are happy with it, it can be turned into a proper plot
        # object like those output from other ``vpl.***()`` commands. It will be
        # automatically added to ``vpl.gcf()`` unless told otherwise.
        plot = polydata.to_plot()

    @checker()
    def test_doc_13(self):
        vpl.quick_test_plot()

    def test_doc_14(self):
        import numpy as np

        vpl.zip_axes(np.arange(10), 4, np.arange(-5, 5))

        # Out: array([[ 0,  4, -5],
        #             [ 1,  4, -4],
        #             [ 2,  4, -3],
        #             [ 3,  4, -2],
        #             [ 4,  4, -1],
        #             [ 5,  4,  0],
        #             [ 6,  4,  1],
        #             [ 7,  4,  2],
        #             [ 8,  4,  3],
        #             [ 9,  4,  4]])

    @checker()
    def test_doc_035(self):
        import numpy as np

        # Define the 2 independent variables
        phi, theta = np.meshgrid(np.linspace(0, 2 * np.pi, 1024),
                                 np.linspace(0, np.pi, 1024))

        # Calculate the x, y, z values to form a sphere
        x = np.cos(phi) * np.sin(theta)
        y = np.sin(phi) * np.sin(theta)
        z = np.cos(theta)

        # You can play around with this. The coordinates must be zipped
        # together into one array with ``shape[-1] == 2``, hence the
        # ``vpl.zip_axes``. And must be between 0 and 1, hence the ``% 1.0``.
        texture_coords = (vpl.zip_axes(phi * 3, theta * 5) / np.pi) % 1.0

        # Pick an image to use. There is a picture of a shark here if you
        # don't have one available.
        path = vpl.data.ICONS["Right"]
        texture_map = vpl.TextureMap(path, interpolate=True)

        # You could convert ``texture_coords`` to ``colors`` now using.
        # colors = texture_map(texture_coords)
        # then pass ``colors`` as the `scalars` argument instead.

        vpl.surface(x, y, z, scalars=texture_coords, texture_map=texture_map)

    @classmethod
    def tearDownClass(cls):
        print("tear down")
        if PyQt5_AVAILABLE:
            qapp = QtWidgets.QApplication.instance()
            if qapp:
                qapp.exit()
                qapp.quit()

if __name__ == "__main__":
    pass
