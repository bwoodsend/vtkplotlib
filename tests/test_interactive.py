# -*- coding: utf-8 -*-
# =============================================================================
# Created on 19:15
#
# @author: Brénainn
#
#
# test_interactive.py
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

from __future__ import print_function, unicode_literals, with_statement
from builtins import super

import numpy as np
import os, sys
from pathlib2 import Path

import pytest
import vtkplotlib as vpl

from tests._common import checker


@pytest.mark.parametrize("invoker", [vpl.gcf().style, vpl.gcf().iren])
@pytest.mark.parametrize("command", vpl.i.vtkCommands)
def test_super_command(invoker, command):
    cb = vpl.i.get_super_callback(invoker, command)
    assert cb is vpl.i.null_super_callback or cb.__self__ is invoker


def test_raise():
    with pytest.raises(RuntimeError):
        vpl.i.get_super_callback()

    def _test(x, y, z):
        vpl.i.get_super_callback()

    with pytest.raises(RuntimeError):
        _test(1, 2, 3)


from tests import docs_code_blocks
for (obj, doc) in docs_code_blocks.docs_from_objects(vpl.i).items():
    globals().update(docs_code_blocks.tests_from_doc(doc, repr(obj)))

if __name__ == "__main__":
    pytest.main([__file__])
