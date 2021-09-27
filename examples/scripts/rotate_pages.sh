#!/usr/bin/env bash

# This example swap the pages of a input PDF file

../pdftools.py --input-file ../input/numbered.pdf --output ../output/rotate_pages.pdf --overwrite --rotate-pages "1=90;2=180;4=270" 
