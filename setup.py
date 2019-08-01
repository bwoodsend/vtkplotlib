# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 19:00:26 2019

@author: Brénainn
"""

from setuptools import setup

setup(name='vtkplotlib',
      version='0.1',
      description='3d plotting using vtk',
      url='https://github.com/bwoodsend/vtkplotlib',
      author='Brénainn Woodsend',
      author_email='bwoodsend@gmail.com',
      license='MIT',
      packages=['vtkplotlib'],
      package_dir={'vtkplotlib': 'vtkplotlib'},
      package_data={'vtkplotlib': ['data/*']},
      data_files=[('icons', ['data/icons/*']),
                  ('models', ['data/models/*'])],
      install_requires=[
             # "vtk", 
             # "numpy",
             # "PyQt5",
              ],
      zip_safe=False,
      )