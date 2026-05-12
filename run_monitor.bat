@echo off
setlocal
if not exist .venv (
  echo Virtual environment not found. Run install_windows.bat first.
  exit /b 1
)
call .venv\Scripts\activate
python -m monitor_5070ti.main
