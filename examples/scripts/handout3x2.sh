#!/usr/bin/env bash

# This example creates a 3x2 lecture handout
# Every page of the output file is a 3x2 grid (3 rows and 2 columns)
# The left columns will contain pages from the input PDF file
# The right columns will be white

../../pdftools --input-file ../input/presentation.pdf --output ../output/handout3x2_W.pdf --add-white-pages --overwrite

../../pdftools --input-file ../output/handout3x2_W.pdf --output ../output/handout3x2.pdf --nup 3 2 --height 0.2 --landscape --frame --paper a4paper

rm ../output/handout3x2_W.pdf

