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

import vtkplotlib as vpl

from tests._common import requires_interaction


def test_data():
    vpl.data.assert_ok()


@requires_interaction
def test_figure_contents_check():
    from tests._common import test_checker
    test_checker()
