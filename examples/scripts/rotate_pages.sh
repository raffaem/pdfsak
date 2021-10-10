#!/usr/bin/env bash

# This example rotate the pages of a input PDF file

../../pdftools --input-file ../input/numbered.pdf --output ../output/rotate_pages.pdf --overwrite --rotate-pages "2=90;3=180;4=270;5=45" 
