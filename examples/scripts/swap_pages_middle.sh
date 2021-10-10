#!/usr/bin/env bash

# This example swap the pages of an input PDF file

../../pdfsak --input-file ../input/numbered.pdf --output ../output/swap_pages_middle.pdf --swap-pages "2,3;4,5"
