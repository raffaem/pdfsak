#!/usr/bin/python3
#coding=utf8
import pdftools, sys
cmdstr = ("-i "+sys.argv[1]+" --out-suffix _1page --split-pages --trim 0 0 0.5\\pdfwidth 0 --overwrite").split()
pdftools.main(cmdstr)
