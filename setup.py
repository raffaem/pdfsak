#!/usr/bin/env python

import setuptools
from pdfsak_version import __version__

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pdfsak",
    version=__version__,
    author="Raffaele Mancuso",
    author_email="raffaelemancuso532@gmail.com",
    description="Utility to manipulate PDF files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/raffaem/pdftools",
    project_urls={
        "Bug Tracker": "https://github.com/raffaem/pdftools/issues",
        "Documentation": "https://pdfsak.readthedocs.io"
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    scripts=['./pdfsak', './pdfsak.bat', './pdfsak_version.py'],
    python_requires=">=3.6",
)
