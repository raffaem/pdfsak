@echo off
REM This example replaces the input PDF file instead of writing to a separate output file.

copy ..\..\input\numbered.pdf ..\..\output\replace_input.pdf

python ..\..\..\pdfsak --input-file ..\..\output\replace_input.pdf --replace-input --extract-pages "1"

