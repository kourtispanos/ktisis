@echo off
cd /d "%~dp0"
echo Ξεκινάει το Ktisis...
echo.
Ktisis.exe
echo.
echo Το πρόγραμμα έκλεισε (κωδικός: %ERRORLEVEL%)
pause
