@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Ξεκινάει το Ktisis...
echo.
"%~dp0Ktisis.exe"
echo.
echo Το πρόγραμμα έκλεισε (κωδικός: %ERRORLEVEL%)
pause
