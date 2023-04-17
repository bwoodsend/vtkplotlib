# -*- coding: utf-8 -*-
"""
Shared variables/markers for testing.
"""

from pathlib import Path

import pytest

TEST_DIR = Path(__file__).parent.absolute().resolve() / "temp"
TEST_DIR.mkdir(exist_ok=True)


def numpy_stl():
    return pytest.importorskip("stl.mesh", reason="Requires numpy-stl")
