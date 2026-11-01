@echo off
title PhishGuard Frontend
cd /d "%~dp0frontend"
if not exist node_modules (
  echo Installing frontend packages...
  call npm install
  if errorlevel 1 goto fail
)
echo.
echo Website running at http://localhost:5173
echo Keep this window open. Press Ctrl+C to stop.
echo.
call npm run dev
goto end
:fail
echo.
echo Frontend setup failed. Read the error above, then run this file again.
pause
:end
