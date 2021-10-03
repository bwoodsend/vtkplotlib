#encoding: utf-8
"""Test the oddities."""

from __future__ import division

import vtkplotlib as vpl

from tests._common import requires_interaction


def test_data():
    vpl.data.assert_ok()


@requires_interaction
def test_figure_contents_check():
    from tests._common import test_checker
    test_checker()
