@echo off
REM Run all the scripts

goto input

:input
cls
set /p response=Press (1) for MiKTeX or (2) for TexLive: 
if %response%==1 goto miktex
if %response%==2 goto texlive
echo Invalid answer
pause
goto exit

:miktex
SET PATH=C:\Users\vbox\AppData\Local\Programs\MiKTeX\miktex\bin\x64\;%PATH%
goto run

:texlive
SET PATH=C:\texlive\2021\bin\win32;%PATH%
goto run

:run
call ..\..\pdfsak --check-all

RD /S /Q "..\output"
mkdir "..\output"
cd ".\scripts"

for /f %%a IN ('dir /b /s "*.bat"') do echo Calling "%%a" & call %%a

cd ..

:exit
