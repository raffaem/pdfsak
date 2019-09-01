#!/usr/bin/python3
#coding=utf8
import pdftools, sys, shlex
cmdstr = '-i \"'+sys.argv[1]+'\" --out-suffix _nup12land --nup 1 2 --overwrite --landscape'
cmdstr_splitted = shlex.split(cmdstr)
#print(cmdstr_splitted)
pdftools.main(cmdstr_splitted)