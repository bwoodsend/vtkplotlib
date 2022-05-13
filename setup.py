# -*- coding: utf-8 -*-
"""
"""

from setuptools import setup, find_packages
import runpy
from os.path import dirname, join

HERE = dirname(__file__)

with open(join(HERE, 'README.md'), "rb") as f:
    long_description = f.read().decode("utf-8")

setup(
    name='vtkplotlib',
    version=runpy.run_path(join(HERE, "vtkplotlib/_version.py"))["__version__"],
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
        "matplotlib",
    ],
    zip_safe=False,
    extras_require={
        "test_minimal": ["pytest", "pytest-order"],
        "test_full": [
            "pytest",
            "pytest-order",
            "PyQt5",
            "numpy-stl",
            "namegenerator",
            "pillow",
        ],
    },
    entry_points={
        "pyinstaller40": ["hook-dirs = vtkplotlib.data:_get_hooks_dir"]
    },
    python_requires=">=3.6",
)
