#!/usr/bin/env bash

# This example replaces the input PDF file instead of writing to a separate output file.

cp ../input/numbered.pdf ../output/replace_input.pdf

../../pdfsak --input-file ../output/replace_input.pdf --replace-input --extract-pages "1"
