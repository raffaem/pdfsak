@echo off
REM This example swap the pages of an input PDF file

python ..\..\..\pdfsak --input-file ..\..\input\numbered.pdf --output ../../output/swap_pages_end.pdf --swap-pages "31,32"
