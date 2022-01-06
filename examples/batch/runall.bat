REM Run all the scripts

RD /S /Q "..\output"
mkdir "..\output"
cd ".\scripts"

for /f %%a IN ('dir /b /s "*.bat"') do call %%a
