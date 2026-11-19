@echo off
rem Windows, inside this set folder (Mock_A01 ...):
rem   judge     judge the whole set (double-click works too)
rem   judge 3   judge problem 3 only        (PowerShell: .\judge 3)
rem   judge progress   show solved problems
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  python "..\Judge\judge.py" %1
) else (
  py -3 "..\Judge\judge.py" %1
)
if "%~1"=="" pause
