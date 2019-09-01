#!/usr/bin/python3
#coding=utf8
import pdftools, sys, shlex, os

white_path = os.path.splitext(sys.argv[1])[0]+"_W.pdf"
#print(white_path)
cmdstr1 = "-i \""+sys.argv[1]+"\" --out-suffix _W --white-page --fitpaper --ignore-existent"
cmdstr2 = "-i \""+white_path+"\" --nup 2 2 --height 0.32 --delta 0mm 0mm --landscape --out-suffix _HANDOUT --frame --overwrite --paginate --paper a4paper -t \"$filename\" 0.4 0.01"
cmdstr1_splitted = shlex.split(cmdstr1)
cmdstr2_splitted = shlex.split(cmdstr2)
pdftools.main(cmdstr1_splitted)
pdftools.main(cmdstr2_splitted)
#os.remove(white_path)