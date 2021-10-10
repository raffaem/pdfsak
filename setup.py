#!/usr/bin/env python

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pdfsak",
    version="1.0",
    author="Raffaele Mancuso",
    author_email="raffaelemancuso532@gmail.com",
    description="Utility to manipulate PDF files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/raffaem/pdftools",
    project_urls={
        "Bug Tracker": "https://github.com/raffaem/pdftools/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    scripts=['./pdftools'],
    python_requires=">=3.6",
)
