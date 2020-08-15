# -*- coding: utf-8 -*-
# =============================================================================
# Created on Sat Feb 29 07:31:44 2020
#
# @author: Brénainn Woodsend
#
#
# _common.py
# Shared variables/markers for testing.
# Copyright (C) 2019-2020  Brénainn Woodsend
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

from builtins import super
import future.utils

import os
import numpy as np
from pathlib2 import Path

import pytest

try:
    import inspect

except ImportError:
    VTKPLOTLIB_WINDOWLESS_TEST = False
    DEFAULT_MODE = ""
else:
    VTKPLOTLIB_WINDOWLESS_TEST = bool(
        int(os.environ.get("VTKPLOTLIB_WINDOWLESS_TEST", "0")))

    if VTKPLOTLIB_WINDOWLESS_TEST:
        DEFAULT_MODE = "r"
    else:
        DEFAULT_MODE = "w"

TEST_DIR = Path(__file__).parent.absolute().resolve() / "temp"
TEST_DIR.mkdir(exist_ok=True)


class AutoChecker(object):
    """Attempts to assess reproducibility of visualisations between runs so I
    don't have to manually click through each test to verify that it looks OK.

    Wraps around any test function which plots something but doesn't call
    ``vpl.show()`` at the end. The wrapped function, if called in **write** mode
    (determined by the **mode** argument to that newly wrapped function) it will
    call the original function, screenshot and store the image, then call
    ``vpl.show()`` so you can verify it. If called in **read** mode, then it
    will call the original function, screenshot the result and verify it matches
    the stored one, then closes so that you don't have to interact with it."""

    def __init__(self):
        self.path = TEST_DIR / "test-data.json"
        self.load()

    def auto_check_contents(self, test_func):
        name = self.name_function(test_func)

        def wrapped(testcase=None, mode=DEFAULT_MODE):
            from vtkplotlib.figures.figure_manager import gcf, close, show

            close()

            np.random.seed(0)
            if testcase is None:
                out = test_func()
            else:
                out = test_func(testcase)
            from vtkplotlib.plots.BasePlot import BasePlot
            from vtkplotlib.figures.BaseFigure import BaseFigure
            if isinstance(out, BasePlot):
                out = None
            if out is None:
                out = gcf()

            if isinstance(out, BaseFigure):
                fig = out
            else:
                fig = "gcf"

            if mode == "r":
                correct_value = self.data[name]
                self.validate(self.reduce(out), correct_value)
                close(fig=fig)
            elif mode == "w":
                self.data[name] = self.reduce(out)
                if not isinstance(out, np.ndarray):
                    show(fig=fig)
                self.save()
            else:
                show(fig=fig)

        return wrapped

    __call__ = auto_check_contents

    @staticmethod
    def reduce_image_array(arr):
        """Serialise an image array into something that can go into a json file
        i.e plain text."""
        # Ideally I'd just use 'shape' and 'crc32_checksum' but there are
        # subtle, visually invisible differences between snapshots from
        # different OSs and VTK versions. So image matching must be fuzzy
        # meaning we have to store the whole image.
        # Interestingly bz2 gives better compression than PNG.
        import zlib, bz2, base64
        return {
            "shape": list(arr.shape),
            "crc32_checksum": zlib.crc32(arr.tobytes("C")),
            "image": base64.b64encode(bz2.compress(arr.tobytes("C"))).decode()
        }

    @classmethod
    def reduce_fig(cls, fig):
        from vtkplotlib.figures.figure_manager import screenshot_fig
        return cls.reduce_image_array(screenshot_fig(fig=fig))

    @classmethod
    def reduce(cls, obj):
        if isinstance(obj, dict):
            return obj
        if isinstance(obj, np.ndarray):
            return cls.reduce_image_array(obj)
        return cls.reduce_fig(obj)

    def save(self):
        import json
        text = json.dumps(self.data, indent=2)
        if future.utils.PY2:
            self.path.write_bytes(text)
        else:
            self.path.write_text(text)

    def load(self):
        import json
        if self.path.exists():
            if future.utils.PY2:
                text = self.path.read_bytes()
            else:
                text = self.path.read_text()
            self.data = json.loads(text)
        else:
            self.data = {}

    @staticmethod
    def name_function(func):
        module = inspect.getmodulename(func.__code__.co_filename)
        name = str(module) + "." + func.__name__
        assert "__main__" not in name
        return name

    def validate(self, old_dic, new_dic):
        assert old_dic["shape"] == new_dic["shape"]
        if old_dic["crc32_checksum"] == new_dic["crc32_checksum"]:
            return True
        old_im = self.extract_dic_image(old_dic)
        new_im = self.extract_dic_image(new_dic)
        self.assertLess(np.abs(old_im - new_im.astype(float)).mean(), 5)

    @staticmethod
    def extract_dic_image(dic):
        import bz2, base64
        shape = dic["shape"]
        bin = bz2.decompress(base64.b64decode(dic["image"].encode()))
        arr = np.frombuffer(bin, np.uint8).reshape(shape)
        return arr

    def show_saved(self, func_name):
        from matplotlib import pylab
        pylab.imshow(self.extract_dic_image(self.data[func_name]))
        pylab.show()


_checker = None


def checker(*no_arguments):
    if len(no_arguments):
        raise TypeError("Checker takes no arguments. You probably forgot the "
                        "parenthesis. Should be `@checker()\\n"
                        "def function...`.")
    global _checker
    if _checker is None:
        _checker = AutoChecker()
    return _checker


def reset():
    checker().data.clear()
    checker().save()
    global _checker
    _checker = None


@checker()
def test_quick_test_plot():
    import vtkplotlib as vpl
    vpl.quick_test_plot()


def test_checker():

    test_quick_test_plot(mode=DEFAULT_MODE and "w")

    checker().save()
    checker().load()

    test_quick_test_plot(mode=DEFAULT_MODE and "r")


requires_interaction = pytest.mark.skipif(VTKPLOTLIB_WINDOWLESS_TEST,
                                          reason="Requires manual interaction.")


def numpy_stl():
    return pytest.importorskip("stl.mesh", reason="Requires numpy-stl")


if __name__ == "__main__":
    test_checker()
