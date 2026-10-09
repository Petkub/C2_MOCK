@echo off
rem Windows:  judge     judge the whole set
rem           judge 3   judge problem 3 only
rem           judge progress   show solved problems
setlocal
cd /d "%~dp0"
set "ARG="
if not "%~1"=="" set "ARG=%~n1.cpp"
where py >nul 2>nul
if errorlevel 1 (
  python "..\Judge\judge.py" %ARG%
) else (
  py -3 "..\Judge\judge.py" %ARG%
)
if "%~1"=="" pause
