# -*- coding: utf-8 -*-
#
# Configuration file for the Sphinx documentation builder.
#
# This file does only contain a selection of the most common options. For a
# full list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))

# -- Project information -----------------------------------------------------

project = 'vtkplotlib'
copyright = '2019-2020, bwoodsend'
author = 'bwoodsend'

# The full version, including alpha/beta/rc tags
from vtkplotlib import __version__ as release
# The short X.Y version
version = ".".join(release.split(".")[:2])

# -- General configuration ---------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.mathjax',
    'sphinx.ext.githubpages',
    'sphinx_copybutton',
    'm2r2',
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.doctest',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
source_suffix = ['.rst', '.md']

# The master toctree document.
master_doc = 'index'

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = None

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
# html_theme_options = {}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# The default sidebars (for documents that don't match any pattern) are
# defined by theme itself.  Builtin themes are using these templates by
# default: ``['localtoc.html', 'relations.html', 'sourcelink.html',
# 'searchbox.html']``.
#
# html_sidebars = {}

# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'vtkplotlibdoc'

# -- Options for LaTeX output ------------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',

    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, document-class [howto, manual, or own class]).
latex_documents = [(master_doc, 'vtkplotlib.tex', 'vtkplotlib Documentation',
                    author, 'manual')]

# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [(master_doc, 'vtkplotlib', 'vtkplotlib Documentation', [author], 1)
            ]

# -- Options for Texinfo output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'vtkplotlib', 'vtkplotlib Documentation', author, 'vtkplotlib',
     'One line description of project.', 'Miscellaneous'),
]

# -- Options for Epub output -------------------------------------------------

# Bibliographic Dublin Core info.
epub_title = project

# The unique identifier of the text. This can be a ISBN number
# or the project homepage.
#
# epub_identifier = ''

# A unique identification for the text.
#
# epub_uid = ''

# A list of files that should not be packed into the epub file.
epub_exclude_files = ['search.html']

# -- Extension configuration -------------------------------------------------

# -- Options for todo extension ----------------------------------------------

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

# -- Globally defined substitutions to be used in rst files -----------------

rst_epilog = "\n"


def add_url(name, url):
    "Convenience way to create URLs."
    global rst_epilog
    rst_epilog += ".. _{}: {}\n".format(name, url)


for vtk_name in [
        'vtkActor', 'vtkActor2D', 'vtkArrowSource', 'vtkBMPReader',
        'vtkBMPWriter', 'vtkCellArray', 'vtkCommand', 'vtkCubeSource',
        'vtkCursor3D', 'vtkFollower', 'vtkImageData', 'vtkImageMapper',
        'vtkInteractorStyleImage', 'vtkInteractorStyleTrackballCamera',
        'vtkJPEGReader', 'vtkJPEGWriter', 'vtkLegendBoxActor', 'vtkLookupTable',
        'vtkMatrix4x4', 'vtkPNGReader', 'vtkPNGWriter', 'vtkPoints',
        'vtkPolyData', 'vtkPolyDataMapper', 'vtkPolyDataReader',
        'vtkPolyDataWriter', 'vtkRenderWindow', 'vtkRenderWindowInteractor',
        'vtkRenderer', 'vtkSTLReader', 'vtkScalarBarActor', 'vtkSphereSource',
        'vtkTIFFReader', 'vtkTIFFWriter', 'vtkTextActor', 'vtkTransform',
        'vtkVectorText', 'vtkWindowToImageFilter', 'vtkObject',
        'vtkInteractorStyle'
]:
    add_url(vtk_name,
            "https://vtk.org/doc/nightly/html/class%s.html#details" % vtk_name)

add_url("wxPython", "https://www.wxpython.org/")

# Borrowed from quickstart.rst
rst_epilog += """
.. _numpy: http://numpy.org/
.. _matplotlib: http://matplotlib.org/
.. _pathlib2: https://pypi.org/project/pathlib2/
.. _vtk: https://pypi.org/project/vtk/
.. _PyQt5: https://pypi.org/project/PyQt5/
.. _numpy-stl: https://pypi.org/project/numpy-stl/
.. _future: https://pypi.org/project/future/
.. _PyInstaller: https://www.pyinstaller.org/
.. _namegenerator: https://pypi.org/project/namegenerator/
"""

# -- Add this file for Google search console ----------
html_extra_path = ["google77eb9775385691af.html"]

# --- Option for autosectionlabel --------

autosectionlabel_prefix_document = True
