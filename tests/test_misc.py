#encoding: utf-8
"""Test the oddities."""

import pytest

import vtkplotlib as vpl

pytestmark = pytest.mark.order(4)


def test_data():
    vpl.data.assert_ok()
