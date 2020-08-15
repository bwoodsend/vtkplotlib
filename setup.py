# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 19:00:26 2019

@author: Brénainn
"""

from setuptools import setup, find_packages
from distutils.command.build import build
import sys
from os import path

HERE = path.split(__file__)[0]

with open(path.join(HERE, "README.md"), "r") as fh:
    long_description = fh.read()

with open(path.join(HERE, "version"), "r") as fh:
    version = fh.read().strip().lstrip("v")


class Build(build):

    def run(self):
        with open(path.join(HERE, "vtkplotlib", "__version__.py"), "w") as fh:
            fh.write("# -*- coding: utf-8 -*-\n__version__ = \"{}\"\n"
                     .format(version)) # yapf: disable
        build.run(self)

setup(name='vtkplotlib',
      version=version,
      description='High level 3D graphics and plotting powered by VTK',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://vtkplotlib.readthedocs.io/en/latest/index.html',
      author='Brénainn Woodsend',
      author_email='bwoodsend@gmail.com',
      license='GNU version 3.0',
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
      cmdclass={"build": Build}
      ) # yapf:disable
