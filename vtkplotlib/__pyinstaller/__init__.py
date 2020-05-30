# .. Copyright © 2020 PyInstaller Development Team
#
#   This file is part of PyInstaller Hook Sample.
#
#   PyInstaller Hook Sample is free software; you can redistribute it and/or
#   modify it under the terms of the GNU General Public License as published
#   by the Free Software Foundation; either version 3 of the License, or (at
#   your option) any later version.
#
#   PyInstaller Hook Sample is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
#   Public License for more details.
#
#   You should have received a copy of the GNU General Public License along
#   with PyInstaller Hook Sample. If not, see <http://www.gnu.org/licenses/>.
#
#   SPDX-License-Identifier: GPL-3.0-or-later
#
# ********************************************************
# ``__pyinstaller/`` |docname| - Provide PyInstaller hooks
# ********************************************************
#
#
# This package provides a hook for PyInstaller
# needed to successfully freeze
# the :doc:`pyi_hooksample package <../__init__.py>`.
# It also provides tests for that hook.
#
# .. toctree::
#   :maxdepth: 1
#
#   hook-pyi_hooksample.py
#   test_hooksample_packaging.py

# For demonstration
# purposes, it also includes the rarely used advanced hook types
# (run-time, pre-find module path, pre-safe import module), though
# these hooks perform no useful role in freezing this project.
#
# .. toctree::
#   :maxdepth: 1
#
#   rthooks/pyi_rth_hooksample.py
#   rthooks.dat
#   rthooks/__init__.py
#   pre_find_module_path/hook-pyi_hooksample.py
#   pre_find_module_path/__init__.py
#   pre_safe_import_module/hook-pyi_hooksample.py
#   pre_safe_import_module/__init__.py

import os

# Functions
# =========
#
# .. _get_hook_dirs:
#
# get_hook_dirs
# -------------
#
# Tell PyInstaller where to find hooks provided by this distribution;
# this is referenced by the :ref:`hook registration <hook_registration>`.
# This function returns a list containing only the path to this
# directory, which is the location of these hooks.

def get_hook_dirs():
    return [os.path.dirname(__file__)]


# .. _get_PyInstaller_tests:
#
# get_PyInstaller_tests
# ---------------------
#
# Tell PyInstaller where to find tests of the hooks provided by this
# distribution; this is referenced by the :ref:`tests registration
# <tests_registration>`. This function returns a list containing only
# the path to this directory, which is the location of these tests.

def get_PyInstaller_tests():
    return [os.path.dirname(__file__)]
