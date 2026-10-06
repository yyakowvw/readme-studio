@echo off
rem Windows: double-click this file to set up your GitHub profile.
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
where py >nul 2>nul && (set PY=py -3) || (set PY=python)
if not exist .venv\Scripts\python.exe (
  echo Preparing readme-studio ^(first run only^)...
  %PY% -m venv .venv || (echo Install Python 3 from https://www.python.org/downloads/ and try again. & pause & exit /b 1)
  .venv\Scripts\python -m pip install --quiet --disable-pip-version-check -r requirements.txt
)
.venv\Scripts\python -m studio init %*
pause
