@echo off

REM Run all the scripts

SET PATH=C:\texlive\2021\bin\win32;%PATH%
..\..\pdfsak --check-all

RD /S /Q "..\output"
mkdir "..\output"
cd ".\scripts"

for /f %%a IN ('dir /b /s "*.bat"') do call %%a
