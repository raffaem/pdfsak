@echo off
REM This example merge 2 input PDF files together in a single output PDF file

python ..\..\..\pdfsak --input-file ..\..\input\article1.pdf --input-file ..\..\input\article2.pdf --output ..\..\output\merge.pdf
