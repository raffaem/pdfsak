REM This example rotate the pages of a input PDF file.
REM The 2nd page is rotated 90 degrees counterclockwise.
REM The 3rd page is rotated 180 degrees counterclockwise (it will be upside down).
REM The 4th page is rotated 270 degrees counterclockwise.
REM The 5th page is rotated 45 degrees counterclockwise.

python ..\..\..\pdfsak --input-file ..\..\input\numbered.pdf --output ..\..\output\rotate_pages.pdf --rotate-pages "2=90;3=180;4=270;5=45" 
