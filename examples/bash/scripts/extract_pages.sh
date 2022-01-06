#!/usr/bin/env bash

# This example extract pages 1, 3, and from 20 onwards

../../../pdfsak --input-file ../../input/numbered.pdf --output ../../output/extract_pages.pdf --extract-pages "1,3,20-"
