#!/usr/bin/env bash

# This example adds:
# - Page numbers in the bottom right corner (in the format `current_page/total_pages`)
# - Current date in the top left corner (in the format `day/month/year`)

../pdftools.py --input-file ./input/wikipedia_algorithm.pdf --output ./output/addtext.pdf --text "\huge \$page/\$pages" br 1 1 --text "\huge \$day/\$month/\$year" tl 0.01 0.01 --overwrite
