#!/usr/bin/python3
#coding=utf8
import sys
sys.path = ["../"]+sys.path
import pdftools
cmdstr = ("--input-file ./pdfs/wikipedia_algorithm.pdf --input-file ./pdfs/wikipedia_bubble_sort.pdf --output ./out/merge.pdf").split()
pdftools.main(cmdstr)