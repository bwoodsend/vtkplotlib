# -*- coding: utf-8 -*-
# =============================================================================
# Created on Sat Aug  3 21:02:41 2019
#
# @author: Brénainn Woodsend
#
#
# test_figures.py tests the contents of the vtkplotlib.figures subpackage.
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

from __future__ import unicode_literals

import numpy as np
import matplotlib.pylab as plt
import os
import sys
from pathlib2 import Path

import vtkplotlib as vpl
import time
from unittest import TestCase, main, skipUnless


class TestFigures(TestCase):
    def test_figure_io(self):
        vpl.close()
        self.assertIs(vpl.gcf(False), None)

        vpl.auto_figure(False)
        self.assertIs(vpl.gcf(), None)

        with self.assertRaises(vpl.figures.figure_manager.NoFigureError):
            vpl.screenshot_fig()

        fig = vpl.figure()
        self.assertIs(vpl.gcf(), None)
        del fig

        vpl.auto_figure(True)
        fig = vpl.gcf()
        self.assertTrue(fig is not None)


        self.assertIs(fig, vpl.gcf())
        vpl.close()
        self.assertIs(vpl.gcf(False), None)
        vpl.scf(fig)
        self.assertIs(fig, vpl.gcf())

        vpl.close()
        fig = vpl.figure()
        self.assertIs(fig, vpl.gcf())
        vpl.close()




    def test_save(self):
        plots = vpl.scatter(np.random.uniform(-10, 10, (30, 3)))

        # I can't get python2 to cooperate with unicode here.
        # The os functions just don't like them.
        if sys.version[0] == "3":

            path = Path.cwd() / u"ҢघԝઌƔࢳܢˀા\\Հએࡓ\u061cཪЈतயଯ\u0886.png"
            try:
                os.mkdir(str(path.parent))
                vpl.save_fig(path)
                self.assertTrue(path.exists())
                os.remove(str(path))
            finally:
                if path.parent.exists():
                    os.rmdir(str(path.parent))

        else:
            path = Path.cwd() / "image.png"
            vpl.save_fig(path)
            os.remove(str(path))

        array = vpl.screenshot_fig(2)
        self.assertEqual(array.shape,
                         tuple(i * 2 for i in vpl.gcf().render_size) + (3,))
        plt.imshow(array)
        plt.show()

        shape = tuple(i * j for (i, j) in zip(vpl.gcf().render_size, (2, 3)))
        vpl.screenshot_fig(pixels=shape).shape
        # The following will fail depending on VTK version
#        self.assertEqual(vpl.screenshot_fig(pixels=shape).shape,
#                         shape[::-1] + (3,))


        vpl.close()
        fig = vpl.figure()
        for plot in plots:
            fig += plot
        vpl.show()


    def test_view(self):
        vpl.auto_figure(True)
        vpl.close()
        grads = np.array(vpl.geometry.orthogonal_bases(np.random.rand(3)))
        point = np.random.uniform(-10, 10, 3)
        vpl.quiver(np.broadcast_to(point, (3, 3)),
                   grads,
                   color=np.eye(3))

        vpl.view(focal_point=point,
                 camera_position=point-grads[0],
                 up_view=grads[1])
#        vpl.view(camera_direction=grads[0],
#                 up_view=grads[1],
#                 )
#
        vpl.reset_camera()
#        vpl.view(point)


        vpl.text("Should be looking in the direction of the red arrow, with the green arrow pointing up")
        vpl.show()


    def test_multi_figures(self):
        vpl.close()

        vpl.auto_figure(False)

        plot = vpl.plot(np.random.uniform(-10, 10, (10, 3)), join_ends=True)
        figs = []
        for i in range(1, 4):
            fig = vpl.figure("figure {}".format(i))
            fig += plot
            vpl.view(camera_direction=np.random.uniform(-1, 1, 3), fig=fig)
            vpl.reset_camera(fig)

            fig.show(False)
            figs.append(fig)
        fig.show()

        vpl.auto_figure(True)


    @skipUnless(vpl.PyQt5_AVAILABLE, "PyQt5 not installed")
    def test_qfigure(self):
        fig = vpl.QtFigure("a qt widget figure")

        self.assertIs(fig, vpl.gcf())

        direction = np.array([1, 0, 0])
        vpl.quiver(np.array([0, 0, 0]), direction)
        vpl.view(camera_direction=direction)
        vpl.reset_camera()

        vpl.show()


    @skipUnless(vpl.PyQt5_AVAILABLE, "PyQt5 not installed")
    def test_qfigure2(self):
        fig = vpl.QtFigure2("a qt widget figure")
        self.assertIs(fig, vpl.gcf())

        vpl.scatter(np.arange(9).reshape((3, 3)).T)
        vpl.quick_test_plot()

        fig.add_all()


        fig.show(block=False)
        fig.qapp.processEvents()

        for i in fig.view_buttons.buttons:
            i.released.emit()
            fig.qapp.processEvents()
            time.sleep(.1)

        fig.screenshot_button.released.emit()
        fig.show_plot_table_button.released.emit()


        fig.show()



    def test_add_remove(self):
        fig = vpl.figure()
        plots = vpl.quick_test_plot(None)
        fig += plots
        fig.show(False)
        fig -= plots
        for i in plots:
            fig += i
            fig.update()
            time.sleep(.05)
        for i in plots:
            fig -= i
            fig.update()
            time.sleep(.05)
        vpl.close(fig)


if __name__ == "__main__":
    main(TestFigures())