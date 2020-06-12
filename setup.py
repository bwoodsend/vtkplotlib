# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 19:00:26 2019

@author: Brénainn
"""

from setuptools import setup, find_packages
from distutils.command.build import build
from os import path

HERE = path.split(__file__)[0]

with open(path.join(HERE, "README.md"), "r") as fh:
    long_description = fh.read()

with open(path.join(HERE, "version"), "r") as fh:
    version = fh.read().strip().lstrip("v")

class Build(build):
    def run(self):
        with open(path.join(HERE, "vtkplotlib", "__version__.py"), "w") as fh:
            fh.write("# -*- coding: utf-8 -*-\n__version__ = \"{}\"\n".format(version))
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
      packages=find_packages(),
      include_package_data=True,
      install_requires=[
             "vtk",
             "numpy",
             "pathlib2",
             "matplotlib",
             "future",
              ],
      zip_safe=False,
      test_suite='nose.collector',
      tests_require=['nose'],
      cmdclass={"build": Build}
      )