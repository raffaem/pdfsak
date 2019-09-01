#!/usr/bin/python3
#coding=utf8
import pdftools, sys, shlex
cmdstr = '-i \"'+sys.argv[1]+'\" --out-suffix _nup21 --nup 2 1 --frame --width 0.87 --delta 0cm 0cm --paginate --overwrite --text \"$filename\" 0.4 0.005'
cmdstr_splitted = shlex.split(cmdstr)
#print(cmdstr_splitted)
pdftools.main(cmdstr_splitted)