#!/usr/bin/env bash

# This example extract the pages of a input PDF file

cp ../input/numbered.pdf ../output/replace_input.pdf

../../pdftools --input-file ../output/replace_input.pdf --replace-input --extract-pages "1"
