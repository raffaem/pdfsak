#!/usr/bin/env bash

# This example swap the pages of an input PDF file

../../pdftools.py --input-file ../input/numbered.pdf --output ../output/swap_pages_start.pdf --swap-pages "1,2;3,4"
