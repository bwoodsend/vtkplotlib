#encoding: utf-8
# =============================================================================
# Created on Tue Sep 24 08:34:56 2019
#
# @author: Brénainn Woodsend
#
#
# test_extras.py tests everything that isn't tested in the other test modules.
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

from __future__ import division

from unittest import TestCase, main, skipUnless, skipIf
import numpy as np

import vtkplotlib as vpl
from vtkplotlib.tests.base import BaseTestCase
from vtkplotlib.tests._figure_contents_check import VTKPLOTLIB_WINDOWLESS_TEST

try:
    from stl.mesh import Mesh
except ImportError:
    Mesh = None


class TestExtras(BaseTestCase):

    def test_as_rgb_a(self):
        rgb, a = (np.array([0.00392157, 1., 0.02745098]), .5)

        for i in [
            (rgb, a),
            (tuple(rgb) + (a,),),
            ((rgb * 255).astype(int), int(a * 255)),
            ("bright green", a),
            ("BRIGHT-GREEN", a),
            ("BRIGHT_GrEeN", a),
            ("#01FF06", a * 255),
        ]:
            _rgb, _a = vpl.colors.as_rgb_a(*i)
            #            print(_rgb, _a)
            self.assertTrue(np.allclose(rgb, _rgb, atol=1 / 255),
                            msg="{} != {}".format(rgb, _rgb))
            self.assertLess(abs(a - _a), 1 / 255)

        self.assertEqual(vpl.colors.as_rgb_a("not a color"), (None, None))

    def test_unicode_paths(self):
        from vtkplotlib.unicode_paths import test
        test()

    def test_data(self):
        vpl.data.assert_ok()

    def test_image_io(self):
        from vtkplotlib import _image_io
        _image_io.test()

    @skipIf(VTKPLOTLIB_WINDOWLESS_TEST, "Requires manual interaction.")
    def test_figure_contents_check(self):
        from vtkplotlib.tests._figure_contents_check import test
        test()
