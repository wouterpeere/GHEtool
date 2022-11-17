# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#

from unittest.mock import Mock, MagicMock
import os
import sys

MOCK_MODULES = ['numpy', 'scipy', 'matplotlib', 'matplotlib.pyplot', 'scipy.interpolate', 'pygfunction', 'pickle',
                'warnings', 'scipy.signal', 'math', 'functools', 'PySide6.QtCore',
                'PySide6.QtGui', 'PySide6.QtWidgets']
for mod_name in MOCK_MODULES:
    sys.modules[mod_name] = Mock()


sys.path.insert(0, os.path.abspath('..'))
import GHEtool

# -- Project information -----------------------------------------------------

project = 'GHEtool'
copyright = '2022, Tobias Blanke & Wouter Peere'
author = 'Tobias Blanke, Wouter Peere'

# The full version, including alpha/beta/rc tags
release = '2.1.0dev'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.

# prevent circular imports...
# import sphinx.builders.html
# import sphinx.builders.latex
# import sphinx.builders.texinfo
# import sphinx.builders.text
# import sphinx.ext.autodoc

extensions = [
    'myst_parser',
    'sphinx.ext.autosectionlabel',
    'sphinx_rtd_theme',
    'sphinx.ext.imgmath'
    # 'sphinx.ext.autodoc',
    # 'numpydoc'
]


# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

rst_epilog = """
.. |n-choose-k| replace:: :math:`{[n] \choose k}`
"""


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['sources/_static']

