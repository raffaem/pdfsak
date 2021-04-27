#!/usr/bin/env bash

# This example split the pages of a input PDF file in half vertically,
# Page 1 of output PDF file contains the _left_ part of page 1 of input PDF file.
# Page 2 of output PDF file contains the _right_ part of page 1 of input PDF file.
# And so on...

../pdftools.py --input-file ./input/wikipedia_algorithm.pdf --output ./output/splitpages.pdf --split-pages --trim 0 0 0.5 0 --overwrite
