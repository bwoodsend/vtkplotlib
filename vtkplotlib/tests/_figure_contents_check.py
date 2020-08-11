# -*- coding: utf-8 -*-
# =============================================================================
# Created on Sat Feb 29 07:31:44 2020
#
# @author: Brénainn Woodsend
#
#
# Checks consistency of test outputs across different platforms.
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

from vtkplotlib.data import DATA_FOLDER
import os
import numpy as np

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


class AutoChecker(object):

    def __init__(self):
        self.path = DATA_FOLDER / "test-data.json"
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


def test():

    test_quick_test_plot(mode=DEFAULT_MODE and "w")

    checker().save()
    checker().load()

    test_quick_test_plot(mode=DEFAULT_MODE and "r")


if __name__ == "__main__":
    test()
