#!/usr/bin/env python3

import sys
if sys.version_info[0] < 3:
    print('pdftools require Python 3, you are using Python ' + '.'.join(str(x) for x in sys.version_info[:3]))
    sys.exit(1)

import pdftools_main
pdftools_main.main(sys.argv[1:])
