@echo off
title PhishGuard Backend
cd /d "%~dp0backend"
if not exist .venv (
  echo Creating Python environment...
  python -m venv .venv
  if errorlevel 1 goto fail
)
call .venv\Scripts\activate.bat
echo Installing Python packages...
python -m pip install -q -r requirements.txt
if errorlevel 1 goto fail
if not exist .env python make_env.py
echo.
echo Backend running at http://localhost:8001   (API docs: http://localhost:8001/docs)
echo Keep this window open. Press Ctrl+C to stop.
echo.
python -m uvicorn app.main:app --port 8001
goto end
:fail
echo.
echo Backend setup failed. Read the error above, then run this file again.
pause
:end
