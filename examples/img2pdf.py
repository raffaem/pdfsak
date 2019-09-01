#!/usr/bin/python3
#coding=utf8
import pdftools, sys
cmdstr = ("-i ./img/i1.jpg -i ./img/i2.jpg --paper A4 -o ./pdfs/img.pdf --debug --debug-no-compile").split()
pdftools.main(cmdstr)