@echo off
REM This example adds:
REM - Page numbers in the bottom right corner (in the format `current_page/total_pages`)
REM - Current date in the top left corner (in the format `day/month/year`)

python ..\..\..\pdfsak --input-file ..\..\input\article1.pdf --output ..\..\output\addtext.pdf --text "\huge $page/$pages" br 1 1 --text "\huge $day/$month/$year" tl 0 0
