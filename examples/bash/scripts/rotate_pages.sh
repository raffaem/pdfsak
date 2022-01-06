#!/usr/bin/env bash

# This example rotate the pages of a input PDF file.
# The 2nd page is rotated 90 degrees counterclockwise.
# The 3rd page is rotated 180 degrees counterclockwise (it will be upside down).
# The 4th page is rotated 270 degrees counterclockwise.
# The 5th page is rotated 45 degrees counterclockwise.

../../../pdfsak --input-file ../../input/numbered.pdf --output ../../output/rotate_pages.pdf --overwrite --rotate-pages "2=90;3=180;4=270;5=45" 
