# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 19:00:26 2019

@author: Brénainn
"""

from setuptools import setup, find_packages
from os import path


with open(path.join(path.split(__file__)[0], "README.md"), "r") as fh:
    long_description = fh.read()

setup(name='vtkplotlib',
      version='1.3.4',
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
      )