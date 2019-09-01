#!/usr/bin/python3
#coding=utf8
import pdftools, sys, shlex
from os import path
white_path = path.splitext(sys.argv[1])[0]+"_W.pdf"
print(white_path)
cmdstr1 = "-i \""+sys.argv[1]+"\" --out-suffix _W --white-page --fitpaper --overwrite"
cmdstr2 = "-i \""+white_path+"\" --out-suffix _HANDOUT --nup 3 2 --frame --overwrite --paginate --delta 0mm 5mm --width 0.45"
cmdstr1_splitted = shlex.split(cmdstr1)
cmdstr2_splitted = shlex.split(cmdstr2)
pdftools.main(cmdstr1_splitted)
pdftools.main(cmdstr2_splitted)
