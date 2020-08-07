# Configuration file for the Sphinx documentation builder.

# -- Path setup --------------------------------------------------------------
# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
import os
import sys
import re
sys.path.insert(0, os.path.abspath('../'))
sys.path.insert(0, os.path.abspath('../slab/'))

# extract version
with open('../_version.py') as f:
    version_file_content = f.read().strip()

pattern = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(pattern, version_file_content, re.M)
if mo:
    version = mo.group(1)
else:
    raise RuntimeError('Unable to find version string in _version.py')

# -- Project information -----------------------------------------------------
project = 'slab'
copyright = '2020, Marc Schoenwiesner, Ole Bialas'
author = 'Marc Schoenwiesner, Ole Bialas'
release = version

# -- General configuration ---------------------------------------------------
needs_sphinx = '1.8'
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.intersphinx', 'sphinx.ext.napoleon']
master_doc = 'index'
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
#autodoc_default_options = {'member-order': 'bysource'}
intersphinx_mapping = {'python': ('https://docs.python.org/', None),
                       'matplotlib': ('http://matplotlib.org/', None),
                       'numpy': ('http://docs.scipy.org/doc/numpy/', None),
                       'scipy': ('http://docs.scipy.org/doc/scipy/reference/', None)}
html_theme = 'alabaster'
