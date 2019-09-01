#!/usr/bin/python3
#coding=utf8
import sys
sys.path = ["../"]+sys.path
import pdftools
cmdstr = ("-i ./pdfs/lshort.pdf --out-suffix _addtext --text $page/$pages 0.9 0.9 --text $day/$month/$year 0.1 0.1 --fitpaper --overwrite").split()
pdftools.main(cmdstr)