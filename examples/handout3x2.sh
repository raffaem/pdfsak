#!/usr/bin/env bash

../pdftools.py --input-file ./input/lectureslides.pdf --output ./output/handout3x2_W.pdf --white-page --overwrite

../pdftools.py --input-file ./output/handout3x2_W.pdf --output ./output/handout3x2.pdf --nup 3 2 --height 0.2 --landscape --frame --overwrite --paper a4paper --text \$filename tl 0.4 0.01

