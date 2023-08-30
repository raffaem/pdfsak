#!/usr/bin/env bash

# This example adds:
# - Page numbers in the bottom right corner (in the format `current_page/total_pages`)
# - Current date in the top left corner (in the format `day/month/year`)

../../../pdfsak --input-file ../../input/article1.pdf --output ../../output/addtext.pdf --font "EB Garamond" --text "\huge \$page/\$pages" br 1 1 --text "\huge \$day/\$month/\$year" tl 0 0 --overwrite --latex-engine xelatex

