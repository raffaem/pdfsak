@echo off

REM Run all the scripts

SET PATH=C:\Users\vbox\AppData\Local\Programs\MiKTeX\miktex\bin\x64\;%PATH%
call ..\..\pdfsak --check-all

RD /S /Q "..\output"
mkdir "..\output"
cd ".\scripts"

for /f %%a IN ('dir /b /s "*.bat"') do echo Calling "%%a" & call %%a

cd ..
