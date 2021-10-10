#!/usr/bin/env bash

# This example creates a 2x2 lecture handout
# Every page of the output file is a 2x2 grid (2 rows and 2 columns)
# The left columns will contain pages from the input PDF file
# The right columns will be white

../../pdfsak --input-file ../input/presentation.pdf --output ../output/handout2x2_W.pdf --add-white-pages --overwrite

../../pdfsak --input-file ../output/handout2x2_W.pdf --output ../output/handout2x2.pdf --nup 2 2 --height 0.32 --landscape --frame --paper a4paper --overwrite

rm ../output/handout2x2_W.pdf
