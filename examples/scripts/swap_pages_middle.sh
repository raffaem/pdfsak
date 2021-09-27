#!/usr/bin/env bash

# This example swap the pages of a input PDF file

../pdftools.py --input-file ./input/numbered.pdf --output ./output/swap_pages_middle.pdf --overwrite --swap-pages "2,3;4,5"
