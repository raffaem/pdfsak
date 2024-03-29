# Configuration file for the Sphinx documentation builder.

# -- Project information

project = 'PDFsak'
copyright = '2022, Raffaele Mancuso'
author = 'Raffaele Mancuso'

import sys
sys.path.append("../../")
from pdfsak_version import __version__
parts = __version__.split(".")
release = parts[0] + "." + parts[1]
version = __version__

# -- General configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}
intersphinx_disabled_domains = ['std']

templates_path = ['_templates']

# -- Options for HTML output

html_theme = 'sphinx_rtd_theme'

# -- Options for EPUB output
epub_show_urls = 'footnote'
