# -*- coding: utf-8 -*-
"""
"""

from setuptools import setup, find_packages
import sys
from os import path
import runpy

HERE = path.split(__file__)[0]

with open(path.join(HERE, "README.md"), "r") as fh:
    long_description = fh.read()

version = runpy.run_path(
    path.join(HERE, "vtkplotlib", "__version__.py"),
)["__version__"]

setup(name='vtkplotlib',
      version=version,
      description='High level 3D graphics and plotting powered by VTK',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://vtkplotlib.readthedocs.io/en/latest/index.html',
      author='Brénainn Woodsend',
      author_email='bwoodsend@gmail.com',
      license='MIT',
      packages=find_packages(exclude=("tests",)),
      include_package_data=True,
      install_requires=[
             "vtk",
             "numpy",
             "pathlib2",
             "matplotlib",
             "future",
              ],
      zip_safe=False,
      extras_require={
          "test_minimal": ["pytest"],
          "test_full": ["pytest",
                        "PyQt5" if sys.version_info.major >= 3 else "python_qt5",
                        "numpy-stl", "namegenerator", "PILLOW"],
      },
      entry_points={
          "pyinstaller40": ["hook-dirs = vtkplotlib.data:_get_hooks_dir"]
      },
      ) # yapf:disable
