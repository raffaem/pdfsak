@echo off
echo WARNING: You need py2exe python module for this (pip install py2exe)
rmdir /s /q dist
py -3.4 -m py2exe.build_exe --bundle-files 0 --compress pdftools.py
upx.exe --best dist/pdftools.exe
