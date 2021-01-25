#!/usr/bin/env bash

../pdftools.py --input-file ./input/lectureslides.pdf --output ./output/handout2x2_W.pdf --white-page --overwrite

../pdftools.py --input-file ./output/handout2x2_W.pdf --output ./output/handout2x2.pdf --nup 2 2 --height 0.32 --landscape --frame --overwrite --paper a4paper --text \$filename tl 0.4 0.01
