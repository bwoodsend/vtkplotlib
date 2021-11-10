# -*- coding: utf-8 -*-
"""
Freeze pytest.main() with vtkplotlib included.
"""
import sys
import vtkplotlib

import pytest

sys.exit(pytest.main(sys.argv[1:] + ["--no-cov", "--tb=native"]))
