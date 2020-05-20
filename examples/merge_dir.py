#!/usr/bin/python3
#coding=utf8
import sys
sys.path = ["../"]+sys.path
import pdftools
cmdstr = ("--input-dir ./pdfs/ --output ./out/merge_dir.pdf").split()
pdftools.main(cmdstr)