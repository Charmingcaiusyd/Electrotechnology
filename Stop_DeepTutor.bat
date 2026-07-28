@echo off
setlocal
cd /d "D:\Backup\Documents\EC"

set "PS1=D:\Backup\Documents\EC\scripts\Stop-DeepTutor.ps1"
if not exist "%PS1%" (
  echo Error: stop helper not found: "%PS1%"
  pause
  exit /b 1
)

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%PS1%"
set "EXITCODE=%ERRORLEVEL%"
if not "%EXITCODE%"=="0" (
  echo.
  echo DeepTutor stop script returned exit code: %EXITCODE%
  pause
  exit /b %EXITCODE%
)

endlocal
