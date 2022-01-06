REM This example creates a 2x2 lecture handout
REM Every page of the output file is a 2x2 grid (2 rows and 2 columns)
REM The left columns will contain pages from the input PDF file
REM The right columns will be white

python ..\..\..\pdfsak --input-file ..\..\input\presentation.pdf --output ..\..\output\handout2x2_W.pdf --add-white-pages

python ..\..\..\pdfsak --input-file ..\..\output\handout2x2_W.pdf --output ..\..\output\handout2x2.pdf --nup 2 2 --height 0.32 --landscape --frame --paper a4paper

del ..\..\output\handout2x2_W.pdf
