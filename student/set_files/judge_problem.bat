@echo off
rem Windows, inside this problem folder:
rem   judge     judge this problem (double-click works too)        (PowerShell: .\judge)
rem   judge progress   show solved problems
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  python "..\..\Judge\judge.py" %1
) else (
  py -3 "..\..\Judge\judge.py" %1
)
if "%~1"=="" pause
